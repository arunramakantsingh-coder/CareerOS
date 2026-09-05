# CareerOS M02 — Profile Reconciliation & Evidence Intelligence Brief v1.5
Date: 2026-09-04
Status: WORKING BRANCH — RUNTIME VERIFICATION REQUIRED

## Roles for this milestone
- **ChatGPT — Product Architect / Application Architect / Lead QA / Security & Verification Authority**
- **DeepSeek — Developer / Coder / Implementation Agent**
- **Arun — Human Runtime Executor / Browser Acceptance / External-provider configuration authority**

## Non-negotiable product rule
CareerOS is an evidence-first career operating system. The canonical profile is user-controlled. Uploaded evidence is authoritative source material; extracted fields are suggestions until reconciled.

## Profile source precedence
1. **CV / Resume** — the only automatic document source permitted to populate the canonical profile in M02.
2. **Google / LinkedIn identity** — permitted to seed identity fields returned by the provider.
3. **Professional Document Vault** — classify, OCR/extract, index and preserve evidence; do NOT automatically copy content into profile sections.
4. **Manual Profile Setup** — user is the final authority and may add/edit missing information.

## Section isolation
- Certifications extracted from a CV must come from the CV certification/credentials section or a strong credential pattern.
- Education must come from the CV education/academic section and strong degree/institution patterns.
- Employment must come from the CV experience/employment section.
- Skills must come from the CV skills/technology/competency section.
- Do not promote arbitrary text from another section into a different profile section merely because a keyword matches.
- Confidence and provenance must be retained for derived values.

## Evidence Library USP
Every document should expose, where available:
- original filename
- detected document class/subtype
- issuer
- classification confidence
- processing/extraction state
- OCR state
- source relative path / ZIP parent
- SHA-256
- Markdown metadata sidecar
- normalized PDF for image evidence
- extraction/profile-enrichment relationship

## Multiple CV / persona foundation
Multiple CV versions remain independently stored evidence. Future persona generation may compare CV variants with a JD and canonical profile, but persona generation must not rewrite the canonical evidence layer.

## Email integration architecture
Do not assume Gmail is the user's only mailbox. The product should support:
- Google OAuth for Gmail where permitted
- provider-specific OAuth for supported providers
- IMAP/SMTP or app-password based connectors for providers without suitable OAuth, with secrets stored server-side only
- a provider-neutral mailbox abstraction for job alerts, recruiter mail, application communication and future automation

Gmail OAuth may remain blocked by Google's consent-screen/testing policy even when Google SSO works. This is an external Google Cloud configuration gate, not a reason to weaken the CareerOS security boundary.

## QA gate
A milestone is NOT VERIFIED until local runtime proves:
- backend/frontend/database healthy
- TypeScript/Python checks pass
- Google SSO lands on Dashboard
- email/password login remains functional
- CV upload works
- bulk/folder/ZIP/image upload works
- evidence records appear in the Evidence Library
- CV-only profile enrichment occurs
- non-CV evidence does not contaminate profile sections
- manual profile editing works without focus/input loss
- dates use date controls and select fields use controlled options
- no regression in existing shell navigation

## Scope boundary
This milestone completes Professional Identity/Profile foundations. Global job search and Live Interview Assistance remain subsequent product milestones. Do not implement them opportunistically inside this change.
