# ADR 0001: explicit local resolution before transparent interception

Date: 2026-10-31

Status: **Accepted** — explicitly accepted by the Kredoxi owner on 2026-10-31.
This decision authorizes the documented synthetic MVP architecture only; it
does not authorize production use, relaxed controls or scope expansion.

## Context

The useful first protection is consumer configuration without credentials plus
authenticated, exact scoped runtime access. Arbitrary applications do not
interpret Kredoxi URIs. [Mechanism research](../mechanisms.md) shows that hooks,
loaders, VFS and proxies affect only specific operations, with platform and
failure risks. OS enforcement is not provided by a user-mode daemon alone.

## Decision

Use Go and its standard library for an explicit resolver client and local
loopback IPv4 HTTPS broker using mutually authenticated TLS 1.3. Bind
`127.0.0.1` on an ephemeral port, trust a dedicated caller-supplied CA and use
the exact URI-SAN principal. Start with one synchronous in-memory synthetic
provider and exact-reference deny-by-default policy. Use the
[v1 grammar and identity contract](../contracts.md). No production vault,
cloud dependency, driver, Kubernetes deployment or native hook is required.

Go offers portable TLS/HTTP/context/test facilities, memory safety for ordinary
code, maintainability and a bounded local build. Its GC/string/runtime copies
mean we cannot promise complete zeroisation. Rust is a credible later choice for
components needing tighter memory ownership, but changing language does not
solve authorised caller exfiltration or privileged memory inspection.

Application configuration integration is deliberate and non-transparent.
Authentication proves an enrolled key holder, not which executable is running.
The synthetic same-account demo is not a defence against same-user key theft.

## Alternatives

| Alternative | Reason not selected first |
| --- | --- |
| In-process resolver/provider only | Smaller but no independently exercised broker boundary or unauthorised transport test |
| OS-native broker IPC first | Stronger OS-account evidence possible, but Linux/Windows semantics require separate adapters/provisioning; next milestone |
| Bearer-token loopback HTTP | Token theft/replay and insecure-transport risk; standard-library mTLS is available |
| Loader/native hooks | ABI/bypass/secure-execution exclusions and reentrancy; not a portable enforcement boundary |
| VFS or Windows minifilter | Caching/size/read compatibility and privileged lifecycle complexity |
| Launcher env/argv injection | Moves plaintext into inspectable process inputs; undermines narrow residence goal |
| Credential-injecting proxy | Useful for named protocols, not arbitrary configuration; destination/auth/TLS design needed |
| Cloud/Kubernetes first | Unnecessary dependencies/privileges for a local synthetic vertical slice |

## Consequences, behavior and evidence

Positive: configuration remains reference-only; broker policy/access events are
testable; providers and transports can be replaced independently.

Costs: consumers change; cert enrollment becomes sensitive material; TLS/JSON
copies and consumer memory contain values; outages are explicit. No root/admin
tamper prevention, per-executable identity or production key lifecycle is
claimed.

Core uses a policy-before-provider ordering: it authenticates the client
certificate before handling the request and checks the exact
principal/reference allowlist before provider lookup. An
unauthorised principal receives `policy_denied` without a provider query, so
cannot distinguish an existing credential from a nonexistent one. An
allowlisted reference absent from the synthetic provider returns
`secret_not_found`; existence is distinguishable to that already-authorised
principal. The owner accepts this scoped disclosure boundary. Wildcard
authorisation, reference listing and unauthorised provider probing are
prohibited. See [contracts](../contracts.md) for exact status semantics and the
information tradeoff.

The pinned [Core protocol source](https://github.com/kredoxi/kredoxi/blob/1896d0c25ca0efca7790f671a8de3c654eb49bc0/docs/protocol.md)
and current implementation/tests are the cross-repository conformance
reference. Architecture CI checks relevant grammar, policy, protocol, limits
and event fields against that live Core contract where available.

The [test strategy](../testing.md) maps threat boundaries and contract
assertions to the implemented Core tests and future hardening gates. Core's
synthetic demo has run and passed in its own session; this Architecture
repository does not claim to have rerun the Go suite.

Revisit after evidence for OS-peer IPC, one configuration-loader adapter and a
handle-based launcher or narrow proxy. The long-term product is not SDK-only.
Any compatibility/security shift needs its own ADR and adversarial tests.

## Acceptance

The owner explicitly accepted this ADR and the documented 403/503 disclosure
tradeoff on 2026-10-31, conditional on authentication and exact-reference
authorisation preceding every provider lookup. The Architecture PR remains open
and unmerged until its CI and remaining review gates pass. This ADR acceptance
does not approve production use, a licence, relaxed security controls or MVP
scope expansion.
