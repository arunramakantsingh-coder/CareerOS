# CareerOS v0.1 Reconciliated Integration Candidate

This package is a controlled merge of the uploaded MASTER and FIXED repositories.

## Baselines
- MASTER: current infrastructure/control-plane baseline
- FIXED: DeepSeek/v0.1 implementation baseline
- Product authority: four CareerOS development/product documents

## Preserved v0.1 foundation
- Authentication/JWT/security
- Tenant/User foundation
- Migrations 011 and 012
- v0.1 product models/API
- CareerOS application shell and v0.1 GUI pages
- API client with auth and v0.1 endpoints

## Reconciled files
- backend/app/main.py: merged MASTER structure + FIXED auth/v0.1 routers
- backend/app/core/config.py: MASTER settings + FIXED auth/JWT settings
- backend/app/models/user.py: MASTER user model + password_hash
- backend/app/models/__init__.py: MASTER model exports + v0.1 models
- backend/requirements.txt: preserved FIXED auth dependencies
- docker-compose.yml: FIXED container-safe / clean Next.js runtime
- frontend: FIXED v0.1 product UI/API client baseline

## Not verified yet
This is an integration candidate, not a VERIFIED release. Next step is UI-only runtime validation.
