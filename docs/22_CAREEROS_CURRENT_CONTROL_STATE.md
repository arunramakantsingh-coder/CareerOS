# CareerOS — Current Control State

## Roles
Human / Product Owner / Runtime & Evidence Acceptance: Arun
Lead AI / Architecture / QA / Verification Gate: capable authorized AI
Coding AI / Implementation Engineer: capable authorized AI with repository write access

CareerOS is **AI-provider neutral**. No particular AI vendor, model, coding assistant, or provider is required. The Lead AI may also serve as the Coding AI when authorized and technically able to implement directly. If the normal Coding AI becomes unavailable, another capable authorized AI may take over without restarting or redesigning the project.

## Current State
The roadmap is being reconciled before additional feature development.

**Coding AI: WAIT for explicit milestone authorization.**

## Migration Clarification
`/api/v1/migration/countries` belongs to Global Mobility/Migration functionality. Global Mobility is later than the core job-hunting loop and must not become the primary development driver while Career Vault, personas, global discovery, email intelligence, matching, skill gaps, applications and interview assistance remain incomplete.

## Immediate Sequence
1. Foundation stability
2. Authentication
3. Career Vault/CV
4. Personas
5. Global Job Discovery
6. Email Intelligence
7. Company/Recruiter Intelligence
8. Job Intelligence
9. Matching
10. 60% Highlight + Skill Gap
11. Application Factory
12. Application CRM
13. Remote Intelligence
14. Live Interview Assistant
15. Analytics/Learning
16. Global Mobility
17. Advanced automation/SaaS

## Runtime
Every milestone must leave a locally usable system. Minimum checks:
- http://localhost:3000
- http://localhost:8000/api/v1/health
- feature-specific UI/API tests

## Freeze
Do not move to the next milestone until the Lead AI issues explicit authorization.
