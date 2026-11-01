# Phase 4: workload identity, endpoint trust, and deployment isolation

**Status:** evidence and decision package only. ADR 0002 remains **Proposed —
decision deferred; not accepted**. ADR 0001 remains Accepted and unchanged.
Nothing here selects or implements a production IPC transport, workload
enrollment system, or production identity model.

## Executive finding

Native IPC can enforce an OS-account boundary when endpoint ownership and
permissions are correctly configured and the peer is authorized from
kernel/token identity. The current experiments do **not** make two
applications running as the same UID/SID distinguishable. Same-account Linux
endpoint replacement and same-SID Windows access/duplicated-handle reuse were
observed. Distinct OS identity is account identity, not executable identity.

The new fake-endpoint tests also show that endpoint reachability is not broker
authentication: the isolated test client accepts a synthetic response from an
attacker-created socket or pipe. The tested request exposes a reference and
false identity claims, but contains no credential or private key. This is not
evidence about the production mTLS client or a production IPC protocol.

**Decision disposition:** keep ADR 0002 Proposed and defer a transport choice
until the owner states the required deployment identity boundary. Windows
cross-SID access denial and actual remote-host denial remain unmeasured.
Combined IPC+mTLS enforcement, workload identity enrollment, production
credential lifecycle, and comparative performance were not tested.

## Evidence provenance and reproducibility

Core PR A is [kredoxi/kredoxi#6](https://github.com/kredoxi/kredoxi/pull/6),
currently open. Its current head is
[`3ca30d9ec17527cc877b7cbdfb7a7e895e60a27a`](https://github.com/kredoxi/kredoxi/commit/3ca30d9ec17527cc877b7cbdfb7a7e895e60a27a).
The Phase 4 experiment tests were added in commit
[`9cae544d85ececd814e2977f0e32741ec1b9b773`](https://github.com/kredoxi/kredoxi/commit/9cae544d85ececd814e2977f0e32741ec1b9b773).
Comparing that commit with the current head shows only the Core plan and
`experiments/ipc/README.md` changed afterward; the Linux and Windows test
source files are unchanged. The final-head CI run therefore validates the
current experiment test source.

| Evidence source | Exact environment and result |
|---|---|
| [Core CI run 41341767034](https://github.com/kredoxi/kredoxi/actions/runs/41341767034), head `3ca30d9` | `governance`, `test (ubuntu-latest)`, and `test (windows-latest)` all completed successfully. |
| [Linux job 124953610811](https://github.com/kredoxi/kredoxi/actions/runs/41341767034/job/124953610811) | Native GitHub-hosted `ubuntu-24.04`, Go `1.27.3 linux/amd64`. The IPC tests, `go test ./...`, build, vet, race/fuzz, formatting, vulnerability and repeat-build checks passed. |
| [Windows job 124953612318](https://github.com/kredoxi/kredoxi/actions/runs/41341767034/job/124953612318) | Native GitHub-hosted Microsoft Windows Server 2025 (`10.0.26100`, `windows-2025-vs2026` image), Go `1.27.3 windows/amd64`. The IPC tests, `go test ./...`, build, vet, formatting, vulnerability and repeat-build checks passed; the race/fuzz step was skipped by workflow design. |
| [Governance job 124953611883](https://github.com/kredoxi/kredoxi/actions/runs/41341767034/job/124953611883) | The pinned cARL governance check passed. |

Core PR #6 documents the focused reproducible command as
`go test ./experiments/ipc -count=1 -v`; the final CI logs also show the
individual native test names and outcomes below. Linux uses the already
present `nobody` account via a helper run as `sudo -n -u nobody` for the
distinct-UID cases. The tests verify the helper's actual UID differs from the
broker UID; they do not create or alter an account. Windows fake-pipe tests use
the current runner token SID and do not provision another account or service
identity. The Windows experiment did not inspect or record the runner token's
administrator membership or integrity level, so no claim is made about those
privileges. No administrator/root attacker was tested. Linux's use of `sudo`
to switch to `nobody` is not a privileged-attacker test.

This Architecture report did not execute Core tests locally. CI output,
source and the Core experiment README are the evidence. A successful CI job
does not convert a skipped, unavailable, or unimplemented scenario into a
pass.

## Identity properties: keep the boundaries separate

| Property | Evidence or mechanism | Establishes | Does not establish |
|---|---|---|---|
| Endpoint access | Linux pathname directory/socket permissions; Windows pipe DACL | Whether an OS token can connect to or manipulate a particular endpoint under that ACL and namespace configuration | That the endpoint is the intended broker, that the caller is a particular program, or that the caller is benign |
| Consumer OS identity | Linux `SO_PEERCRED`; Windows pipe client token/SID during impersonation | Kernel/token-reported account context for the tested connection/message | Executable identity, code integrity, package provenance, or per-process separation inside one account |
| Broker authentication | The client must authenticate the endpoint before trusting a response | Identity of the server only if a validated mechanism and trust policy are actually used | The fake-endpoint experiments implement no broker-authentication check; endpoint names, permissions and randomness do not substitute |
| Exact-reference authorization | Broker derives a principal from trusted evidence and applies the exact allowlist before provider lookup | Permission for one principal/reference/action when the policy check is performed | Authentication, endpoint authenticity, secret custody, or permission to other references |
| Transport confidentiality/integrity | TLS 1.3/mTLS on the accepted ADR 0001 path; local IPC has its own OS/protocol properties | Confidentiality/integrity only for a transport that is actually configured and verified | That layering two transports creates independent protection or binds a key to a process |
| Key custody and proof | mTLS proves possession of an accepted private key | A caller possessing the key can authenticate as that key's principal | Which process has the key, whether it is non-exportable, or whether the process is trustworthy |
| Executable integrity/provenance | No mechanism in these experiments | Nothing | Neither UID/SID, PID, process name, path nor an unbound file hash proves the running executable |
| Lifecycle and handles | Tested endpoint creation/stale-name cases, Windows pipe name reuse, duplicated connected-handle reuse | The specific tested create/cleanup/cancellation/handle outcomes | Production service install/update/restart/recovery, universal race resistance, key rotation/revocation, or termination monitoring |
| Tamper resistance and health | None implemented by the experiments | Nothing | A local event or successful write does not prove durable ingestion, application consumption, anti-tamper, anti-rollback or health |

Authentication and authorization remain separate. A real future broker must
derive a principal from validated OS/key evidence, authorize the exact
reference before provider lookup, and preserve ADR 0001's
`policy_denied` / authorized `secret_not_found` boundary. The experiment's
`TestRequestValidationAndAuthorizationOrder` passed, but that is a synthetic
test-protocol assertion, not production IPC integration.

## Experiment results and evidence state

“Observed” below means the named test passed in the native run. “Configured
only,” “blocked,” and “not measured” are not passes.

| Scenario and test | Expected behavior | Observed result | Evidence state and limit |
|---|---|---|---|
| Linux client connects to attacker-created socket: `TestLinuxClientAcceptsSyntheticFakeBroker` | Client authenticates broker before trusting a response. | The fake server observes the connected peer's actual UID plus the reference and deliberately false UID/PID/principal claims, sends a synthetic response, and the test client accepts it. The raw request is checked for synthetic value/private-key material. | **Observed:** this experiment client does not authenticate its broker. A reference is disclosed to the reachable fake endpoint. The test request contains no credential/private key; no production client behavior or real-secret disclosure is established. |
| Windows client connects to attacker-created pipe: `TestWindowsClientAcceptsSyntheticFakeBroker` | Client authenticates broker before trusting a response. | The fake pipe is ACLed for the current token SID, observes the actual impersonated client SID and false claims, returns a synthetic response, and the test client accepts it. The request is checked for value/private-key material. | **Observed:** this experiment client does not authenticate its broker. The request exposes its reference, not a credential/private key. This is same-SID test evidence only. |
| Linux different UID attempts endpoint replacement: `TestLinuxDifferentUIDCannotReplaceBrokerEndpoint` | Unrelated UID cannot rename or unlink a broker-owned endpoint, even if the socket mode is broad. | On native Ubuntu CI, the test's broker-owned immediate directory was mode `0700`; the socket was deliberately `0666`. The existing `nobody` UID's rename and unlink operations were denied, and the original socket remained the same file. | **Observed** for that actual UID, directory, mount, runner and test. Ancestor directories, mount configuration, ACLs, namespaces and group effects were not audited or varied. Do not generalize to every deployment. |
| Linux unrelated UID access/policy: `TestLinuxDistinctUIDDeniedByKernelAndPolicy` and `TestLinuxDifferentUIDBlockedBySocketMode` | Kernel permissions or OS-derived peer policy deny an unrelated UID. | Both passed on native Ubuntu CI. The peer-policy case exercises the actual distinct UID and `SO_PEERCRED`; the socket-mode test uses the specific tested mode/parent configuration. | **Observed** for those setups. No GID/supplementary-group matrix was run. UID policy is not executable identity. |
| Linux same-account endpoint replacement: `TestLinuxSameAccountCanReplacePathnameEndpoint` | Same-UID process is distinct from the intended client or cannot substitute its pathname endpoint. | Passed on native Ubuntu CI; the test demonstrates same-account replacement. | **Observed:** same-UID processes share the tested filesystem authority. Native IPC does not distinguish their applications on this evidence. |
| Linux pre-created/stale pathname: `TestLinuxEndpointPrecreationAndStalePathFailClosed` | Existing or stale endpoint path is not silently trusted or removed unsafely. | Passed on native Ubuntu CI for the test cases. | **Observed** for those cases only; not a proof against every startup/restart race, parent-directory substitution or privileged actor. |
| Copied mTLS key on Linux: `TestLinuxCopiedSyntheticMTLSKeyWorksFromDifferentUID` | Key proof should not be confused with OS account identity. | Passed on native Ubuntu CI: a helper given the synthetic enrolled key authenticated from a different UID. | **Observed:** key possession is reusable when the key is copied. This is not combined IPC+mTLS enforcement, production key custody, or evidence that mTLS itself identifies an OS process. |
| Windows DACL and same-SID peer: `TestWindowsPipeDACLAndSameAccountPeerIdentity` | Explicit ACL and OS token identity are applied; same-SID access works. | Passed on native Windows CI. | **Observed** for same-SID access. Different-SID denial was not measured. |
| Windows impersonation failure/restoration: `TestWindowsImpersonationFailureFailsClosed` and `TestWindowsRestorationIsVerifiedBeforeThreadUnlock` | Fail closed on the injected invalid-handle failure and verify restoration order. | Both passed on native Windows CI. | **Observed** for the test-injected failure and tested restoration ordering; no real `RevertToSelf` failure or privileged cross-identity authorization was induced. |
| Windows overlapped cancellation: `TestWindowsOverlappedReadTimeoutWaitsForCancellation` | Do not release pending I/O resources before cancellation completion. | Passed on native Windows CI; the test creates a pending read and verifies follow-on behavior after timeout/cancellation. | **Observed** for the test lifecycle. Draining has no second deadline and could wait indefinitely if I/O never completes. |
| Windows names and handles: `TestWindowsPipeFirstInstanceAndNameReuse`, `TestWindowsDuplicatedClientHandleRetainsAccess` | Reject occupied first-instance creation; establish name-reuse and connected-handle behavior. | Both passed on native Windows CI. A duplicated connected handle retains access. | **Observed:** endpoint name ownership does not revoke a handle already duplicated to a process. Arbitrary handle inheritance and all restart races were not tested. |
| Windows cross-SID access | DACL denies a caller with a different SID. | No second Windows SID/account was available; no identity was simulated. | **Blocked / not measured.** The configured DACL is not evidence of cross-SID denial. |
| Windows remote-host access | Remote client is denied. | `TestWindowsRemotePipeDenialFlagIsConfigured` was explicitly skipped because no authorized remote host was available. | **Configured only / not measured.** No remote connection was attempted. |
| IPC plus mTLS | Both controls are required and add a stated independent protection. | No combined enforcement test or production path exists. | **Not measured.** No defense-in-depth or independent-factor claim is supported. |
| Application consumption, workload health, key lifecycle or rollback | Observe that the workload consumed the value and can recover/rotate safely. | Not exercised by these endpoint tests. | **Not measured.** A synthetic response accepted or a transport write completed is not proof of application consumption, continued health, durable telemetry or lifecycle operation. |

The names and results above appear in the final Core run's native job output.
The broader CI suite also reports passing build, `go test ./...`, vet,
formatting, vulnerability and build-integrity checks. Linux race and configured
fuzz checks passed; Windows skipped the race/fuzz step by workflow design.
These checks do not expand the scope of the IPC assertions.

## Threat and deployment implications

### Endpoint and broker trust

The Linux `0700` parent blocked the tested unrelated UID from replacing or
unlinking a `0666` socket. That depends on the immediate directory's tested
owner/mode and on trusted parent/mount/namespace setup. A same-UID process
successfully replaced the pathname. The experiment did not audit the complete
directory ancestry or demonstrate a deployment-safe service manager,
mount/namespace policy, or administrator/root-resistant endpoint.

The fake broker tests are direct endpoint-trust evidence. A reachable fake
endpoint can read the request reference and choose the synthetic response
accepted by the test client. The request intentionally contains false
identity fields, which are observations rather than authority; the fake
servers inspect OS peer context independently. The tests explicitly do not
send a secret or private key in the IPC request, so they show metadata
exposure and missing server authentication in the experiment, not actual
credential theft from a production workload. No process name, executable path
or hash is an acceptable substitute for a validated broker identity.

Pre-created/stale names fail closed in the named Linux and Windows tests, but
this is not a proof against every endpoint replacement, broker restart or
namespace race. Windows pipe DACL enforcement was exercised only for the
current SID; duplicating an already-connected handle preserves access.
Impersonation verifies client-side token context for server authorization; it
does not authenticate the server to the client.

### Same-account and attacker boundaries

**Native IPC alone cannot distinguish two applications running under the
same UID/SID on the evidence available here.** Kernel credentials and Windows
access tokens identify an OS principal. If two processes share that principal,
both receive the same account-level authority unless a separately reviewed,
independent control supplies additional trustworthy evidence. The tests
demonstrate same-account endpoint replacement/access and do not establish
process isolation.

A privileged administrator/root/kernel attacker is analytical threat-model
context only. No privileged attacker, endpoint takeover by such an actor, host
security change, or anti-tamper control was tested. Such an attacker can
generally replace user-mode binaries/configuration, inspect or terminate
processes, access privileged material and interfere with local telemetry.

### Workload identity and deployment lifecycle

No experiment enrolls a workload identity, creates a broker service identity,
maps an OS principal to policy, protects a per-workload key, or rotates,
revokes, recovers or removes those identities. These are deployment design
questions, not implemented controls. Any production option must specify:

- which authority provisions broker and workload identities, and whether
  consumers use one shared account or separate least-privilege accounts;
- exact endpoint owner, DACL/ACL, parent-directory and mount/namespace
  requirements, and how startup rejects a substituted endpoint;
- how identity-to-principal policy is enrolled, versioned, changed and rolled
  back without widening exact-reference authorization;
- how keys are created, protected, rotated, revoked and recovered, and whether
  key proof is genuinely independent of the OS account boundary;
- install, upgrade, startup/readiness, restart, outage, recovery and removal
  behavior, including stale endpoint cleanup and in-flight/duplicated handles;
- the supported OS/version matrix and negative tests for each identity and
  endpoint policy.

The copies, unit tests and CI do not measure installation effort, operations
cost, availability, latency, throughput or comparative performance. Do not
claim a cost or performance win. Observability must distinguish trusted OS
principal evidence, authentication, authorization, delivery attempt,
successful transport write, application consumption, and independent health.
The broker cannot claim consumption merely because a write succeeded.
Telemetry must remain redacted and must not enumerate provider references or
expose secrets; cancellation does not prove that every buffer or inherited
handle has been erased.

## Deployment candidate comparison

| Candidate | Security boundary and evidence | Enrollment, key custody and operations | Residual risk, support and cost |
|---|---|---|---|
| **1. Shared user** — broker and consumers run under one account | All processes share the OS principal. Linux same-UID endpoint replacement and Windows same-SID access/handle reuse are observed. | Simplest install, start/restart and removal; no per-workload OS enrollment. Does not remove the need to protect any mTLS key. | No application-to-application boundary. One compromised process can use the shared account's endpoint/key access. Lowest operational complexity, but cannot satisfy per-workload isolation. |
| **2. Dedicated broker; consumers share a separate account** | A distinct broker account can own a protected endpoint; Linux shows an existing unrelated UID denied modification in one `0700` directory configuration. Windows cross-SID enforcement remains unmeasured. All consumers still share one principal. | Requires provisioning/service ownership, ACL/DACL and namespace setup, startup ordering, update/restart/recovery and removal procedures. None was deployed or tested. | Can separate broker resources from consumers only when each OS boundary is configured correctly; compromise of the shared consumer account affects all its workloads. Platform support and operating burden are unmeasured. |
| **3. Dedicated broker and per-workload OS identities** | OS identity could scope each workload only if the OS/runtime supplies that principal at the actual endpoint/policy boundary. No workload identity provisioning or per-workload experiment exists. | Requires workload enrollment/mapping, least-privilege identity creation, policy updates, rotation/revocation, upgrade, restart, recovery and deprovisioning. | Better account-level scope is a design possibility, not a proven app identity. Same-identity compromise remains in scope; deployment complexity and cross-platform behavior are unmeasured. |
| **4. Dedicated identities plus cryptographic key proof** | Could require both OS-principal authorization and proof of a separately protected enrolled key. The copied-key test shows a copied synthetic mTLS key authenticates from a different UID; combined IPC+mTLS enforcement is untested. | Adds key generation/custody/enrollment/rotation/revocation/recovery to dedicated identity and endpoint lifecycle. Independent protection must be demonstrated, not assumed from two checks. | If the key is readable/copyable by the same workload or account, the checks may fail together. More moving parts and no measured independent security gain, platform support, cost or performance benefit. |
| **5. Existing explicit mTLS only** | ADR 0001's accepted synthetic baseline authenticates key possession and protects the TLS channel, then applies exact-reference policy. Copied-key experiment confirms another process that receives the key can act as its key holder. No OS-account or executable identity is claimed. | Preserves current design and portable path. Production enrollment, key custody, rotation, revocation, recovery and deployment hardening remain future design work. | No local account boundary; key theft/reuse and same-account compromise remain. Lowest architecture change now; security-support claims remain limited to the evidence in Core. |

This is a qualitative comparison, not a measured ranking of implementation or
operational cost. No option is selected by this report.

## ADR 0002 decision package

**Proposed disposition for owner review: defer the decision; retain ADR 0002 in
Proposed status.** The current evidence is enough to state that Linux
pathname permissions and `SO_PEERCRED` can provide an account-level boundary
in the tested setup, and that endpoint access does not authenticate the
broker. It is not enough to claim equivalent Windows cross-SID/remote
enforcement, application identity, independent combined factors, or
production workload identity.

Before accepting an option, the owner must decide:

1. Is one shared consumer account acceptable, or must every workload have a
   distinct OS principal? Is a dedicated broker identity mandatory?
2. Are clients strictly same-host, or must any supported deployment allow
   remote clients?
3. If both IPC and mTLS are proposed, what distinct threat does each prevent,
   how are their credentials independently protected, and what test proves the
   combined requirement?
4. Which OS/version and identity-provider/lifecycle contracts are support
   requirements, and who provisions, owns, rotates, revokes and recovers them?
5. Which authorized disposable Windows environment will measure cross-SID
   DACL denial and actual remote-host denial? Which deployment-specific parent,
   mount, startup/restart and duplicated-handle cases are required?

If a later deployment contract requires distinct workload identities, evaluate
candidate 3 and candidate 4 against that explicit requirement. If same-user
workloads must remain mutually isolated, none of these experiments proves that
OS-account native IPC can achieve it. Do not accept ADR 0002, modify ADR 0001,
select a transport, or implement production IPC from this evidence alone.

## Evidence links

- [Core PR #6](https://github.com/kredoxi/kredoxi/pull/6), current head
  [`3ca30d9`](https://github.com/kredoxi/kredoxi/commit/3ca30d9ec17527cc877b7cbdfb7a7e895e60a27a)
- [Core Phase 4 test-source commit `9cae544`](https://github.com/kredoxi/kredoxi/commit/9cae544d85ececd814e2977f0e32741ec1b9b773)
- [Core experiment README at current head](https://github.com/kredoxi/kredoxi/blob/3ca30d9ec17527cc877b7cbdfb7a7e895e60a27a/experiments/ipc/README.md)
- [Core Linux tests at current head](https://github.com/kredoxi/kredoxi/blob/3ca30d9ec17527cc877b7cbdfb7a7e895e60a27a/experiments/ipc/ipc_linux_test.go)
- [Core Windows tests at current head](https://github.com/kredoxi/kredoxi/blob/3ca30d9ec17527cc877b7cbdfb7a7e895e60a27a/experiments/ipc/ipc_windows_test.go)
- [Core CI run 41341767034](https://github.com/kredoxi/kredoxi/actions/runs/41341767034)
- [Phase 3 evidence report](native-ipc-identity-evidence.md)
- [ADR 0002](adr/0002-native-ipc-identity-evaluation.md)
