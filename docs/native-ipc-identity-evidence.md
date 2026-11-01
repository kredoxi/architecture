# Phase 3: practical OS-identity evidence

**Status:** synthetic research evidence only. ADR 0002 remains **Proposed —
decision deferred; not accepted**. ADR 0001 remains accepted and unchanged:
explicit Go resolution over loopback mTLS 1.3. No production transport,
resolver, protocol, policy, telemetry, or platform-support change is made by
these experiments.

## Scope and evidence standard

Core PR A adds isolated test-only experiments under `experiments/ipc/` using
synthetic references, values, certificates, and keys. The tests exercise native
Unix pathname sockets on Linux and named pipes on Windows, then compare selected
observations with the existing mTLS key-holder model. The Architecture
repository did not run the Core Go tests; the results below are attributed to
Core source and CI.

“Observed” means the scenario ran against the named operating system and the
reported assertion passed. “Configured only” means an option was set but its
enforcement outcome was not exercised. “Blocked/not measured” means the
environment did not permit a conclusion. No result here is process or
executable attestation.

## Source revisions and runs

| Evidence | Revision / environment | What it establishes |
|---|---|---|
| [Initial detailed native CI run 41329082490](https://github.com/kredoxi/kredoxi/actions/runs/41329082490) | Test commit `dcd43347dc9ec350e1d1ae9c536608cf8669ee35`; Go 1.27.3; jobs `governance` (124915176485), `test (ubuntu-latest)` (124915176698), and `test (windows-latest)` (124915176717) | Historical detailed evidence for the initial experiment source |
| [Initial PR-head CI run 41329564731](https://github.com/kredoxi/kredoxi/actions/runs/41329564731) | Core PR #5 head `9b201887eb75c4b85eafc0ed86e8c2f077655859`; `governance` (124916614814), `test (ubuntu-latest)` (124916615130), and `test (windows-latest)` (124916615097) all successful | Historical checks for the earlier PR revision used by the original report |
| [Final Core PR #5 head](https://github.com/kredoxi/kredoxi/commit/0a7ade6282ee5effc33954eee801509fc81d90cb) | PR head `0a7ade6282ee5effc33954eee801509fc81d90cb`; includes Windows overlapped-I/O cancellation and restoration-order hardening | Final reviewed experiment source before merge |
| [Core PR-head CI run 41337784450](https://github.com/kredoxi/kredoxi/actions/runs/41337784450) | Exact PR head `0a7ade6282ee5effc33954eee801509fc81d90cb`; `governance` (124941175765), `test (ubuntu-latest)` (124941176024), and `test (windows-latest)` (124941176069) all successful | Native Linux/Windows tests, race/fuzz where supported, and governance on the final PR head |
| [Core PR #5](https://github.com/kredoxi/kredoxi/pull/5), merged | Merged 2026-11-01T18:43:30Z; merge commit `0c465c56a6732265bdad8ec3eba143a11b2a9895`; same experiment tree as final PR head | Establishes the final source revision on Core main |
| [Core main CI run 41338072128](https://github.com/kredoxi/kredoxi/actions/runs/41338072128) | Exact Core main merge commit `0c465c56a6732265bdad8ec3eba143a11b2a9895`; `governance` (124942039957), `test (windows-latest)` (124942040204), and `test (ubuntu-latest)` (124942040212) all successful | Post-merge default-branch verification |

The original report's run 41329082490 belongs to commit `dcd4334`; later
run 41329564731 belongs to `9b20188`. Core PR #5 then added commit
`e4b5484` ("Harden Windows IPC experiment cleanup") and finalized its head at
`0a7ade6`. The compare from `9b201887eb75c4b85eafc0ed86e8c2f077655859` to
that final head shows changes to the task contract/plan, experiment README, and
Windows experiment source. Therefore the original detailed Windows assertions
are historical; the final Windows changes are validated by run 41337784450
and were rerun on main by 41338072128. The merge commit has no file changes
relative to the tested final PR head, and current main CI is separately cited.

The reproducible experiment command is:

```sh
go test ./experiments/ipc -count=1 -v
```

At both final-head run 41337784450 and default-branch run 41338072128, Core
reports `go test ./...`, `go build ./...`, `go vet ./...`, `govulncheck`,
formatting checks and build-integrity checks passing. Native Linux race and
two five-second resolver fuzz jobs passed. The Windows race/fuzz job was
skipped by workflow design; the Windows README also documents that a local
race run was unavailable because that host had `CGO_ENABLED=0` and no GCC.
The exact fuzz command lines are visible in the Linux CI job logs, rather than
inferred from the README.

## Environment and identity model

**Linux:** native GitHub Actions `ubuntu-latest` runner; the job log identifies
Ubuntu 24.04.5 LTS / `ubuntu-24.04`. Go 1.27.3. In both final PR-head run
41337784450 and main run 41338072128, the cross-UID cases passed using the
already-existing `nobody` account via passwordless `sudo -n -u nobody`; the
job logs showed no skip. No account was created or modified. The test used a
traversable `0711` parent with a `0600` socket for kernel permission denial,
then a `0666` socket to exercise broker policy from the actual `SO_PEERCRED`
UID. These are disposable CI test settings, not deployment recommendations
or guarantees.

**Windows:** the local experiment environment is documented as Windows NT
`10.0.26300.0`, Go 1.27.3, `windows/amd64`. Native `windows-latest` CI on both
final PR head `0a7ade6` and merged main `0c465c5` passed the same-SID, token
restoration and overlapped-cancellation regression tests. The named-pipe DACL
was scoped to the current user SID; helper-process tests ran under the same
authorized SID. No separate Windows account/SID or remote Windows host was
available for a denial test. The remote-client-reject flag was configured,
not shown to reject an actual remote connection.

No experiment used real credentials, persistent accounts, or privileged
attacker access. Linux used passwordless switching only to the already-existing
`nobody` account; no account was created and no host security setting was
changed. No simulated cross-account identity was substituted.

## Scenario results

| Scenario | Expected | Observed | Evidence state and residual risk |
|---|---|---|---|
| Exact-reference policy and provider order | Deny unallowed references before provider lookup; an authorized missing reference may reach the provider and return `secret_not_found`. | `TestRequestValidationAndAuthorizationOrder` passed on native Linux and Windows in final-head run 41337784450 and main run 41338072128; denied requests recorded zero lookups and authorized missing references one lookup. | **Observed** in the synthetic test protocol only. Does not itself validate the production wire/API. |
| Linux peer identity and forged fields | Derive UID/GID/PID from `SO_PEERCRED`; request-supplied identity does not override it. | `TestLinuxPolicyDenialPrecedesLookup` and `TestLinuxSocketOwnerModesAndPeerIdentity` passed in native Linux runs 41337784450 and 41338072128. | **Observed** for connected socket credentials and test policy. UID is an account boundary, not code identity. |
| Linux endpoint permissions | With a traversable `0711` parent and `0600` socket, a different UID cannot connect. | `TestLinuxDifferentUIDBlockedBySocketMode` passed in both final-head and main Linux jobs; no skip. | **Observed** OS permission denial in that setup. It depends on trusted ownership and parent-directory integrity. |
| Linux copied-key mTLS comparison | A process given the synthetic enrolled key can authenticate independently of its OS UID. | `TestLinuxCopiedSyntheticMTLSKeyWorksFromDifferentUID` passed in runs 41337784450 and 41338072128. | **Observed** key-possession behavior. This is not a combined IPC+mTLS test; a key accessible to an attacker remains reusable. |
| Linux same-account process and endpoint substitution | Same UID can use the authorized account boundary; test whether it can replace a pathname endpoint. | `TestLinuxSameAccountCanReplacePathnameEndpoint` passed in both native Linux runs. | **Observed** same-account access and endpoint substitution. Path protections do not separate processes sharing directory-write access. |
| Linux pre-existing/stale endpoint and cleanup | Refuse occupied paths and avoid deleting a substituted path during cleanup. | `TestLinuxEndpointPrecreationAndStalePathFailClosed` passed in both final-head and main Linux jobs. | **Observed** only for tested lifecycle cases; no claim about every filesystem race or deployment lifecycle. |
| Windows named-pipe DACL and same-SID helper | Explicit current-SID DACL permits a same-SID helper and OS token identity, not request fields, supplies the caller SID. | `TestWindowsPipeDACLAndSameAccountPeerIdentity` passed in native Windows final-head run 41337784450 and main run 41338072128. | **Observed** same-SID access. Different-SID denial was **not measured**. |
| Windows impersonation failure | Failure fails closed without provider lookup or broker-token leakage. | `TestWindowsImpersonationFailureFailsClosed` passed on final PR head and main; it exercises an invalid handle. | **Observed** for the injected invalid-handle failure; a distinct real OS impersonation failure was not induced. |
| Windows successful impersonation/restoration | Observe the client SID for the request, then restore broker thread/process context. | Same-SID test and `TestWindowsRestorationIsVerifiedBeforeThreadUnlock` passed in native Windows runs 41337784450 and 41338072128. | **Observed** token context/order behavior; no real `RevertToSelf` failure was induced and this does not attest client code. |
| Windows overlapped timeout and cancellation | Cancel a timed-out pipe I/O and wait for terminal completion before releasing OVERLAPPED/event/buffer resources. | `TestWindowsOverlappedReadTimeoutWaitsForCancellation` creates a real pending read, times it out, and confirms the client can write after cancellation. It passed in both final-head and main Windows jobs. | **Observed** cancellation/completion ordering. Completion drain has no upper time bound; an OS operation that never completes can hold the caller indefinitely. |
| Windows pipe name and connected handles | Reject an occupied first-instance name; demonstrate name reuse after close and whether a connected handle can be duplicated. | `TestWindowsPipeFirstInstanceAndNameReuse` and `TestWindowsDuplicatedClientHandleRetainsAccess` passed in both final-head and main Windows jobs. | **Observed**. Possession of a connected handle remains a reusable capability. |
| Windows remote-client rejection | An actual remote Windows client is denied. | `TestWindowsRemotePipeDenialFlagIsConfigured` explicitly skipped in both final-head and main Windows jobs because no separate authorized remote host was available. | **Configured only / not measured**; do not claim remote denial. |
| Windows cross-SID denial | A client under a different SID is denied by the pipe DACL. | No separate Windows account/SID was available. | **Blocked / not measured**; no simulated identity substituted. |
| Malformed, duplicate, oversized, trailing, and concurrent requests | Reject invalid frames; preserve exact policy under concurrency and keep denied requests from provider lookup. | Shared malformed-input, policy, and concurrency tests passed on native platforms. | **Observed** in the bounded experiment protocol, not a production protocol conformance result. |
| Combined IPC and mTLS | If both are required, show a specific additional protection beyond either mechanism. | No combined authentication design was implemented or measured. | **Not measured**. No independent-factor or defense-in-depth claim is justified. |

The [merged Core README and native tests](https://github.com/kredoxi/kredoxi/tree/0c465c56a6732265bdad8ec3eba143a11b2a9895/experiments/ipc)
are the final source for scenario details. The Linux cross-UID results above
are limited to the exact `nobody`, socket-mode, and test-policy configurations;
they do not prove process integrity. The final PR-head and main Windows CI logs
confirm the named cancellation/restoration regressions passed and explicitly
record the remote-denial skip.

## Implemented, tested, and untested boundaries

- **Implemented for research:** test-only IPC protocol/servers, native peer
  identity acquisition, synthetic provider/policy, endpoint setup and cleanup,
  and OS-specific test helpers in Core PR A.
- **Tested:** the scenarios marked observed above on native operating systems.
  The cross-UID Linux boundary came from actual kernel permissions and
  `SO_PEERCRED`, not a mock. Windows same-SID/token behavior came from native
  named-pipe tests.
- **Configured but not proven:** Windows remote-client rejection flag.
- **Post-review Windows robustness coverage:** pending overlapped-I/O
  cancellation/completion draining and restored-thread-context verification
  before unlocking are covered by
  `TestWindowsOverlappedReadTimeoutWaitsForCancellation` and
  `TestWindowsRestorationIsVerifiedBeforeThreadUnlock`, respectively. Both
  passed in final PR-head run 41337784450 and merged-main run 41338072128.
- **Potential unbounded wait:** after cancellation, the Windows implementation
  waits for terminal I/O completion without a second deadline before releasing
  operation resources. This avoids releasing outstanding I/O state but may
  wait indefinitely if completion never arrives.
- **Not implemented or tested:** production IPC transport, production account
  enrollment/lifecycle, separate Windows SID denial, Windows remote-host
  denial, combined IPC+mTLS authentication, executable integrity or process
  attestation, anti-tamper enforcement, and production telemetry integration.

Cross-compilation is not runtime evidence. Same-UID or same-SID access is not
process isolation. Linux numeric PID, Windows client PID, process name, path,
hash, or request fields are not evidence of executable integrity. An authorized
or compromised process under the allowed account can use that account's IPC
permissions; a process that obtains a copied mTLS private key can act as its
key holder. Neither mechanism prevents an authorized application from reading
its own resolved value from memory. Root/administrator compromise, arbitrary
blocking-provider preemption, complete zeroization, and endpoint protection
against privileged replacement remain outside the evidence.

## Security claims not established by these experiments

- **Authorization and enumeration:** the synthetic test policy rejects
  unallowlisted references before provider lookup and returns
  `policy_denied` without revealing existence; the test's lookup counter
  remains zero. An authorized but absent reference can return
  `secret_not_found` after a lookup, so an already-authorized principal can
  distinguish absence. This confirms the experiment's policy order, not
  production IPC integration.
- **Fallback behavior:** no plaintext or alternate-transport fallback was
  added. The IPC experiment does not exercise production outage/fallback
  behavior and therefore is not proof of that separate control.
- **Credential exposure and lifecycle:** all values and keys are synthetic.
  The copied mTLS key is sent to a helper through a bounded stdin pipe; the
  test checks captured output/telemetry for key and value leakage. This says
  nothing about real-key storage, enrollment, rotation, revocation, secure
  deletion, memory dumps, or zeroization.
- **Endpoint, handle, and process lifecycle:** Linux tests report pre-existing
  and stale path handling, cleanup safety, and a successful same-account
  endpoint substitution. Windows tests cover occupied first-instance
  rejection/name reuse, duplicated connected-handle reuse, disconnect, and
  server shutdown without a client. These are bounded test lifecycles, not
  persistent-service recovery, termination monitoring, or immunity to
  same-account endpoint/handle manipulation.
- **Account versus process trust:** Linux UID and Windows SID/token checks
  identify OS account context only. Same-UID/SID processes can use the
  permitted endpoint; no measured mechanism proves executable integrity or
  code provenance.

## Decision matrix

| Option | Security gain supported by evidence | Residual risk / missing evidence | Complexity, portability and operations |
|---|---|---|---|
| **A. Keep mTLS only** | Preserves the accepted, portable key-holder authentication and TLS channel. The copied-key experiment demonstrates that possession is reusable by another process, including another UID when the key is copied. | No OS account boundary; key custody and same-account compromise remain decisive. | Existing baseline; lowest added platform-specific operational cost. |
| **B. Add native IPC as an optional local transport** | Linux tests show actual socket permission and peer-UID boundaries for different UIDs in the tested setup. Windows tests show same-SID access and token context, but not denial of a different SID. | Same-user/same-SID processes can use the boundary; endpoint substitution/handles remain concerns; Windows cross-SID and remote denial are unmeasured. No executable attestation. | Adds distinct transport, OS-specific packaging, endpoint lifecycle and policy mapping, support matrix, tests, and operational documentation. |
| **C. Replace mTLS for same-host traffic** | Could rely on OS account/token permissions where the deployment explicitly trusts those identities. | No experiment proves replacement is safe across supported Windows identities or future non-local use; loses mTLS key-holder authentication on that path; same-account callers remain allowed. | Couples enrollment, identity and transport to each OS; migration and portability costs are not measured. |
| **D. Require IPC and mTLS together** | Could require both OS-account access and an enrolled-key proof if a design keeps the two controls independently protected. | The combined path was not built or tested. Key custody may share the same account boundary, so an independent factor or material gain is unproven; both layers can add failure modes without stopping same-account code. | Highest lifecycle, key/endpoint, debugging, compatibility and support complexity; no performance measurement exists. |
| **E. Defer transport selection and implementation** | Keeps accepted ADR 0001 behavior while preserving the evidence and making the deployment identity question explicit. | Does not add OS-account separation to the current mTLS path. The current baseline remains key-holder authentication only. | No production migration cost now; requires owner choices and additional native denial tests before an ADR decision. |

## Recommendation for owner review

**Recommend option E for now: keep ADR 0002 Proposed and defer a transport
selection or implementation.** This is an evidence-based deferral, not a claim
that native IPC has no value. Linux demonstrates a useful distinct-UID
boundary in the tested configuration and shows why a copied mTLS key is a
separate capability. Windows demonstrates same-SID token behavior but lacks
the negative cross-SID and remote-host measurements needed for a comparable
claim. Same-account access and Linux pathname substitution also prevent a
process-isolation claim. The combined IPC+mTLS objective has no experiment.

If the intended deployment requires a broker boundary between distinct OS
accounts, the owner can request a scoped follow-up to test Windows cross-SID
denial and actual remote-client denial in authorized disposable environments,
then reassess optional native IPC against that explicit identity model. Do not
select option B merely from Linux results or imply that it secures processes
running under the same identity. Replacing mTLS or requiring both needs
additional explicit objectives and evidence.

## Owner decisions still required

1. Is a separate broker/service identity from each consumer a minimum supported
   deployment requirement, or are same-user applications within scope?
2. Must the broker support only same-host clients, or any non-local clients?
3. Which transport is to remain the supported baseline, if any future option is
   approved: mTLS only, optional local IPC, replacement for local clients, or
   a combined design with a stated independent protection objective?
4. Who provisions, owns, rotates, revokes, and recovers OS identities,
   endpoint permissions, and any mTLS material; what platform/version floor is
   required?
5. Before acceptance, which authorized environment will measure Windows
   cross-SID DACL denial and actual remote-client rejection, plus any
   deployment-specific endpoint replacement/handle lifecycle cases?

No performance comparison was run; do not infer latency, throughput, or cost
from these functional tests.

## Governance provenance

Core PR A separately reconciled its cARL v1.0.2 managed trust-boundary artifact
in commit
[1b9ab3a](https://github.com/kredoxi/kredoxi/commit/1b9ab3a2651581e04817e773e1daea09fc374f49):
the managed file was restored to the canonical artifact, while the
product-specific additive controls remain in Core's user-owned
`.github/carl/kredoxi-controls.md`. Those controls state that the stdin
bootstrap is development-only, process separation does not enforce OS identity,
and distinct-user enforcement, zeroization, and privileged-actor protection
are not established. This governance reconciliation is separate from the
native experiment results and does not change ADR 0002's status.

## Evidence references

- [Core experiment README at merged main revision](https://github.com/kredoxi/kredoxi/blob/0c465c56a6732265bdad8ec3eba143a11b2a9895/experiments/ipc/README.md)
- [Core Linux tests at merged main revision](https://github.com/kredoxi/kredoxi/blob/0c465c56a6732265bdad8ec3eba143a11b2a9895/experiments/ipc/ipc_linux_test.go)
- [Core Windows tests at merged main revision](https://github.com/kredoxi/kredoxi/blob/0c465c56a6732265bdad8ec3eba143a11b2a9895/experiments/ipc/ipc_windows_test.go)
- [Core common experiment tests at merged main revision](https://github.com/kredoxi/kredoxi/blob/0c465c56a6732265bdad8ec3eba143a11b2a9895/experiments/ipc/experiment_test.go)
- [Windows robustness commit `e4b5484`](https://github.com/kredoxi/kredoxi/commit/e4b5484de99e9789c1dcd634e1e0e3fbedb63ed5)
- [Final Core PR-head CI run 41337784450](https://github.com/kredoxi/kredoxi/actions/runs/41337784450)
- [Post-merge Core main CI run 41338072128](https://github.com/kredoxi/kredoxi/actions/runs/41338072128)
- [Historical Core PR-head CI run 41329564731](https://github.com/kredoxi/kredoxi/actions/runs/41329564731)
- [Historical detailed Core CI run 41329082490](https://github.com/kredoxi/kredoxi/actions/runs/41329082490)
- [ADR 0002: native IPC identity evaluation](adr/0002-native-ipc-identity-evaluation.md)
