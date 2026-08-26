#requires -Version 5.1
$ErrorActionPreference = "Stop"

$ProjectRoot = (Get-Location).Path
$ComposePath = Join-Path $ProjectRoot "docker-compose.yml"
$ResultRoot = Join-Path $ProjectRoot "test-results\UI-FIX-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

if (-not (Test-Path -LiteralPath $ComposePath)) {
    throw "docker-compose.yml not found in current directory: $ProjectRoot"
}

New-Item -ItemType Directory -Path $ResultRoot -Force | Out-Null
$Report = Join-Path $ResultRoot "UI-FIX-REPORT.txt"

function Log {
    param([string]$Text, [string]$Color = "White")
    $line = "$(Get-Date -Format 'HH:mm:ss') $Text"
    Add-Content -LiteralPath $Report -Value $line
    Write-Host $line -ForegroundColor $Color
}

"CareerOS v0.1 - Next.js UI Cache Fix v2`nProject: $ProjectRoot`nStarted: $(Get-Date)`n" |
    Set-Content -LiteralPath $Report -Encoding UTF8

Log "Fixing stale Next.js .next cache only for the v0.1 frontend." "Yellow"

# Backup compose
$backup = Join-Path $ResultRoot "docker-compose.yml.before-ui-fix"
Copy-Item -LiteralPath $ComposePath -Destination $backup -Force
Log "Backup created: $backup" "Green"

# Ensure frontend command clears .next before starting.
$compose = Get-Content -LiteralPath $ComposePath -Raw
$old = 'command: npm run dev'
$new = 'command: sh -c "rm -rf /app/.next && npm run dev"'

if ($compose.Contains($old)) {
    $compose = $compose.Replace($old, $new)
    Set-Content -LiteralPath $ComposePath -Value $compose -Encoding UTF8
    Log "Updated frontend clean-start command." "Green"
} elseif ($compose.Contains($new)) {
    Log "Frontend clean-start command already present." "Green"
} else {
    throw "Expected frontend command was not found."
}

docker compose config | Out-Null
Log "Compose syntax: PASS" "Green"

# Docker emits normal stop/remove messages on stderr. Capture them without
# converting them into PowerShell terminating errors.
Log "Stopping v0.1 frontend..." "Cyan"
$stopOutput = & docker compose stop frontend 2>&1
$stopExit = $LASTEXITCODE
$stopOutput | Add-Content -LiteralPath $Report
if ($stopExit -ne 0 -and ($stopOutput -join "`n") -notmatch "No such service|is not running") {
    throw "docker compose stop frontend failed. Exit code: $stopExit"
}

Log "Removing v0.1 frontend container..." "Cyan"
$rmOutput = & docker compose rm -sf frontend 2>&1
$rmExit = $LASTEXITCODE
$rmOutput | Add-Content -LiteralPath $Report
if ($rmExit -ne 0 -and ($rmOutput -join "`n") -notmatch "No such service|No stopped containers") {
    throw "docker compose rm frontend failed. Exit code: $rmExit"
}

# Remove stale anonymous frontend volumes associated with the compose project.
Log "Removing stale frontend anonymous volumes (v0.1 only)..." "Cyan"
$volumes = @(& docker volume ls --format "{{.Name}}" 2>$null)
$projectName = (docker compose config --format json | ConvertFrom-Json).name
if (-not $projectName) { $projectName = "careeros-v01" }

foreach ($volume in $volumes) {
    if ($volume -match "^${projectName}_" -and $volume -match "node_modules|next") {
        & docker volume rm $volume 2>&1 | Add-Content -LiteralPath $Report
    }
}

Log "Rebuilding frontend image..." "Cyan"
& docker compose build frontend 2>&1 | Tee-Object -FilePath (Join-Path $ResultRoot "frontend-build.log") -Append
if ($LASTEXITCODE -ne 0) {
    throw "Frontend Docker image build failed."
}

Log "Starting frontend..." "Cyan"
& docker compose up -d --force-recreate frontend 2>&1 | Tee-Object -FilePath (Join-Path $ResultRoot "frontend-start.log") -Append
if ($LASTEXITCODE -ne 0) {
    throw "Frontend startup failed."
}

Start-Sleep -Seconds 6

Log "=== FRONTEND STATUS ===" "Cyan"
docker compose ps frontend | Tee-Object -FilePath $Report -Append

Log "=== FRONTEND LOGS ===" "Cyan"
docker compose logs frontend --tail=120 | Tee-Object -FilePath $Report -Append

Log "Waiting for http://localhost:3000 ..." "Cyan"
$ready = $false
for ($i = 1; $i -le 20; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 8
        if ($r.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 3
    }
}

if ($ready) {
    Log "[PASS] UI root -> HTTP 200" "Green"
}
else {
    Log "[FAIL] UI root did not return HTTP 200" "Red"
}

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

$failures = 0
Log "=== UI ROUTE CHECK ===" "Cyan"

foreach ($route in $routes) {
    try {
        $r = Invoke-WebRequest -Uri ("http://localhost:3000" + $route) -UseBasicParsing -TimeoutSec 15
        if ($r.StatusCode -eq 200) {
            Log "[PASS] $route -> HTTP 200" "Green"
        }
        else {
            Log "[FAIL] $route -> HTTP $($r.StatusCode)" "Red"
            $failures++
        }
    }
    catch {
        Log "[FAIL] $route -> $($_.Exception.Message)" "Red"
        $failures++
    }
}

$finalLog = Join-Path $ResultRoot "frontend-final.log"
docker compose logs frontend --tail=250 | Set-Content -LiteralPath $finalLog -Encoding UTF8
Log "Frontend log: $finalLog"

if ($ready -and $failures -eq 0) {
    Log "=== RESULT: UI STARTUP + ALL ROUTES PASS ===" "Green"
    Log "Open http://localhost:3000 for visual UI testing." "Green"
    exit 0
}

Log "=== RESULT: UI STILL HAS FAILURES ===" "Red"
Log "Review UI-FIX-REPORT.txt and frontend-final.log." "Yellow"
exit 1
