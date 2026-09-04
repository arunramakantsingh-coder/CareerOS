# CareerOS — Consolidated Product Requirements Baseline

This document consolidates the product requirements established across the CareerOS design/control conversations. It is a requirements record, not a claim that every item is already implemented.

## A. Product philosophy

CareerOS is a **career operating system**, not a conventional job portal. The candidate's professional identity, evidence and career history form the foundation. Jobs are interpreted against that foundation.

Core loop:

```text
Professional Identity
→ Evidence / Career Vault
→ Profile Intelligence
→ Personas
→ Global Opportunity Discovery
→ Job Intelligence / Job DNA
→ Capability & Evidence Matching
→ Skill Gaps
→ Application Intelligence
→ Interview Intelligence
→ Outcomes / Learning
→ Improved Career Profile
```

## B. First-run user journey

```text
Login / SSO
   ↓
Dashboard
   ↓
Professional Identity
   ├── Profile
   ├── Profile Setup / Builder
   ├── Profile Intelligence
   ├── CV intake
   ├── Professional Document Vault
   ├── Career Vault
   └── Personas
```

Onboarding should not become a separate product island. It is part of the Professional Identity/Profile journey and may prefill the same canonical profile model.

## C. Authentication and integrations

### Google
- Google SSO/OIDC for identity.
- Separate Gmail authorization for mailbox access.
- Gmail is intended to support recruiting/application/interview email intelligence, not merely to prove identity.
- OAuth credentials are server-side configuration.

### LinkedIn
- LinkedIn SSO/OIDC.
- Profile synchronization where permitted by the LinkedIn API/product access available to the application.
- Do not promise arbitrary CV download unless the approved LinkedIn API capability actually provides it.

### General
- Provider authorization is separate from local session authentication.
- Provider credentials never belong in Git.
- Redirect URI configuration is an external provider-side dependency.

## D. Profile Builder

The Profile page is the user's editable career record. It should be comprehensive enough to resemble the profile-building experience of a serious job portal while retaining CareerOS's evidence/provenance model.

Required sections:

1. Personal details
2. Resume/CV
3. Resume headline
4. Profile summary
5. Key skills
6. IT skills
7. Employment / Work Experience 1..N
8. Education 1..N
9. Certifications
10. Projects
11. Accomplishments
12. Career profile / target roles / preferences
13. Profile Performance
14. Missing information / completeness prompts
15. Evidence/provenance for machine-populated fields

Rules:

- User can manually add missing information.
- User can edit automatically populated information.
- User-confirmed information must not be silently overwritten by later extraction.
- AI may suggest; the user remains the authority over personal career facts.

## E. CV intake

CV upload is an independently visible capability.

Expected behavior:

- Upload/replace CV.
- Multiple file selection where useful.
- Parse and extract structured information.
- Use the CV as a high-value profile evidence source.
- Show extraction/processing state and errors.
- Keep the CV record distinct from the broader professional document vault.

## F. Professional Document Vault

The vault is a durable evidence store, not simply an upload widget.

Required intake modes:

- multiple file upload
- drag-and-drop multiple files
- folder selection
- ZIP upload
- camera/scan capture where browser security and device capabilities allow it
- individual document upload

Expected processing:

```text
file
→ metadata
→ hash / duplicate detection
→ safe type validation
→ extraction
→ OCR fallback
→ classification
→ structured facts
→ confidence
→ provenance
→ searchable/indexed evidence
```

The vault must retain enough metadata/indexing to explain where a profile fact came from.

## G. Profile Intelligence

Profile Intelligence reconciles evidence into structured profile suggestions.

It should be able to answer:

- What information is known?
- What source produced it?
- How confident is the extraction?
- What conflicts exist between sources?
- What fields are missing?
- What can be suggested automatically?
- What needs user confirmation?

Preferred flow:

```text
Evidence
→ Extraction
→ Confidence
→ Reconciliation
→ Suggestion
→ User confirmation
→ Canonical profile
```

## H. Navigation and UI

### Vertical navigation — domains

The vertical bar is for the operating-system/domain structure:

- Overview
- Professional Identity
- Opportunity
- Interview & Insight
- Global
- Project Control

### Horizontal navigation — contextual tools

The horizontal bar must **not duplicate the vertical domains**. It exposes sub-functions for the selected domain.

Example Professional Identity context:

- Profile
- Profile Setup
- Profile Intelligence
- CV & Documents / Document Vault
- Career Vault
- Personas

Opportunity, Interview & Insight, Global and Project Control should similarly expose their own contextual sub-navigation.

### Persistent shell

- Profile identity remains visible at the top of every page.
- Dashboard/Home remains reachable from the shell.
- Three-dot/overflow control is for additional application features/settings, not another copy of navigation.
- Application settings are global application settings, not profile settings.
- The shell should feel like a professional operating system: layered/translucent, dimensional, technically sophisticated, readable, calm and consistent.

## I. Forms and interaction

Global form contract:

- Text boxes must accept complete strings without losing focus after the first character.
- Controlled inputs must use stable state/update behavior.
- Date fields use a compact calendar/date-picker with month/year navigation.
- Enumerated fields use dropdowns rather than free text when the domain is controlled.
- Seniority dropdown must include:
  - Entry-Level
  - Mid-Level
  - Senior-Level
  - Lead / Principal
  - Executive / C-Suite
- Forms need validation, loading, empty and error states.

## J. Opportunity / global job search

This comes after the profile foundation. The system should search globally using the candidate's evidence-backed profile and personas rather than title-only queries.

The later matching model must consider:

- capabilities
- responsibilities
- technologies
- architecture/domain
- leadership/seniority
- industry
- transferable skills
- location/remote
- salary
- work authorization
- mobility constraints
- mandatory requirements
- preferred requirements

Skill Match is distinct from Overall Career Fit. A job at **60% Skill Match or higher** is a visible high-potential signal.

## K. Live Interview Assistant

This is a **real live interview assistance workspace**, not interview preparation.

Future intent:

- operate alongside permitted Teams/Zoom/Google Meet or other meeting workflows
- receive live transcript/audio context through supported and permissioned mechanisms
- detect the interviewer's question/topic
- provide very short, indicative answer cues
- keep the answer panel high-signal and non-paragraphic
- ground career-specific claims in the candidate's verified profile/evidence

Example style:

```text
Weight: Highest wins — Cisco local
Local Preference: Highest wins — AS-wide
AS Path: Shortest wins
Origin: IGP > EGP > Incomplete
MED: Lowest wins
```

Do not convert this panel into a long essay generator. Keep it concise enough to glance at during a live conversation. Existing control policy requires permission-aware use when the interviewer/assessment explicitly allows AI assistance.

## L. Project control

The application must expose and maintain:

- Bug Tracker
- Project Tracker
- Roadmap
- Module / Version Registry
- Current Control State
- AI-to-AI handover documentation

The records must distinguish:

```text
PLANNED
AUTHORIZED
IMPLEMENTING
IMPLEMENTED
EXECUTED
OBSERVED
QA REVIEW
VERIFIED
DEFERRED
SUPERSEDED
RETIRED
```

## M. Versioning / Git discipline

- v0.1 Personal Job & Interview Copilot is frozen.
- v0.2 Global Job Intelligence extends the same architecture.
- Use versioned milestone/working branches.
- Create a backup checkpoint before risky changes.
- Work in a focused branch/module workspace.
- Test locally.
- Open a PR / provide pull instructions.
- Review actual diff and runtime evidence.
- Merge only after approval.
- Never rewrite historical module records to make old code appear newer.

## N. Evidence and truth

A feature is not verified because a file exists or an AI says it works.

Required lifecycle:

```text
IMPLEMENTED
→ TESTED
→ OBSERVED
→ REVIEWED
→ VERIFIED
```

The canonical evidence model must protect against invented career facts. Generated application/profile/interview content should remain traceable to available evidence when it makes factual claims.
