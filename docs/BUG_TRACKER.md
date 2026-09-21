# CareerOS — Bug Tracker

## M02 Profile / OAuth / Vault — 2026-09-04

### Resolved in implementation — runtime verification required
- **BUG-007 — Google SSO callback loop.** Google account chooser worked but the session returned to `/login`. Repair uses the frontend-origin OAuth callback and fragment token handoff so `localStorage` is written on `localhost:3000` rather than `localhost:8000`.
- **BUG-008 — Dedicated CV upload validation.** `relative_paths` is now transported as a deterministic JSON list for multipart requests.
- **BUG-009 — Professional Document Vault bulk validation.** Multi-file/folder/ZIP intake uses the same list protocol; single CV intake remains separate.
- **BUG-010 — Evidence metadata sidecar.** Evidence ingestion retains the original file and creates the requested human-readable Markdown metadata record containing identity, hash, classification, extraction/OCR state and derived artifacts.
- **BUG-011 — Image evidence normalization.** Image/scanner evidence can retain the original while producing a PDF derivative for downstream workflows.
- **BUG-012 — Documents page auth import.** Missing `useAuth` import repaired.
- **BUG-013 — Profile contamination.** Non-CV professional documents could contribute generic extracted information to the canonical profile. **Fixed in v1.5:** only documents classified as `cv` may automatically enrich the canonical profile.
- **BUG-014 — Section cross-contamination.** Loose CV regexes could classify arbitrary text as certification/education/skills. **Fixed in v1.5:** section-aware parser with conservative certification and education extraction.
- **BUG-015 — Duplicate navigation semantics.** Horizontal navigation repeated vertical navigation. **Fixed in v1.5:** vertical bar represents domains; horizontal bar represents tools within the selected domain. Professional Identity now exposes Profile → CV & Documents → Profile Setup → Evidence Library → Career Vault → Personas.
- **BUG-016 — Profile Setup had become a separate onboarding universe.** **Fixed in v1.5:** Profile Setup is now a unified application route and legacy `/onboarding` redirects into the profile builder.
- **BUG-017 — Evidence Library was embedded rather than first-class.** **Fixed in v1.5:** dedicated Evidence Library route with detected document class, confidence, processing state, provenance and hash columns.
- **BUG-018 — Command/Techno date controls and selects visually diverged from the OS theme.** **Fixed in v1.5:** dark color-scheme, primary accent and themed option surfaces are applied to native controls.

### External configuration gate
- **BUG-019 — Gmail mailbox authorization blocked by Google OAuth Testing policy.** This is not a CareerOS callback failure. Google can allow the basic Google SSO scope while separately blocking Gmail API scopes until the account is added as a test user or the OAuth application completes the appropriate Google verification/publishing process. **Action:** Google Cloud Console → Google Auth Platform → Audience → Test users → add the intended Gmail account; then retry Gmail connection.

## Verification rule
Implementation-complete is not VERIFIED. A defect is VERIFIED only after the local Docker runtime and browser acceptance test pass. Preserve all backup/version branches before merging milestone changes.
