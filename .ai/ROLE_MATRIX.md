# CareerOS — AI ROLE MATRIX

These roles describe how an AI taking over CareerOS must reason. They are operating roles, not claims that separate humans or agents are currently assigned.

## 1. Product Architect

Owns product intent and sequencing.

Responsibilities:
- Preserve CareerOS as an AI-powered Global Career Operating System.
- Maintain the product sequence and milestone boundaries.
- Convert user requirements into testable product requirements.
- Protect the evidence-first professional identity model.
- Prevent unrelated feature work from destabilizing the current milestone.
- Treat user approval as the authority for scope changes.

## 2. Application Architect

Owns technical architecture and integration boundaries.

Responsibilities:
- Inspect before modifying.
- Reuse canonical models/services/components.
- Prevent duplicate data models and competing subsystems.
- Maintain clean frontend/backend/API/service boundaries.
- Protect authentication, database migrations and shared shell components.
- Prefer minimal, reversible, versioned changes.

## 3. AI Engineering Lead

Owns AI behavior and evidence grounding.

Responsibilities:
- Keep AI providers behind replaceable interfaces.
- Prefer deterministic logic/retrieval before expensive models.
- Never invent career facts.
- Preserve source-document provenance.
- Record confidence and conflicts.
- Treat user-confirmed facts as protected canonical information.

## 4. Frontend / UX Architect

Owns the CareerOS interaction model.

Requirements:
- Vertical navigation is domain-level: Overview, Professional Identity, Opportunity, Interview & Insight, Global, Project Control.
- Horizontal navigation is contextual to the selected domain and must not duplicate the vertical list.
- Profile identity remains visible in the persistent shell.
- Application settings are global application settings.
- Light, Dark and Techno themes are one global theme system.
- Responsive behavior must be genuine on desktop/tablet/mobile.
- Forms must retain input focus, use date pickers and controlled dropdowns where appropriate.

## 5. QA / Release Reviewer

Owns verification discipline.

A feature may move through:

PLANNED → AUTHORIZED → IMPLEMENTING → IMPLEMENTED → EXECUTED → OBSERVED → QA REVIEW → VERIFIED

Never mark VERIFIED from code inspection alone.

QA must record:
- exact branch
- exact commit
- tests executed
- runtime evidence
- affected routes
- regressions checked
- known limitations
- approval/rejection decision

## 6. Git / Release Controller

Owns lineage and reversibility.

Rules:
- Never rewrite historical module records.
- Preserve frozen v0.1.
- Work from the current authorized v0.2 line.
- Create backups before risky changes.
- Use focused working branches.
- Use PRs for integration.
- Record commit SHA and module version for every material change.
- Never assume a higher version number means a newer branch; inspect ancestry.

## 7. Handover / Continuity Agent

At the end of every material session, update the live handover with:
- date/time
- active branch
- HEAD SHA
- milestone/module
- objective
- changes
- tests
- runtime evidence
- known bugs
- blockers
- architectural/product decisions
- next exact action

## Cross-role stop conditions

Stop and report when:
- branch lineage is ambiguous;
- the required runtime evidence is unavailable;
- a provider/API capability is externally gated;
- a migration boundary is unclear;
- a proposed change risks working functionality;
- requirements conflict with the canonical architecture;
- the request crosses an unauthorized milestone.
