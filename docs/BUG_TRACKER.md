# CareerOS — Bug Tracker

## M02 Profile Repair v1.2

- BUG-001 — FastAPI validation arrays were rendered as React children during document upload. **Fixed** by normalizing API error payloads before rendering.
- BUG-002 — CV intake and professional bulk vault were not clearly separated. **Fixed** in the Documents UI.
- BUG-003 — Horizontal navigation duplicated the vertical module list. **Fixed** by making the horizontal strip a career journey: Home → Build Profile → Discover → Apply → Interview → Insights.
- BUG-004 — Mobile camera capture was unreliable, especially over LAN HTTP. **Mitigated** with a real browser camera scanner when secure-context APIs are available plus a file/capture fallback and clear secure-context guidance.
- BUG-005 — OAuth provider buttons had weak configuration feedback. **Superseded by BUG-007** after runtime reproduction identified the callback-origin defect.
- BUG-006 — Profile builder did not expose a complete manual career form. **Fixed** with editable personal, experience, education, certification and skills sections using existing canonical models.

## M02 OAuth + Vault Repair v1.4 — 2026-09-04

- BUG-007 — Google OAuth reached the Google account chooser successfully but returned to CareerOS as unauthenticated. **Implementation fixed; local runtime verification pending.** Root cause: the backend callback response on `localhost:8000` attempted to write `localStorage`; browser storage is origin-scoped, so the token never reached the frontend origin on `localhost:3000`. Repair: backend now redirects to `/oauth/callback` using a URL fragment; the frontend callback stores the token in the correct origin, loads `/api/v1/auth/me`, persists the user session, and opens the dashboard.
- BUG-008 — Dedicated CV upload returned `Input should be a valid list`. **Implementation fixed; local runtime verification pending.** Root cause: multipart `relative_paths` was declared as `List[str]` while the single-file client supplied a scalar form value. Repair: clients serialize paths as one JSON array and backend parses that deterministic field.
- BUG-009 — Professional Document Vault multi-file/folder upload returned the same `Input should be a valid list` validation error. **Implementation fixed; local runtime verification pending.** Same protocol repair as BUG-008, preserving one path per uploaded file.
- BUG-010 — Evidence pipeline did not persist the previously requested human-readable Markdown sidecar for each ingested document. **Implementation added; local runtime verification pending.** Each persisted evidence file now receives a `.metadata.md` record containing document identity, SHA-256, classification, extraction method, OCR state, derived-artifact path and extracted text. The original remains authoritative.
- BUG-011 — Image/scanner evidence had OCR but no normalized PDF derivative. **Implementation added; local runtime verification pending.** JPG/JPEG/PNG/TIF/TIFF/WEBP uploads retain the original image and create a derived PDF for downstream document workflows.
- BUG-012 — Documents page referenced `useAuth()` without importing it in the current branch source. **Fixed in v1.4 repair branch; build/runtime verification pending.**

## Rule
Keep defects visible, classify them, and do not mark a fix VERIFIED until local runtime testing passes. Implementation-complete is not runtime-verified.
