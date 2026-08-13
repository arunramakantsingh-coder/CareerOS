# CareerOS — Product Blueprint

## Product Position
CareerOS is:
- a career intelligence platform
- a semantic job discovery engine
- a personalized application factory
- a career CRM
- a global mobility/migration intelligence platform
- an AI interview preparation system
- a long-term career decision engine

It is not primarily a job board, resume builder or blind auto-apply bot.

## Core Loop
1. Understand the user's career.
2. Model capabilities/evidence.
3. Discover jobs.
4. Convert each JD into Job DNA.
5. Match the job to career/persona.
6. Evaluate location, remote, salary and migration fit.
7. Generate application package.
8. Obtain human approval where required.
9. Track recruiter/interview/offer outcomes.
10. Learn from outcomes.

## Core Differentiator
Search and ranking must understand capabilities, responsibilities, technologies, architecture domains, leadership, governance, industry, seniority and transferable skills.

A role such as `Digital Resilience Transformation Lead` may be highly relevant to Network Architect, Security Architect or Cyber Security Architect personas when the JD contains enterprise networking, Palo Alto, Zero Trust, governance, cloud connectivity, resilience and leadership.

## Seven Major Engines
1. Career Intelligence Engine
2. Persona Engine
3. Job Intelligence Engine
4. Matching Engine
5. Application Factory
6. Global Mobility Engine
7. Career CRM & Outcome Engine

## Career Vault
Authoritative source of truth for identity/contact, education, employment, responsibilities, projects/achievements, skills/technologies, architecture domains, leadership, certifications, industry/domain, preferences and evidence.

## Personas
- Network Architect
- Security Architect
- Cyber Security Architect
- Infrastructure Architect
- Network Manager
- IT Manager
- Custom Persona

Personas alter positioning and weighting without duplicating the Career Vault.

## Career Ontology + Job DNA
Normalized ontology connects titles, skills, technologies, responsibilities, domains and capabilities.

## Job Sources
India: Naukri, foundit, LinkedIn, Indeed, employer pages.
Middle East: Naukrigulf, Bayt, GulfTalent, LinkedIn, Indeed, recruiter sites.
Australia: SEEK, Jora, Indeed, LinkedIn, employer pages.
New Zealand: SEEK NZ, Trade Me Jobs, Indeed, LinkedIn, employer pages.
Global Remote: FlexJobs, Remote OK, We Work Remotely, Remotive, Wellfound, employer pages.
Additional international: Glassdoor, Dice, ZipRecruiter, recruitment firms and employer sites.

Respect terms, robots rules, API conditions and automation restrictions. Prefer APIs, feeds, alerts, permitted integrations and public employer pages.

## Remote Intelligence
Support worldwide, India-only, US-only, EU/EEA, APAC/EMEA, country-specific, timezone, employment/contractor restrictions, EOR and remote eligibility.

## Global Mobility
Initial countries: Australia, New Zealand, UAE, Qatar, Saudi Arabia, Singapore, UK, Canada and Germany/EU. Use official, versioned immigration rules. Combine career fit, visa/migration fit, salary, sponsorship, location, remote and relocation into a Global Opportunity Score.

## Application Factory
Select best persona, retrieve relevant evidence, tailor resume, optimize ATS without keyword stuffing, generate useful cover letters/application answers/recruiter messages, run Truth & Compliance and require approval where necessary.

## Interview Intelligence
Technical, architecture, leadership/behavioral, company research, personalized answer frameworks, post-interview learning and round preparation.

## Career CRM
Track discovery, analysis, shortlist, approval, application, recruiter contact, interview, offer, rejection/withdrawal/hold, recruiter/hiring-manager records and application/resume history.

## Analytics & Learning
Track conversion by persona, source, country, salary band, common gaps, successful positioning, role/capability clusters and recommendations.

## SaaS
Indicative tiers:
- Free
- Pro
- Global
- Executive

Architecture should support subscriptions from the beginning while payment integration may be deferred.

## Technology Direction
Modern responsive web app, early Firebase/managed hosting where suitable, PostgreSQL target production DB, pgvector for semantic search, object storage, Cloud Run/FastAPI for production backend and hybrid AI architecture.

## Security
Strict tenant isolation, encryption, least privilege, MFA, audit logs, secrets management, PII minimization, user export/deletion, prompt-injection defenses, file scanning, rate limiting and explicit consent for model-training use.

## Roadmap
MVP-1: Career Vault, personas, job import, JD analysis, Job DNA, semantic matching, tailored resume and application tracker.
MVP-2: more connectors, company intelligence, recruiter intelligence, remote eligibility, interview AI and analytics.
V2: Australia/NZ/global migration, visa pathways, sponsorship, salary and relocation.
V3: subscriptions, advanced automation, career coaches/recruiter features, B2B and broader global coverage.
