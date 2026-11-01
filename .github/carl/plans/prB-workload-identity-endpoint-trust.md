# Architecture PR B: Phase 4 workload identity and endpoint trust

## Plan metadata

- Status: active; evidence, architecture decision package, and documentation only
- Author: Copilot
- Created: 2026-11-01

## Goal

Record a reproducible Phase 4 evidence report and decision package comparing
OS-account, endpoint, broker-authentication, key-possession, and deployment
identity boundaries. Reconcile Phase 3 evidence against Core PR A's actual
source revision and native CI, identify what remains unmeasured, and leave ADR
0002 Proposed until the owner accepts a decision. Do not select or implement a
production transport.

## Affected files

- `.github/carl/current-pr-contract.md`
- `.github/carl/plans/prB-workload-identity-endpoint-trust.md`
- `.github/carl/plans/prB-os-identity-evidence.md` (mark the completed Phase 3 plan historical)
- `.github/carl/memory.md`
- `docs/phase4-workload-identity-endpoint-trust.md`
- `docs/adr/0002-native-ipc-identity-evaluation.md`
- `docs/roadmap.md`
- `docs/testing.md`
- `docs/threat-model.md`

No Core source, production code, protocol, telemetry schema, CI workflow,
runtime manifest, credentials, or privileged host configuration is in scope.

## Step-by-step changes

1. Verify the current Architecture baseline, Core PR A head and file patches,
   native CI jobs/logs, test source, and cARL effective policy.
2. Record evidence with exact tested revision, runner/OS, Go version,
   privilege/account model, command, test name, result, and explicit limits.
   Separate OS-enforced, configured-only, blocked, unmeasured, and analytic
   cases.
3. Add a decision matrix for shared-user deployment, a dedicated broker and
   consumer under a shared account, separate broker/workload identities,
   separate identities plus cryptographic key proof, and the existing mTLS-only
   baseline. Assess security properties and operational lifecycle without
   unmeasured performance or production-support claims.
4. Analyze endpoint replacement/pre-creation/restart, parent and mount trust,
   same-account abuse, copied-key/fake-broker behavior, connected-handle
   lifetime, Linux UID/GID/group conditions, Windows SID boundaries, and
   unavailable cross-SID/remote-denial evidence.
5. Distinguish OS principal evidence, broker authentication, exact-reference
   authorization, attempted delivery, transport write, application
   consumption, and health/telemetry. Preserve ADR 0001's lookup boundary.
6. Link the report from ADR 0002 and reconcile roadmap, threat-model, testing,
   and durable memory. Keep ADR 0002 Proposed/deferred/not accepted; do not
   change ADR 0001 or select a production architecture.
7. Run the documented Architecture tests/validator, current cARL diagnostics,
   link/source-reference and secret checks, and final diff hygiene; then open
   the separate Architecture PR and leave it open.

## Contract assertions

1. Evidence is traceable to exact Core source revisions and CI job results;
   native Windows/Linux observations are not inferred from mocks or
   cross-compilation.
2. Each scenario explicitly identifies tested conditions and expected,
   observed, blocked, or unmeasured outcomes; no skipped or unavailable case
   is described as a pass.
3. The identity-property model keeps endpoint access, OS principal,
   authentication, exact-reference authorization, transport protection, key
   custody, executable integrity, lifecycle, and tamper resistance distinct.
4. The comparison covers the five specified deployment candidates, including
   operations and residual risk, without performance assertions lacking a
   comparable executed benchmark.
5. ADR 0002 remains Proposed/deferred/not accepted, ADR 0001 remains
   Accepted/unchanged, and no production implementation or support claim is
   introduced.

## Test strategy

- `python3 -m unittest discover -s tests -v`
- `python3 scripts/validate_architecture.py`
- Run the repository's current cARL CLI `status`, `doctor`, `pack effective
  --json`, and `trace`; verify effective packs, healthy status, and no drift.
- Verify local Markdown links and referenced source/run identifiers, scan for
  obvious committed secrets, and run `git diff --check`.
- Review ADR statuses and confirm no Core or production source changed.
- Do not rerun or claim Core native security tests from this Architecture
  checkout; cite only verified Core PR A source and CI.

## Risks

The evidence is synthetic and narrow. It does not show production broker
authentication, combined IPC+mTLS enforcement, executable attestation, a
distinct Windows SID test, Windows remote-host denial, or production
enrollment/rotation/revocation. Linux parent-directory/mount ancestry and
groups must not be generalized beyond the measured setup. An OS account or
certificate identifies an authority boundary, not benign code; same-identity
processes and privileged attackers retain substantial access.

## cARL/docs reconciliation

The confirmed experiment outcomes and unresolved deployment identity boundary
are durable architecture truth. Update the report, ADR 0002, roadmap,
threat-model, testing guidance, and memory cache. Do not modify invariants,
runtime state, pack selection, trust policy, loader adapters, or ADR 0001.
