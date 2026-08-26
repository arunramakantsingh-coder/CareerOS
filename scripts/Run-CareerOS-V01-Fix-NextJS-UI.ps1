#requires -Version 5.1
$ErrorActionPreference = "Stop"

$ProjectRoot = (Get-Location).Path
$ComposePath = Join-Path $ProjectRoot "docker-compose.yml"
$FrontendPath = Join-Path $ProjectRoot "frontend"
$ResultRoot = Join-Path $ProjectRoot "test-results\UI-FIX-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

if (-not (Test-Path -LiteralPath $ComposePath)) { throw "docker-compose.yml not found in: $ProjectRoot" }
if (-not (Test-Path -LiteralPath $FrontendPath)) { throw "frontend directory not found: $FrontendPath" }

New-Item -ItemType Directory -Path $ResultRoot -Force | Out-Null
$Report = Join-Path $ResultRoot "UI-FIX-REPORT.txt"

function Log {
    param([string]$Text, [string]$Color = "White")
    $line = "$(Get-Date -Format 'HH:mm:ss') $Text"
    Add-Content -LiteralPath $Report -Value $line
    Write-Host $line -ForegroundColor $Color
}

"CareerOS v0.1 - UI Next.js Cache Fix`nProject: $ProjectRoot`nStarted: $(Get-Date)`n" |
    Set-Content -LiteralPath $Report -Encoding UTF8

Log "Diagnosed: Next.js .next build-artifact mismatch (missing webpack chunk ./73.js)." "Yellow"
Log "Fix: recreate ONLY the v0.1 frontend and clear /app/.next before next dev." "Yellow"

$backup = Join-Path $ResultRoot "docker-compose.yml.before-ui-fix"
Copy-Item -LiteralPath $ComposePath -Destination $backup -Force
Log "Backup: $backup" "Green"

$compose = Get-Content -LiteralPath $ComposePath -Raw
$old = 'command: npm run dev'
$new = 'command: sh -c "rm -rf /app/.next && npm run dev"'

if ($compose.Contains($old)) {
    $compose = $compose.Replace($old, $new)
    Set-Content -LiteralPath $ComposePath -Value $compose -Encoding UTF8
    Log "Updated frontend dev command to clear /app/.next on every start." "Green"
} elseif ($compose.Contains($new)) {
    Log "Frontend clean-start command already present." "Green"
} else {
    throw "Expected frontend command was not found in docker-compose.yml."
}

docker compose config | Out-Null
Log "Compose syntax: PASS" "Green"

Log "Stopping/removing ONLY v0.1 frontend container..." "Cyan"
docker compose stop frontend 2>&1 | Out-Null
docker compose rm -sf frontend 2>&1 | Out-Null

Log "Building frontend image..." "Cyan"
docker compose build frontend

Log "Starting frontend..." "Cyan"
docker compose up -d --force-recreate frontend
Start-Sleep -Seconds 8

Log "=== FRONTEND STATUS ===" "Cyan"
docker compose ps frontend | Tee-Object -FilePath $Report -Append

Log "=== FRONTEND LOGS ===" "Cyan"
docker compose logs frontend --tail=120 | Tee-Object -FilePath $Report -Append

Log "Waiting for http://localhost:3000 ..." "Cyan"
$ready = $false
for ($i = 1; $i -le 18; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 8
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 3 }
}

if ($ready) { Log "[PASS] UI root -> HTTP 200" "Green" }
else { Log "[FAIL] UI root did not return HTTP 200" "Red" }

$routes = @(
    "/","/login","/onboarding","/career-vault","/personas","/jobs",
    "/applications","/application-studio","/company-intelligence",
    "/interviews","/live-interview","/global-mobility","/analytics","/settings"
)

$failures = 0
Log "=== UI ROUTE CHECK ===" "Cyan"
foreach ($route in $routes) {
    try {
        $r = Invoke-WebRequest -Uri ("http://localhost:3000" + $route) -UseBasicParsing -TimeoutSec 15
        if ($r.StatusCode -eq 200) { Log "[PASS] $route -> HTTP 200" "Green" }
        else { Log "[FAIL] $route -> HTTP $($r.StatusCode)" "Red"; $failures++ }
    } catch {
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
Log "Use UI-FIX-REPORT.txt and frontend-final.log for the next fix." "Yellow"
exit 1
