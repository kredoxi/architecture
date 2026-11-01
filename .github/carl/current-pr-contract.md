# Architecture baseline PR contract

Status: owner accepted ADR 0001 and its enumeration boundary on 2026-10-31.
Keep this contract active until the updated PR revision passes CI and remaining
review gates; keep the PR open and unmerged.

## Goal and approved scope

Work only in kredoxi/architecture. Define the threat model, research resolution
and interception, record the owner-accepted MVP ADR, and define
reference, identity, policy, provider and runtime contracts. Add minimal
read-only architecture CI that reconciles against Core. Persist practical
requirements, architecture, compatibility, test strategy, roadmap and licensing
tradeoffs. Install the user-requested cARL runtime through its supported CLI and
sync the production Copilot loader. Open/update the PR; do not merge until
remaining review gates pass and the owner separately requests it.

## Constraints and forbidden scope

Preserve bundled invariants, tool policy, trust boundaries and loader authority.
Use an explicit profile to activate all core controls plus Go and CI/CD; leave
unrelated packs installed and selected but inactive, with no overrides.
Replace upstream-project text in user-owned memory with verified Kredoxi truth.
Do not hand-edit the runtime manifest or fabricate pack checks.

Do not implement the core MVP here, change organisation controls, choose a
licence, use real credentials, install privileged interception, publish releases,
make checks required or merge, force-push or edit another checkout.

## Expected files and step-by-step plan

1. Verify installed runtime, pack evaluation and production Copilot adapter.
2. Write README.md and docs/*.md, including docs/adr/*.md, with primary-source
   citations and explicit distinctions between proposed and demonstrated work.
3. Reconcile .github/carl/memory.md and profiles.json without relaxing controls.
   Add .gitattributes to preserve canonical LF runtime bytes on Windows checkout.
4. Validate contracts, grammar, examples, relative links, Core protocol source,
   obvious-secret patterns and diff hygiene with standard-library scripts.
5. Add a PR/main-push workflow with read-only permissions, immutable-pinned
   actions and verified cARL effective policy; do not add a required check.
6. Run cARL status/doctor/effective/trace; regenerate map/reconcile.
7. Commit/push the bounded work and update the open PR. The owner accepted the
   ADR; keep the PR open and unmerged until CI and review gates pass.

No new Python dependency or publishing workflow was added. The minimal
read-only Architecture CI is in scope; future release prerequisites are
documented.

## Contract assertions

| Assertion | Validation |
| --- | --- |
| A1: four tiers distinguish passive theft, same-user, authorised RCE and root/admin | Review threat model and residual-risk language |
| A2: references are not capabilities and explicit resolution is not interception | Review ADR, grammar and identity policy |
| A3: parser/provider/runtime/event contracts are versioned and fail securely | Review examples and requirement/test traceability |
| A4: effective governance keeps core controls without overrides | CLI effective/trace plus loader and canonical-file review |
| A5: delivery does not claim implementation, support, licence or security tests not executed | Review status, roadmap and PR description |
| A6: only an allowlisted principal reaches provider lookup; `policy_denied` and `secret_not_found` are distinct | Compare Core broker implementation, protocol, tests and documented enumeration boundary |
| A7: workflow permissions are read-only and dependencies are immutably pinned; the `validate` identity and a successful run are verified, but no check is configured as required | Review workflow and GitHub check-run evidence |

## Stop conditions and escalation

Stop on conflicting approved requirements, broken governance composition,
unexpected conflicting user changes, required weakening of a control, or a
need for real-secret or privileged-host access. Report source retrieval,
tool permission or PR delivery failures explicitly.

## Risks and reconciliation

External documentation establishes mechanism semantics, not Kredoxi test
results. The owner accepted ADR 0001 on 2026-10-31. The provider is never queried
before successful authentication and exact-reference authorisation; only an
allowlisted caller may observe `secret_not_found`. No wildcard, listing or
unauthorised probing is permitted. Preserve the accepted boundary in memory,
threat model and tests. Keep the PR open/unmerged until CI and remaining review
gates pass; do not make a check required or expand the MVP.

## Phase 3 Architecture PR B scope amendment

Status: owner-directed research/reporting only; ADR 0002 remains Proposed,
deferred and not accepted.

### Goal and approved scope

Record and compare the synthetic OS-identity experiment evidence from Core PR A.
Add `docs/native-ipc-identity-evidence.md`, link it from ADR 0002, and make
directly related evidence-reference updates to `docs/testing.md`,
`docs/threat-model.md`, and this durable memory. Add a task-scoped plan at
`.github/carl/plans/prB-os-identity-evidence.md`.

### Forbidden scope and invariants

Do not accept ADR 0002, change ADR 0001, or select a production transport. Do
not implement IPC, change Core production code, protocol, resolver, or
telemetry; create accounts; run privileged tests; or claim executable
attestation, same-account isolation, combined IPC+mTLS assurance, or
performance gains. Distinguish tested, configured-only, blocked, and
unmeasured scenarios. Preserve exact-reference authorization before provider
lookup and the `policy_denied` / authorized `secret_not_found` boundary.

### Contract assertions and validation

1. Evidence is traceable to Core PR A's source revision, exact native CI runs,
   commands, operating systems, toolchain, and account model; the current PR
   head is checked separately from the commit with detailed test evidence.
2. Each scenario separates expected behavior, observed result, evidence state,
   and residual risk; no skipped or unavailable case is represented as a pass.
3. The comparison covers mTLS-only, optional native IPC, replacement, requiring
   both, and deferral; recommendation does not imply ADR acceptance.
4. The report identifies identity-model, transport, lifecycle, and remaining
   cross-SID/remote-denial decisions for the owner.

Run the Architecture workflow's documented `python3 -m unittest discover -s
tests -v` and `python3 scripts/validate_architecture.py` checks with the
current cARL effective/status/doctor outputs. Run cARL status, doctor, plan,
effective and trace checks; inspect the final diff and `git diff --check`.
Do not run Core code locally from this Architecture checkout.

### Owner-authorized final integration amendment

The owner has independently confirmed Core PR #5 merged to Core `main` at
`0c465c56a6732265bdad8ec3eba143a11b2a9895`, with default-branch CI run
41338072128 successful. This amendment supersedes the earlier "keep PR open
and unmerged" instruction only for Architecture PR #4 and only after all of
these gates pass:

1. Update the report's current-source references to the merged Core revision,
   retaining historical exact tested revisions and CI provenance.
2. Verify the final Windows cancellation and impersonation regression names,
   native PR-head and main-branch results, and remaining skip/limits directly
   against source and CI.
3. Keep ADR 0001 Accepted and unchanged, ADR 0002 Proposed/deferred/not
   accepted, and all production code unchanged.
4. Re-run cARL diagnostics, all Architecture validation and the required
   `validate` check on the updated PR head; confirm base freshness, no review
   blockers and that branch protection permits merge.
5. Only then merge Architecture PR #4 using a repository-supported protected
   merge method and verify the resulting merge commit, `main` SHA and
   default-branch Architecture CI.

This is a narrow, user-authorized merge-stage amendment; it does not revise
the evidence acceptance criteria or authorize ADR 0002, production changes,
or other merges.

## Phase 4 Architecture PR B scope amendment

Status: owner-directed Architecture evidence and decision-package work;
this amendment supersedes the earlier Phase 3 PR B scope for the current task.
ADR 0002 remains Proposed/deferred/not accepted.
The prior one-time merge authorization applied only to Architecture PR #4,
which is already merged; that authorization is exhausted and does not apply
to this PR B. Open the new PR and leave it unmerged.

### Goal and approved scope

Produce `docs/phase4-workload-identity-endpoint-trust.md` using independently
verified Core PR A source, native CI and test output. Compare the five requested
identity/deployment candidates; distinguish OS principal, endpoint access,
broker authentication, authorization, transport protection, key custody,
executable integrity, lifecycle and tamper resistance; analyze endpoint and
deployment implications; and reconcile ADR 0002, roadmap, threat model, testing
guidance and durable memory. Create the task plan at
`.github/carl/plans/prB-workload-identity-endpoint-trust.md`. Mark the earlier
Phase 3 plan historical. Open the separate Architecture PR and leave it open.

### Forbidden scope and invariants

Do not accept ADR 0002, change ADR 0001, choose or implement a production
transport or enrollment system, modify Core or production code/protocol/
telemetry, provision identities, run privileged tests, claim production
support, or make performance assertions without comparable measurements.
Do not claim Windows cross-SID or remote-host denial; they remain unmeasured
unless new direct evidence proves otherwise. Preserve exact-reference
authorization before provider lookup and ADR 0001's `policy_denied` /
authorized `secret_not_found` boundary.

### Contract assertions and validation

1. Evidence names exact Core source revisions, CI run/job, OS/runner,
   Go/toolchain, privilege and account model, command, test and observed result.
2. Passing, configured-only, blocked, skipped and unmeasured cases remain
   distinct; no unavailable test is reported as a pass.
3. The comparison explicitly treats same-account workloads as the same OS
   principal absent independent evidence, and separates transport/key
   authentication from authorization and executable integrity.
4. The operational assessment covers enrollment, rotation/revocation,
   install/start/restart/recovery/removal and policy rollback without implying
   those controls exist.
5. ADR 0002 remains Proposed/deferred/not accepted; ADR 0001 remains Accepted
   and unchanged; production implementation is out of scope.

Run Architecture unit tests, `scripts/validate_architecture.py`, cARL status,
doctor, effective-pack and trace diagnostics, link/source/run consistency and
secret checks, and `git diff --check`. Review the final change and open PR
without merging. Do not run Core code from this checkout.

### Stop conditions

Stop and report if source or CI provenance cannot establish a claimed result,
the verified baseline differs materially from the requested comparison, a
documentation change would silently change an accepted architecture decision,
or a required action needs production/privileged access.

### Owner-authorized final integration amendment — Architecture PR #5 only

The owner explicitly authorized merging Core PR #6 first and Architecture PR
#5 second. Core PR #6 is now merged at `d10dfcf6032cfbbbadf0d874805107fd6fa57061`;
its exact PR head was `28b2f90014c821d4507092c882987ca1e80d2847`. Its default-
branch CI run `41350453082` on the merge SHA passed governance, Ubuntu and
Windows. This authorizes final evidence-chain reconciliation and a conditional
merge of Architecture PR #5 only after all of the following:

1. Update Phase 4 Architecture evidence to cite Core PR #6's exact final tested
   source and merge chain, including the test-only `cmd/demo` readiness race
   fix at `6673f2b96409c8ee099fa5644ea5510975eec7b8`; preserve historical
   tested revisions and name outcomes accurately.
2. Explicitly retain the limitation that the three-role Linux case—authorized
   distinct consumer A reaching broker B without endpoint replacement rights,
   while unrelated UID U is denied by policy—was not demonstrated. The current
   `0700` namespace replacement test and `0711` namespace peer-policy test do
   not combine those outcomes. Keep Windows cross-SID/remote denial unmeasured.
3. Keep ADR 0002 Proposed/deferred/not accepted, ADR 0001 Accepted/unchanged,
   and all production code, protocol, transport and identity-enrollment scope
   unchanged.
4. Re-run cARL status/doctor/effective/trace and Architecture unit/validator
   checks. Verify current base, exact updated-head `validate` success, no
   unresolved review conversations or blockers, and that protection requires
   `validate` with no approval count unmet.
5. Only if every gate passes, merge Architecture PR #5 using a repository-
   supported protected merge method without bypassing checks; read back the
   merge commit and `main` SHA and verify default-branch Architecture CI.

This amendment supersedes the earlier PR B instruction to leave the new PR
open only for this explicitly authorized Architecture PR #5 integration. It
does not authorize any other merge or ADR 0002 acceptance.
