# CareerOS — Current AI Handover State

**Snapshot date:** 2026-09-03  
**Source branch:** `working/m02-profile-builder-v1.3-20260902`  
**Source commit:** `a3dc54842961362b708b8849ac2e7ec79feab4f0`  
**Safety checkpoint:** `backup/pre-ai-handover-20260903` at the same commit

## 1. Current milestone

**M02 — Profile Builder / Professional Identity reconciliation**

Current focus is to complete and verify the profile-first foundation before moving to Opportunity / Global Job Discovery.

## 2. What the current profile branch contains

Compared with `release/v0.2-global-job-intelligence` at `1da1670`, the profile branch is 67 commits ahead. The comparison includes substantial work around:

- candidate/profile API
- document intake and extraction
- OAuth routes
- profile intelligence
- document model
- extraction/ingestion utilities
- Docker/config updates
- profile/login/onboarding/documents/settings UI
- unified CareerOS shell
- bulk document upload
- document scanner
- theme context
- API client/error handling
- project tracker
- bug tracker
- roadmap
- module/version registry
- profile intelligence UI

This confirms that the current profile line is materially newer than the v0.2 release baseline.

## 3. Critical branch reconciliation finding

The branch `working/live-interview-workspace-v0.2.2-20260902` is **not a linear continuation** of the current profile branch.

Git comparison at handover time:

```text
base: working/m02-profile-builder-v1.3-20260902 @ a3dc548
head: working/live-interview-workspace-v0.2.2-20260902 @ 29ec546
status: diverged
head ahead: 1 commit
head behind: 16 commits
merge base: 9bd4d80
```

The live-interview branch's only unique changed file in that comparison is:

`frontend/src/app/live-interview/page.tsx`

Therefore the live-interview feature must be **reconciled onto the current profile-first line** before it becomes the next integrated release. Do not simply switch the user's local checkout to the old live-interview branch.

## 4. Known documentation drift

`docs/PROJECT_TRACKER.md` on the current profile branch still names `working/m02-profile-repair-v1.2-20260902` as its current working branch. That is stale relative to the actual current branch `working/m02-profile-builder-v1.3-20260902`.

`docs/README.md` also contains older v0.1/v0.2 wording. The new AI takeover files are the current handover overlay; future agents must reconcile stale documentation against actual Git refs and runtime evidence instead of blindly trusting old status text.

## 5. Current known verification risks

### Authentication / OAuth

Backend OAuth routes exist in the current profile line, but provider-side credentials and callback registration are external prerequisites. No AI may mark Google/LinkedIn OAuth VERIFIED without an actual provider authorization flow and callback runtime test.

Google identity sign-in and Gmail mailbox authorization are separate permissions.

### Documents / CV / Vault

The implementation contains dedicated CV/document intake work, including batch upload and scanner components. The earlier runtime bug where FastAPI validation objects were rendered directly as React children was recorded as fixed, but the fix still requires local regression evidence.

### Profile

A manual profile builder is intended to cover personal information, resume, headline, summary, skills, employment, education, certifications, projects, accomplishments, career profile and performance/completeness. Evidence-derived values must remain editable and traceable.

### Navigation / UI

The shell is intended to have domain-level vertical navigation and contextual horizontal navigation. The horizontal bar must not repeat the vertical domain list.

### Forms

A previously observed defect caused text inputs to lose focus after one character. This must be explicitly regression-tested across representative controlled inputs before the profile milestone is considered stable.

## 6. Current verification state

Do not use `VERIFIED` for the profile milestone yet solely from repository inspection.

Correct state:

```text
IMPLEMENTATION PRESENT
RUNTIME / E2E ACCEPTANCE PENDING
```

## 7. Immediate next work

1. Keep the profile branch as the current working line.
2. Reconcile stale project-control documentation.
3. Complete local QA for Profile Builder + CV + Document Vault + Profile Intelligence.
4. Verify OAuth with real provider configuration when credentials are available.
5. Verify form focus/date-picker/dropdown behavior.
6. Record defects and retest results.
7. Only after profile/evidence foundation passes, reconcile Live Interview onto the current line.
8. Then move to Opportunity / Global Job Discovery.

## 8. Stop conditions for the next AI

Stop and report rather than improvising if:

- branch lineage is ambiguous;
- two documents disagree about current milestone;
- a database migration boundary changes;
- an external OAuth/API capability is unavailable;
- a proposed fix risks a previously working module;
- runtime evidence cannot be obtained;
- a request would cross into the next milestone without authorization.
