# ADR 0001: explicit local resolution before transparent interception

Date: 2026-10-31

Status: selected architecture baseline for the requested MVP; implementation
properties remain subject to core-repository evidence.

## Context

The useful first protection is consumer configuration without credentials plus
authenticated, exact scoped runtime access. Arbitrary applications do not
interpret Kredoxi URIs. [Mechanism research](../mechanisms.md) shows that hooks,
loaders, VFS and proxies affect only specific operations, with platform and
failure risks. OS enforcement is not provided by a user-mode daemon alone.

## Decision

Use Go and its standard library for an explicit resolver client and local
loopback mutually authenticated TLS 1.3 broker. Start with one synthetic
in-memory provider and exact-reference deny-by-default policy. Use the
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
| Bearer token loopback HTTP | Token theft/replay and insecure-transport risk; standard-library mTLS is available |
| Loader/native hooks | ABI/bypass/secure-execution exclusions and reentrancy; not a portable enforcement boundary |
| VFS or Windows minifilter | Caching/size/read compatibility and privileged lifecycle complexity |
| Launcher env/argv injection | Moves plaintext into inspectable process inputs; undermines narrow residence goal |
| Credential-injecting proxy | Useful for named protocols, not arbitrary configuration; destination/auth/TLS design needed |
| Cloud/Kubernetes first | Unnecessary dependencies/privileges for a local synthetic vertical slice |

## Consequences and evidence

Positive: configuration remains reference-only; broker policy/access events are
testable; providers and transports can be replaced independently.

Costs: consumers change; cert enrollment becomes sensitive material; TLS/JSON
copies and consumer memory contain values; outages become explicit application
failures. No root/admin tamper prevention, per-executable identity or production
key lifecycle is claimed.

The [test strategy](../testing.md) must demonstrate allowed/denied resolution,
outages, no config/diagnostic leakage, malformed requests, concurrency and the
authorised-malicious-caller limitation before calling the MVP working.

Revisit after evidence for OS-peer IPC, one configuration-loader adapter and a
handle-based launcher or narrow proxy. The long-term product is not SDK-only.
Any compatibility/security shift needs its own ADR and adversarial tests.
