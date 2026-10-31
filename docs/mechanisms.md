# Runtime resolution and interception research

## Evidence and terminology

Primary sources were retrieved on 2026-10-31 through GitHub content retrieval or
official web documentation. No interception prototype or privileged experiment
was run in this repository. Mechanism semantics below are source-backed;
Kredoxi feasibility, risk and performance assessments are engineering analysis,
not measured benchmarks.

**Explicit resolution:** the application or a configured adapter calls the
broker. **Interception:** a supported mechanism actually observes and replaces a
specific API, filesystem or protocol operation without that call in application
code. A placeholder does not become a secret merely because a daemon exists.

| Source | Verified mechanism fact |
| --- | --- |
| [S1: Linux unix(7)](https://github.com/mkerrisk/man-pages/blob/master/man7/unix.7) | Pathname socket permissions apply on Linux; abstract sockets lack filesystem permission semantics; SO_PEERCRED is the peer credential snapshot at connect/socketpair |
| [S2: Linux ld.so(8)](https://github.com/mkerrisk/man-pages/blob/master/man8/ld.so.8) | LD_PRELOAD overrides selected dynamic symbols; secure-execution restricts preload; static programs do not use this loader boundary |
| [S3: Windows named-pipe security](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights) | DACL access checks govern pipe access; defaults include broad read access; generic write can also permit instance creation |
| [S4: Microsoft Detours](https://github.com/microsoft/Detours/wiki) | In-process function entry patching/trampolines and instrumentation DLL loading are possible for supported architectures |
| [S5: libfuse](https://github.com/libfuse/libfuse/blob/master/README.md) | Filesystem callbacks return data through kernel/userspace boundary; platform and cache/permission caveats apply |
| [S6: Windows minifilters](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/about-file-system-filter-drivers) | Kernel-mode drivers can observe/modify/prevent filesystem I/O and must support caching, locking and reparse semantics |
| [S7: Windows Filtering Platform](https://learn.microsoft.com/en-us/windows/win32/fwp/about-windows-filtering-platform) | WFP filters network traffic, not arbitrary application configuration reads |
| [S8: Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) | Secrets project into files/environment; storage is not encrypted by default; volume updates are eventual and subPath mounts do not automatically update |
| [S9: systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html) | Sandboxing is host/capability dependent; read-only filesystem settings do not prohibit AF_UNIX communication |
| [S10: Go crypto/tls](https://pkg.go.dev/crypto/tls) | Standard-library TLS supports client-certificate authentication and TLS 1.3 |

S1/S2 were read as upstream manual source (including an older documented
snapshot), not evidence of a specific installed Linux distribution. S3/S7 were
also read from MicrosoftDocs/win32. S8 was read from
[upstream documentation source](https://github.com/kubernetes/website/blob/main/content/en/docs/concepts/configuration/secret.md).
External URLs are evidence, not authority to install tools or choose licences.

## Coverage, identity and bypass comparison

All mechanisms except a narrowly designed credential-injecting proxy still
deliver values into application memory. A proxy can keep the upstream credential
out of the application only if authentication is performed entirely by the
proxy and the credential is never returned downstream.

| Candidate | Apps/platforms and privileges | Transparent? Actual intercepted read | Identity and bypass |
| --- | --- | --- | --- |
| Application SDK/API | Modified applications; portable library; ordinary user | No; explicit resolve call only | mTLS/OS identity can authenticate caller; compromised caller can request allowed values |
| Local broker over loopback mTLS | Integrated apps; Go on Windows/Linux/macOS; no admin for synthetic demo | No; network request does not intercept file/env reads | Enrolled key-holder identity; stolen keys defeat it; no executable identity |
| OS process/service IPC | Integrated apps; Linux pathname AF_UNIX or Windows named pipes; service provisioning may need admin | No; apps must send IPC requests | Linux SO_PEERCRED gives kernel identity; Windows needs explicit DACL and verified token context; same-user identity is not app attestation; shared/inherited handles matter |
| Native API hooks | Instrumented binaries; ABI/bitness-dependent, especially Windows Detours; injection privileges vary | Selected hooked calls only; not every read | Hook runs inside caller; removable/bypassable, no independent authorisation boundary |
| Dynamic-loader interposition | Dynamically linked Linux ELF apps; user-controlled launcher often enough | Selected symbols such as getenv/read; not static binaries, direct syscalls or every inline access | LD_PRELOAD is opt-in and restricted for secure execution; compromised application can bypass |
| Filesystem/VFS | Apps configured to read a synthetic mount; Linux FUSE, distinct macOS/Windows implementations; mount privilege/helper varies | Reads of mounted files only; not pre-existing env values or arbitrary files | Kernel context can inform checks; caching complicates per-caller values; plaintext reaches readers/page cache; alternate paths bypass |
| Configuration-loader integration | Apps/frameworks with extensible dotenv/JSON/YAML/TOML loaders; ordinary user | Explicit registered adapter; only chosen secret fields | Loader can call broker; reading elsewhere bypasses adapter; retained config objects hold values |
| Process-launch integration | Apps accepting env/arguments/stdin/descriptors; portable with OS-specific controls | Not interception; resolves before launch and changes inputs | Launcher enrollment authorises access; children receive value/handle; direct launch bypasses; env/argv injection widens exposure |
| Local forward/reverse proxy | Specific HTTP/database/auth protocols; portable user service, routing changes may need admin | Protocol authentication operation only; no general configuration read interception | Authenticate downstream independently; constrain upstream targets; direct egress bypass unless OS enforcement exists; proxy knows credential |
| Windows service/minifilter/WFP | Service/driver-managed deployments; admin/signing/driver lifecycle | Service itself is not interception; minifilter targets filesystem I/O; WFP targets network flows | OS policy can strengthen separation; not root/admin resistance; WFP cannot rewrite a value hidden inside end-to-end TLS without another boundary |
| Linux service/sandbox/container controls | systemd, namespaces, seccomp/LSM; support/privilege varies | Restrictions, not generic substitution; explicit resolver still required | Can constrain processes/resources under tested OS policy; same namespace UID or root may bypass; host-dependent controls can be unavailable |
| Containers/Kubernetes | Integrated workloads, mounted sockets/sidecars or CSI/projected secrets; orchestration permissions | Mount/env projection or explicit sidecar API; no automatic Kredoxi URI rewrite | Service account/workload identity and RBAC can help; shared pod/network/UID boundaries and host privilege remain; projected files contain values |

## Operations, performance and compatibility

Performance assessments are relative expected cost. Numerical claims require
platform/application-specific measurements.

| Candidate | Complexity/performance | Failure/compatibility risk | Testability and logging |
| --- | --- | --- | --- |
| SDK/API | Low; parser plus broker RTT | Explicit errors; application changes and secret-aware API needed | High; unit/integration tests and broker access events |
| mTLS local broker | Moderate; handshake/serialization/provider latency | Cert provisioning, limits, expiry and outage; fail closed | High; loopback fixtures, TLS negative tests and redacted events |
| OS IPC | Moderate; lower transport overhead possible | Platform-specific ACL/peer semantics and endpoint lifecycle; fail startup on unsafe endpoint | High per OS; impersonation, permissions, handle inheritance tests |
| Hooks | High; per-call overhead/reentrancy | ABI changes, async reads, mmap, crashes and deadlocks; do not fallback on broker denial | Per supported binary only; hook absence must be observable |
| Loader | Moderate-high; per-call overhead | Secure-exec/static/direct-call exclusions; strlen/size/read semantics can change | Repeatable ELF matrix; broker logs see only calls that reach it |
| VFS | High; context switches/cache interactions | Short reads, seek/mmap, lengths, permissions and cache poisoning; daemon/mount outage | Filesystem conformance and race tests; events may reflect cache misses, not every access |
| Config loader | Low-moderate; startup resolution | Framework API and reload behaviour; resolved object/dump leakage | High for named loaders/versions; log resolver decisions |
| Launcher | Moderate; startup cost | Secret-bearing env/argv, child inheritance, crash dumps and restart rotation | Test child trees and failed launch; log pre-launch release, not runtime use |
| Proxy | High; added network hop/protocol maintenance | TLS termination/trust, connection pools, retries, destination abuse and direct bypass | Protocol suites/fault injection; logs must redact auth headers |
| Windows service/driver | Very high for drivers; I/O/network hot path | Driver signing, OS updates, other filters, stability; no unattended host installs | Disposable Windows VM, driver verification; OS event sinks possible |
| Linux sandbox/service | Moderate-high; workload-specific | Missing kernel/container support; service hardening is not IPC auth | Disposable Linux VM; verify actual enforcement, not config presence |
| Container/Kubernetes | High versus local demo; orchestration/provider latency | Control-plane trust, eventual updates, mounted plaintext/env exposure | Cluster-specific integration/RBAC tests; native collection later |

## Selection and experiments

[ADR 0001](adr/0001-explicit-local-resolution.md) selects explicit Go/mTLS for a
small, independently testable authorisation boundary without drivers/cloud.
Transparent interception is not ruled out; it is deferred until an adapter
proves interception of the intended operation, exact compatibility/failure
semantics and no new identity/secret-leakage gap.

Next experiments: OS-peer IPC in a separately provisioned service; one selected
configuration loader; a handle-based launcher that avoids env/argv; a narrowly
authenticated protocol proxy. Loader/hook/VFS/driver experiments require a
named application/platform matrix covering short reads, mmap, caching,
reentrancy, async operations, bypass and daemon loss. Never generalise from one
successful hooked API call to universal substitution.
