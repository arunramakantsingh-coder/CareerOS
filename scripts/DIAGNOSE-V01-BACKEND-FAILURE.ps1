$ErrorActionPreference = "Continue"

$Root = (Get-Location).Path
$ReportDir = Join-Path $Root ("test-results\BACKEND-DIAGNOSTIC-" + (Get-Date -Format "yyyyMMdd-HHmmss"))

New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null

function Section {
    param([string]$Title)

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Save-Command {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    $File = Join-Path $ReportDir "$Name.txt"

    try {
        & $Command 2>&1 | Tee-Object -FilePath $File
    }
    catch {
        $_ | Out-String | Tee-Object -FilePath $File
    }
}

Section "CareerOS v0.1 BACKEND FAILURE DIAGNOSTIC"

Write-Host "Project:"
Write-Host $Root -ForegroundColor Yellow

Write-Host ""
Write-Host "Report:"
Write-Host $ReportDir -ForegroundColor Yellow

Section "1. COMPOSE SERVICE STATUS"

Save-Command "01-compose-ps" {
    docker compose -p careeros-v01 ps -a
}

Section "2. BACKEND CONTAINER STATUS"

Save-Command "02-backend-ps" {
    docker compose -p careeros-v01 ps -a backend
}

Section "3. POSTGRES STATUS"

Save-Command "03-postgres-ps" {
    docker compose -p careeros-v01 ps -a postgres
}

Section "4. FRONTEND STATUS"

Save-Command "04-frontend-ps" {
    docker compose -p careeros-v01 ps -a frontend
}

Section "5. BACKEND LOGS - LAST 300 LINES"

Save-Command "05-backend-logs" {
    docker compose -p careeros-v01 logs backend --tail=300
}

Section "6. POSTGRES LOGS - LAST 150 LINES"

Save-Command "06-postgres-logs" {
    docker compose -p careeros-v01 logs postgres --tail=150
}

Section "7. FRONTEND LOGS - LAST 150 LINES"

Save-Command "07-frontend-logs" {
    docker compose -p careeros-v01 logs frontend --tail=150
}

Section "8. BACKEND IMAGE"

Save-Command "08-backend-image" {
    docker image inspect careeros-v01-backend
}

Section "9. COMPOSE CONFIGURATION"

Save-Command "09-compose-config" {
    docker compose -p careeros-v01 config
}

Section "10. BACKEND HEALTH ENDPOINT"

try {

    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/health" `
        -UseBasicParsing `
        -TimeoutSec 10 `
        -ErrorAction Stop

    Write-Host "Backend health: HTTP $($response.StatusCode)" -ForegroundColor Green

}
catch {

    Write-Host "Backend health request FAILED." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Section "11. DOCKER EVENTS / EXIT STATUS"

Save-Command "11-backend-inspect" {
    docker inspect careeros-v01-backend-1
}

Section "12. SEARCH LOGS FOR COMMON FAILURE TYPES"

$BackendLogFile = Join-Path $ReportDir "05-backend-logs.txt"

if (Test-Path $BackendLogFile) {

    $log = Get-Content $BackendLogFile -Raw

    $patterns = @(
        "Traceback",
        "Exception",
        "Error",
        "ImportError",
        "ModuleNotFoundError",
        "SyntaxError",
        "sqlalchemy",
        "alembic",
        "database",
        "connection refused",
        "password authentication failed",
        "relation .* does not exist",
        "column .* does not exist",
        "psycopg",
        "pydantic",
        "settings",
        "JWT",
        "passlib",
        "bcrypt"
    )

    foreach ($pattern in $patterns) {

        $matches = Select-String `
            -InputObject $log `
            -Pattern $pattern `
            -AllMatches `
            -CaseSensitive:$false

        if ($matches) {

            Write-Host ""
            Write-Host "MATCH: $pattern" -ForegroundColor Yellow

            $lines = $log -split "`r?`n" |
                Where-Object {
                    $_ -match $pattern
                } |
                Select-Object -First 10

            $lines | ForEach-Object {
                Write-Host $_ -ForegroundColor Red
            }
        }
    }
}

Section "13. FINAL DIAGNOSTIC LOCATION"

Write-Host ""
Write-Host "All diagnostic files:" -ForegroundColor Green
Write-Host $ReportDir -ForegroundColor Yellow

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " DIAGNOSTIC COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host ""
Write-Host "PowerShell terminal remains open." -ForegroundColor Green
Write-Host ""
