# Reference, identity, provider and runtime contracts

**Status:** v1 design baseline, not a claim that these fields/interfaces exist in
the core implementation. The cross-repository agreement is Go explicit
resolution, loopback TLS 1.3 mTLS, exact-reference policy, synthetic memory
provider, the reference and principal examples below. Wire/event/provider
details require reconciliation with implementation before declaring conformance.

## Reference grammar v1

Canonical example:

```dotenv
DATABASE_PASSWORD=kredoxi://v1/demo/example/password
```

The namespace `demo` is a logical policy namespace, not a vault hostname.
`example` is a logical resource, `password` a field. Only the operator's mapping
selects providers and underlying provider identifiers. References contain no
credential, broker endpoint, cloud token or access authority.

ABNF-style grammar (quoted literals are case-sensitive):

```text
reference = %s"kredoxi://v1/" segment "/" segment "/" segment
segment   = lower [*61(tail) final]
lower     = %x61-7A
digit     = %x30-39
tail      = lower / digit / "-"
final     = lower / digit
```

The equivalent segment regex is:

```text
[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?
```

Segments are 1-63 ASCII bytes, start with a letter, end in a letter/digit and
allow interior hyphens. The whole reference is at most 204 ASCII bytes.
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

Principal suffixes use the segment rule above; compare the complete canonical
URI, not display names/CN or substrings. Verify the trusted issuer chain,
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

Policy is an immutable schema-valid startup snapshot. Proposed example:

```json
{
  "schema_version": 1,
  "revision": 1,
  "allow": [
    {
      "principal": "urn:kredoxi:principal:demo-consumer",
      "action": "resolve",
      "reference": "kredoxi://v1/demo/example/password"
    }
  ],
  "mappings": [
    {
      "reference": "kredoxi://v1/demo/example/password",
      "provider": "synthetic",
      "key": "demo-example-password"
    }
  ]
}
```

Reject unknown fields, duplicate JSON keys/rules/mappings, invalid references,
unsupported schema/actions and missing referenced providers. No wildcards,
prefix match, regex, inherited grants or client-selected provider/endpoint.
No match is denial; authenticated-but-disallowed returns no value and does not
invoke the provider. Unknown and denied references have the same public error
category to limit enumeration; restricted events can distinguish categories.
Changing policy requires validated restart. Revision is provenance, not a
trusted monotonic anti-rollback control.

Production enrollment, certificate renewal/revocation and separation of service
accounts require a later decision. Short-lived certs reduce, not eliminate,
key-theft exposure. Each request must enforce current identity/policy lifetime,
including persistent connections; previous authorisation cannot be cached.

## Provider contract

Proposed Go interface, separate from any concrete implementation package:

```go
type Provider interface {
    Resolve(ctx context.Context, key string) (Secret, error)
}

type Secret struct {
    Value     []byte
    Version   string
    ExpiresAt time.Time
}
```

`key` comes only from an authorised broker mapping. It is not a caller path,
URL or CLI command. `Resolve` honours deadlines/cancellation, is concurrency
safe and transfers ownership of a fresh value buffer to the broker. Return
neither a shared mutable slice nor secret-bearing error text. A zero expiry
means the provider declares no expiry, not permission to cache forever.
Version is non-secret opaque provenance; no enumeration/write/delete/list API
is exposed to consumers.

Reject empty or oversized values (MVP cap 16 KiB), expired values, invalid
version metadata and unavailable providers explicitly. Provider errors use
typed categories such as `not_found`, `unavailable`, `timeout`, `invalid_value`
and `internal`; the broker never forwards raw backend errors. Clear owned
buffers on every path, without claiming complete runtime zeroisation.

The synthetic provider creates only synthetic data in memory, has no external
credentials and is explicitly development/test-only. Do not persist generated
secrets or commit authentication keys/certificates. Future encrypted local,
Azure, GCP and CyberArk adapters need least-privilege provider identity, expiry,
rotation, cancellation and dependency/licensing review before activation.

## Runtime contract

Proposed API: `POST /v1/resolve` on an operator-enrolled literal loopback
endpoint. Verify loopback at bind/connect, not just an untrusted hostname.
No public listener, redirects, proxy-environment discovery, endpoint supplied
by reference, insecure HTTP fallback, batch resolve, list or write operation.

Request (`Content-Type: application/json`):

```json
{"schema_version":1,"reference":"kredoxi://v1/demo/example/password"}
```

Reject unsupported methods/paths, content encoding, unknown or duplicate
fields, invalid UTF-8, malformed JSON, multiple JSON values and unsupported
schema. A body cannot declare principal identity. Server generates its own
request identifier; unauthenticated clients fail before provider access.

Success fields: `schema_version` (1), `request_id` (opaque server identifier),
`value_base64` (encoded provider bytes), `version` (opaque provider version),
`expires_at` (UTC RFC3339 or null). Base64 is a wire encoding, not encryption
or a safe-to-log value. Response bytes are secret-bearing and must never appear
in logs, caches, error diagnostics or screenshots. Clients validate bounded
base64, expected schema and expiry before use.

Failure fields: `schema_version`, `request_id`, `error` (fixed category).
No plaintext body, raw provider detail, parsed arbitrary input or certificate
dump is returned.

| Outcome | Proposed HTTP status/category |
| --- | --- |
| Malformed input/schema/reference | 400 / `invalid_request` |
| Authenticated denied or unknown reference | 403 / `access_denied` |
| Unsupported method/content type | 405 / `invalid_request`; 415 / `invalid_request` |
| Oversized input | 413 / `request_too_large` |
| Concurrency/rate limit | 429 / `resource_limit` |
| Provider or required event sink unavailable | 503 / `unavailable` |
| Provider deadline | 504 / `timeout` |
| Internal non-secret failure | 500 / `internal` |

All responses disable caching with `Cache-Control: no-store`. MVP limits are
4 KiB request bodies, 16 KiB raw secret values, 32 active requests, 10-second
total request/write deadline and a 5-second provider deadline within it.
Apply an enrolled-principal rate limit (initial target 10 requests/second,
burst 20), plus unauthenticated connection limits. These are design targets,
not benchmarks or implemented-limit claims. Bound TLS handshake/header reads
and reject excess work without spawning unbounded goroutines.

## Event contract v1

Use structured local JSON events with OS-native sinks/EDR collection as future
adapters, not a mandatory proprietary backend. Proposed decision example:

```json
{
  "schema_version": 1,
  "timestamp": "2026-10-31T00:00:00Z",
  "event_type": "resolution_decision",
  "request_id": "demo-request-001",
  "principal_id": "demo-enrolled-consumer",
  "authentication_method": "mtls",
  "reference_id": "demo-ref-001",
  "policy_revision": 1,
  "decision": "allow",
  "provider_id": "synthetic",
  "status": "authorised",
  "error_category": null,
  "agent_version": "development",
  "mode": "enforce"
}
```

Event types include decision, release attempt, resolution failure and health.
IDs above are public example aliases, not hashes of secrets. Use operator-owned
opaque aliases in the MVP. If a later sink uses HMAC pseudonyms, its separate
protected telemetry key needs rotation and lifecycle design. Bare hashes of
guessable reference names are vulnerable to dictionary recovery.

Unauthenticated/malformed requests omit identity/reference/provider when
unavailable; do not fabricate them. Unknown/unbounded input is never echoed.
Never record values (including base64), master/private keys, tokens, unnecessary
environment data, body/header dumps or raw provider errors. Enforce mode records
decisions that actually gate release; audit-only mode cannot imply denial.

Event sink failures are explicit. Require successful decision/release-attempt
writes before release, with bounded sink latency. A successful durable write
does not establish tamperproofing, receipt or application use. Protect files
and retention, and avoid log floods and disk exhaustion.
