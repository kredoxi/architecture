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
| T03 | Unknown reference | Fixed denied/not-found public category; no value or enumeration detail |
| T04 | Unenrolled/unauthorised caller | TLS reject or policy deny; provider invocation count remains zero |
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

Fuzz reference and strict request parsing; include exact 1/63/64-byte segment
boundaries, 204-byte whole-reference cap and wire value limits. Unit tests alone
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

## Documentation validation in this repository

Review R01-R14 against this matrix and the PR's A1-A5 assertions. Check local
Markdown destinations/anchors, fences, JSON examples, grammar boundaries and
`git diff --check`. Run cARL status/doctor/effective/trace and reconcile generated
map/memory using the current CLI. External source retrieval establishes
references, not perpetual URL availability. No core build/security test is
claimed by these checks.
