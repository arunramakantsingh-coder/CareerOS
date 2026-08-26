#requires -Version 5.1

$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\Projects\CareerOS-v0.1-Personal-Job-Interview-Copilot-FINAL\CareerOS-v0.1"
Set-Location $ProjectRoot

$ResultsRoot = Join-Path $ProjectRoot ("test-results\UI-FIX-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Path $ResultsRoot -Force | Out-Null

$Report = Join-Path $ResultsRoot "UI-FIX-REPORT.txt"

function Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )

    $line = "$(Get-Date -Format 'HH:mm:ss') $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $Report -Value $line
}

function Invoke-DockerSafe {
    param(
        [Parameter(Mandatory)]
        [string[]]$Args
    )

    # Docker frequently writes normal progress/status messages to stderr.
    # PowerShell 5.1 can convert those into NativeCommandError when the
    # global error preference is Stop. Temporarily suppress that behavior.
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        $output = & docker.exe @Args 2>&1
        $exitCode = $LASTEXITCODE

        foreach ($line in $output) {
            Add-Content -LiteralPath $Report -Value ([string]$line)
            Write-Host ([string]$line)
        }

        return $exitCode
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
}

function Assert-Docker {
    param(
        [string[]]$Args,
        [string]$Description
    )

    Log $Description "Cyan"

    $exitCode = Invoke-DockerSafe -Args $Args

    if ($exitCode -ne 0) {
        throw "$Description failed. Docker exit code: $exitCode"
    }

    Log "$Description : PASS" "Green"
}

"CareerOS v0.1 - Next.js UI Fix v6" | Set-Content $Report -Encoding UTF8
"Project: $ProjectRoot" | Add-Content $Report
"Started: $(Get-Date)" | Add-Content $Report

Log "=== NEXT.JS UI FIX v6 ===" "Cyan"

$ComposePath = Join-Path $ProjectRoot "docker-compose.yml"

if (-not (Test-Path -LiteralPath $ComposePath)) {
    throw "docker-compose.yml not found."
}

# --------------------------------------------------
# Backup
# --------------------------------------------------

$Backup = Join-Path $ResultsRoot "docker-compose.yml.before-ui-fix-v6"
Copy-Item -LiteralPath $ComposePath -Destination $Backup -Force

Log "Compose backup: $Backup" "Green"

# --------------------------------------------------
# Remove /app/.next volume
# --------------------------------------------------

$composeText = Get-Content -LiteralPath $ComposePath -Raw

if ($composeText -match '(?m)^\s*-\s*/app/\.next\s*$') {

    $lines = Get-Content -LiteralPath $ComposePath

    $lines = $lines | Where-Object {
        $_ -notmatch '^\s*-\s*/app/\.next\s*$'
    }

    $lines | Set-Content -LiteralPath $ComposePath -Encoding UTF8

    Log "Removed /app/.next Docker volume." "Green"
}
else {
    Log "/app/.next Docker volume already absent." "Green"
}

# --------------------------------------------------
# Clean Next startup
# --------------------------------------------------

$composeText = Get-Content -LiteralPath $ComposePath -Raw

if ($composeText -match 'command:\s*npm run dev') {

    $composeText = $composeText.Replace(
        'command: npm run dev',
        'command: sh -c "rm -rf /app/.next && npm run dev"'
    )

    Set-Content -LiteralPath $ComposePath -Value $composeText -Encoding UTF8

    Log "Configured clean Next.js startup." "Green"
}
else {
    Log "Clean Next.js startup command already configured." "Green"
}

# --------------------------------------------------
# Compose validation
# --------------------------------------------------

Assert-Docker @("compose","config") "Compose validation"

# --------------------------------------------------
# Stop frontend
# --------------------------------------------------

Log "Stopping v0.1 frontend..." "Yellow"
$stopExit = Invoke-DockerSafe @("compose","stop","frontend")

if ($stopExit -eq 0) {
    Log "Frontend stop completed." "Green"
}
else {
    Log "Frontend stop returned exit code $stopExit; continuing cleanup." "Yellow"
}

# --------------------------------------------------
# Remove frontend container + anonymous volumes
# --------------------------------------------------

Log "Removing v0.1 frontend container and anonymous volumes..." "Yellow"
$removeExit = Invoke-DockerSafe @("compose","rm","-sfv","frontend")

if ($removeExit -eq 0) {
    Log "Frontend container removal completed." "Green"
}
else {
    Log "Frontend removal returned exit code $removeExit; continuing." "Yellow"
}

# --------------------------------------------------
# Remove host .next
# --------------------------------------------------

$HostNext = Join-Path $ProjectRoot "frontend\.next"

if (Test-Path -LiteralPath $HostNext) {

    Remove-Item -LiteralPath $HostNext -Recurse -Force

    Log "Removed host frontend\.next." "Green"
}
else {
    Log "Host frontend\.next not present." "Green"
}

# --------------------------------------------------
# Build frontend
# --------------------------------------------------

Assert-Docker @("compose","build","frontend") "Frontend image build"

# --------------------------------------------------
# Start frontend
# --------------------------------------------------

Assert-Docker @(
    "compose",
    "up",
    "-d",
    "--force-recreate",
    "frontend"
) "Frontend container start"

Start-Sleep -Seconds 8

# --------------------------------------------------
# Status
# --------------------------------------------------

Log "=== FRONTEND STATUS ===" "Cyan"
Invoke-DockerSafe @("compose","ps","frontend") | Out-Null

# --------------------------------------------------
# Wait for UI
# --------------------------------------------------

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
    Log "[PASS] UI root -> HTTP 200" "Green"
}
else {
    Log "[FAIL] UI root -> no HTTP 200" "Red"
}

# --------------------------------------------------
# UI route test
# --------------------------------------------------

$Routes = @(
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

$FailCount = 0

Log "=== UI ROUTE CHECK ===" "Cyan"

foreach ($route in $Routes) {

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
            $FailCount++

        }

    }
    catch {

        Log "[FAIL] $route -> $($_.Exception.Message)" "Red"
        $FailCount++

    }
}

# --------------------------------------------------
# Capture frontend logs
# --------------------------------------------------

$FrontendLog = Join-Path $ResultsRoot "frontend-final.log"

$logOutput = Invoke-DockerSafe @(
    "compose",
    "logs",
    "frontend",
    "--tail=300"
)

$logOutput |
    Out-String |
    Set-Content -LiteralPath $FrontendLog -Encoding UTF8

Log "Frontend log: $FrontendLog"

# --------------------------------------------------
# Final result
# --------------------------------------------------

if ($ready -and $FailCount -eq 0) {

    Log "==========================================" "Green"
    Log "UI STARTUP + ALL ROUTES PASS" "Green"
    Log "==========================================" "Green"
    Log "Open http://localhost:3000 for visual UI review." "Green"

    exit 0
}

Log "==========================================" "Red"
Log "UI STILL HAS FAILURES" "Red"
Log "==========================================" "Red"
Log "Report: $Report" "Yellow"
Log "Frontend log: $FrontendLog" "Yellow"

exit 1

