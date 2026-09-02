# CareerOS — Bug Tracker

## M02 Profile Repair v1.2

- BUG-001 — FastAPI validation arrays were rendered as React children during document upload. **Fixed** by normalizing API error payloads before rendering.
- BUG-002 — CV intake and professional bulk vault were not clearly separated. **Fixed** in the Documents UI.
- BUG-003 — Horizontal navigation duplicated the vertical module list. **Fixed** by making the horizontal strip a career journey: Home → Build Profile → Discover → Apply → Interview → Insights.
- BUG-004 — Mobile camera capture was unreliable, especially over LAN HTTP. **Mitigated** with a real browser camera scanner when secure-context APIs are available plus a file/capture fallback and clear secure-context guidance.
- BUG-005 — OAuth provider buttons had weak configuration feedback. **In review**; backend routes exist and runtime provider credentials/callbacks must be verified locally.
- BUG-006 — Profile builder did not expose a complete manual career form. **Fixed** with editable personal, experience, education, certification and skills sections using existing canonical models.

## Rule
Keep defects visible, classify them, and do not mark a fix verified until local runtime testing passes.
