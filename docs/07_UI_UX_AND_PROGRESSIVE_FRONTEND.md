# CareerOS — UI/UX & Progressive Frontend Contract

## Principle

The frontend must be developed **with** the application backend.

Not:

```text
Backend first → UI later
```

Use:

```text
Feature
→ Database
→ API
→ Domain logic
→ UI
→ Tests
→ Verify
```

---

# 1. Visual foundation

CareerOS should feel like:

- premium professional SaaS
- career intelligence platform
- executive workspace
- information-rich but readable
- responsive
- coherent
- explainable

Lovable is a visual/reference source only.

The production GUI must be native to Next.js/TypeScript/Tailwind and connected to real backend APIs.

---

# 2. Navigation

## CURRENT — v0.1

- Dashboard
- Career Passport
- Career Vault
- Personas
- Jobs
- Applications
- Resume Studio
- Company Intelligence
- Interviews
- Live Interview
- Analytics
- Settings

## NEXT — v0.2

- Global Job Intelligence
- Capability Discovery
- Semantic Discovery
- Job DNA
- Career Capability Graph
- Global Job Sources
- Remote Intelligence
- Time-zone compatibility
- Salary Intelligence
- Sponsorship matching

## FUTURE — v0.3

- Relocation Intelligence
- Migration Intelligence
- Australia
- New Zealand
- UK
- Canada
- Europe

Planned surfaces may be shown with a clear version label.

Never make roadmap UI look like a functional backend feature.

---

# 3. Dashboard

The dashboard should communicate the CareerOS concept.

### Career Passport

- current positioning
- experience
- capabilities
- career strength
- completeness
- evidence coverage

### Job Intelligence

- jobs discovered
- 60%+ skill matches
- high-fit opportunities
- missing-skill alerts

### Global Opportunity

- compatible countries
- remote-compatible opportunities
- relocation-ready opportunities
- mobility readiness

### Interview

- upcoming
- preparation status

### High-value opportunity

Show:

- advertised title
- company
- location
- career fit
- skill match
- location
- salary
- remote
- visa/relocation where applicable
- gaps
- recommendation

---

# 4. Login screen

The original project concept recommends five access paths:

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

Important: WhatsApp should be a verification/contact/notification channel, not the only authentication mechanism.

---

# 5. Onboarding

Progressive steps:

### 1 Identity
Name, email, phone, country, city.

### 2 Career
Role, experience, domains, skills, technologies, industries, leadership.

### 3 Opportunity preferences
Target roles, countries, locations, remote, salary, relocation, sponsorship.

### 4 Career goals
Better job, senior role, leadership, international, remote, relocation, transition.

### 5 Career Passport
Resume, LinkedIn, certifications, projects, achievements.

---

# 6. Career Passport

Sections:

- Identity
- Summary
- Experience
- Skills
- Technologies
- Architecture
- Leadership
- Governance
- Certifications
- Projects
- Achievements
- Evidence
- Personas
- Resume Versions

---

# 7. Jobs UI

Do not make job cards title-only.

The modern job card should expose:

```text
CAREER FIT
SKILL MATCH
EXPERIENCE FIT
REMOTE FIT
LOCATION FIT
SALARY FIT
MOBILITY/VISA FIT
```

Then:

- Why this matches
- Matched
- Partial
- Transferable
- Missing
- Hard failures
- recommended persona

---

# 8. Skill Gap UX

At the job level:

```text
Skill Match 64%

MATCHED
✓ Palo Alto
✓ Security Architecture

PARTIAL
△ Cloud Security

MISSING
△ Kubernetes
△ Terraform

[View cumulative Skill Gap]
```

At the cumulative level:

```text
TOP MARKET GAPS

Kubernetes       18 jobs
Terraform        14 jobs
Cloud Security   11 jobs
Zero Trust        7 jobs
```

---

# 9. Persona UI

Show:

- persona name
- positioning
- target roles
- capabilities
- industries
- countries
- salary
- work mode
- weights
- evidence coverage
- performance

---

# 10. Application Studio

Show the chain:

```text
Job
→ Selected Persona
→ Evidence
→ Resume
→ Truth Validation
→ Cover Letter
→ Answers
→ Approval
```

---

# 11. Interview UI

Include:

- preparation
- company
- role
- technical
- architecture
- behavioral
- mock
- live
- notes
- outcome
- next-round preparation

---

# 12. UI acceptance

A page is accepted only if:

- route works
- authentication works
- loading state works
- empty state works
- error state works
- validation works
- real API data renders
- mutations persist
- refresh preserves state
- build succeeds
- relevant E2E passes

---

# 13. Progressive UI rule

Every verified backend module must immediately gain/retain its corresponding functional UI.

Do not accumulate backend-only features that the user cannot see or use.
