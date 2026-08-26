# CareerOS — Original Project Idea (Reconstructed Canonical Version)

> This document restructures the original `ORIGNAL_PROJECT_IDEA.md` into a progressive product story. It intentionally preserves the original ideas instead of reducing them to a generic job-board specification.

---

# Stage 0 — Origin and Problem

The original idea is not simply "find a job."

The problem is:

> A candidate has a complex career that cannot be represented reliably by one CV headline or one job title. Job opportunities are distributed across portals, recruiter messages, company sites and email alerts. The candidate needs an AI system that understands the career, discovers opportunities beyond title matching, determines whether they are realistically valuable, helps prepare truthful applications, and learns from outcomes.

The intended future behavior is therefore an **AI Career Agent** combining:

**Recruiter + Job Search Engine + Career Strategist + Resume Analyst + Application Assistant + Personal Career Manager.**

The original vision explicitly describes an end-to-end loop in which the user uploads a CV, AI understands the candidate, generates personas, searches globally, interprets email, discovers opportunities, finds the original company JD, analyzes the match, ranks the opportunity, alerts the user, assists with applications, tracks outcomes and learns. 

---

# Stage 1 — Candidate Profile Intelligence

The candidate should be able to start with a CV/profile and basic preferences.

AI should identify, where evidence exists:

- identity/contact
- career history
- employers
- job titles
- responsibilities
- years of experience
- skills
- technologies
- architecture domains
- security domains
- networking domains
- cloud
- certifications
- education
- industries
- projects
- leadership
- management
- achievements
- locations
- work preferences
- contract/permanent experience
- consulting experience

The system must understand **actual capabilities**, not only the headline.

---

# Stage 2 — Multiple CVs → Unified Career Record

CareerOS must support multiple CVs because different CVs may emphasize different:

- titles
- responsibilities
- technologies
- skills
- projects
- industries
- certifications
- achievements
- career experiences

The system should:

1. parse each CV
2. extract structured information
3. normalize terminology
4. detect duplicates
5. identify conflicts
6. merge complementary facts
7. preserve provenance
8. build the unified Career Vault

### Career Vault rule

The Career Vault is the authoritative internal career record.

AI may rewrite, summarize, prioritize, reorder and tailor facts.

AI may not invent employers, dates, technologies, certifications, projects, metrics or years of experience.

---

# Stage 3 — Career Passport and Career Capability Graph

The original idea evolved beyond a CV repository.

### Career Passport

```text
Career Passport
├── Identity
├── Career Summary
├── Experience
├── Skills
├── Architecture Domains
├── Technologies
├── Certifications
├── Projects
├── Achievements
├── Leadership
├── Governance
├── Career Evidence
├── Personas
└── Resume Versions
```

### Career Vault

The Career Vault is the **evidence layer** of the Career Passport.

### Career Capability Graph

The long-term differentiator is the ability to represent capability strength across:

- architecture
- security
- networking
- cloud
- governance
- transformation
- leadership
- technologies
- transferable capabilities

The graph must make it possible to reason about jobs whose advertised title differs from the candidate's familiar roles.

---

# Stage 4 — Persona Intelligence

The original concept requires multiple professional personas to be derived from the same career evidence.

Example persona family:

1. Network Architect
2. Security Architect
3. Cyber Security Architect
4. Cloud Security Architect
5. Infrastructure Architect
6. Security Engineering Manager
7. Firewall/SASE Architect
8. Network Transformation Architect
9. Security Consultant
10. Cybersecurity Program/Technical Lead
11. Network Manager
12. IT Manager
13. Custom Persona

The implementation baseline formally defines at least:

- Network Architect
- Security Architect
- Cyber Security Architect
- Infrastructure Architect
- Network Manager
- IT Manager
- Custom Persona

Personas must not duplicate the underlying career facts.

A persona changes:

- positioning
- weighting
- target roles
- industries
- capabilities
- countries
- locations
- salary
- work mode
- presentation strategy

---

# Stage 5 — Global Job Discovery

The original vision calls for continuous discovery across:

- LinkedIn
- Naukri
- Indeed
- Glassdoor
- foundit/Monster
- Dice
- ZipRecruiter
- Wellfound
- direct employer career pages
- recruitment/staffing portals
- public/government sources where permitted
- email alerts
- recruiter communications

The architecture must be extensible.

### Compliance rule

Prefer:

- APIs
- feeds
- alerts
- permitted integrations
- public employer pages
- manual import

Never bypass:

- authentication
- CAPTCHA
- anti-bot controls
- rate limits
- access restrictions

---

# Stage 6 — Email Intelligence

Authorized email can be a job intelligence source.

CareerOS should identify:

- job alerts
- recruiter emails
- staffing-company notifications
- company vacancy alerts
- application acknowledgements
- interview invitations
- rejection emails
- recruiter outreach
- hiring-manager communications
- new vacancy notifications
- recommendations

The AI should determine whether a message represents a genuine opportunity and add it into the central opportunity pipeline.

The long-term design also allows new job sources to be learned/discovered from incoming messages.

---

# Stage 7 — Job Opportunity Extraction

Each discovered job becomes a normalized canonical opportunity.

Extract:

- advertised title
- company
- location
- country
- remote model
- employment model
- salary
- source
- external reference
- raw JD
- canonical JD
- requirements
- seniority
- responsibilities
- technologies
- recruiter
- hiring manager where legitimately available
- application URL
- original employer reference
- work authorization
- relocation
- sponsorship

---

# Stage 8 — Company Portal Intelligence

A job found through an aggregator may be a copy of the employer's original vacancy.

CareerOS should attempt to identify the **original employer vacancy**, preserving source references and provenance.

The original company page becomes a stronger source where available.

---

# Stage 9 — Job DNA

Every job is converted into Job DNA.

```text
Job DNA
├── Role Family
├── Advertised Title
├── Seniority
├── Capabilities
├── Technologies
├── Responsibilities
├── Architecture Domains
├── Leadership
├── Governance
├── Industry
├── Location
├── Employment Model
├── Salary
├── Mandatory Requirements
├── Preferred Requirements
└── Mobility Constraints
```

The employer's advertised title is never replaced.

---

# Stage 10 — Capability-Centric Matching

The core differentiator is:

**SEARCH BY CAREER CAPABILITY, NOT JOB TITLE.**

Discovery becomes:

```text
TITLE DISCOVERY
      +
CAPABILITY DISCOVERY
      +
SEMANTIC DISCOVERY
      ↓
JOB DNA
      ↓
CAREER/PERSONA MATCH
```

A role such as **Digital Resilience Transformation Lead** may be relevant to Network Architect, Security Architect or Cyber Security Architect when the JD requires capabilities such as:

- enterprise networking
- Palo Alto
- Zero Trust
- cloud connectivity
- security transformation
- resilience
- governance
- leadership

Title similarity must not dominate.

---

# Stage 11 — Match Score and Explanation

The system should distinguish:

### Strong match

Candidate is highly qualified.

### Partial match

Candidate is a viable fit with identifiable gaps.

### Weak match

The opportunity is unlikely to provide sufficient value.

The match must explain:

- why it matches
- matched skills/capabilities
- partial skills
- missing skills
- hard failures
- evidence
- persona relevance

---

# Stage 12 — 60% Skill-Match Opportunity Signal

This is an explicit CareerOS product rule added to the handoff.

```text
Skill Match >= 60%
        ↓
HIGHLIGHT AS HIGH-POTENTIAL OPPORTUNITY
```

This is **not** an automatic application rule and is not the same as Overall Career Fit.

A job can therefore show:

```text
Career Fit        72%
Skill Match       64%   ← highlighted
Hard Failures      0
```

The UI must immediately expose:

- matched skills
- partial skills
- missing skills
- mandatory missing skills
- transferable skills
- persona comparison
- experience comparison

Boundary behavior must be testable:

```text
59% → not threshold-qualified
60% → threshold-qualified
61% → threshold-qualified
```

---

# Stage 13 — Cumulative Skill Gap Intelligence

This turns job analysis into career development.

For every analyzed opportunity, CareerOS records skill/capability gaps.

### Observation

```text
User
Job
Persona
Skill/Capability
Matched / Partial / Missing
Mandatory / Preferred
Confidence
Evidence
Timestamp
Source
```

### Aggregate

```text
User
Skill/Capability
Jobs Seen
Jobs Missing
Jobs Partial
Mandatory Missing Count
Personas Affected
Role Families Affected
First Seen
Last Seen
Priority
Learning Status
Verified Status
```

The dashboard can answer:

- Which skills do I miss most often?
- Which missing skills are mandatory most often?
- Which personas are affected?
- Which role families are affected?
- Which gaps block the highest-value opportunities?
- Which skills should I work on first?
- Which gaps are already being closed?

Example:

```text
Skill             Jobs Missing   Mandatory   Priority
-------------------------------------------------------
Kubernetes        18             13          HIGH
Terraform         14              6          HIGH
Cloud Security    11              7          HIGH
Zero Trust         7              2          MEDIUM
```

The cumulative record must be database-backed and recalculable from observations.

---

# Stage 14 — Global Opportunity Intelligence

A job is not judged only on career fit.

The original vision defines a multi-dimensional opportunity view:

```text
Career Fit
+
Visa Fit
+
Location Fit
+
Salary Fit
+
Remote Fit
+
Relocation Fit
=
Global Opportunity
```

Example:

```text
Career Fit        94%
Capability Match  96%
Remote Fit         0%
Relocation Fit    95%
Visa Fit          82%
Salary Fit        88%

Global Opportunity Score 91%
```

---

# Stage 15 — Remote Intelligence

Remote must be classified by actual eligibility:

- worldwide
- India only
- US only
- EU/EEA
- APAC
- EMEA
- country restricted
- unknown

Also evaluate:

- timezone
- employment model
- work authorization
- contractor
- EOR
- sponsorship
- relocation

---

# Stage 16 — Global Mobility

Initial target countries:

1. Australia
2. New Zealand
3. UAE
4. Qatar
5. Saudi Arabia
6. Singapore
7. UK
8. Canada
9. Germany/EU

Migration data must be structured/versioned.

Every rule must have:

- country
- visa/pathway
- requirement
- value
- effective date
- expiry date when applicable
- official source
- last verified date

Immigration rules must not live only inside prompts.

---

# Stage 17 — Application Factory

The application pipeline is:

```text
Job
→ Persona
→ Evidence
→ Resume
→ ATS alignment
→ Truth validation
→ Cover Letter
→ Application Answers
→ Recruiter Message
→ Hiring Manager Message
→ Approval
→ Submission
→ CRM
```

The candidate can configure:

### Manual
AI searches/analyzes; user applies.

### Assisted
AI prepares/fills; user reviews/submits.

### Automatic
Only where explicitly authorized, technically permitted and compliant.

---

# Stage 18 — Intelligent Form Filling

Application questions such as:

- seniority
- years of experience
- visa status
- relocation
- certifications
- salary expectations

must be answered using verified Career Vault facts and preferences.

Never invent an answer.

---

# Stage 19 — Human Control

Important decisions remain user-controlled.

Automation must be configurable.

The system should support approval gates.

---

# Stage 20 — Recruiter and Hiring Manager Intelligence

Where permitted and available, record:

- recruiter
- hiring manager
- source
- role association
- outreach
- communication history

Do not fabricate identity or employer information.

---

# Stage 21 — Career CRM

Track:

```text
DISCOVERED
→ ANALYZED
→ SHORTLISTED
→ READY_FOR_REVIEW
→ APPROVED
→ APPLIED
→ RECRUITER_CONTACT
→ INTERVIEW
→ OFFER
→ ACCEPTED
```

Alternates:

- REJECTED
- WITHDRAWN
- ON_HOLD

Track:

- recruiters
- hiring managers
- interviews
- offers
- notes
- reminders
- resume versions
- application history

---

# Stage 22 — Interview Intelligence

The interview workspace includes:

- preparation
- company context
- role context
- technical
- architecture
- behavioral
- mock interview
- live assistant
- notes
- outcomes
- performance
- gaps
- next-round preparation

Answers remain evidence-backed.

---

# Stage 23 — Continuous Learning

CareerOS learns from:

- jobs applied to
- jobs ignored
- applications
- recruiter responses
- interviews
- offers
- rejection
- user corrections
- skill gaps
- persona performance
- source performance

The loop is:

```text
Career
→ Search
→ Match
→ Application
→ Outcome
→ Learning
→ Career improvement
```

---

# Stage 24 — AI Agent Architecture

The original idea describes cooperating agents such as:

- Profile Intelligence Agent
- Job Discovery Agent
- Email Intelligence Agent
- Job Extraction Agent
- Company Intelligence Agent
- JD Analysis Agent
- Matching Agent
- Ranking Agent
- Application Agent
- Form Intelligence Agent
- Notification Agent
- Career Analytics Agent

The implementation should keep AI provider-neutral.

---

# Stage 25 — User Identity / Modern Authentication

The original preferred login design contains:

### OAuth/social

- Google
- LinkedIn
- Apple
- Facebook

### Direct

- Email + Password

### Phone

- Phone OTP

### WhatsApp

- WhatsApp OTP / verification

The original design explicitly states WhatsApp should be a **verification/contact/notification channel**, not the only authentication mechanism.

Later notification preferences can include:

- job match alerts
- interview reminders
- application updates
- recruiter responses
- high-value opportunity alerts

---

# Stage 26 — Modern Onboarding

The original idea proposes:

### Step 1 — Identity
- name
- email
- phone
- country
- city

### Step 2 — Career
- current role
- years of experience
- domains
- skills
- technologies
- industries
- leadership level

### Step 3 — Opportunity Preferences
- target roles
- target countries
- preferred locations
- remote preference
- salary
- relocation
- sponsorship

### Step 4 — Career Goals
- better job
- senior role
- leadership
- international opportunity
- remote
- relocation
- career transition

### Step 5 — Career Passport
- resume
- LinkedIn profile
- certifications
- projects
- achievements

---

# Stage 27 — Progressive UI

The architecture should be visible in the UI.

### v0.1

Show as current:

- Personal Job & Interview Copilot
- Login
- Onboarding
- Career Passport
- Career Vault
- Personas
- Resume Studio
- Job discovery
- Applications
- Company Intelligence
- Interview Prep
- Live Interview
- Analytics
- Settings

### v0.2

Visible as planned/progressively implemented:

- Global Job Intelligence
- Capability Discovery
- Semantic Discovery
- Job DNA
- Career Capability Graph
- Global Job Sources
- Remote Intelligence
- Time-zone compatibility
- Relocation intelligence
- Salary intelligence
- Visa/sponsorship matching
- international opportunities

### v0.3

Visible as planned:

- Relocation
- Migration
- UK
- Canada
- Europe
- Australia
- New Zealand

Do not fake future functionality. Show a clearly marked roadmap/coming version surface instead.

---

# Stage 28 — Long-Term North Star

CareerOS becomes a system that continuously understands professional identity and connects it to the best realistic opportunities worldwide while keeping the user in control of important decisions and submissions.

---

# Final original vision

```text
UPLOAD CV
→ UNDERSTAND CANDIDATE
→ CAREER PASSPORT
→ PERSONAS
→ GLOBAL JOB DISCOVERY
→ EMAIL INTELLIGENCE
→ COMPANY VACANCY
→ JOB DNA
→ CAPABILITY MATCH
→ 60%+ SKILL HIGHLIGHT
→ SKILL GAP INTELLIGENCE
→ GLOBAL OPPORTUNITY SCORE
→ APPLICATION
→ TRUTH
→ APPROVAL
→ CRM
→ INTERVIEW
→ OUTCOME
→ LEARNING
→ BETTER CAREER PROFILE
```
