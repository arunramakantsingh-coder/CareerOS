# CareerOS M02 — OAuth + Professional Vault Repair v1.4

Date: 2026-09-04
Branch: `working/m02-oauth-vault-repair-v1.4-20260904`
Base: `working/m02-profile-builder-v1.3-20260902` @ `5e945c4`
Backup: `backup/m02-profile-builder-v1.3-pre-oauth-vault-fix-20260904`
Status: IMPLEMENTED — LOCAL RUNTIME VERIFICATION REQUIRED

## Scope

This repair is deliberately narrow. It does not redesign CareerOS or replace the existing profile/authentication architecture.

### OAuth

Root cause of the Google sign-in loop: the backend OAuth callback was served from port 8000 and attempted to write the CareerOS access token into `localStorage`. Browser storage is scoped by origin, therefore the token was written (when permitted) for `http://localhost:8000`, not the CareerOS frontend at `http://localhost:3000`. The frontend subsequently had no token and returned the user to login.

Repair:

1. Provider callback creates the CareerOS JWT as before.
2. Backend redirects to frontend `/oauth/callback` with the JWT in the URL fragment (fragment is not sent to the server in HTTP requests).
3. Frontend callback stores `access_token` on the frontend origin.
4. Frontend callback loads `/api/v1/auth/me` with the token.
5. User record is stored and browser is redirected to `/`.

Gmail authorization remains separate from sign-in and retains the readonly Gmail scope flow.

## Upload protocol

Root cause of `Input should be a valid list`: `relative_paths` was declared as a multipart `List[str]`, but a single CV upload supplied one scalar field. Multipart/Pydantic coercion produced HTTP 422 before the upload pipeline executed.

Repair:

- Frontend sends one `relative_paths` form field containing a JSON array.
- Backend accepts the form field as a string and parses the JSON array.
- The same protocol works for CV, multiple files and browser folder uploads.
- Legacy scalar values are accepted as a one-item compatibility fallback.

## Evidence pipeline additions

For every supported ingested document, CareerOS continues to preserve the original uploaded file as authoritative evidence and now additionally persists:

- SHA-256
- extracted/OCR text in DB source metadata
- classification and confidence
- canonical stored filename
- per-document Markdown metadata sidecar
- extraction method and OCR state
- source relative path / ZIP path
- profile enrichment through the existing `ExtractionService`

For image evidence (JPG/JPEG/PNG/TIF/TIFF/WEBP):

- original image is preserved
- OCR is attempted
- a normalized PDF is created as a **derived** artifact
- derived PDF path is recorded in evidence metadata

## Runtime gates

Do not merge this repair into a release/version branch until all of the following are observed locally:

1. `docker compose ps` — postgres healthy, backend up, frontend up.
2. `GET /api/v1/health` — HTTP 200.
3. Frontend TypeScript check — exit code 0.
4. Google sign-in — account chooser → CareerOS dashboard, not login.
5. `/api/v1/auth/me` succeeds after Google sign-in.
6. Dedicated CV upload succeeds without HTTP 422.
7. Multiple document upload succeeds without HTTP 422.
8. Evidence records appear in the Documents library.
9. Uploaded document has `.metadata.md` sidecar under `data/documents/...`.
10. Image upload has original evidence + derived PDF.
11. Extracted data becomes visible through the existing profile/profile-intelligence pipeline where supported by the parser.
12. No regression in email/password login.

Only after these observations may the repair be marked VERIFIED.
