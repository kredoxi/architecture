# Kredoxi architectural truth cache

## Purpose and authority

Kredoxi is conventional runtime credential-substitution software, not an AI
agent. This repository owns architecture, requirements, threat-model boundaries,
ADRs and contracts. Implementation belongs in kredoxi/kredoxi; shared community
governance belongs in kredoxi/.github. The Kredoxi organisation is the project
authority. Upstream cARL is a governance dependency, not the product authority.

Canonical agent governance is in .github/carl and effective instruction packs.
Harness files are loaders, not independent authorities. Current files win over
stale cache entries. Preserve bundled invariants, tool tiers and trust boundaries.

## Design baseline and limits

The selected MVP is Go explicit resolution through a local mutually
authenticated TLS 1.3 broker, exact-reference deny-by-default authorisation and
a memory-only synthetic provider. URI example:
`kredoxi://v1/demo/example/password`. Enrolled principal example:
`urn:kredoxi:principal:demo-consumer`.

Authentication proves possession of an enrolled key, not executable identity.
References alone grant no access. Authorised applications still receive values
in memory. Same-user key theft, malicious authorised dependencies, application
RCE and administrator/root compromise are not prevented by this MVP.

The owner accepted ADR 0001 on 2026-10-31 for the documented synthetic MVP only;
this is not production-use approval, licence selection, security-control
relaxation or scope expansion. The broker must authenticate the client before
lookup and require exact principal/reference authorisation before calling a
provider. Unallowlisted references return `policy_denied` without revealing
whether a provider entry exists; an allowlisted but absent reference returns
`secret_not_found`, disclosing absence only to that already-authorised
principal. No wildcard grants, reference listing or unauthorised provider
probing are permitted. Certificate possession is not executable identity.

An SDK/API is explicit integration, not transparent interception. OS-peer IPC,
configuration/launch adapters and protocol proxies require separate evidence.
The long-term product is not restricted to SDK integrations.

See docs/threat-model.md and docs/architecture.md for product trust boundaries,
docs/contracts.md for runtime/provider contracts, and docs/testing.md for proof gates.
Documentation here is not evidence that core components or security tests ran.
Supported platforms must be based on reproducible execution in the core repo.

## Governance operating model

Use the installed current cARL CLI, not an older PATH entry. All core packs are
repository defaults; Go and CI/CD are active in the architecture profile.
Unrelated platform/cloud/language packs remain installed and selected but
inactive. No overrides weaken the core controls. Use effective/trace diagnostics
and read the ordered definitions before execution.

Use an approved PR contract for bounded changes. Reconcile durable truth after
architecture changes. The CLI owns runtime.json and managed asset repair;
memory and profiles are deliberately user-owned. Do not copy upstream-project
release processes into Kredoxi or infer redistribution rights.

## Open decisions

No licence, production encrypted vault, release-signing policy, OS tamper
enforcement or production credential enrollment has been approved. Compare
options, record limits and request approval before introducing them.

Grammar/wire/policy are reconciled to the core session's reported MVP baseline:
three 1-32-byte ASCII segments, lowercase letter first and lowercase/digit/hyphen
afterward (trailing hyphen allowed); POST /v1/resolve with exactly reference;
response value/error/request_id, omitting empty value/error; policy version 1
with principal-to-exact-reference allowlists and an independent compiled
compact-JSON SHA-256 demo pin. Pin validation is not privileged anti-rollback.
The implemented Provider interface is Resolve(context.Context, Reference)
(string,error); synthetic output is generated 64-character hex. Only the
trusted synchronous synthetic provider honours deadlines; arbitrary blocking
provider work is not preempted. Event schema uses policy_decision, not decision.
Configured limits are documented in docs/contracts.md. Future owned-byte
provider lifecycle and additional hardening remain proposals. Reconcile
cross-repository drift without claiming unexecuted tests or unsupported fields.

Core PR A's synthetic native IPC experiments provide limited OS-account
evidence: Linux CI observed cross-UID pathname-socket permission and
`SO_PEERCRED` policy denial, while a copied synthetic mTLS key remained usable
by a different UID. Windows native tests observed same-SID pipe access,
impersonation/restoration and duplicated-handle reuse; cross-SID and remote
denial were not measured. No combined IPC+mTLS test or executable attestation
exists. See [the Architecture evidence report](../../docs/native-ipc-identity-evidence.md);
ADR 0002 remains Proposed and no transport is selected.

<!-- BEGIN GENERATED: reconcile -->
## Repository snapshot

This section is regenerated by `carl reconcile`. Do not edit manually.

**Languages:** Python
**Last reconciled:** 2026-11-01

### Key directories

- `.agents`
- `.agents/rules`
- `.cursor`
- `.cursor/rules`
- `.github` — GitHub configuration and Copilot instruction root
- `.github/carl` — cARLv2 governance artefacts and templates
- `.github/carl/plans` — Prompt-as-code planning artefacts
- `.github/instructions` — Copilot instruction packs
- `.github/instructions/cloud` — Cloud guidance packs
- `.github/instructions/core` — Core governance packs
- `.github/instructions/languages` — Language-specific guidance packs
- `.github/instructions/platform` — Platform guidance packs
- `.github/workflows` — GitHub Actions workflows
- `docs` — Documentation
- `docs/adr`
- `scripts` — Build and automation scripts
- `tests`

### Workflows

- `.github/workflows/architecture-validation.yml` — architecture-validation workflow

### Governance artefacts

- `.github/carl/current-pr-contract.md` — Active PR scope and constraints
- `.github/carl/current-pr-contract.template.md` — PR contract template
- `.github/carl/invariants.yml` — Runtime invariants enforced by all implementation PRs
- `.github/carl/memory.md` — Durable architectural truth cache
- `.github/carl/packs.json`
- `.github/carl/profiles.example.json`
- `.github/carl/profiles.json`
- `.github/carl/repo-map.example.json` — Repo map template example
- `.github/carl/repo-map.json` — Generated cognitive repository map
- `.github/carl/runtime.json`
- `.github/carl/tool-policy.yml` — Tool permission tier definitions
- `.github/carl/trust-boundaries.md` — Trust boundary documentation

### Documentation

- `AGENTS.md`
- `CLAUDE.md`
- `README.md` — Repository overview and pack catalogue
<!-- END GENERATED: reconcile -->
