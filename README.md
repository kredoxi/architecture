# Kredoxi architecture

Kredoxi replaces credential values in application configuration with non-secret
references, resolving them at an authenticated, authorised runtime boundary.
It is conventional security software, not an AI agent.

**Status:** architecture baseline for review, not a released implementation or
proven security guarantee. The selected MVP is an explicitly integrated Go
resolver, a local mTLS broker and a synthetic provider. An agent running beside
an unmodified application does not substitute references automatically.

## Reading order

| Document | Purpose |
| --- | --- |
| [Requirements](docs/requirements.md) | Vision, non-goals and traceable acceptance criteria |
| [Architecture](docs/architecture.md) | Context, components, trust boundaries and lifecycle |
| [Threat model](docs/threat-model.md) | Four attacker tiers, controls and residual risks |
| [Mechanism research](docs/mechanisms.md) | Explicit integration versus interception, with primary sources |
| [ADR 0001](docs/adr/0001-explicit-local-resolution.md) | Narrow MVP selection and consequences |
| [Contracts](docs/contracts.md) | Reference grammar, identity, policy, providers, runtime and events |
| [Test strategy](docs/testing.md) | Synthetic vertical slice and adversarial evidence gates |
| [Roadmap](docs/roadmap.md) | Compatibility, future integrations and release prerequisites |
| [Governance](docs/governance.md) | Verified cARL integration and outstanding CI controls |
| [Licensing options](docs/licensing.md) | Tradeoffs; no licence selected |

The [Kredoxi organisation](https://github.com/kredoxi) is the project authority.
Implementation belongs in [kredoxi/kredoxi](https://github.com/kredoxi/kredoxi);
shared community governance belongs in
[kredoxi/.github](https://github.com/kredoxi/.github).

Authorised applications still receive secrets in memory and can leak them.
Same-user key theft, application compromise and administrator/root compromise
are not solved by this MVP. No EDR-grade tamper resistance, production vault,
supported-platform claim or distribution permission is implied. All examples
and tests must use synthetic credentials.
