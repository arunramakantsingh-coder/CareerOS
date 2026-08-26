# CareerOS One-Script Local Execution Rule

## Rule
All local CareerOS development, build, repair, verification and milestone testing should be driven from the project root through PowerShell scripts whenever practical.

The human operator should not be required to repeatedly navigate directories or manually reproduce long command sequences.

## Standard loop

1. Start from the CareerOS project root.
2. Run one orchestrating PowerShell script.
3. The script should:
   - verify the project structure;
   - validate Docker/Compose;
   - apply safe, narrowly-scoped automatic fixes when they are deterministic;
   - build/rebuild the application;
   - start the services;
   - run database migrations;
   - run backend tests and compilation checks;
   - run API and frontend smoke tests;
   - perform requested deeper tests;
   - capture logs and failures;
   - write a timestamped report.
4. Failures must be explicitly highlighted and must not be reported as passing.
5. Automatic fixes must be reversible and backed up before modification.
6. Secrets, credentials and local private configuration must never be added to the report or committed.
7. ChatGPT reviews the generated report and decides whether the next code change is required.

## Human responsibilities

The human should normally only:

- run the root-level script;
- review obvious high-risk prompts;
- open the application when requested;
- provide the generated report/screenshots when requested;
- provide final approval for milestone acceptance and Git operations.

## Important

A test script is an execution tool, not proof of success. A milestone is only considered verified after the actual tests/builds and end-to-end evidence pass.
