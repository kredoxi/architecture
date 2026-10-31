# Roadmap and compatibility boundaries

## Current versus proposed support

| Surface | Current evidence | Proposed/required next gate |
| --- | --- | --- |
| Architecture documents | Grammar/wire/policy reconciled to core session report | Review evolving contracts against core test evidence |
| Go explicit resolver/mTLS | Core session reports working demo/tests; not executed here | Publish reproducible core evidence and adversarial matrix |
| Windows | Documentation/governance prepared on Windows | Build/run actual consumer/broker; cert/filesystem/permission tests |
| Linux | IPC/loader mechanism research only | Actual runtime tests; separate SO_PEERCRED/pathname socket adapter |
| macOS | Go transport portability is a design expectation | Runtime compatibility, cert/filesystem checks; separate native IPC research |
| Containers/Kubernetes | Research only | Workload identity, mounted-IPC/RBAC/volume and host-boundary tests |
| Hooks/loaders/VFS/drivers/proxies | Evaluated, not supported | Named application/platform experiments and explicit ADR |

No supported runtime OS/version/architecture list is claimed in this repository.
The core repo must publish a tested matrix including actual OS, architecture,
Go version and executed commands; compiling elsewhere does not establish support.

## Milestones

1. **Synthetic explicit vertical slice:** align parser/policy/provider/wire/events,
   prove allowed/denied mTLS access, no config/log leakage, outage and Tier 3
   limits. Mark synthetic components development-only.
2. **OS service/IPC isolation:** Linux pathname socket/kernel peer credentials
   and Windows named-pipe DACL/token verification as separate transports.
   Provision least-privilege broker identity; test endpoint ownership,
   impersonation, handle inheritance and same-user limits.
3. **Practical adapters:** one documented configuration loader; handle-based
   launcher avoiding env/argv; narrow credential-injecting proxy if justified.
   Measure startup/request cost, rotation, compatibility and bypass.
4. **Production provider readiness:** choose encrypted local store or one
   enterprise provider based on need; separate trust keys, enrollment, policy
   integrity/anti-rollback decision, expiry/revocation and recovery. No provider
   breadth for appearances.
5. **Selected interception research:** named hook/loader/VFS target, OS-supported
   enforcement only where justified, disposable tests. Preserve explicit
   fallback errors and prove the actual read boundary.
6. **Operational/release readiness:** native security events/EDR collection,
   health observer, capacity/retention, approved licence/distribution,
   signing/provenance and verified repository checks.

## CI/CD and release prerequisites

The architecture validation workflow runs on relevant PRs and pushes to `main`.
It uses read-only `contents: read`, pins checkout to an immutable SHA, downloads
the current cARL release with checksum verification, and uses the Python
standard library for focused contract/example/grammar/link/secret/hygiene checks.
It reconciles the Core protocol where available. It uses no application
credentials, privileged execution or production provider.

Do not configure the check as required until it succeeds and its exact GitHub
check identity has been verified. This PR does not change repository rulesets.
For the core repo require build, unit/integration/adversarial
tests, race where supported, lint/vet/static/dependency vulnerability checks,
secret scanning and artefact integrity.

Use least-privilege `contents: read`, pinned verified actions/tools and isolated
untrusted PR jobs without secrets. Do not use privileged `pull_request_target`
to execute PR code. cARL doctor reports findings but may return zero on errors:
validate healthy status and structured effective/trace output, not doctor exit
alone. No blanket success fallback for missing governance.

Branch rules must prevent force pushes/deletion and require applicable checks,
without requiring another maintainer's approval in a single-maintainer org.
Organisation rules, 2FA, scanning/push protection, Dependabot and private
disclosure capability are separate live-verification tasks, not controls
established by these documents.

No automatic public release. After licence/distribution approval, define
immutable signed artefacts, trusted signing roots/key rotation, SBOM,
build provenance and checksum/signature verification. A checksum alone does not
authenticate publisher identity. Document recovery/rollback without accepting
downgraded policy or untrusted binaries.
