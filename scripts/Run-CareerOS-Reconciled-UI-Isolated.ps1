#requires -Version 5.1
<#
CareerOS v0.1 - RECONCILED UI-ONLY ISOLATED TEST

Safety:
- NEVER touches C:\Projects\CareerOS
- Uses a separate Compose project name: careeros-reconciled-ui
- Uses isolated host ports:
    PostgreSQL 5433
    Backend     8100
    Frontend    3100
- Does not run migrations, pytest, backend feature tests, auth tests, or DB tests.
- Stops immediately if Compose/build/start fails.
- Verifies the actual reconciled containers are running BEFORE any HTTP test.
- Tests only the reconciled frontend UI.
#>

$ErrorActionPreference = "Stop"

$ProjectRoot = (Get-Location).Path

if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "docker-compose.yml"))) {
    throw "Run this script from the RECONCILED project root containing docker-compose.yml."
}

$ExpectedRoot = "C:\Projects\CareerOS-v0.1-RECONCILED"
if ((Split-Path -Leaf $ProjectRoot) -ne "CareerOS-v0.1" -or $ProjectRoot -notlike "$ExpectedRoot*") {
    Write-Host ""
    Write-Host "SAFETY STOP" -ForegroundColor Red
    Write-Host "This script is intended for:" -ForegroundColor Yellow
    Write-Host "$ExpectedRoot\CareerOS-v0.1" -ForegroundColor Cyan
    Write-Host "Current directory:" -ForegroundColor Yellow
    Write-Host $ProjectRoot -ForegroundColor Cyan
    exit 1
}

$ComposeBase = Join-Path $ProjectRoot "docker-compose.yml"
$OverridePath = Join-Path $ProjectRoot "docker-compose.ui-isolated.yml"
$ResultsRoot = Join-Path $ProjectRoot ("test-results\UI-ISOLATED-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
$ReportPath = Join-Path $ResultsRoot "RECONCILED-UI-REPORT.txt"
$FrontendLog = Join-Path $ResultsRoot "frontend.log"

New-Item -ItemType Directory -Path $ResultsRoot -Force | Out-Null

function Write-Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $line = "$(Get-Date -Format 'HH:mm:ss') $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $ReportPath -Value $line
}

function Invoke-Docker {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & docker.exe @Arguments 2>&1
        $exitCode = $LASTEXITCODE

        foreach ($item in $output) {
            $text = [string]$item
            Add-Content -LiteralPath $ReportPath -Value $text
            Write-Host $text
        }

        return $exitCode
    }
    finally {
        $ErrorActionPreference = $saved
    }
}

function Invoke-Compose {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    $composeArgs = @(
        "compose",
        "-p", "careeros-reconciled-ui",
        "-f", $ComposeBase,
        "-f", $OverridePath
    ) + $Arguments

    return Invoke-Docker -Arguments $composeArgs
}

@"
CareerOS v0.1 - Reconciled UI Only Isolated Validation
Project: $ProjectRoot
Compose project: careeros-reconciled-ui
Host ports: PostgreSQL=5433, Backend=8100, Frontend=3100
Started: $(Get-Date)
"@ | Set-Content -LiteralPath $ReportPath -Encoding UTF8

Write-Log "=== SAFETY CHECK ===" "Cyan"

# Explicit proof that the master path is not being used.
if ($ProjectRoot -like "C:\Projects\CareerOS") {
    throw "SAFETY STOP: script is pointing at the master repository."
}
Write-Log "Master repository protection: PASS" "Green"

# ---------------------------------------------------------
# Docker availability
# ---------------------------------------------------------
Write-Log "Checking Docker Desktop / daemon..." "Cyan"
$dockerInfo = Invoke-Docker @("info")
if ($dockerInfo -ne 0) {
    throw "Docker daemon is not available. Start Docker Desktop and rerun."
}
Write-Log "Docker daemon: PASS" "Green"

# ---------------------------------------------------------
# Create isolated compose override WITHOUT modifying base
# ---------------------------------------------------------
@'
services:
  postgres:
    ports:
      - "5433:5432"

  backend:
    ports:
      - "8100:8000"

  frontend:
    ports:
      - "3100:3000"
    environment:
      NEXT_PUBLIC_API_URL: "http://localhost:8100"
'@ | Set-Content -LiteralPath $OverridePath -Encoding UTF8

Write-Log "Created isolated Compose override: $OverridePath" "Green"

# ---------------------------------------------------------
# Validate merged Compose
# ---------------------------------------------------------
Write-Log "Validating isolated Compose configuration..." "Cyan"
$configExit = Invoke-Compose @("config")
if ($configExit -ne 0) {
    throw "Compose validation FAILED. No containers were started."
}
Write-Log "Compose validation: PASS" "Green"

# ---------------------------------------------------------
# Clean ONLY this isolated Compose project
# ---------------------------------------------------------
Write-Log "Cleaning previous reconciled UI test stack only..." "Yellow"
$downExit = Invoke-Compose @("down", "--remove-orphans")
if ($downExit -ne 0) {
    throw "Isolated Compose cleanup failed."
}

# ---------------------------------------------------------
# Build
# ---------------------------------------------------------
Write-Log "Building reconciled UI stack..." "Cyan"
$buildExit = Invoke-Compose @("build")
if ($buildExit -ne 0) {
    throw "Reconciled build FAILED. No UI HTTP tests will be executed."
}
Write-Log "Reconciled build: PASS" "Green"

# ---------------------------------------------------------
# Start
# ---------------------------------------------------------
Write-Log "Starting reconciled UI stack..." "Cyan"
$upExit = Invoke-Compose @("up", "-d")
if ($upExit -ne 0) {
    throw "Reconciled Compose startup FAILED. No UI HTTP tests will be executed."
}
Write-Log "Compose startup command: PASS" "Green"

Start-Sleep -Seconds 5

# ---------------------------------------------------------
# Verify actual containers are running BEFORE any HTTP test
# ---------------------------------------------------------
Write-Log "=== CONTAINER VERIFICATION ===" "Cyan"

$psOutput = @()
$psExit = Invoke-Compose @("ps")
if ($psExit -ne 0) {
    throw "Unable to inspect reconciled container status."
}

# Query each service individually with JSON and require a running state.
$requiredServices = @("postgres", "backend", "frontend")
$runningServices = @()

foreach ($service in $requiredServices) {
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $json = & docker.exe compose -p careeros-reconciled-ui -f $ComposeBase -f $OverridePath ps --format json $service 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $saved
    }

    foreach ($line in $json) {
        Add-Content -LiteralPath $ReportPath -Value ([string]$line)
    }

    if ($code -ne 0) {
        throw "Could not query service '$service'."
    }

    $joined = ($json -join "`n")

    if ([string]::IsNullOrWhiteSpace($joined)) {
        throw "Required service '$service' is not running / not present."
    }

    try {
        $obj = $joined | ConvertFrom-Json
        $state = [string]$obj.State
    }
    catch {
        $state = $joined
    }

    if ($state -notmatch "running|up") {
        throw "Required service '$service' is not running. Reported state: $state"
    }

    $runningServices += $service
    Write-Log "[PASS] Container $service is running." "Green"
}

if ($runningServices.Count -ne 3) {
    throw "Not all required reconciled containers are running. HTTP tests will NOT execute."
}

Write-Log "All reconciled containers are confirmed running." "Green"

# ---------------------------------------------------------
# Wait for frontend ONLY
# ---------------------------------------------------------
Write-Log "Waiting for reconciled UI: http://localhost:3100 ..." "Cyan"

$uiReady = $false

for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $response = Invoke-WebRequest `
            -Uri "http://localhost:3100/" `
            -UseBasicParsing `
            -TimeoutSec 8

        if ($response.StatusCode -eq 200) {
            $uiReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 3
    }
}

if (-not $uiReady) {
    Write-Log "[FAIL] Reconciled UI root did not return HTTP 200." "Red"
    Invoke-Compose @("logs", "frontend", "--tail=200") | Set-Content -LiteralPath $FrontendLog -Encoding UTF8
    throw "UI is not ready. No further route testing executed."
}

Write-Log "[PASS] http://localhost:3100/ -> HTTP 200" "Green"

# ---------------------------------------------------------
# UI routes ONLY
# ---------------------------------------------------------
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

$failCount = 0

Write-Log "=== RECONCILED UI ROUTE TEST ===" "Cyan"

foreach ($route in $routes) {
    try {
        $response = Invoke-WebRequest `
            -Uri ("http://localhost:3100" + $route) `
            -UseBasicParsing `
            -TimeoutSec 15

        if ($response.StatusCode -eq 200) {
            Write-Log "[PASS] $route -> HTTP 200" "Green"
        }
        else {
            Write-Log "[FAIL] $route -> HTTP $($response.StatusCode)" "Red"
            $failCount++
        }
    }
    catch {
        Write-Log "[FAIL] $route -> $($_.Exception.Message)" "Red"
        $failCount++
    }
}

# Capture frontend log
Invoke-Compose @("logs", "frontend", "--tail=300") | Set-Content -LiteralPath $FrontendLog -Encoding UTF8

# ---------------------------------------------------------
# Final result
# ---------------------------------------------------------
Write-Log ""
Write-Log "============================================" "Cyan"
Write-Log "RECONCILED UI TEST RESULT" "Cyan"
Write-Log "============================================" "Cyan"
Write-Log "UI root ready : $uiReady"
Write-Log "Route failures: $failCount"
Write-Log "Report        : $ReportPath"
Write-Log "Frontend log  : $FrontendLog"

if ($uiReady -and $failCount -eq 0) {
    Write-Log "UI STARTUP + ALL ROUTES = PASS" "Green"
    Write-Log "Opening http://localhost:3100" "Green"
    Start-Process "http://localhost:3100"
    exit 0
}

Write-Log "UI VALIDATION = FAIL" "Red"
exit 1

