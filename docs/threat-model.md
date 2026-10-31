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
| Reference replay/enumeration | Tiers 1-2 | mTLS and exact allowlist before provider lookup, T03/T04/T13/T21 | Unallowlisted caller cannot enumerate provider existence; allowlisted caller can distinguish absent provider entry via `secret_not_found` |
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
