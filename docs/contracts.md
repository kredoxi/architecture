# Reference, identity, provider and runtime contracts

**Status:** grammar, request/response and policy below are reconciled to the core
MVP implementation session's reported contract on 2026-10-31. Runtime test
results remain core-repository evidence, not tests executed here. Requirements
for production providers and additional hardening are identified separately.
No compatibility baseline existed before this initial reconciliation.

## Reference grammar v1

Canonical example:

```dotenv
DATABASE_PASSWORD=kredoxi://v1/demo/example/password
```

The namespace `demo` is a logical policy namespace, not a vault hostname.
`example` is a logical resource, `password` a field. The MVP uses the configured
synthetic provider; future operator-owned mappings may select providers.
References contain no
credential, broker endpoint, cloud token or access authority.

ABNF-style grammar (quoted literals are case-sensitive):

```text
reference = %s"kredoxi://v1/" segment "/" segment "/" segment
segment   = lower *31(tail)
lower     = %x61-7A
digit     = %x30-39
tail      = lower / digit / "-"
```

The equivalent segment regex is:

```text
[a-z][a-z0-9-]{0,31}
```

Segments are 1-32 ASCII bytes, start with a lowercase letter and allow subsequent
lowercase letters, digits and hyphens, including a trailing hyphen.
The whole reference is at most 111 ASCII bytes.
Exactly three nonempty path segments follow the version authority. The parser
must consume the whole input: no trimming, substring detection or interpolation.
Reject uppercase, Unicode, controls, percent encoding (including double
encoding), backslashes, dot segments, duplicate/trailing slashes, query,
fragment, port, userinfo and extra path segments. Do not URL-decode or use a
generic URI normaliser to repair input. Canonicalisation is validation followed
by identity, not lossy transformation.

Ordinary non-reference strings are not resolver inputs. Configuration adapters
only call resolution for designated reference fields; a string starting with
`kredoxi:` but not conforming must fail rather than pass through as a password.
No scheme registration with the OS or public URI registry is implied.

| Example | Result |
| --- | --- |
| `kredoxi://v1/demo/example/password` | Valid canonical reference |
| `kredoxi://v1/a/b/c` | Valid minimum segments |
| `kredoxi://v1/a/b/c-` | Valid trailing hyphen |
| `kredoxi://v1/demo/example/password?version=2` | Reject query |
| `kredoxi://v1/demo/../password` | Reject traversal |
| `kredoxi://v1/demo/%65xample/password` | Reject encoding |
| `kredoxi://v1/Demo/example/password` | Reject case |
| `kredoxi://v1/demo/example/password/` | Reject trailing slash |
| `prefix-kredoxi://v1/demo/example/password` | Reject substring |
| `kredoxi://v2/demo/example/password` | Unsupported version, no downgrade |

`v1` versions reference semantics, independently of API/event versions and
provider value versions. Introduce future grammar versions explicitly; no
automatic rewrite or fallback. Secret rotation changes provider values behind
a stable reference. Policy names are compared as exact canonical bytes.

## Identity and authorisation

The demo principal is an enrolled client certificate with exactly one accepted
URI SAN:

```text
urn:kredoxi:principal:demo-consumer
```

Compare the complete enrolled URI, not display names/CN or substrings.
Do not infer a reference-segment grammar for all future principal identifiers.
Verify the trusted issuer chain,
validity window, client-auth EKU and enrolled principal. Reject missing,
ambiguous/multiple accepted principal SANs or malformed identity. Successful TLS
authentication does not imply authorisation.

The client verifies the broker's enrolled trust root and server endpoint
SAN/server-auth EKU; never use `InsecureSkipVerify` or accept a caller-selected
trust store through the reference. Require TLS 1.3, disable secret-bearing
early-data/replay paths, and do not use session resumption in the first demo
unless reauthentication/expiry semantics are tested.

This is **key-holder identity**, not executable identity. Caller process name,
PID, headers or JSON identity claims are never trusted. Same-user theft of the
key and malicious code inside an enrolled process remain Tier 2/3 limits.
Broker/private provider credentials are separate from consumer credentials.
Control-plane policy/enrollment changes are offline operator actions, not
`resolve` permissions.

Policy is an immutable startup snapshot. Implemented format:

```json
{
  "version": 1,
  "allow": {
    "urn:kredoxi:principal:demo-consumer": [
      "kredoxi://v1/demo/example/password"
    ]
  }
}
```

Resolution is the sole operation; there is no action or provider-mapping field
in this policy. Exact allowlisted reference strings are matched for the enrolled
principal. No wildcards, prefix match, regex, inherited grants or client-selected
provider/endpoint.
No match is denial; authenticated-but-disallowed returns no value and does not
invoke the provider. Unknown and denied references have the same public error
category to limit enumeration; restricted events can distinguish categories.
The demo verifies a SHA-256 policy pin independently compiled into its trusted
binary, computed over bytes produced by `json.Compact`. This removes insignificant
JSON whitespace but does not sort keys; key ordering still affects the pin.
It detects changes relative to that demo trust anchor, not replacement of the
binary itself. Version denotes policy format, not a monotonic revision.
Changing policy requires validated restart and a corresponding trusted pin.
Production signature/anti-rollback enforcement is not implemented.

Additional schema hardening requires rejection of duplicate/unknown fields and
malformed rules; do not infer those tests solely from successful pin validation.

Production enrollment, certificate renewal/revocation and separation of service
accounts require a later decision. Short-lived certs reduce, not eliminate,
key-theft exposure. Each request must enforce current identity/policy lifetime,
including persistent connections; previous authorisation cannot be cached.

## Provider contract

Implemented MVP interface:

```go
type Provider interface {
    Resolve(context.Context, Reference) (string, error)
}
```

`Reference` is the parsed canonical reference authorised by the broker before
the provider call. The synthetic provider returns a generated 64-character hex
string. It exposes no enumeration/write/delete/list operation or production
provider endpoint. The trusted synchronous synthetic implementation honours
deadlines; a Go context cannot preempt an arbitrary blocking provider.

String return values and runtime/JSON/TLS copies prevent guaranteed erasure.
Owned-byte values, version/expiry metadata, bounded output and provider-neutral
typed errors are future contract proposals, not current interface fields.
Future adapters must honour cancellation themselves or run in a separately
bounded process; do not claim in-process timeout forcibly stops backend work.
They require least-privilege mapping, explicit failure and sanitised errors.

The synthetic provider creates only synthetic data in memory, has no external
credentials and is explicitly development/test-only. Do not persist generated
secrets or commit authentication keys/certificates. Future encrypted local,
Azure, GCP and CyberArk adapters need least-privilege provider identity, expiry,
rotation, cancellation and dependency/licensing review before activation.

## Runtime contract

Implemented API: `POST /v1/resolve` on an operator-enrolled loopback
endpoint. Verify loopback at bind/connect, not just an untrusted hostname.
No public listener, redirects, proxy-environment discovery, endpoint supplied
by reference, insecure HTTP fallback, batch resolve, list or write operation.

Request (`Content-Type: application/json`):

```json
{"reference":"kredoxi://v1/demo/example/password"}
```

The request has exactly `reference`, with no body schema_version or principal
claim. `/v1/resolve` versions the protocol. Server-generated request IDs correlate
events/responses; unauthenticated clients cannot access the provider.
Strict input hardening must reject unsupported methods/paths/content encoding,
unknown or duplicate fields, invalid UTF-8/JSON and trailing values; the
core-repository test evidence establishes which checks are implemented.

Implemented response fields are `value`, `error` and `request_id`. `value` and
`error` have omitempty semantics: success includes value; failure includes error
and must omit value. The synthetic demo value is a generated 64-character hex
string, not a base64 field. It is secret-bearing test data and must never appear
in diagnostics. No response schema_version, provider version or expiry field
is currently reported; those require future explicit protocol evolution.

Failure responses must contain no resolved value, raw provider detail, arbitrary
input echo or certificate dump. An encoded secret is still a secret; neither
hex nor any future base64 representation is safe to log.

| Outcome | Future hardening target, not confirmed current status table |
| --- | --- |
| Malformed input/schema/reference | 400 / `invalid_request` |
| Authenticated denied or unknown reference | 403 / `access_denied` |
| Unsupported method/content type | 405 / `invalid_request`; 415 / `invalid_request` |
| Oversized input | 413 / `request_too_large` |
| Concurrency/rate limit | 429 / `resource_limit` |
| Provider or required event sink unavailable | 503 / `unavailable` |
| Provider deadline | 504 / `timeout` |
| Internal non-secret failure | 500 / `internal` |

No caching is implemented. The core session reports these configured limits:

| Resource | Configured MVP bound |
| --- | --- |
| Live sockets, including before TLS | 16 |
| Concurrent resolutions | 8 |
| MaxHeaderBytes | 4096, plus Go HTTP parser-buffer allowance; not an exact total wire cap |
| Request body | 1024 bytes |
| Client parsed response | 2048 bytes |
| JSON nesting | Depth 8 |
| Header/read/write/idle | 1 / 2 / 4 / 2 seconds |
| Provider/client/shutdown | 2 / 8 / 5 seconds |

These are reported settings, not measurements or security tests executed here.
Only the trusted synchronous synthetic provider honours its deadline; arbitrary
provider preemption is not implemented. A per-principal rate limiter, production
value cap/expiry contract and durable event-sink deadline remain future hardening
decisions. Response caching must be disabled; no plaintext/stale fallback.

## Event contract v1

Use structured local JSON events with OS-native sinks/EDR collection as future
adapters, not a mandatory proprietary backend. The confirmed event fields are
`schema_version`, `timestamp`, `event_type`, `request_id`, optional `principal_id`
and `reference_id`, `authentication_method`, `policy_decision`, `provider_id`,
`status`, optional `error_category`, `agent_version` and `mode`.
Illustrative decision event (alias values are not literal runtime pseudonyms):

```json
{
  "schema_version": 1,
  "timestamp": "2026-10-31T00:00:00Z",
  "event_type": "resolution_decision",
  "request_id": "demo-request-001",
  "principal_id": "demo-enrolled-consumer",
  "authentication_method": "mtls-uri-san",
  "reference_id": "demo-ref-001",
  "policy_decision": "allow",
  "provider_id": "synthetic",
  "status": "authorised",
  "agent_version": "development",
  "mode": "enforce"
}
```

The MVP emits schema_version 1 events with keyed per-run principal/reference
pseudonyms, `mtls-uri-san` authentication, decision, synthetic provider,
status/error/category/version/mode. IDs above are illustrative aliases, not
literal emitted pseudonyms or hashes of secrets. Per-run keys make cross-run
correlation intentionally unstable; stable operational pseudonyms need a
separate protected telemetry-key lifecycle. Bare hashes of guessable reference
names are vulnerable to dictionary recovery.

The core `resolved` status denotes an audited release attempt, not client
receipt or application use. A future independently managed observer is required
to report process termination reliably.

Unavailable principal/reference and absent errors use optional fields; do not
fabricate authenticated identity. Provider remains the configured synthetic
provider label, not a caller-selected value. Unknown/unbounded input is never echoed.
Never record values (including base64), master/private keys, tokens, unnecessary
environment data, body/header dumps or raw provider errors. Enforce mode records
decisions that actually gate release; audit-only mode cannot imply denial.

Event sink failures are explicit. Require successful decision/release-attempt
writes before release, with bounded sink latency. A successful durable write
does not establish tamperproofing, receipt or application use. Protect files
and retention, and avoid log floods and disk exhaustion.
