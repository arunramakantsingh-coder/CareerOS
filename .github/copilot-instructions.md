# CareerOS — Repository-wide Copilot Instructions

CareerOS is an existing AI-powered Global Career Operating System built around a canonical professional identity/evidence model. Extend and repair the current implementation; do not rebuild the product.

## Read first

Read `AI_TAKEOVER.md` and `AGENTS.md` before changing code. For current handover state also read `docs/AI_TAKEOVER/02_CURRENT_STATE_20260903.md`, `docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`, `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`, and `docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`.

## Product boundaries

- v0.1 Personal Job & Interview Copilot is frozen.
- Current v0.2 work is profile-first: Profile Builder, CV intake, Professional Document Vault and Profile Intelligence precede Personas, Global Job Discovery and later Live Interview Assistance.
- Keep CV intake separate from the Professional Document Vault.
- Keep application settings separate from career/profile data.
- Vertical navigation is domain-level; horizontal navigation is contextual and must not duplicate the vertical list.
- Career facts must remain evidence-backed and user-editable.

## Engineering safety

- Inspect before changing; reuse before creating; patch before replacing.
- Prefer small, reversible, reviewable changes.
- Never modify an applied Alembic migration.
- Never commit credentials, tokens, `.env` values or private keys.
- Never trust client-supplied tenant identity.
- Never fabricate career/job/company/immigration facts.
- Do not silently expand milestone scope.
- Do not claim tests or verification that were not actually executed.

## Git / verification

Use the exact current branch and inspect ancestry before working. The repository currently has a known divergence between the profile-builder and live-interview working branches; see `docs/AI_TAKEOVER/02_CURRENT_STATE_20260903.md`. Do not treat a higher-looking version number as proof of freshness.

Before stopping, record changes, tests, runtime evidence, bugs, blockers and the exact next action in `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`.

A feature is only VERIFIED after executable evidence and reviewer approval.

## UI quality

The product should feel like a coherent career operating system: persistent profile identity, clear hierarchy, dimensional/translucent professional UI, concise information density, accessible forms, stable controlled inputs, compact date pickers and explicit dropdowns. Avoid duplicate navigation and avoid placeholder UI presented as completed functionality.
