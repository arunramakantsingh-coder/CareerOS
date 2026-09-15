# CareerOS Intelligence Engine Architecture

## Purpose

CareerOS Intelligence Engine is the reusable reasoning, retrieval, research and orchestration layer for the whole platform. It is not a CV-only parser and it is not a second system of record.

## Product relationship

```text
Professional Identity
  -> CV & Professional Document Vault
  -> Evidence Library
  -> Career Vault
  -> Personas
  -> Connections
  -> Opportunity
  -> Interview & Insight
  -> Global Intelligence
             ^
             |
      CareerOS Intelligence Engine
```

The intelligence layer reads validated CareerOS data and permitted external sources, reasons over retrieved evidence, and writes structured findings through validated application services.

## Conceptual deployment

```text
Frontend (Next.js)
        |
        v
Backend API (FastAPI)
        |
        +-------------------+
        |                   |
        v                   v
PostgreSQL / pgvector   Intelligence Engine
                            |
                            +-- local/provider-neutral model runtime
                            +-- retrieval
                            +-- tool registry
                            +-- document intelligence
                            +-- research/search orchestration
                            +-- validation
```

The development implementation begins with an isolated Intelligence Engine container. A concrete local model is selected only after the developer host hardware is checked.

## Core responsibilities

### Identity Intelligence
- CV/document understanding
- entity resolution
- chronology normalization
- structured employment, education, certification, skills and achievement extraction
- conflict detection
- evidence reconciliation
- profile completeness

### Search Intelligence
- global keyword and semantic search
- natural-language navigation
- search across Profile, Documents, Evidence, Career Vault and Connections
- evidence-backed result synthesis

### Opportunity Intelligence
- JD / Job DNA extraction
- persona/JD matching
- profile/JD matching
- explainable fit percentages
- missing factors / skill gaps
- strengths, risks and recommended actions

### Organization and Recruiter Intelligence
- organization research and relationship records
- registered-profile/application history
- recruiter identification from approved communications
- company/role/contact enrichment
- hiring signals and communication linkage

### Research Intelligence
- permitted web research
- external API use
- multi-source synthesis
- structured findings stored back into CareerOS

### Interview Intelligence
- preparation
- contextual evidence retrieval
- live interview assistance
- post-interview analysis
- learning/insight generation

## Controlled reasoning pattern

```text
Intent
  -> plan
  -> retrieve/search
  -> call approved tools
  -> normalize
  -> reason
  -> validate
  -> persist structured result
  -> present with provenance
```

The model must use tools for CareerOS data access. It must not invent career facts or execute arbitrary database mutations.

## Document intelligence flow

```text
Upload
  -> secure validation
  -> document storage
  -> layout/text extraction
  -> Markdown/JSON representation
  -> classification
  -> entity/fact extraction
  -> contextual validation
  -> confidence/trust state
  -> entity resolution / deduplication
  -> provenance/evidence links
  -> Career Vault candidate update
  -> review queue
  -> finalized Profile
```

The Professional Document Vault remains the evidence repository. Multiple CV versions contribute to one Career Vault rather than creating independent profiles.

## Trust model

Use:

`EXTRACTED | INFERRED | USER-CONFIRMED | CONFLICTING | MISSING`

High confidence may populate automatically with provenance. Medium confidence may populate as inferred and enter review. Low confidence should be suggested rather than silently populated. Conflicts must not overwrite verified facts.

## Search and findings

Use hybrid retrieval where useful:

`keyword/full-text + vector similarity + metadata filters + reranking`

Searchable chunks retain tenant/user, document, section/page, fact and trust metadata. User-facing findings should include evidence references and clearly distinguish source facts, extracted facts, AI inference and recommendations.

## Storage boundary

Normalized CareerOS relational models remain authoritative. Intelligence-specific structures are added only when needed and through new Alembic migrations. Avoid one unqueryable JSON blob for the whole intelligence system.

## Frontend visibility

Every future capability uses an explicit status:

- WORKING
- BETA
- COMING SOON
- PLANNED

This allows the frontend to act as both the product interface and an implementation-progress map without pretending unfinished functionality is available.

## Safety and regression gate

The intelligence layer must not break:

- registration
- login/session/logout
- Google authentication
- current Profile
- CV upload
- document persistence
- Evidence Library
- Career Vault
- Personas
- Settings
- database/migrations
- major existing routes

Never delete the PostgreSQL volume or perform destructive resets as a troubleshooting shortcut.
