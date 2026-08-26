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

function Invoke-Docker {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "docker.exe"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    foreach ($arg in $Arguments) {
        [void]$psi.ArgumentList.Add($arg)
    }

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi

    [void]$process.Start()

    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()

    $process.WaitForExit()

    $outText = $stdout.Result
    $errText = $stderr.Result

    if ($outText) {
        Add-Content -LiteralPath $Report -Value $outText
        Write-Host $outText
    }

    if ($errText) {
        Add-Content -LiteralPath $Report -Value $errText
        Write-Host $errText -ForegroundColor DarkGray
    }

    return $process.ExitCode
}

"CareerOS v0.1 - Next.js UI Fix v5" | Set-Content $Report -Encoding UTF8
"Project: $ProjectRoot" | Add-Content $Report
"Started: $(Get-Date)" | Add-Content $Report

Log "=== NEXT.JS UI FIX v5 ===" "Cyan"

$Compose = Join-Path $ProjectRoot "docker-compose.yml"

if (-not (Test-Path $Compose)) {
    throw "docker-compose.yml not found."
}

# --------------------------------------------------
# Backup
# --------------------------------------------------

$Backup = Join-Path $ResultsRoot "docker-compose.yml.before-ui-fix-v5"
Copy-Item $Compose $Backup -Force
Log "Compose backup: $Backup" "Green"

# --------------------------------------------------
# Remove /app/.next volume
# --------------------------------------------------

$composeText = Get-Content $Compose -Raw

if ($composeText -match '(?m)^\s*-\s*/app/\.next\s*$') {

    $lines = Get-Content $Compose

    $lines = $lines | Where-Object {
        $_ -notmatch '^\s*-\s*/app/\.next\s*$'
    }

    $lines | Set-Content $Compose -Encoding UTF8

    Log "Removed /app/.next Docker volume." "Green"
}

# --------------------------------------------------
# Clean startup command
# --------------------------------------------------

$composeText = Get-Content $Compose -Raw

if ($composeText -match 'command:\s*npm run dev') {

    $composeText = $composeText.Replace(
        'command: npm run dev',
        'command: sh -c "rm -rf /app/.next && npm run dev"'
    )

    Set-Content $Compose $composeText -Encoding UTF8

    Log "Configured clean Next.js startup." "Green"
}
else {
    Log "Clean Next.js startup command already configured." "Green"
}

# --------------------------------------------------
# Compose validation
# --------------------------------------------------

Log "Validating Compose..." "Cyan"

$exit = Invoke-Docker @("compose","config")

if ($exit -ne 0) {
    throw "docker compose config failed."
}

Log "Compose validation PASS." "Green"

# --------------------------------------------------
# Stop frontend
# --------------------------------------------------

Log "Stopping v0.1 frontend..." "Cyan"

Invoke-Docker @("compose","stop","frontend") | Out-Null

# Stop/remove failures caused by an already-stopped container
# are intentionally tolerated here.

# --------------------------------------------------
# Remove frontend container and anonymous volumes
# --------------------------------------------------

Log "Removing v0.1 frontend container..." "Cyan"

Invoke-Docker @("compose","rm","-sfv","frontend") | Out-Null

# --------------------------------------------------
# Remove host .next
# --------------------------------------------------

$hostNext = Join-Path $ProjectRoot "frontend\.next"

if (Test-Path $hostNext) {
    Remove-Item $hostNext -Recurse -Force
    Log "Removed frontend\.next." "Green"
}
else {
    Log "No frontend\.next found." "Green"
}

# --------------------------------------------------
# Rebuild frontend
# --------------------------------------------------

Log "Building frontend image..." "Cyan"

$exit = Invoke-Docker @("compose","build","frontend")

if ($exit -ne 0) {
    throw "Frontend image build failed."
}

Log "Frontend image build PASS." "Green"

# --------------------------------------------------
# Start frontend
# --------------------------------------------------

Log "Starting frontend..." "Cyan"

$exit = Invoke-Docker @(
    "compose",
    "up",
    "-d",
    "--force-recreate",
    "frontend"
)

if ($exit -ne 0) {
    throw "Frontend start failed."
}

Start-Sleep -Seconds 8

# --------------------------------------------------
# Status
# --------------------------------------------------

Log "=== FRONTEND STATUS ===" "Cyan"

Invoke-Docker @("compose","ps","frontend") | Out-Null

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
# UI Routes
# --------------------------------------------------

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

Log "=== UI ROUTE CHECK ===" "Cyan"

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
            $failCount++

        }

    }
    catch {

        Log "[FAIL] $route -> $($_.Exception.Message)" "Red"
        $failCount++

    }
}

# --------------------------------------------------
# Final logs
# --------------------------------------------------

$frontendLog = Join-Path $ResultsRoot "frontend-final.log"

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "docker.exe"
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true

foreach ($arg in @("compose","logs","frontend","--tail=300")) {
    [void]$psi.ArgumentList.Add($arg)
}

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi

[void]$p.Start()

$stdout = $p.StandardOutput.ReadToEndAsync()
$stderr = $p.StandardError.ReadToEndAsync()

$p.WaitForExit()

@(
    $stdout.Result
    $stderr.Result
) | Set-Content -LiteralPath $frontendLog -Encoding UTF8

Log "Frontend log: $frontendLog"

# --------------------------------------------------
# Final result
# --------------------------------------------------

if ($ready -and $failCount -eq 0) {

    Log "============================================" "Green"
    Log "UI STARTUP + ALL ROUTES PASS" "Green"
    Log "============================================" "Green"
    Log "Open http://localhost:3000 for visual UI testing." "Green"

    exit 0
}

Log "============================================" "Red"
Log "UI STILL HAS FAILURES" "Red"
Log "============================================" "Red"
Log "Report: $Report" "Yellow"
Log "Frontend log: $frontendLog" "Yellow"

exit 1
