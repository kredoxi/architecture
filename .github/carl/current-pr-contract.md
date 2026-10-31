# Architecture baseline PR contract

Status: approved for assisted execution by the user's execution brief and retry,
including core-contract reconciliation; closes as historical scope when the
validated, reconciled baseline PR revision is published.

## Goal and approved scope

Work only in kredoxi/architecture. Define the threat model, research resolution
and interception, select a narrow MVP in an ADR, and define reference, identity,
policy, provider and runtime contracts. Persist practical requirements,
architecture, compatibility, test strategy, roadmap and licensing tradeoffs.
Install the user-requested cARL runtime through its supported CLI and sync the
production Copilot loader. Open a PR; do not merge.

## Constraints and forbidden scope

Preserve bundled invariants, tool policy, trust boundaries and loader authority.
Use an explicit profile to activate all core controls plus Go and CI/CD; leave
unrelated packs installed and selected but inactive, with no overrides.
Replace upstream-project text in user-owned memory with verified Kredoxi truth.
Do not hand-edit the runtime manifest or fabricate pack checks.

Do not implement the core MVP here, change organisation controls, choose a
licence, use real credentials, install privileged interception, publish releases,
merge PRs, force-push or edit another checkout.

## Expected files and step-by-step plan

1. Verify installed runtime, pack evaluation and production Copilot adapter.
2. Write README.md and docs/*.md, including docs/adr/*.md, with primary-source
   citations and explicit distinctions between proposed and demonstrated work.
3. Reconcile .github/carl/memory.md and profiles.json without relaxing controls.
   Add .gitattributes to preserve canonical LF runtime bytes on Windows checkout.
4. Check Markdown links, fenced examples and diff whitespace; run cARL status,
   doctor, pack effective and trace; regenerate map/reconcile using the CLI.
5. Commit the bounded work, open the requested PR and report remaining risks.

No new tooling dependency or publishing/CI workflow is required for this
documentation-only baseline. Future CI/release prerequisites are documented.

## Contract assertions

| Assertion | Validation |
| --- | --- |
| A1: four tiers distinguish passive theft, same-user, authorised RCE and root/admin | Review threat model and residual-risk language |
| A2: references are not capabilities and explicit resolution is not interception | Review ADR, grammar and identity policy |
| A3: parser/provider/runtime/event contracts are versioned and fail securely | Review examples and requirement/test traceability |
| A4: effective governance keeps core controls without overrides | CLI effective/trace plus loader and canonical-file review |
| A5: delivery does not claim implementation, support, licence or security tests not executed | Review status, roadmap and PR description |

## Stop conditions and escalation

Stop on conflicting approved requirements, broken governance composition,
unexpected conflicting user changes, required weakening of a control, or a
need for real-secret or privileged-host access. Report source retrieval,
tool permission or PR delivery failures explicitly.

## Risks and reconciliation

External documentation establishes mechanism semantics, not Kredoxi test
results. Cross-repository wire contracts remain provisional until core
implementation confirms them. Update memory to retain that distinction.
Close this contract after delivery; a completed contract is historical scope,
not a restriction on future approved work.
