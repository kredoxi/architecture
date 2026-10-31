# Vision, requirements and scope

## Problem and non-goals

Configuration, source and environment-file disclosure should reveal references,
not credentials. Resolution must authenticate a principal, authorise a specific
reference and report access without recording values. References are not
capabilities: knowing one grants no authority.

Kredoxi does not eliminate application memory exposure, exfiltration by an
authorised caller, privileged host compromise, malicious dependencies executing
inside a caller, or denial of service. Monitoring is not enforcement. A daemon
alone cannot change arbitrary file reads.

This repository addresses Phase B of the execution brief. It defines core
implementation and adversarial acceptance gates; it does not claim Phase C/D
executed here. Organisation settings must be verified in the separate governance
workstream before being reported as enabled.

## Requirements and traceability

| ID | Requirement | Design and evidence gate |
| --- | --- | --- |
| R01 | Consumer configuration contains references, not values | [Grammar](contracts.md#reference-grammar-v1); T01 in [tests](testing.md) |
| R02 | Canonical parsing without traversal or ambiguous encoding | Grammar; T02, T08 |
| R03 | Authenticated principal, not asserted process name/PID | [Identity](contracts.md#identity-and-authorisation); T04, T09 |
| R04 | Deny-by-default exact scoped authorisation | Identity; T10, T13 |
| R05 | Replaceable providers with bounded cancellation | [Provider](contracts.md#provider-contract); T03, T05, T12 |
| R06 | Explicit secure failure and resource limits | [Runtime](contracts.md#runtime-contract); T06, T07, T20 |
| R07 | Versioned privacy-conscious access events | [Events](contracts.md#event-contract-v1); T11, T14 |
| R08 | Honest tiers and tamper limits | [Threat model](threat-model.md); T15, T16 |
| R09 | Actual read interception evaluated before adoption | [Research](mechanisms.md); adapter experiments |
| R10 | Local synthetic authenticated vertical slice | [ADR](adr/0001-explicit-local-resolution.md); demo gate |
| R11 | Platform support based on execution evidence | [Roadmap](roadmap.md); per-platform test gate |
| R12 | Address replay, caching, rotation, rollback and TOCTOU | Architecture; T13, T15, T17-T20 |
| R13 | Preserve cARL and least-privilege change control | [Governance](governance.md); effective contract verification |
| R14 | No unapproved licence or production release | [Licensing](licensing.md); release gate |

## MVP scope

A consumer reads a synthetic reference, requests resolution from a local mTLS
broker, uses the returned synthetic bytes without printing them, and discards
owned buffers. Another authenticated principal is denied; an unenrolled client
is rejected. Broker/provider outage produces explicit failure, not a plaintext
fallback. No automatic export to the environment or command line is allowed.

Use one synthetic memory-only provider, not an insecure production vault.
Never access real local credentials, cloud accounts, personal secret stores or
browser credentials. No cloud integration is required to demonstrate the slice.
Convenience client code and an API are integrations, not transparent interception.

Azure Key Vault, Google Secret Manager, CyberArk, encrypted local vaults,
OS-native IPC/events, launch/configuration adapters and protocol proxies remain
future replaceable integrations. The product is not permanently SDK-only.
