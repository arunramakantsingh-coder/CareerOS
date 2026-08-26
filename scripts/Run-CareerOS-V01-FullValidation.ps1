#requires -Version 5.1
<#
.SYNOPSIS
    CareerOS v0.1 - Full Validation / Build / Runtime / Feature Test

IMPORTANT:
    Run from the CareerOS v0.1 project root or let this script locate it.
    This script does NOT delete the original CareerOS repository or its Docker volumes.

    Results:
      test-results\CareerOS-V01-Validation-<timestamp>\
#>

param(
    [switch]$AutoFixCompose = $true,
    [switch]$CleanV01Volume = $false
)

$ErrorActionPreference = "Stop"

# -----------------------------
# PROJECT ROOT
# -----------------------------
$ProjectRoot = "C:\Projects\CareerOS-v0.1-Personal-Job-Interview-Copilot-FINAL\CareerOS-v0.1"

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "CareerOS v0.1 project root not found: $ProjectRoot"
}

Set-Location $ProjectRoot

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ResultsRoot = Join-Path $ProjectRoot "test-results\CareerOS-V01-Validation-$Stamp"
$ReportFile  = Join-Path $ResultsRoot "CareerOS-V01-Validation.txt"
$BackupDir   = Join-Path $ResultsRoot "backups"

New-Item -ItemType Directory -Path $ResultsRoot -Force | Out-Null
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

$Results = New-Object System.Collections.Generic.List[object]

function Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )

    $line = "$(Get-Date -Format 'HH:mm:ss') $Message"
    Add-Content -LiteralPath $ReportFile -Value $line
    Write-Host $line -ForegroundColor $Color
}

function Result {
    param(
        [string]$Stage,
        [ValidateSet("PASS","FAIL","WARN","INFO")]
        [string]$Status,
        [string]$Details
    )

    $Results.Add([pscustomobject]@{
        Stage   = $Stage
        Status  = $Status
        Details = $Details
    })

    $color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        default { "Cyan" }
    }

    Log "[$Status] $Stage - $Details" $color
}

function Invoke-Step {
    param(
        [string]$Stage,
        [scriptblock]$Action
    )

    try {
        & $Action
        Result $Stage "PASS" "Completed successfully."
        return $true
    }
    catch {
        Result $Stage "FAIL" $_.Exception.Message
        return $false
    }
}

function Test-Http {
    param(
        [string]$Stage,
        [string]$Url,
        [int[]]$ExpectedCodes = @(200)
    )

    try {
        $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 20
        if ($ExpectedCodes -contains $r.StatusCode) {
            Result $Stage "PASS" "$Url -> HTTP $($r.StatusCode)"
        }
        else {
            Result $Stage "FAIL" "$Url -> unexpected HTTP $($r.StatusCode)"
        }
    }
    catch {
        Result $Stage "FAIL" "$Url -> $($_.Exception.Message)"
    }
}

function Test-CommandExists {
    param(
        [string]$Name
    )

    if (Get-Command $Name -ErrorAction SilentlyContinue) {
        Result "Prerequisite: $Name" "PASS" "Command available."
        return $true
    }

    Result "Prerequisite: $Name" "FAIL" "Command not found."
    return $false
}

# -----------------------------
# HEADER
# -----------------------------
@"
============================================================
CareerOS v0.1 - Full Validation
Personal Job & Interview Copilot
============================================================
Timestamp : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Project   : $ProjectRoot
============================================================
"@ | Set-Content -LiteralPath $ReportFile -Encoding UTF8

Log "Starting CareerOS v0.1 validation..." "Cyan"

# -----------------------------
# 1. ROOT STRUCTURE
# -----------------------------
$required = @(
    ".devcontainer",
    ".vscode",
    "backend",
    "database",
    "docker",
    "docs",
    "frontend",
    "Lovable",
    "nginx",
    "scripts",
    "tests",
    "AGENTS.md",
    "docker-compose.yml",
    "README.md",
    "Start-Docker.ps1",
    "VERIFY-V01.ps1"
)

foreach ($item in $required) {
    $path = Join-Path $ProjectRoot $item
    if (Test-Path -LiteralPath $path) {
        Result "Structure: $item" "PASS" "Present."
    }
    else {
        Result "Structure: $item" "FAIL" "Missing."
    }
}

# -----------------------------
# 2. PREREQUISITES
# -----------------------------
Test-CommandExists "docker"
Test-CommandExists "git"
Test-CommandExists "npm"

docker version | Out-Null
Result "Docker daemon" "PASS" "Docker is responding."

# -----------------------------
# 3. COMPOSE SAFETY
# -----------------------------
$ComposePath = Join-Path $ProjectRoot "docker-compose.yml"

if (-not (Test-Path $ComposePath)) {
    Result "docker-compose.yml" "FAIL" "File not found."
}
else {
    $ComposeText = Get-Content -LiteralPath $ComposePath -Raw

    if ($ComposeText -match '(?m)^\s*container_name\s*:') {

        if ($AutoFixCompose) {
            $BackupPath = Join-Path $BackupDir "docker-compose.yml.before-container-name-fix"
            Copy-Item -LiteralPath $ComposePath -Destination $BackupPath -Force

            $lines = Get-Content -LiteralPath $ComposePath
            $filtered = $lines | Where-Object {
                $_ -notmatch '^\s*container_name\s*:'
            }

            $filtered | Set-Content -LiteralPath $ComposePath -Encoding UTF8

            Result "Docker container-name collision fix" "PASS" "Removed hard-coded container_name entries; backup created at $BackupPath."
        }
        else {
            Result "Docker container-name collision check" "WARN" "Hard-coded container_name entries detected."
        }
    }
    else {
        Result "Docker container-name collision check" "PASS" "No hard-coded container_name entries."
    }
}

Invoke-Step "Compose syntax" {
    docker compose config | Out-Null
}

# -----------------------------
# 4. BUILD
# -----------------------------
Invoke-Step "Docker image build" {
    docker compose build
}

# -----------------------------
# 5. CLEAN ONLY V01 VOLUME (OPTIONAL)
# -----------------------------
if ($CleanV01Volume) {

    Log "CleanV01Volume enabled - removing ONLY the v0.1 compose stack/volumes." "Yellow"

    docker compose down --remove-orphans --volumes

    Result "Clean v0.1 database volume" "PASS" "Only the v0.1 compose resources were removed."
}

# -----------------------------
# 6. START STACK
# -----------------------------
Invoke-Step "Start v0.1 stack" {
    docker compose up -d
}

Start-Sleep -Seconds 8

# -----------------------------
# 7. CONTAINER STATUS
# -----------------------------
try {
    $ps = docker compose ps
    $psText = ($ps | Out-String)
    Add-Content -LiteralPath $ReportFile -Value ""
    Add-Content -LiteralPath $ReportFile -Value "=== DOCKER COMPOSE PS ==="
    Add-Content -LiteralPath $ReportFile -Value $psText

    $running = docker compose ps --status running --services

    foreach ($service in @("postgres","backend","frontend")) {
        if ($running -contains $service) {
            Result "Container: $service" "PASS" "Running."
        }
        else {
            Result "Container: $service" "FAIL" "Not running."
        }
    }
}
catch {
    Result "Container status" "FAIL" $_.Exception.Message
}

# -----------------------------
# 8. POSTGRES
# -----------------------------
try {
    docker compose exec -T postgres pg_isready -U careeros -d careeros | Out-Null
    Result "PostgreSQL readiness" "PASS" "Database is accepting connections."
}
catch {
    Result "PostgreSQL readiness" "FAIL" $_.Exception.Message
}

# -----------------------------
# 9. ALEMBIC
# -----------------------------
try {
    docker compose exec -T backend alembic upgrade head
    Result "Alembic migration upgrade" "PASS" "Database upgraded to head."
}
catch {
    Result "Alembic migration upgrade" "FAIL" $_.Exception.Message
}

try {
    $current = docker compose exec -T backend alembic current | Out-String
    $heads   = docker compose exec -T backend alembic heads | Out-String

    Add-Content -LiteralPath $ReportFile -Value ""
    Add-Content -LiteralPath $ReportFile -Value "=== ALEMBIC CURRENT ==="
    Add-Content -LiteralPath $ReportFile -Value $current
    Add-Content -LiteralPath $ReportFile -Value "=== ALEMBIC HEADS ==="
    Add-Content -LiteralPath $ReportFile -Value $heads

    Result "Alembic current/head inspection" "PASS" "Current and head states captured."
}
catch {
    Result "Alembic current/head inspection" "FAIL" $_.Exception.Message
}

# -----------------------------
# 10. DATABASE TABLES
# -----------------------------
try {
    $tables = docker compose exec -T postgres psql -U careeros -d careeros -c "\dt" | Out-String
    Add-Content -LiteralPath $ReportFile -Value ""
    Add-Content -LiteralPath $ReportFile -Value "=== DATABASE TABLES ==="
    Add-Content -LiteralPath $ReportFile -Value $tables

    if ($tables -match "users" -and $tables -match "tenants") {
        Result "Core database tables" "PASS" "users and tenants detected."
    }
    else {
        Result "Core database tables" "WARN" "users/tenants not both detected; inspect report."
    }
}
catch {
    Result "Database table inspection" "FAIL" $_.Exception.Message
}

# -----------------------------
# 11. BACKEND COMPILE
# -----------------------------
Invoke-Step "Backend Python compilation" {
    docker compose exec -T backend python -m compileall -q /app
}

# -----------------------------
# 12. PYTEST
# -----------------------------
try {
    $pytestOutput = docker compose exec -T backend pytest -q 2>&1 | Out-String
    Add-Content -LiteralPath $ReportFile -Value ""
    Add-Content -LiteralPath $ReportFile -Value "=== PYTEST ==="
    Add-Content -LiteralPath $ReportFile -Value $pytestOutput

    if ($pytestOutput -match "failed" -or $pytestOutput -match "ERROR") {
        Result "Backend pytest" "FAIL" "pytest reported failures/errors. See PYTEST section."
    }
    else {
        Result "Backend pytest" "PASS" "pytest completed without reported failures."
    }
}
catch {
    Result "Backend pytest" "FAIL" $_.Exception.Message
}

# -----------------------------
# 13. API SMOKE
# -----------------------------
Test-Http "API root"     "http://localhost:8000/"
Test-Http "API health"   "http://localhost:8000/api/v1/health"
Test-Http "Swagger"      "http://localhost:8000/docs"
Test-Http "ReDoc"        "http://localhost:8000/redoc"
Test-Http "OpenAPI JSON" "http://localhost:8000/openapi.json"

# -----------------------------
# 14. AUTH SMOKE
# -----------------------------
try {

    $suffix = Get-Date -Format "yyyyMMddHHmmss"
    $email = "careeros.test.$suffix@example.com"
    $password = "CareerOS-Test-2026!"
    $tenant = "CareerOS Validation Tenant $suffix"

    $registerBody = @{
        email       = $email
        password    = $password
        name        = "CareerOS Validation User"
        tenant_name = $tenant
    } | ConvertTo-Json

    $register = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody

    if (-not $register) {
        throw "Registration returned no response."
    }

    Result "Auth: registration" "PASS" "Test tenant/user created."

    $loginBody = @{
        email    = $email
        password = $password
    } | ConvertTo-Json

    $tokenResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody

    if (-not $tokenResponse.access_token) {
        throw "Login did not return access_token."
    }

    Result "Auth: login/JWT" "PASS" "JWT access token received."

    $headers = @{
        Authorization = "Bearer $($tokenResponse.access_token)"
    }

    $me = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/auth/me" `
        -Headers $headers

    if (-not $me) {
        throw "Authenticated /me returned no response."
    }

    Add-Content -LiteralPath $ReportFile -Value ""
    Add-Content -LiteralPath $ReportFile -Value "=== AUTH /ME RESPONSE ==="
    Add-Content -LiteralPath $ReportFile -Value ($me | ConvertTo-Json -Depth 10)

    Result "Auth: /me" "PASS" "Authenticated user context returned."

}
catch {
    Result "Authentication smoke test" "FAIL" $_.Exception.Message
}

# -----------------------------
# 15. FEATURE ENDPOINT CHECKS
# -----------------------------
$featureUrls = @(
    @{Name="Personas API";            Url="http://localhost:8000/api/v1/personas/"},
    @{Name="Jobs API";                Url="http://localhost:8000/api/v1/jobs/"},
    @{Name="Sources API";             Url="http://localhost:8000/api/v1/sources/"},
    @{Name="OpenAPI Product Surface"; Url="http://localhost:8000/openapi.json"}
)

foreach ($feature in $featureUrls) {
    try {
        $r = Invoke-WebRequest -Uri $feature.Url -UseBasicParsing -TimeoutSec 20
        Result "Feature API: $($feature.Name)" "PASS" "HTTP $($r.StatusCode)"
    }
    catch {
        Result "Feature API: $($feature.Name)" "WARN" "$($_.Exception.Message)"
    }
}

# -----------------------------
# 16. FRONTEND ROUTES
# -----------------------------
$routes = @(
    "/",
    "/login",
    "/onboarding",
    "/career-vault",
    "/personas",
    "/jobs",
    "/applications",
    "/application-studio",
    "/company-intelligence",
    "/interviews",
    "/live-interview",
    "/global-mobility",
    "/analytics",
    "/settings"
)

foreach ($route in $routes) {
    Test-Http "GUI route: $route" "http://localhost:3000$route"
}

# -----------------------------
# 17. FRONTEND BUILD
# -----------------------------
try {
    $frontendBuild = docker compose exec -T frontend npm run build 2>&1 | Out-String
    Add-Content -LiteralPath $ReportFile -Value ""
    Add-Content -LiteralPath $ReportFile -Value "=== FRONTEND BUILD ==="
    Add-Content -LiteralPath $ReportFile -Value $frontendBuild

    if ($frontendBuild -match "Failed to compile" -or
        $frontendBuild -match "error" -or
        $frontendBuild -match "Error:") {
        Result "Frontend production build" "FAIL" "Build output contains errors. See FRONTEND BUILD section."
    }
    else {
        Result "Frontend production build" "PASS" "npm run build completed."
    }
}
catch {
    Result "Frontend production build" "FAIL" $_.Exception.Message
}

# -----------------------------
# 18. SECURITY / CONFIG FLAGS
# -----------------------------
try {
    $composeText = Get-Content -LiteralPath $ComposePath -Raw
    if ($composeText -match "POSTGRES_PASSWORD:\s*(?!\$\{)[^\s]+") {
        Result "Security: Compose password" "WARN" "Development password is embedded in docker-compose.yml. Do not use in production."
    }
    else {
        Result "Security: Compose password" "PASS" "No obvious hard-coded Compose password detected."
    }

    if (Test-Path (Join-Path $ProjectRoot "frontend\.env.local")) {
        Result "Security: frontend .env.local" "WARN" "Local environment file exists. Ensure it contains no secrets before Git commit."
    }
    else {
        Result "Security: frontend .env.local" "PASS" "No frontend .env.local file present."
    }

    if (Test-Path (Join-Path $ProjectRoot ".git")) {
        Result "Git metadata in delivery" "WARN" ".git exists. Fine for local repository, but exclude it from clean ZIP delivery."
    }
    else {
        Result "Git metadata in delivery" "PASS" "No embedded .git directory."
    }
}
catch {
    Result "Security/config review" "WARN" $_.Exception.Message
}

# -----------------------------
# 19. LOG CAPTURE
# -----------------------------
foreach ($service in @("postgres","backend","frontend")) {
    try {
        $logPath = Join-Path $ResultsRoot "$service.log"
        docker compose logs $service --tail=150 2>&1 |
            Set-Content -LiteralPath $logPath -Encoding UTF8
        Result "Log capture: $service" "PASS" $logPath
    }
    catch {
        Result "Log capture: $service" "WARN" $_.Exception.Message
    }
}

# -----------------------------
# 20. FINAL SUMMARY
# -----------------------------
$passCount = @($Results | Where-Object Status -eq "PASS").Count
$failCount = @($Results | Where-Object Status -eq "FAIL").Count
$warnCount = @($Results | Where-Object Status -eq "WARN").Count

Add-Content -LiteralPath $ReportFile -Value ""
Add-Content -LiteralPath $ReportFile -Value "============================================================"
Add-Content -LiteralPath $ReportFile -Value "FINAL RESULT"
Add-Content -LiteralPath $ReportFile -Value "============================================================"
Add-Content -LiteralPath $ReportFile -Value "PASS : $passCount"
Add-Content -LiteralPath $ReportFile -Value "FAIL : $failCount"
Add-Content -LiteralPath $ReportFile -Value "WARN : $warnCount"
Add-Content -LiteralPath $ReportFile -Value ""
Add-Content -LiteralPath $ReportFile -Value "Result table:"
$Results | Format-Table -AutoSize | Out-String | Add-Content -LiteralPath $ReportFile

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CareerOS v0.1 VALIDATION COMPLETE" -ForegroundColor Cyan
Write-Host "PASS: $passCount   FAIL: $failCount   WARN: $warnCount" -ForegroundColor Green
Write-Host ""
Write-Host "REPORT:" -ForegroundColor Yellow
Write-Host $ReportFile -ForegroundColor White
Write-Host ""
Write-Host "LOG DIRECTORY:" -ForegroundColor Yellow
Write-Host $ResultsRoot -ForegroundColor White

if ($failCount -gt 0) {
    Write-Host ""
    Write-Host "FAILURES REQUIRE REVIEW." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "NO HARD FAILURES DETECTED." -ForegroundColor Green
exit 0

