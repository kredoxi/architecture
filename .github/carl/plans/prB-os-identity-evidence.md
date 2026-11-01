# Architecture PR B: practical OS-identity evidence report

## Plan metadata

- Status: active; documentation and evidence reconciliation only
- Author: Copilot
- Created: 2026-11-01
- Last updated: 2026-11-01

## Goal

Publish a traceable comparison of the synthetic Linux pathname-socket and
Windows named-pipe identity experiments against the existing mTLS key-holder
baseline. Recommend whether the evidence is sufficient to choose a future
transport, while preserving the approved ADR 0001 architecture and leaving
production implementation to a later owner-approved decision.

## Approved scope

- Verify Core PR A's current branch head, experiment README, test source,
  workflow results and commit relationship.
- Add `docs/native-ipc-identity-evidence.md`, link it from ADR 0002, and make
  focused evidence-reference updates to `docs/testing.md`,
  `docs/threat-model.md`, and `.github/carl/memory.md`.
- Amend the active contract with the report scope and assertions.
- Run architecture documentation tests, the documented validator, cARL
  diagnostics, link/secret checks, and diff hygiene; open PR B without merging.

## Non-goals and forbidden scope

- Do not accept ADR 0002, amend ADR 0001, choose a production transport, or
  authorize a non-local broker.
- Do not modify Core, implement IPC, alter production resolver/protocol/
  telemetry, create OS accounts, elevate privileges, or run destructive tests.
- Do not claim executable identity, same-account isolation, independent
  IPC+mTLS factors, performance improvements, or unmeasured platform support.
- Do not describe a configured flag, skipped test, blocked environment,
  cross-compilation, or architecture documentation check as observed OS
  enforcement.

## Contract assertions

1. Every result names its source revision, OS/runtime/toolchain, privilege and
   account model, command, expected behavior, observed behavior, and evidence
   state where available.
2. Linux cross-UID socket permission, Linux peer-UID policy, copied-key mTLS,
   Windows same-SID access, Windows impersonation/handle behavior, and
   Windows unavailable denials are not conflated.
3. Policy denial occurs before provider lookup; authorized missing-reference
   behavior remains separate and unchanged.
4. The decision matrix assesses five alternatives and makes no architecture
   selection; the recommendation states its evidence limits and owner choices.

## Expected files

- `docs/native-ipc-identity-evidence.md`
- `docs/adr/0002-native-ipc-identity-evaluation.md`
- `docs/testing.md`
- `docs/threat-model.md`
- `.github/carl/memory.md`
- `.github/carl/current-pr-contract.md`
- this plan

## Test strategy

- `python3 -m unittest discover -s tests -v`
- `python3 scripts/validate_architecture.py` with the effective pack, cARL
  status and doctor outputs required by the workflow
- `carl status`, `carl doctor`, `carl pack effective --json`, `carl trace`,
  and `carl plan` diagnostics
- Verify local Markdown links and obvious-secret scan via the repository
  validator; run `git diff --check`
- Verify ADR 0002 still states Proposed/deferred/not accepted and ADR 0001 is
  unchanged

These are Architecture documentation checks, not a rerun of Core runtime or
security tests.

## Risks

The evidence is synthetic and cross-repository. Some Windows access-denial
scenarios are not measured; the Linux detailed results are from an earlier
successful run where comparison to the current PR head must show experiment
source unchanged. The experiment is not a production IPC integration and does
not prove executable trust, same-user isolation, or that combining IPC with
mTLS provides independent protection.

## cARL/docs reconciliation

The measured results and owner decisions are durable evidence, so link the
report from ADR 0002, test strategy, threat model, and the memory cache. Keep
the recorded ADR status and production transport unchanged.

## Final integration amendment

Core PR #5 merged at
`0c465c56a6732265bdad8ec3eba143a11b2a9895`; PR-head tests on
`0a7ade6282ee5effc33954eee801509fc81d90cb` passed in run 41337784450, and
default-branch CI on the merge commit passed in run 41338072128. The evidence
report must retain the earlier test-source revisions/runs while adding this
verification chain and the Windows regression test names. The owner
conditionally authorized merging Architecture PR #4 after the refreshed
report, local validation, required `validate` check, and blocker/protection
review all pass. Merge only this PR and verify default-branch CI afterward.
ADR 0002 remains Proposed/deferred/not accepted; production code stays
unchanged.
