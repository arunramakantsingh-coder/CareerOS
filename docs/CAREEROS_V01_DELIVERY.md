# CareerOS v0.1 Delivery Candidate

## Scope implemented in this workspace

The current workspace preserves the existing CareerOS FastAPI/Next.js/PostgreSQL/Alembic foundation and layers a v0.1 product workflow on top of it.

Implemented/extended:

- JWT authentication and tenant-bound identity
- Career Vault profile/evidence APIs
- Existing personas, jobs, JD/Job DNA, matching, resume and remote/mobility foundations retained
- Application Factory and CRM persistence
- Truth & Compliance review endpoint
- Company Intelligence persistence
- Interview preparation persistence
- Live Interview Assistant persistence and evidence-backed guidance
- Analytics summary
- Responsive CareerOS GUI with Lovable-inspired visual language
- Login/onboarding/application studio/company intelligence/live interview/job detail screens
- Migration 012 for v0.1 product workflow tables
- Local verification script

## Verification discipline

This is a **delivery candidate, not VERIFIED**. The repository must be tested against a clean PostgreSQL database and an existing database, backend tests must pass, the frontend production build must succeed, tenant isolation must be exercised, and the critical v0.1 journey must be tested before the project is called verified.

## Design rule

Lovable remains a visual/reference source. The production GUI is implemented in the existing Next.js/TypeScript/Tailwind architecture. No fake demo data should be used as evidence of backend completion.

## AI/local-first rule

The v0.1 workflow is designed to operate without a paid external AI API for the baseline journey. Deterministic extraction/guidance is used where appropriate; a provider abstraction can be connected to Ollama or another model provider later without redesigning the product data model.
