# Test strategy and evidence gates

**Status:** required tests for the core MVP, not executed security tests in this
documentation repository. Source retrieval and cARL diagnostics are not evidence
of runtime security. Store actual commands, platform/tool versions and outcomes
with the core implementation PR.

## Synthetic vertical slice

Generate ephemeral test enrollment keys/certificates; never commit them.
Create a synthetic credential in a memory-only provider and consumer config
with the canonical reference. Start a loopback mTLS broker with an exact policy.
Authenticate the allowed consumer, resolve and use the bytes in a synthetic
operation, then discard owned buffers. Scan original consumer config for the
synthetic value; it must contain only the reference.

Capture redacted access events and independently verify no secret, base64 value,
auth key or token appears in diagnostics. Authenticate a denied principal and
try an unenrolled client: neither gets bytes or invokes the provider. Stop the
broker, fail the provider and fail the event sink: demonstrate explicit errors,
no stale/plaintext fallback and correct resource cleanup.

The demo must finish without leaving listeners, test keys or secret-bearing
artefacts. Printed output can say an operation succeeded, not print its value.

## Adversarial matrix

| ID | Test | Required observation |
| --- | --- | --- |
| T01 | Stolen config/source artefacts | Consumer config contains reference, not synthetic value; enrolled keys are kept separately |
| T02 | Invalid/overlong reference | Whole-string parser rejects wrong case/version/length/Unicode, not partial match |
| T03 | Unknown reference | For both present and absent references, an authenticated unallowlisted principal receives the same `policy_denied` response before provider lookup; an allowlisted but absent reference returns `secret_not_found` |
| T04 | Unenrolled/unauthorised caller | Authenticate before lookup; TLS rejects an unenrolled client, and exact policy denies an unallowlisted principal with no provider call or existence signal |
| T05 | Provider unavailable | Explicit sanitised error; no alternate/stale/plaintext fallback |
| T06 | Broker unavailable | Client error, not using reference as password; no orphan consumer work |
| T07 | Malformed IPC/API | Oversize, duplicate/unknown fields, invalid UTF-8/JSON, trailing values, compressed body rejected under limits |
| T08 | Traversal/encoding | Reject dots, slash/backslash, percent/double encoding, userinfo, query and fragment |
| T09 | Incorrect identity claim | Body/header/PID/name cannot affect transport-derived principal; wrong SAN/EKU/issuer/expiry rejected |
| T10 | Policy mismatch | Exact allowlist only; prefix/wildcard/action mismatch denied without provider call |
| T11 | Diagnostic leakage | Scan events/stdout/stderr/errors/traces for raw and encoded sentinel values; no body/key dumps |
| T12 | Concurrent clients | Different principals/values never share buffers, IDs or responses; run Go race tests |
| T13 | Repetition/replay/revocation | Reauthorise and emit events each request; wrong principal denied; expiry checked on persistent connections |
| T14 | Termination/event sink failure | Explicit consumer failure and external health observation where observer exists; no release on failed required event write |
| T15 | Tampered/rolled-back policy | Malformed policy rejected; immutable running snapshot unaffected; no false signed/anti-rollback claim |
| T16 | Authorised malicious consumer | Can retrieve/exfiltrate allowed synthetic value; document expected Tier 3 limit; other references denied |
| T17 | Broker impersonation/downgrade | Wrong server SAN/root/TLS version/redirect rejected; no insecure retry |
| T18 | Filesystem races/redirection | Test symlink/reparse, parent ownership, check/reopen race and caller endpoints; unsupported real-secret protections remain explicit |
| T19 | Rotation/cache/expiry | New request sees new provider version; expired/empty/oversized/shared-buffer values rejected; old delivered bytes cannot be recalled |
| T20 | DoS/slow client/provider/sink | Test exact size/concurrency/rate/deadline targets; bounded goroutines and cancellation; recovery after saturation |
| T21 | Enumeration boundary | Compare present and absent references for an authenticated unallowlisted principal: both return `policy_denied` and provider-call count stays zero. An allowlisted absent reference may return `secret_not_found`; prove no wildcard/list operation or unauthorised probe exists. |
| T22 | Linux IPC account boundary | In disposable Linux infrastructure, test pathname socket parent/socket ownership and modes with broker, authorized consumer, unrelated UID, and same-UID process; verify abstract sockets are not used as if filesystem ACLs applied |
| T23 | Linux peer and PID lifetime | Derive identity only from `SO_PEERCRED`; reject body/header/PID-name claims; force peer exit/reuse and test any `/proc`/image lookup race; do not treat a numeric PID as a stable process handle |
| T24 | Windows pipe DACL and token | In disposable Windows infrastructure, verify explicit pipe security descriptors against broker, intended consumer, unrelated SID/logon session, and remote client; ensure default DACL is not relied on |
| T25 | Windows impersonation | Verify authorization runs under the pipe client's impersonation token, checks failure, always reverts to self, and never executes privileged work after an impersonation failure |
| T26 | Process and executable claims | Spoof process names, request fields and PID-based lookup timing; show OS account/token or key-holder authentication is not executable integrity |
| T27 | Distinct OS identities | Run broker and consumer under separate disposable accounts/service identities and test key/config/endpoint access; report exact OS version, setup and privileges or mark blocked—not simulated |
| T28 | IPC handle/endpoint substitution | Test inherited/duplicated handles, endpoint pre-creation/replacement, stale socket cleanup, pipe instance access, and broker restart without identity fallback |
| T29 | Native telemetry mapping | Map existing event versions to journald/syslog or Event Log/ETW, test redaction and collector outage/loss; distinguish decision, attempted delivery, transport write and application consumption |
| T30 | Anti-tamper and rollback | Verify signed update/integrity and monotonic policy-version design in a disposable target; show that digest-only checks and successful local log writes do not establish anti-rollback or durable SIEM receipt |

Fuzz reference and strict request parsing; include exact 1/32/33-byte segment
boundaries, 111-byte whole-reference cap and wire value limits. Unit tests alone
do not prove OS isolation. Integration tests must cross the actual TLS boundary
and count provider calls for denied requests.

## Platform and safety gates

Run build, unit, integration, race, formatting, vet/static checks and dependency
analysis using the core repository's verified commands. Do not invent a green
command without executing it. Go race support/toolchain prerequisites vary by
target. Cross-compilation is not runtime compatibility evidence.

Only synthetic ordinary-user tests can run on developer hosts. Privileged
termination, debugging, driver, sandbox/namespace or invasive race tests require
disposable, explicitly authorised VM/container environments. Never disable EDR
or alter host security settings. Record unavailable tests as gaps.

Document GC/copy/zeroisation and dump limits; a successful log scan does not prove
memory erasure. OS-peer IPC needs peer credential, socket/DACL, fake endpoint,
handle inheritance and PID reuse tests on each OS. Hook/loader/VFS/proxy adapters
must prove the intended operation is intercepted and test bypass/outage, not
just show a resolver call.

Core PR A now reports a subset of the IPC account-boundary experiments in the
[Phase 3 evidence report](native-ipc-identity-evidence.md). Those results do
not close the remaining proof gates or establish a production transport;
anti-tamper, native telemetry, Windows cross-SID denial, and actual remote-pipe
denial remain unmeasured. Do not claim separate OS identities unless tests ran
in authorized disposable infrastructure. The current mTLS identity proves key
possession; IPC peer credentials prove only the OS identity scope documented
by each platform. Neither establishes that the authorized consumer used or
kept a credential safe.

## Documentation validation in this repository

Review R01-R14 against this matrix and the PR's A1-A5 assertions. Check local
Markdown destinations/anchors, fences, JSON examples, grammar boundaries and
`git diff --check`. Run cARL status/doctor/effective/trace and reconcile generated
map/memory using the current CLI. External source retrieval establishes
references, not perpetual URL availability. No core build/security test is
claimed by these checks.
