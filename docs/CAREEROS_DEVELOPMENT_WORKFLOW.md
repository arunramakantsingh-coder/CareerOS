# CareerOS — Development & AI Collaboration Workflow

## Purpose

This is the operating procedure for the human, ChatGPT, DeepSeek and GitHub.

## Roles

### Human
- defines priorities
- runs approved PowerShell scripts
- provides approvals
- performs credential/account actions
- decides milestone readiness

### ChatGPT
- product/technical architect
- task/specification author
- security/quality reviewer
- GitHub repository/diff reviewer
- documentation governance reviewer

### DeepSeek
- repository investigator
- coding engineer
- implementation planner
- test/fix engineer
- branch/PR worker

### GitHub
- canonical source
- branch/PR history
- reviewable record

## Standard Loop

```text
YOU
  ↓
CHATGPT
  ↓
Task specification
  ↓
DEEPSEEK
  ↓
Reads current GitHub + MD files
  ↓
Inspects existing implementation
  ↓
Creates PowerShell implementation script
  ↓
YOU run script from project root
  ↓
Tests / validation
  ↓
GitHub branch / PR
  ↓
CHATGPT reads actual repository + diff
  ↓
APPROVE / CHANGES REQUIRED
  ↓
DEEPSEEK fixes
  ↓
Tests
  ↓
PR review
  ↓
Human approval
  ↓
Merge
  ↓
Update project status
```

## GitHub Rule

When information exists in GitHub, use GitHub instead of stale chat snippets, old ZIPs or memory.

DeepSeek must read the current GitHub branch before coding.

ChatGPT must inspect the actual repository/diff at review.

## Milestone Trigger

The human may simply say:

> `Milestone X is complete; review the repository.`

The reviewer must inspect the relevant branch/PR/commit, affected files, tests, builds, dependencies, migrations, contracts and documentation.

## DeepSeek Mandatory Prompt Contract

Every coding prompt must require DeepSeek to:
1. read `AGENTS.md`
2. read `CAREEROS_VERSION_ARCHITECTURE.md`
3. read relevant Specification, Blueprint, Assessment, Roadmap, Workflow and Status sections
4. inspect current GitHub implementation
5. inspect the existing subsystem
6. preserve working functionality
7. avoid rebuild/parallel frameworks
8. protect tenant/security boundaries
9. preserve migration history
10. avoid unsupported/fabricated data
11. avoid unauthorized scraping/account automation
12. execute applicable tests
13. report exact files and actual test results
14. stop at the requested task

## PowerShell-First Rule

For source-code implementation, DeepSeek must provide a complete PowerShell script beginning at the project root:

```powershell
PS C:\Projects\CareerOS>
```

The script handles directories, files, complete file contents, dependencies, migrations, tests and validation.

The human should not manually `cd`, create individual files/folders or paste partial code into multiple files.

## Script Safety

Scripts should verify root, fail on unexpected errors, avoid destructive operations unless approved, show important operations, verify generated files, run targeted tests and report final Git status.

## Documentation Rule

After every material milestone:
- update `CAREEROS_PROJECT_STATUS.md`
- update roadmap if sequencing changes
- update assessment when implementation status changes
- update SPEC/BLUEPRINT/VERSION_ARCHITECTURE when intended product/architecture changes

## Branch Rule

Use dedicated implementation branches. Never merge directly into `main` without human review.

## Safe Upload Rule

Normal milestone: do not upload the whole project to ChatGPT. Use GitHub.

Upload local artifacts only when GitHub cannot contain the required information, such as logs, screenshots, sanitized local DB/schema evidence, private documents, design mockups or sanitized local configuration.

Never upload `.env`, passwords, API keys, tokens, private keys/certificates, `node_modules`, `.next`, `__pycache__`, `.git`, Git worktrees, caches or unnecessary build artifacts.

## Design References

Keep Lovable/exported visual material in `design-reference/`. It is reference material, not production source of truth.

## Stop Conditions

Stop for clarification when requirements conflict, destructive migration is proposed, credentials are requested, access conditions are unclear, or a major framework/security-boundary change is proposed.

## Definition of Done

Done means implementation exists, applicable tests/builds pass, repository state is understood, PR is reviewable, documentation is current and known critical regressions are resolved.
