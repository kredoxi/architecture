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
