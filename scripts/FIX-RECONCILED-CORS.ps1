#requires -Version 5.1

$ErrorActionPreference = "Stop"

$Root = "C:\Projects\CareerOS-v0.1-RECONCILED\CareerOS-v0.1"
$Compose = Join-Path $Root "docker-compose.reconciled-ui.yml"
$Config = Join-Path $Root "backend\app\core\config.py"
$ResultDir = Join-Path $Root ("test-results\CORS-FIX-" + (Get-Date -Format "yyyyMMdd-HHmmss"))

Set-Location $Root
New-Item -ItemType Directory -Path $ResultDir -Force | Out-Null

$Report = Join-Path $ResultDir "CORS-FIX-REPORT.txt"

function Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )

    $line = "$(Get-Date -Format 'HH:mm:ss') $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $Report -Value $line
}

Log "=== RECONCILED CORS FIX ===" "Cyan"

# --------------------------------------------------
# Protect master
# --------------------------------------------------

if (-not (Test-Path "C:\Projects\CareerOS")) {
    throw "Master repository not found."
}

Log "Master protection: PASS" "Green"

# --------------------------------------------------
# Backup config
# --------------------------------------------------

if (-not (Test-Path $Config)) {
    throw "Backend config.py not found."
}

$Backup = "$Config.before-cors-3100"
Copy-Item $Config $Backup -Force

Log "Config backup: $Backup" "Green"

# --------------------------------------------------
# Read config
# --------------------------------------------------

$text = Get-Content $Config -Raw

# Add 3100 if not already present.
if ($text -match 'http://localhost:3100') {

    Log "localhost:3100 already present in backend config." "Green"

}
else {

    # Existing configuration contains localhost:3000.
    # Add localhost:3100 immediately after it.
    $pattern = '"http://localhost:3000",'

    if ($text.Contains($pattern)) {

        $replacement = @"
"http://localhost:3000",
        "http://localhost:3100",
"@

        $text = $text.Replace($pattern, $replacement.TrimEnd())

    }
    else {

        throw "Could not find the expected localhost:3000 origin in config.py."
    }

    Set-Content -LiteralPath $Config -Value $text -Encoding UTF8

    Log "Added http://localhost:3100 to ALLOWED_ORIGINS." "Green"
}

# --------------------------------------------------
# Show resulting origin config
# --------------------------------------------------

Log "=== RESULTING CORS CONFIG ===" "Cyan"

Select-String `
    -Path $Config `
    -Pattern "localhost:3000|localhost:3100|ALLOWED_ORIGINS|allow_origins" `
    -Context 1,2 |
    Out-String |
    Tee-Object -FilePath $Report -Append

# --------------------------------------------------
# Verify standalone Compose
# --------------------------------------------------

if (-not (Test-Path $Compose)) {
    throw "docker-compose.reconciled-ui.yml not found."
}

$old = $ErrorActionPreference
$ErrorActionPreference = "Continue"

docker compose `
    -f $Compose `
    -p careeros-reconciled-ui `
    config 2>&1 |
    Tee-Object -FilePath (Join-Path $ResultDir "compose-config.txt")

$composeExit = $LASTEXITCODE

$ErrorActionPreference = $old

if ($composeExit -ne 0) {
    throw "Compose validation failed."
}

Log "Compose validation: PASS" "Green"

# --------------------------------------------------
# Rebuild/restart backend + frontend
# --------------------------------------------------

Log "Rebuilding/restarting reconciled backend and frontend..." "Cyan"

$old = $ErrorActionPreference
$ErrorActionPreference = "Continue"

docker compose `
    -f $Compose `
    -p careeros-reconciled-ui `
    up -d --build --force-recreate backend frontend 2>&1 |
    Tee-Object -FilePath (Join-Path $ResultDir "restart.txt")

$restartExit = $LASTEXITCODE

$ErrorActionPreference = $old

if ($restartExit -ne 0) {
    throw "Backend/frontend restart failed."
}

Log "Backend/frontend restart: PASS" "Green"

Start-Sleep -Seconds 8

# --------------------------------------------------
# Test preflight directly
# --------------------------------------------------

Log "Testing CORS preflight..." "Cyan"

try {

    $preflight = Invoke-WebRequest `
        -Uri "http://localhost:8100/api/v1/auth/login" `
        -Method OPTIONS `
        -Headers @{
            Origin = "http://localhost:3100"
            "Access-Control-Request-Method" = "POST"
            "Access-Control-Request-Headers" = "content-type"
        } `
        -UseBasicParsing `
        -TimeoutSec 10

    Log "OPTIONS status: $($preflight.StatusCode)" "Green"
    Log "Allow-Origin: $($preflight.Headers["Access-Control-Allow-Origin"])" "Green"
    Log "Allow-Methods: $($preflight.Headers["Access-Control-Allow-Methods"])" "Green"

}
catch {

    $status = $_.Exception.Response.StatusCode.value__

    if ($status) {
        throw "CORS preflight still failing with HTTP $status."
    }

    throw "CORS preflight network error: $($_.Exception.Message)"
}

# --------------------------------------------------
# Final
# --------------------------------------------------

Log ""
Log "========================================" "Green"
Log "CORS FIX COMPLETE" "Green"
Log "========================================" "Green"
Log "Open http://localhost:3100 and test Login/Register." "Green"

Start-Process "http://localhost:3100"

Write-Host ""
Write-Host "Report:" -ForegroundColor Yellow
Write-Host $Report -ForegroundColor Cyan