# CareerOS v0.1 scripts

Use **BUILD-AND-TEST-V01.ps1** as the single entry point.

From the project root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\BUILD-AND-TEST-V01.ps1
```

It uses the Docker Compose project name `careeros-v01`, so it does not operate on the separate master `CareerOS` Compose project.

It validates Compose, clears the v0.1 frontend `.next` cache, rebuilds the v0.1 frontend/backend, starts PostgreSQL/backend/frontend, checks backend health, checks the frontend, and verifies all required UI routes.

For log collection on a failure:

```powershell
.\scripts\BUILD-AND-TEST-V01.ps1 -ShowLogs
```
