#requires -Version 5.1

$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\Projects\CareerOS-v0.1-Personal-Job-Interview-Copilot-FINAL\CareerOS-v0.1"
$ComposePath = Join-Path $ProjectRoot "docker-compose.yml"
$ResultsRoot = Join-Path $ProjectRoot ("test-results\UI-FIX-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
$ReportFile = Join-Path $ResultsRoot "UI-FIX-REPORT.txt"

Set-Location $ProjectRoot
New-Item -ItemType Directory -Path $ResultsRoot -Force | Out-Null

function Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )

    $line = "$(Get-Date -Format 'HH:mm:ss') $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $ReportFile -Value $line
}

function Run-Cmd {
    param(
        [string]$Command,
        [string]$Arguments
    )

    $output = & cmd.exe /c "$Command $Arguments" 2>&1
    $exitCode = $LASTEXITCODE

    foreach ($line in $output) {
        Add-Content -LiteralPath $ReportFile -Value $line
    }

    if ($exitCode -ne 0) {
        throw "$Command $Arguments failed with exit code $exitCode"
    }

    return $output
}

if (-not (Test-Path -LiteralPath $ComposePath)) {
    throw "docker-compose.yml not found: $ComposePath"
}

@"
CareerOS v0.1 - Next.js UI Fix v3
Project: $ProjectRoot
Started: $(Get-Date)
"@ | Set-Content -LiteralPath $ReportFile -Encoding UTF8

Log "=== NEXT.JS UI FIX v3 ===" "Cyan"

# ------------------------------------------------------------
# 1. BACKUP COMPOSE
# ------------------------------------------------------------

$backup = Join-Path $ResultsRoot "docker-compose.yml.before-ui-fix"
Copy-Item -LiteralPath $ComposePath -Destination $backup -Force
Log "Backup created: $backup" "Green"

# ------------------------------------------------------------
# 2. REMOVE /app/.next ANONYMOUS VOLUME
# ------------------------------------------------------------

$compose = Get-Content -LiteralPath $ComposePath -Raw

if ($compose -match '(?m)^\s*-\s*/app/\.next\s*$') {

    $lines = Get-Content -LiteralPath $ComposePath

    $filtered = $lines | Where-Object {
        $_ -notmatch '^\s*-\s*/app/\.next\s*$'
    }

    $filtered | Set-Content -LiteralPath $ComposePath -Encoding UTF8

    Log "Removed /app/.next anonymous Docker volume." "Green"
}
else {
    Log "/app/.next anonymous volume not present." "Green"
}

# ------------------------------------------------------------
# 3. USE CLEAN NEXT DEV STARTUP
# ------------------------------------------------------------

$compose = Get-Content -LiteralPath $ComposePath -Raw

$compose = $compose.Replace(
    'command: npm run dev',
    'command: sh -c "rm -rf /app/.next && npm run dev"'
)

Set-Content -LiteralPath $ComposePath -Value $compose -Encoding UTF8

Log "Configured Next.js to clear .next before dev startup." "Green"

# ------------------------------------------------------------
# 4. VALIDATE COMPOSE
# ------------------------------------------------------------

Run-Cmd "docker" "compose config"
Log "Compose configuration: PASS" "Green"

# ------------------------------------------------------------
# 5. STOP ONLY V01 FRONTEND
# ------------------------------------------------------------

Log "Stopping ONLY v0.1 frontend..." "Yellow"

try {
    Run-Cmd "docker" "compose stop frontend"
}
catch {
    Log "Frontend stop returned a non-zero result; continuing to container removal." "Yellow"
}

# ------------------------------------------------------------
# 6. REMOVE ONLY FRONTEND CONTAINER + ANONYMOUS VOLUMES
# ------------------------------------------------------------

Log "Removing ONLY v0.1 frontend container and anonymous volumes..." "Yellow"

try {
    Run-Cmd "docker" "compose rm -sfv frontend"
}
catch {
    Log "Frontend container was already absent; continuing." "Yellow"
}

# ------------------------------------------------------------
# 7. CLEAR HOST FRONTEND .NEXT IF IT EXISTS
# ------------------------------------------------------------

$hostNext = Join-Path $ProjectRoot "frontend\.next"

if (Test-Path -LiteralPath $hostNext) {
    Remove-Item -LiteralPath $hostNext -Recurse -Force
    Log "Removed host frontend\.next cache." "Green"
}
else {
    Log "No host frontend\.next cache found." "Green"
}

# ------------------------------------------------------------
# 8. BUILD FRONTEND
# ------------------------------------------------------------

Log "Building frontend image..." "Cyan"

Run-Cmd "docker" "compose build frontend"

Log "Frontend build: PASS" "Green"

# ------------------------------------------------------------
# 9. START FRONTEND
# ------------------------------------------------------------

Log "Starting frontend..." "Cyan"

Run-Cmd "docker" "compose up -d --force-recreate frontend"

Start-Sleep -Seconds 8

Log "Frontend container started." "Green"

# ------------------------------------------------------------
# 10. STATUS
# ------------------------------------------------------------

Log "=== FRONTEND STATUS ===" "Cyan"

Run-Cmd "docker" "compose ps frontend"

# ------------------------------------------------------------
# 11. FRONTEND LOGS
# ------------------------------------------------------------

Log "=== FRONTEND LOGS ===" "Cyan"

$frontendLog = Join-Path $ResultsRoot "frontend-startup.log"

$logOutput = & cmd.exe /c "docker compose logs frontend --tail=150" 2>&1
$logOutput | Set-Content -LiteralPath $frontendLog -Encoding UTF8
$logOutput | ForEach-Object {
    Add-Content -LiteralPath $ReportFile -Value $_
}

# ------------------------------------------------------------
# 12. WAIT FOR ROOT
# ------------------------------------------------------------

Log "Waiting for http://localhost:3000 ..." "Cyan"

$ready = $false

for ($i = 1; $i -le 20; $i++) {

    try {

        $response = Invoke-WebRequest `
            -Uri "http://localhost:3000/" `
            -UseBasicParsing `
            -TimeoutSec 8

        if ($response.StatusCode -eq 200) {
            $ready = $true
            break
        }

    }
    catch {
        Start-Sleep -Seconds 3
    }
}

if ($ready) {
    Log "[PASS] http://localhost:3000/" "Green"
}
else {
    Log "[FAIL] http://localhost:3000/" "Red"
}

# ------------------------------------------------------------
# 13. UI ROUTES
# ------------------------------------------------------------

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

$failedRoutes = 0

Log "=== UI ROUTE TEST ===" "Cyan"

foreach ($route in $routes) {

    try {

        $response = Invoke-WebRequest `
            -Uri ("http://localhost:3000" + $route) `
            -UseBasicParsing `
            -TimeoutSec 15

        if ($response.StatusCode -eq 200) {

            Log "[PASS] $route -> HTTP 200" "Green"

        }
        else {

            Log "[FAIL] $route -> HTTP $($response.StatusCode)" "Red"
            $failedRoutes++

        }

    }
    catch {

        Log "[FAIL] $route -> $($_.Exception.Message)" "Red"
        $failedRoutes++

    }
}

# ------------------------------------------------------------
# 14. CAPTURE FINAL LOG
# ------------------------------------------------------------

$finalLog = Join-Path $ResultsRoot "frontend-final.log"

$logs = & cmd.exe /c "docker compose logs frontend --tail=300" 2>&1

$logs | Set-Content -LiteralPath $finalLog -Encoding UTF8

Log "Final frontend log: $finalLog"

# ------------------------------------------------------------
# 15. RESULT
# ------------------------------------------------------------

if ($ready -and $failedRoutes -eq 0) {

    Log "============================================" "Green"
    Log "UI STARTUP + ALL ROUTES = PASS" "Green"
    Log "============================================" "Green"
    Log "Open http://localhost:3000 for visual inspection." "Green"

    exit 0
}

Log "============================================" "Red"
Log "UI STILL HAS FAILURES" "Red"
Log "============================================" "Red"
Log "See: $ReportFile" "Yellow"
Log "See: $finalLog" "Yellow"

exit 1

