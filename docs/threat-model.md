# Tiered threat model

## Assets and assumptions

Assets include credential values; reference metadata; future vault encryption
keys; provider tokens; enrollment keys; process/OS context; policy/mappings and
trust anchors; telemetry; agent configuration and binaries. References are not
secrets, but names can expose infrastructure.

Assume intact reviewed binaries, trusted OS/TLS, correct enrollment, exact
deny-by-default policy and synthetic provider data. The MVP does not provide a
production vault, sandbox, anti-debugging, EDR enforcement or signed/anti-rollback
policy. These assumptions must be verified, not inherited as guarantees.

## Capability tiers

| Tier | Attacker capability | Intended protection | Explicit limit |
| --- | --- | --- | --- |
| 1: passive artefact theft | Reads source, `.env`, YAML, JSON, TOML or config without runtime control | Consumer configuration reveals references, not values; references alone cannot authenticate | Names may reveal metadata; theft of enrollment keys adds a different capability |
| 2: unprivileged local compromise | Accesses files/processes permitted to the compromised account | Reject unenrolled or policy-mismatched clients; OS separation may protect broker material once tested | Same-user key theft, debugging and inherited handles can defeat credential-holder identity; same-account demo is not process isolation |
| 3: application compromise | Executes in an authorised consumer, including dependency compromise or RCE | Bound requests to the principal's exact allowlist and observe access | Attacker can retrieve permitted values, inspect memory and exfiltrate them; events do not prove legitimate intent |
| 4: privileged host compromise | Administrator/root, kernel or equivalent service control | External monitoring may observe failures | Attacker can replace binaries/policy/trust stores, inspect memory, steal keys, kill services and suppress logs; no EDR-grade tamper prevention |

An attacker who steals an enrolled private key is no longer merely stealing
non-secret application configuration. TLS authenticates that key holder; it
does not recognise malicious intent.

## Attack paths, controls and residual risks

| Attack path | Capability | Control/evidence gate | Residual risk |
| --- | --- | --- | --- |
| Source/config disclosure | Tier 1 | Scan consumer artefacts, T01 | Reference metadata and public synthetic fixtures remain visible |
| Reference replay/enumeration | Tiers 1-2 | Authenticate first; exact principal/reference allowlist before provider lookup, T03/T04/T13/T21 | Unauthenticated or unallowlisted callers cannot distinguish existing from nonexistent provider entries; an allowlisted caller can distinguish absence via `secret_not_found` |
| Stolen tokens/enrollment keys | Tiers 2-4 | Protected short-lived enrollment; future revocation | Key possession works until effective expiry/revocation |
| Asserted identity/PID reuse | Tier 2 | Transport-derived identity, reject body claims, T09 | Certificate is not OS/executable attestation |
| IPC abuse/cross-client confusion | Tier 2 | Authentication, generated IDs, limits, isolated buffers, T07/T12 | Local resource exhaustion remains possible |
| Environment inspection/dumps/memory scraping | Tiers 2-4 | No environment injection; leakage tests, T11/T16 | Application/runtime memory still contains values |
| Malicious dependency/application RCE | Tier 3 | Exact principal scope, observable requests, T16 | Authorised values can be exfiltrated |
| Compromised developer tool/AI assistant | Tiers 2-4 or supply chain | Synthetic-only access, restricted tools and reviewed governance | Tools with process/file authority can alter code or steal keys; cARL is not a sandbox |
| Agent termination | Tiers 2-4 | Explicit outage failure and independent observer, T06/T14 | No unkillable-service or uptime guarantee |
| Binary replacement/hook bypass | Tiers 2-4 | Future protected install/integrity evidence, T14/T15 | User-mode integration is bypassable by its application or privileged attacker |
| Configuration/provider redirection | Tier 2 | Operator mappings and enrolled server trust, T18 | Trusted operator/compromised broker can redirect |
| Symlink/reparse/TOCTOU | Tier 2 | Open-once snapshot, object/parent ACL validation, T18 | Checks require OS implementation; privileged races out of guarantee |
| Policy tamper/rollback/downgrade | Tiers 2-4 | Immutable snapshot and demo independently compiled compact-JSON SHA-256 pin, T15 | Intact binary required; not production signature trust or anti-rollback |
| Provider compromise | Trusted dependency compromised | Least privilege, output limits and redacted errors, T05/T19 | Provider knows values and can return malicious/stale data |
| Log/diagnostic leakage | Tiers 1-4 | Schema allowlist, pseudonyms, no bodies/raw errors, T11 | Caller/provider may log independently; OS dumps need deployment controls |
| Kredoxi supply-chain compromise | Build/install authority | Review, dependency checks, verified pinned tooling, release gate | A trusted malicious build can bypass user-mode controls |
| Flood/slow requests | Tiers 2-3 | Deadline/body/concurrency/rate limits, T20 | Host/authorised-client DoS not eliminated |
| Broker impersonation/TLS downgrade | Tier 2 | Verify server identity, TLS floor, no insecure retry, T17 | Stolen server key/replaced trust can impersonate |
| Event deletion/forgery | Tiers 2-4 | Protected sink, release gated on event write, T14 | Durability is not tamperproofing; privileged suppression remains possible |

## Enforcement versus observation

Authentication, exact policy, resource limits and tested OS permissions enforce
their specific boundaries. Health signals, audit events and integrity alerts
are observations. Detecting a replaced binary does not prevent replacement.

Tier 3 tests should intentionally demonstrate that a malicious authorised
consumer can retrieve its allowed value. That is a documented limitation,
not a failed claim of protection. Privileged/invasive tests belong only in
explicitly authorised disposable VMs; do not modify host security software.

The minimum useful claim is: under intact broker/enrollment/policy, stolen
consumer configuration reveals no credential, and a caller lacking an
authorised enrolled identity cannot resolve its reference. The
[test strategy](testing.md) defines proof gates; this repository does not claim
they have run. Parser unit tests do not establish process isolation, runtime
exfiltration prevention or privileged tamper resistance.

The owner accepted the scoped enumeration boundary in ADR 0001: authentication
and exact-reference authorisation must succeed before any provider lookup.
Unallowlisted principals receive `policy_denied` for both present and absent
references; only a principal already allowed a reference can observe
`secret_not_found`. No wildcard grants, reference listing or unauthorised
provider probes are permitted. Certificate possession remains key-holder
identity, not executable identity.

## Native IPC identity limits (research only)

Linux `SO_PEERCRED` can provide connection-time PID/real UID/real GID for
connected AF_UNIX sockets, while pathname socket permissions can enforce a
filesystem account/group boundary on Linux. Abstract sockets have no
filesystem ACL. Numeric PID follow-up can race with process exit and PID reuse;
neither PID nor UID/GID proves executable integrity. systemd sandboxing can
reduce broker privilege and filesystem reach, but is host-dependent and does
not authenticate IPC clients.

Windows named-pipe DACLs enforce access using caller access tokens, and pipe
impersonation can expose a client security context for authorization-sensitive
operations. The server must fail closed if impersonation fails. A service SID
can scope access to service-owned objects, but is not executable identity.
`GetNamedPipeClientProcessId` returns a PID, not a stable executable proof.
Pipe defaults are not least-privilege; specify and verify a DACL. Protected
services are an anti-malware-specific mechanism with ELAM/signing
prerequisites, not a generally available Kredoxi control.

These are source-backed capabilities, not controls implemented or tested here.
Distinct-account and IPC endpoint tests require disposable authorized
infrastructure; this repository has not run them. Neither OS peer credentials
nor mTLS prevents a compromised authorized consumer from reading its own
resolved secret from memory. See [Proposed ADR 0002](adr/0002-native-ipc-identity-evaluation.md)
and the [test strategy](testing.md) for the open transport alternatives and
evidence gates. Core PR A reports the limited native synthetic cases that did
run in the [Phase 3 evidence report](native-ipc-identity-evidence.md); it does
not establish production controls or executable identity.

## Phase 4 endpoint and workload-identity evidence (research only)

The [Phase 4 report](phase4-workload-identity-endpoint-trust.md) records
additional synthetic endpoint tests from Core PR A. Both native fake-endpoint
tests accept a synthetic response from an attacker-created socket/pipe because
the experiment client does not authenticate the broker. The request discloses
the reference and false identity claims but contains no credential or private
key; this is endpoint-trust/metadata evidence, not a production credential
theft result. Endpoint names, DACLs and random names are not server
authentication.

Linux's tested unrelated UID could not rename or unlink a socket inside the
broker-owned `0700` directory even when the socket mode was `0666`; the
directory's full ancestry, mounts, namespaces and group behavior were not
audited. A same-UID process successfully replaced the pathname. Windows tests
show same-SID pipe access and duplicated connected-handle reuse, but do not
measure cross-SID or remote-host denial. These results enforce or expose only
the tested OS-account/endpoint boundary.

The Linux endpoint results are separate experiments, not one three-principal
deployment proof: the `0700` broker-owned directory blocks the tested
unrelated UID from both replacement and traversal, whereas the `0711` peer
policy setup lets an unrelated UID connect and denies it before provider
lookup. No authorized distinct UID was shown resolving through the protected
endpoint while unable to replace it.

Consequently, native IPC alone cannot distinguish applications that share
the same UID/SID. PID, process name, executable path or an unbound hash does
not add executable identity. Broker authentication, exact-reference
authorization, channel protection, key custody, workload enrollment,
executable integrity, lifecycle and anti-tamper remain separate controls.
No combined IPC+mTLS, production workload identity, key rotation/revocation,
policy rollback, application consumption, performance, or privileged-attacker
test is established. ADR 0002 remains Proposed/deferred; see its Phase 4
decision package and the [roadmap](roadmap.md) for unresolved deployment
choices.
