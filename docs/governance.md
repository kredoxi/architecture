# cARL governance integration

## Verified repository state

On 2026-10-31 the user-requested Winget package `goldjg.cARL` supplied CLI/runtime
1.0.2, source `goldjg/cARL`, tag `v1.0.2`, commit
`5e60b70fc45d7ec036c6b3e702a9a01bced223d9`. The full Winget binary path was used
because another `carl` PATH entry resolved to an older installation.

Supported `init` installed 38 managed runtime artefacts. `pack select` recorded
selection without removing the bundled packs. `harness sync copilot` installed
the production Copilot loader. `status` reported Healthy, no missing/drifted
artefacts and healthy adapters. `pack effective` and `trace` verified the
following additive policies with no overrides or conflicts:

```text
core/baseline
core/carl
core/cognition-governance
core/dependency
core/identity
core/memory-cache
core/pr-contract
core/security
core/tool-permission-tiers
languages/go
platform/cicd
```

All core controls are repository defaults in `.github/carl/profiles.json`.
Go and CI/CD are the architecture profile. Other bundled packs remain installed
and selected but inactive; presence is not activation. Do not load inactive packs
as a substitute for evaluating canonical state.

The canonical contract covers this documentation/governance PR. Bundled memory
described upstream cARL rather than Kredoxi; user-owned memory was intentionally
replaced with this repository's purpose, product boundaries and open decisions.
Bundled invariants, trust boundaries, tool policy, instruction definitions and
loader authority were preserved. Product boundaries are documented in
[architecture](architecture.md) and [threat model](threat-model.md), linked from
memory, rather than weakening bundled agent trust controls.

Diagnostic/loader availability is not proof that a model follows every prose
rule or that Kredoxi is secure.

`.gitattributes` preserves LF text on checkout, including the managed runtime
artefacts. This prevents Windows autocrlf conversion from creating byte-level
cARL drift in a fresh checkout.

## Supported maintenance procedure

Use the current verified CLI from within this checkout. Windows invocation:

```powershell
$carl = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\goldjg.cARL_Microsoft.Winget.Source_8wekyb3d8bbwe\carl.exe"
& $carl --version
& $carl status
& $carl doctor
& $carl pack effective --json
& $carl trace --json
& $carl harness status
```

Review findings, not only exit codes: doctor is diagnostic and can exit zero
with findings. `init` is for empty installations; `init --adopt` preserves
existing artefacts when no manifest exists. Do not hand-edit runtime.json,
silently run repair on user changes, overwrite protected memory, or infer pack
state from directory enumeration. Upstream
[CLI reference](https://github.com/goldjg/cARL/blob/v1.0.2/CLI.md) is the tool
integration reference, not Kredoxi product authority.

After structural changes run `map` then `reconcile` through the CLI to update
derived repository inventory/memory. Read approved contract/invariants/trust
boundaries/tool policy and effective non-overridden packs before execution.

## Remaining controls

The `Architecture validation` workflow uses `contents: read`,
immutable-pinned checkout, checksummed cARL 1.0.2 and standard-library Python
validation. Its `validate` job has completed successfully on the open PR. This
PR does not configure it as a required check or change rulesets. Organization
security settings, dependency alerts or release workflows are not configured
here. Verify live settings separately; do not report recommendations as enabled.
Licence/redistribution review remains open.

Core provider/event/resource contracts were reconciled against the Core
implementation PR's protocol and broker source. CI checks the protocol file
against the current Core default branch or open implementation PR, and falls
back to the pinned reviewed revision if Core has not published that file.
The core session reports a clean standard-library
vulnerability scan after requiring Go 1.27.3; retain its scan output/toolchain
evidence with Core rather than treating this architecture statement as an
independently executed validation.
