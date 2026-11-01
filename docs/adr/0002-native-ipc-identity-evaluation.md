# ADR 0002: evaluate native IPC and OS-backed caller identity

Date: 2026-10-31

Status: **Proposed — decision deferred; not accepted**

This document records research and alternatives for owner review. It does not
change [ADR 0001](0001-explicit-local-resolution.md), select a transport, approve
implementation, or claim platform support. ADR 0001 remains accepted: the
synthetic MVP uses explicit Go resolution over loopback mutual TLS 1.3.

## Context

The current transport authenticates possession of an enrolled client key and
protects the TLS channel. It does not establish the caller's OS account,
process, or executable identity. A native local IPC endpoint can ask the OS to
enforce endpoint access and expose kernel-authenticated peer credentials, but
the evidence and semantics are platform-specific.

The question is whether a future local deployment should retain mTLS, add an
OS-native IPC transport alongside it, or replace mTLS for same-host traffic.
This ADR intentionally leaves that decision open. Process separation alone is
not a distinct security identity, and neither a PID nor a process name is
executable attestation.

## Identity properties are not interchangeable

| Evidence | What it establishes | What it does not establish |
| --- | --- | --- |
| mTLS client certificate | A peer proved possession of a private key accepted by the configured trust policy; TLS protects the connection against eavesdropping, tampering, and message forgery | Which OS account, process, or executable used the key; whether an authorized process is benign |
| Linux `SO_PEERCRED` | Kernel-reported peer PID, real UID, and real GID captured at connection time for supported connected Unix sockets | Executable identity, code integrity, or a permanent binding between a later PID lookup and the original process |
| Windows named-pipe access check | The caller's access token was allowed the requested pipe access by the pipe security descriptor's DACL | That the caller is a particular executable or that it will behave benignly |
| Windows pipe impersonation token | The server thread can act under the client security context associated with the last message read, subject to token/privilege rules | Executable integrity or a safe identity if impersonation fails and the server continues under its own token |
| PID/process name/path | A locator or descriptive value that can help monitoring or investigation | Authentication, authorization, a stable process handle, or executable integrity |
| Executable signature/hash check | Evidence about the inspected file bytes at the time and through the mechanism checked | That the running process still maps those bytes, that the check was race-free, or that the process is uncompromised |

Authorization remains a separate decision: derive a principal from trusted
transport or OS evidence, then apply the exact principal/reference policy
before provider lookup. Never accept caller-supplied PID, account name, image
path, executable hash, or principal headers as authority.

## Linux: Unix-domain sockets

Linux `AF_UNIX` pathname sockets support local stream communication and
`SO_PEERCRED`, which returns credentials in effect when `connect`, `listen`, or
`socketpair` established the connection. For pathname sockets Linux checks
directory permissions at creation and socket write permission on stream
connect; this socket-mode behavior is not portable POSIX security semantics.
Linux abstract-namespace sockets have no filesystem ownership or permission
controls. A deployment relying on path ACLs therefore needs a protected parent
directory, deliberate owner/group/mode, safe endpoint creation and cleanup, and
tests against endpoint replacement and stale sockets.

`SO_PEERCRED` supplies an OS account boundary, not application identity. If the
consumer and another process run as the same UID, UID-based policy does not
distinguish them; file and key access granted to that UID is likewise generally
available to its processes. GID and PID can add context but do not turn an
account into an executable identity. The returned PID is a numeric process
identifier, not a lifetime-stable handle. If the process exits, a later lookup
by PID can race with PID reuse; even a stable process reference would not stop
that process from calling `exec` or prove its loaded code is trustworthy.
Avoid a check-`/proc`-then-authorize design. If a future policy needs image
identity, it requires a separately reviewed, OS-supported integrity/attestation
mechanism and a race analysis, not a process-name allowlist.

Systemd can run the broker under a dedicated `User=`/`Group=`, provision a
runtime directory and apply controls such as `ProtectSystem=`, `ProtectHome=`,
`PrivateTmp=`, `NoNewPrivileges=`, address-family restrictions and syscall
filters. These controls reduce service privileges and filesystem exposure;
they do not authenticate the IPC peer. systemd documents that some sandboxing
features depend on kernel/manager support and may be unavailable in containers
or user services. Read-only path settings do not themselves block communication
through AF_UNIX sockets.

## Windows: named pipes and service identities

Windows named pipes use security descriptors and DACL access checks against
the caller's access token. The default pipe security descriptor is too broad
for this use: Microsoft documents that it grants read access to Everyone and
the anonymous account. A future endpoint must provide an explicit, least-
privilege DACL, protect its namespace, restrict access to the intended service
and consumer identities, and test that remote clients are not admitted.

The server can call `ImpersonateNamedPipeClient` after reading a request and
perform an authorization-sensitive file or object access under that client's
security context. The API impersonates the context associated with the last
message read; the server must check the return value, fail closed on failure,
and reliably call `RevertToSelf` after the operation. Continuing under a
privileged broker token after an impersonation failure would create a confused
deputy risk. Access tokens carry user and group SIDs and privileges. A
Windows service SID can be added to a service process token to scope access to
service-owned objects; it is an OS service identity, not proof of the client
executable. The broker and consumer should use distinct least-privilege
identities and explicit ACLs if those are part of the threat model.

`GetNamedPipeClientProcessId` returns a client PID, not an executable
attestation or a lifetime-bound process handle. Following that PID to query a
path, token, or image creates a process-exit/PID-reuse and time-of-check/
time-of-use problem unless the identity is obtained and bound with a separately
validated OS mechanism. Process names and request fields remain spoofable.
Pipe ACLs and impersonation establish account/token-based authority, not the
integrity of the application using that token.

Windows protected services are not a general-purpose anti-tamper switch:
Microsoft documents the protected-service model for anti-malware services,
requires an Early Launch Anti-Malware (ELAM) driver and prescribed signing/
registration, and describes availability beginning with Windows 8.1. Kredoxi
cannot assume eligibility for this mechanism. It must not be presented as a
deployable Kredoxi control without a separately approved, supported design.

## Transport alternatives — no selection made

| Option | Benefits | Costs and residual risk |
| --- | --- | --- |
| Keep loopback mTLS only | Preserves current portable protocol and explicit key enrollment; channel confidentiality/integrity and client-key authentication are testable | Does not bind a key to an OS account or process; key theft or same-account access can impersonate the enrolled client |
| Add native IPC as an alternative local transport | Can use Linux UID/GID or Windows token/DACL enforcement for same-host account boundaries while retaining mTLS for portable or non-local transports; allows OS-specific adapters to be reviewed separately | Duplicates transport and lifecycle surfaces; requires per-OS packaging, endpoint ACLs, principal mapping, supported-version policy, and distinct-identity integration tests; does not provide executable integrity |
| Replace mTLS for same-host traffic with native IPC | Avoids local TCP listener and certificate ceremony for deployments whose policy can rely on OS identity; may simplify local endpoint access control | Loses transport-level key identity and portable behavior on this path; tightly couples protocol, identity, enrollment and authorization to each OS; same-user callers and compromised authorized consumers remain risks |
| Layer mTLS over native IPC | Retains a cryptographic key proof and protocol channel over local IPC | Duplicates identity and channel mechanisms; does not by itself resolve key-to-process binding; more complexity without a demonstrated requirement |

Native IPC and mTLS are not automatically additive protections. A native
transport can replace mTLS on one local path while mTLS remains a separate
transport for other deployments; alternatively, both mechanisms can be
required if there is a specific, tested defense-in-depth objective. Do not
silently fall back from one transport or authentication mode to another.

The implementation choice is deferred pending owner approval of the deployment
identity boundary: separate OS accounts/service identities versus same-user
applications; whether the broker must support non-local clients; required OS
versions; and the value of independent key-based authentication after native
peer authorization. No option is approved by this proposal.

### Owner-directed follow-up (research only)

The owner directed follow-up evaluation to prioritize native IPC as a possible
alternative same-host transport, retaining the current mTLS implementation as
the reference baseline and a candidate for portable or future non-local
scenarios. This is a research-priority decision only: ADR 0002 remains
Proposed; it does not select or authorize an additional production transport,
non-local broker access, replacement of mTLS, or implementation.

The experiments must compare Linux pathname Unix sockets with `SO_PEERCRED`
and Windows named pipes with access-token identity in disposable environments
where elevated setup is required. Measure what account separation adds against
same-user compromise, key/private-material exposure, endpoint permissions,
process isolation, impersonation, PID reuse/TOCTOU and confused-deputy risks.
Include setup/upgrade/operations cost, platform-specific failure behavior, and
whether layering both IPC and mTLS provides a demonstrable security benefit
beyond either alone. Return reproducible evidence and a comparative
recommendation before seeking architectural approval. Do not enable a second
production transport or non-local access during this research.

The owner-directed Phase 3 results and comparison are recorded in the
[practical OS-identity evidence report](../native-ipc-identity-evidence.md).
That report is research evidence only; this ADR remains Proposed, deferred and
not accepted.

## Deployment, integrity and anti-tamper requirements

Any later OS-native transport proposal must specify least-privilege service
identity, protected executable/configuration/key ownership, explicit endpoint
ACLs, safe startup and shutdown, denial behavior, resource limits, credential
rotation, and recovery. Separate broker and consumer accounts must be tested
only in disposable, authorized infrastructure where needed. Do not create
persistent privileged accounts, weaken host controls, disable EDR, or change
production services.

Future anti-tamper work must separately address signed and verified updates,
binary/configuration integrity, protected secret-store permissions, policy
rollback resistance, independent health/termination monitoring, broker-bypass
detection, privilege separation, and fail-secure recovery. A signature or
digest alone does not prevent rollback; an attacker-writable expected digest is
not a trust anchor. OS monitoring, file integrity measurement, service
hardening, and EDR ingestion are conditional controls and must be validated on
the target OS. None makes an authorized application's own memory unreadable to
that application or a privileged administrator/root.

## Telemetry and verification boundaries

Keep the existing versioned, redacted event contract as the source event model.
Future platform adapters can emit events to journald/syslog on Linux or Windows
Event Log/ETW, after an explicit schema mapping and platform test. Native
collectors can add provenance such as process/account metadata, but they do
not prove that a credential was consumed by the application. Keep separate:
broker authorization decision, attempted delivery, confirmed transport write,
application consumption (not observable from broker alone), suspicious endpoint
or process access, and independent health/termination observations.

A successful event API call or local write is not proof of durable storage,
tamper resistance, collector ingestion, or SIEM receipt. Collector outage,
buffer loss, retention, access control, and forwarding must be independently
defined. Do not add a mandatory proprietary backend. Do not claim OS or EDR
telemetry can reliably observe a compromised application reading its own
memory.

This repository contains research and test requirements only. No Linux or
Windows distinct-account test, IPC implementation, anti-tamper control, or
platform telemetry adapter was executed or implemented for this proposal.

## Required evidence before acceptance or implementation

1. Define the intended OS/account/process trust boundary and whether local
   consumers can be untrusted processes running as the same account.
2. Prototype Linux pathname-socket ownership/permissions and peer-credential
   derivation, and Windows pipe DACL/token impersonation in separate,
   disposable environments.
3. Test positive/negative access using distinct accounts, endpoint spoofing,
   inherited/duplicated handles, impersonation failure, PID reuse/TOCTOU,
   process replacement, key theft, malformed requests, broker outage and
   concurrent principals.
4. Confirm no request-supplied identity can elevate access, and that exact
   principal/reference authorization still precedes provider lookup with the
   ADR 0001 `policy_denied` / `secret_not_found` boundary unchanged.
5. Test fail-closed behavior and platform logging mappings, including event
   sink failure, delivery-state accuracy, collector loss and secret redaction.
6. Publish actual OS versions, privileges, account setup, commands, results,
   unsupported cases and bypasses. Mocks and cross-compilation are not OS
   enforcement evidence.
7. Obtain explicit owner approval for the selected transport and identity
   model before recording an Accepted ADR or implementing it.

## Primary sources

Retrieved 2026-10-31; they establish documented mechanism behavior, not Kredoxi
test results:

- [Linux `unix(7)`](https://man7.org/linux/man-pages/man7/unix.7.html) —
  `SO_PEERCRED`, pathname/abstract sockets and socket permissions.
- [Linux `pidfd_open(2)`](https://man7.org/linux/man-pages/man2/pidfd_open.2.html) —
  PID file descriptors, lifetime monitoring and PID reuse guarantees/limits.
- [systemd `systemd.exec`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html) —
  service sandbox controls and support limitations.
- [systemd `systemd.service`](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) —
  service lifecycle and readiness behavior.
- [Microsoft named-pipe security and access rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights) —
  DACL checks and the default pipe descriptor.
- [Microsoft `ImpersonateNamedPipeClient`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient) —
  last-message token context and failure handling.
- [Microsoft `GetNamedPipeClientProcessId`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getnamedpipeclientprocessid) —
  named-pipe client PID API.
- [Microsoft access tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens) and
  [`SERVICE_SID_INFO`](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/ns-winsvc-service_sid_info) —
  token contents and service SID behavior.
- [Microsoft protected anti-malware services](https://learn.microsoft.com/en-us/windows/win32/services/protecting-anti-malware-services-) —
  protected-service scope, ELAM and signing prerequisites.
- [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446) — TLS 1.3 channel security properties.
- [systemd journal fields](https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html),
  [Windows Event Logging](https://learn.microsoft.com/en-us/windows/win32/eventlog/about-event-logging),
  and [ETW](https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing) —
  platform event interfaces and provenance/collection boundaries.
- [The Update Framework specification](https://theupdateframework.github.io/specification/latest/) —
  update-system threat model including rollback and freeze attacks.
