# Roadmap and compatibility boundaries

## Current versus proposed support

| Surface | Current evidence | Proposed/required next gate |
| --- | --- | --- |
| Architecture documents | Grammar/wire/policy reconciled to core session report | Review evolving contracts against core test evidence |
| Go explicit resolver/mTLS | Core session reports working demo/tests; not executed here | Publish reproducible core evidence and adversarial matrix |
| Windows | Documentation/governance prepared on Windows | Build/run actual consumer/broker; cert/filesystem/permission tests |
| Linux | Core synthetic IPC experiments pass native CI for `SO_PEERCRED`, unrelated-UID policy denial, and a broker-owned `0700` endpoint directory blocking rename/unlink by the existing `nobody` UID; no production IPC or service identity | Keep account-level findings scoped to the tested directory, UID, mount and runner. Parent/mount ancestry, group effects, deployment lifecycle and workload identity remain unverified |
| Windows | Core synthetic native tests pass for same-SID pipe access, impersonation/restoration, cancellation, fake-endpoint acceptance and duplicated-handle reuse; no production IPC or service identity | Cross-SID DACL denial and actual remote-host denial remain unmeasured; require authorized disposable Windows identities/host before claiming either |
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
2. **Phase 3 — native OS-identity evidence (research complete; limited):**
   Core's earlier synthetic Linux/Windows IPC experiments establish only the
   named account-level behaviors: Linux `SO_PEERCRED`/pathname permission and
   copied-key cases, plus Windows same-SID access, impersonation/restoration,
   cancellation and handle tests. They do not establish production IPC,
   executable identity, same-account process separation, or Windows
   cross-SID/remote denial. See the [Phase 3 evidence report](native-ipc-identity-evidence.md).
3. **Phase 4 — workload identity, endpoint trust and deployment isolation
   (evidence report complete; ADR 0002 remains Proposed/not accepted): Core's
   merged synthetic evidence adds Linux broker-endpoint rename/unlink denial
   for one unrelated UID and fake endpoint acceptance on both platforms.
   Architecture records the source-to-CI evidence chain and compares five
   deployment candidates, but no deployment identity model or transport is
   selected. The combined Linux case of an authorized distinct consumer
   reaching broker B without endpoint replacement rights while unrelated UID
   U is denied remains unverified; the separate tests do not prove it. The
   owner must decide whether deployments require
   a dedicated broker and shared or per-workload consumer identities; whether
   clients are local-only; and what enrollment, key custody,
   rotation/revocation, endpoint ownership, install/update/restart/recovery/
   removal and policy rollback controls are required. Windows cross-SID and
   actual remote denial remain unmeasured. Do not claim production controls,
   support or performance, and do not implement a transport until the owner
   accepts an explicit identity model and ADR. See the [Phase 4 evidence
   report](phase4-workload-identity-endpoint-trust.md).
4. **Practical adapters:** one documented configuration loader; handle-based
   launcher avoiding env/argv; narrow credential-injecting proxy if justified.
   Measure startup/request cost, rotation, compatibility and bypass.
5. **Production provider readiness:** choose encrypted local store or one
   enterprise provider based on need; separate trust keys, enrollment, policy
   integrity/anti-rollback decision, expiry/revocation and recovery. No provider
   breadth for appearances.
6. **Selected interception research:** named hook/loader/VFS target, OS-supported
   enforcement only where justified, disposable tests. Preserve explicit
   fallback errors and prove the actual read boundary.
7. **Operational/release readiness:** map the versioned event contract to
   journald/syslog or Windows Event Log/ETW and validate collector ingestion,
   loss, retention and redaction; add an independent health observer; establish
   binary/configuration integrity, policy anti-rollback and recovery evidence;
   complete capacity/retention, approved licence/distribution,
   signing/provenance and verified repository checks. A local event write is
   not proof of durable storage or SIEM receipt.

## CI/CD and release prerequisites

The architecture validation workflow runs on relevant PRs and pushes to `main`.
It uses read-only `contents: read`, pins checkout to an immutable SHA, downloads
the current cARL release with checksum verification, and uses the Python
standard library for focused contract/example/grammar/link/secret/hygiene checks.
It reconciles the Core protocol where available. It uses no application
credentials, privileged execution or production provider.

The `validate` job identity and a successful run have been verified. This PR
does not configure the check as required or change repository rulesets; any
ruleset update is a separate owner decision.
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
