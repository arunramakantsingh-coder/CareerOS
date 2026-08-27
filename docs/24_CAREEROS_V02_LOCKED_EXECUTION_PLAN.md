# CareerOS v0.2 — LOCKED PRODUCT EXECUTION PLAN
Version: 1.0
Status: AUTHORITATIVE — PRODUCT OWNER LOCKED DIRECTION

## 1. Product objective

The immediate goal is to build a genuinely useful CareerOS system for the first real user.

The development priority is the complete personal job-hunting loop:

```text
IDENTITY
  ↓
CAREER DOCUMENTS
  ↓
AI PROFILE
  ↓
PROFILE RECONCILIATION
  ↓
PERSONAS
  ↓
GLOBAL JOB DISCOVERY
  ↓
EMAIL / RECRUITER INTELLIGENCE
  ↓
JOB INTELLIGENCE
  ↓
MATCHING
  ↓
SKILL GAPS
  ↓
APPLICATION ASSISTANCE
  ↓
APPLICATION CRM
  ↓
REMOTE INTELLIGENCE
  ↓
INTERVIEW / LIVE INTERVIEW
  ↓
ANALYTICS / LEARNING
```

Global Mobility / migration / visa functionality is deliberately later.

## 2. Locked onboarding journey

The product starts from the public CareerOS website.

```text
CAREEROS WEBSITE
      ↓
SIGN UP / SIGN IN
      ↓
BASIC ACCOUNT
      ↓
IDENTITY / CONSENT
      ↓
CV UPLOAD OR DRAG & DROP
      +
PROFESSIONAL DOCUMENT VAULT
      ↓
AI DOCUMENT EXTRACTION
      ↓
INITIAL CANDIDATE PROFILE
      ↓
PROFILE COMPLETENESS %
      ↓
PROFILE RECONCILIATION
      ↓
LINKEDIN + PRIMARY EMAIL + PRIMARY PHONE
      ↓
ENRICHMENT / VERIFICATION
      ↓
CANONICAL CAREER PROFILE
      ↓
PERSONAS
      ↓
JOB MATCHING ENGINE
```

## 3. Professional Document Vault

The user may upload/drag-and-drop professional evidence including, where relevant:

- CVs/resumes
- experience/employment letters
- offer/appointment letters
- relieving/experience certificates
- payslips
- professional certifications
- training certificates
- degree certificates
- college/university records
- school certificates
- project evidence
- achievement evidence
- other career-related documents

The Vault is both:

1. evidence storage, and
2. the source layer for AI Profile Intelligence.

The system must preserve provenance: which document supplied each extracted fact.

Sensitive documents require secure storage, access control, encryption, scanning and deletion/export controls.

## 4. AI Profile Engine

The engine should extract, where supported by evidence:

- personal/contact information
- employers
- titles
- employment dates
- responsibilities
- achievements
- skills
- technologies
- architecture/security/networking domains
- cloud
- certifications
- education
- industries
- projects
- leadership/management
- locations
- work preferences
- consulting/contract experience

The engine must distinguish:

```text
EXTRACTED
INFERRED
USER-CONFIRMED
CONFLICTING
MISSING
```

AI must never fabricate candidate facts.

## 5. Profile completeness

The dashboard/profile area must show a profile completeness score.

Example:

```text
PROFILE COMPLETENESS
████████████████░░░░ 82%

Identity             ✓
Contact              ✓
Career history       ✓
Skills               ✓
Certifications       ✓
Education            ✓
LinkedIn             ✓
Primary email        ✓
Primary phone        ✓
Preferences          ░
Missing evidence     ░
```

The score must be explainable and must not be treated as a job-match score.

## 6. Identity requirements

Target sign-in/registration architecture:

- Email/password
- Google OAuth/OIDC
- LinkedIn OAuth/OIDC
- Facebook OAuth/OIDC
- Apple OAuth/OIDC where configured
- Phone OTP
- WhatsApp verification/OTP where supported

Important distinction:

```text
AUTHENTICATION
= who is the user?

EXTERNAL AUTHORIZATION
= what external data has the user explicitly authorized?
```

Examples of separate authorization:

- LinkedIn profile data
- Gmail/Google Workspace
- Microsoft mailbox
- future external services

LinkedIn, primary email and primary phone are required identity/profile anchors for the Career Intelligence flow, subject to explicit user consent and provider capabilities.

WhatsApp is not required to be the sole login mechanism.

## 7. Profile reconciliation

After document extraction and identity enrichment:

```text
Documents
   +
LinkedIn/profile data
   +
User-confirmed data
   +
Primary contact data
   ↓
PROFILE RECONCILIATION
   ↓
CANONICAL CANDIDATE PROFILE
```

Conflicts must be surfaced rather than silently overwritten.

Example:

```text
CV: Senior Network Architect — 2021–2024
Employment letter: Senior Network Architect — 2021–2025
Status: CONFLICT
Action: user review required
```

## 8. Dynamic personas

Personas are derived from the canonical career evidence.

The user should not have to manually create every persona.

Example:

```text
Network Architect
Security Architect
Cybersecurity Architect
Cloud Security Architect
Infrastructure Security Architect
Security Engineering Manager
Firewall/SASE Architect
Network Transformation Architect
Security Consultant
Technical Program/Transformation Lead
```

Personas change positioning and matching weights, not the underlying evidence.

## 9. Global job discovery

After profile/persona readiness, CareerOS begins job discovery.

Source registry must be extensible and include, where permitted:

- LinkedIn
- Naukri
- Indeed
- Glassdoor
- foundit/Monster
- Dice
- ZipRecruiter
- Wellfound
- NaukriGulf
- Bayt
- GulfTalent
- FlexJobs
- SEEK Australia
- SEEK New Zealand
- Trade Me Jobs
- Jora
- Remote OK
- We Work Remotely
- Remotive
- company career portals
- staffing/recruitment portals
- public/government sources where permitted
- recruiter sources
- authorized email feeds

Use permitted APIs, feeds, alerts, public pages or manual import. Do not bypass CAPTCHA, authentication, anti-bot controls or access restrictions.

## 10. Email intelligence

After the user explicitly authorizes mailbox access, CareerOS should identify:

- job alerts
- recruiter emails
- staffing-company messages
- company vacancy alerts
- application acknowledgements
- interview invitations
- rejection emails
- recruiter outreach
- hiring-manager communications
- job recommendations

Relevant opportunities enter the same canonical job pipeline as portal discoveries.

## 11. Job Intelligence and Matching

Every canonical job should have:

```text
Job DNA
  +
Candidate Profile
  +
Persona
  +
Preferences
  ↓
MATCH ENGINE
  ↓
MATCH SCORE + EXPLANATION
```

Matching is capability/evidence-centric, not title-centric.

The engine should expose:

- matched skills
- partial skills
- missing skills
- experience gaps
- mandatory missing requirements
- transferable capabilities
- persona used
- evidence
- hard failures

## 12. 60% rule

The product rule is:

```text
Skill Match >= 60%
        ↓
HIGHLIGHT JOB
```

Boundary tests:

```text
59% = not threshold-qualified
60% = threshold-qualified
61% = threshold-qualified
```

This is a recommendation/high-potential signal, NOT automatic application approval.

## 13. Cumulative Skill Gap Intelligence

Each analyzed job contributes observations:

```text
User
Job
Persona
Skill
Matched / Partial / Missing
Mandatory / Preferred
Evidence
Confidence
Timestamp
```

Aggregated intelligence answers:

- which skills are repeatedly missing
- which are mandatory most often
- which personas are affected
- which role families are affected
- which gaps block high-value jobs
- what the user should strengthen

## 14. Application assistance

The system progresses toward:

```text
DISCOVERED
→ ANALYZED
→ MATCHED
→ RECOMMENDED
→ APPROVED
→ APPLIED
→ ACKNOWLEDGED
→ INTERVIEW
→ OFFER
→ CLOSED
```

Application generation must be evidence-backed.

Automatic submission is later and always subject to explicit user-controlled rules.

## 15. Interview intelligence

CareerOS must eventually support:

- interview preparation
- role-specific preparation
- company preparation
- likely-question generation
- answer guidance
- live interview assistance

Live interview assistance should favor short, actionable cues rather than long paragraphs.

## 16. What is deliberately NOT the immediate priority

Do not allow these to displace the core job-hunting loop:

- visa/migration implementation
- Australia/NZ migration pathways
- sponsorship intelligence
- full SaaS monetization
- advanced autonomous application submission
- broad commercial multi-tenant hardening

They remain on the roadmap.

## 17. Milestone order

```text
M01  Foundation / Stabilization                 VERIFIED
M02  Identity + Career Intake                   NEXT
M03  AI Profile + Profile Reconciliation
M04  Dynamic Personas
M05  Global Job Discovery
M06  Email / Recruiter Intelligence
M07  Job Intelligence + Job DNA
M08  Matching + 60% + Skill Gap
M09  Application Factory
M10  Application CRM
M11  Remote Intelligence
M12  Interview + Live Interview
M13  Analytics / Learning
M14  Global Mobility
M15  Production / SaaS Hardening
```

M02 may include the technical foundation needed for document intake, but later milestones must still be used for deeper AI/profile functionality where appropriate.

## 18. Milestone authorization rule

DeepSeek may implement only the explicitly authorized milestone.

Authorization must identify:

- milestone ID
- objective
- in-scope features
- out-of-scope features
- acceptance criteria
- required tests
- required UI
- required runtime evidence

No AI may silently promote a later-stage feature into the current milestone.

## 19. Definition of done

```text
CODE
 ↓
UNIT/INTEGRATION TESTS
 ↓
BACKEND API
 ↓
FRONTEND UI
 ↓
RUNTIME EXECUTION
 ↓
ARUN OBSERVATION
 ↓
CHATGPT QA
 ↓
REGRESSION
 ↓
STABILITY GATE
 ↓
REGISTRY UPDATE
 ↓
VERIFIED
```

A command/script/report is not itself proof of runtime success.

## 20. Product Owner lock

This document records the Product Owner's current direction.

If a future change materially alters:

- product flow
- identity model
- external integrations
- privacy
- security
- data model
- version boundaries
- automation behavior

the change must be explicitly surfaced for Product Owner approval and recorded in the registry.
