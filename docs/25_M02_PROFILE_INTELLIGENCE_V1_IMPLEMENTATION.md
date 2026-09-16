# CareerOS M02 — Profile Intelligence v1.0

Status: IMPLEMENTING / NOT VERIFIED
Branch: `feature/m02-profile-intelligence-v1.0`
Base: `release/v0.2-global-job-intelligence` at `16563b4`

## Objective
Build the first complete evidence-driven profile intake slice without replacing the existing authentication or canonical candidate model.

## In scope
- Google OAuth/OIDC sign-in foundation.
- Google/Gmail external authorization foundation using a separate consent flow.
- LinkedIn OIDC sign-in and authenticated profile sync foundation.
- Professional Document Vault bulk ingestion.
- Multi-file upload.
- Desktop drag/drop.
- Folder selection via browser directory picker.
- ZIP ingestion with path traversal, file-count, archive-size and per-file limits.
- Mobile camera capture through browser file input.
- PDF/DOCX/TXT/image text extraction.
- OCR fallback for scanned PDFs/images.
- Content SHA-256 duplicate detection.
- Document classification and confidence.
- Canonical vault filename generation.
- Persistent local evidence storage for development.
- Automatic extraction into the existing CandidateProfile, ProfessionalExperience, CandidateSkill, CandidateCertification and CandidateEducation models.
- Provenance via existing `source_type` / `source_id` fields and extraction/document relationships.
- Evidence-backed Profile Intelligence UI.
- Mobile API base resolution from the browser hostname instead of assuming browser localhost.

## Explicit limitations
- LinkedIn OIDC self-service provides identity/lite profile data, not an arbitrary downloadable LinkedIn CV. CareerOS therefore supports LinkedIn identity/profile sync now and treats a LinkedIn-exported PDF as a normal Vault document. Deeper LinkedIn profile fields require the relevant LinkedIn partner/API permissions.
- OAuth provider credentials must be supplied through local `.env`; no secrets are committed.
- OAuth token storage currently uses the existing `ExternalIdentity` fields. Production encryption/key-management hardening remains required before production deployment.
- OAuth state is signed and short-lived but not yet backed by a server-side one-time state store.
- Full conflict-review UI and user-approved reconciliation workflow are the next profile slice; automatic extraction only fills blank canonical fields and does not overwrite non-empty values.
- Project/Achievement ingestion is not written into a duplicate candidate-specific model; the current canonical structures are preserved for a later reconciliation pass.

## Runtime acceptance targets
- Existing password login remains working.
- `/api/v1/health` remains healthy.
- `/api/v1/auth/login` remains functional.
- `/api/v1/documents/batch-upload` accepts multiple files.
- Folder and ZIP uploads create independent document records.
- Original evidence remains on disk under `data/documents/` in development.
- Profile Intelligence displays extracted canonical data and provenance.
- Mobile browser opened at `http://<LAN-IP>:3000` calls `http://<LAN-IP>:8000` when no explicit API URL is configured.

## Verification rule
This module is NOT `VERIFIED` until Arun supplies local runtime evidence and UI acceptance results, followed by ChatGPT QA.
