#requires -Version 5.1

$ErrorActionPreference = "Stop"

$Root = "C:\Projects\CareerOS-v0.1-RECONCILED\CareerOS-v0.1"
$Compose = Join-Path $Root "docker-compose.reconciled-ui.yml"
$EnvFile = Join-Path $Root "frontend\.env.local"
$ResultDir = Join-Path $Root ("test-results\AUTH-FIX-" + (Get-Date -Format "yyyyMMdd-HHmmss"))

Set-Location $Root

New-Item -ItemType Directory -Path $ResultDir -Force | Out-Null

$Report = Join-Path $ResultDir "AUTH-FIX-REPORT.txt"

function Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )

    $line = "$(Get-Date -Format 'HH:mm:ss') $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $Report -Value $line
}

Log "=== CAREEROS RECONCILED AUTH NETWORK FIX ===" "Cyan"

# ---------------------------------------------------------
# MASTER PROTECTION
# ---------------------------------------------------------

if (-not (Test-Path "C:\Projects\CareerOS")) {
    throw "Master repository not found."
}

Log "Master protection: PASS" "Green"

# ---------------------------------------------------------
# SET FRONTEND API ENDPOINT
# ---------------------------------------------------------

if (-not (Test-Path $EnvFile)) {

    New-Item -ItemType File -Path $EnvFile -Force | Out-Null

}
else {

    Copy-Item $EnvFile "$EnvFile.before-auth-network-fix" -Force
}

@(
    "NEXT_PUBLIC_API_URL=http://localhost:8100"
) | Set-Content -LiteralPath $EnvFile -Encoding UTF8

Log "Frontend API endpoint set to http://localhost:8100" "Green"

# ---------------------------------------------------------
# REQUIRE STANDALONE COMPOSE
# ---------------------------------------------------------

if (-not (Test-Path $Compose)) {

    throw @"
Standalone Compose file not found:

$Compose

We will NOT use docker-compose.ui-isolated.yml because that file is only an override.
"@
}

Log "Standalone Compose file found." "Green"

# ---------------------------------------------------------
# VALIDATE COMPOSE
# ---------------------------------------------------------

$old = $ErrorActionPreference
$ErrorActionPreference = "Continue"

$composeOutput = & docker compose `
    -f $Compose `
    -p careeros-reconciled-ui `
    config 2>&1

$composeExit = $LASTEXITCODE

$ErrorActionPreference = $old

$composeOutput |
    Set-Content -LiteralPath (Join-Path $ResultDir "compose-config.txt") -Encoding UTF8

if ($composeExit -ne 0) {

    throw @"
Standalone Compose validation FAILED.

See:
$(Join-Path $ResultDir "compose-config.txt")
"@
}

Log "Standalone Compose: PASS" "Green"

# ---------------------------------------------------------
# VERIFY REQUIRED PORTS
# ---------------------------------------------------------

foreach ($port in @(5433,8100,3100)) {

    $listener = Get-NetTCPConnection `
        -LocalPort $port `
        -State Listen `
        -ErrorAction SilentlyContinue

    if ($listener) {

        Log "Port $port is listening." "Green"

    }
    else {

        Log "Port $port is not currently listening." "Yellow"

    }
}

# ---------------------------------------------------------
# VERIFY BACKEND HTTP
# ---------------------------------------------------------

Log "Testing backend http://localhost:8100/openapi.json ..." "Cyan"

try {

    $openapi = Invoke-WebRequest `
        -Uri "http://localhost:8100/openapi.json" `
        -UseBasicParsing `
        -TimeoutSec 10

    if ($openapi.StatusCode -eq 200) {

        Log "Backend OpenAPI: PASS" "Green"

    }
    else {

        throw "OpenAPI returned HTTP $($openapi.StatusCode)."
    }

}
catch {

    Log "Backend OpenAPI: FAIL" "Red"

    throw @"
The browser cannot authenticate because the reconciled backend is not reachable
on http://localhost:8100.

Actual error:
$($_.Exception.Message)
"@
}

# ---------------------------------------------------------
# VERIFY AUTH ROUTER EXISTS
# ---------------------------------------------------------

$api = $openapi.Content

if ($api -match "/api/v1/auth/login") {

    Log "Auth login route advertised: PASS" "Green"

}
else {

    throw "OpenAPI does not contain /api/v1/auth/login."
}

if ($api -match "/api/v1/auth/register") {

    Log "Auth register route advertised: PASS" "Green"

}
else {

    throw "OpenAPI does not contain /api/v1/auth/register."
}

# ---------------------------------------------------------
# TEST CORS
# ---------------------------------------------------------

Log "Testing browser CORS access..." "Cyan"

try {

    $corsResponse = Invoke-WebRequest `
        -Uri "http://localhost:8100/openapi.json" `
        -Method GET `
        -Headers @{
            Origin = "http://localhost:3100"
        } `
        -UseBasicParsing `
        -TimeoutSec 10

    $allowOrigin = $corsResponse.Headers["Access-Control-Allow-Origin"]

    if ($allowOrigin) {

        Log "CORS Access-Control-Allow-Origin: $allowOrigin" "Green"

    }
    else {

        Log "WARNING: Backend did not return Access-Control-Allow-Origin." "Yellow"
        Log "This may be the direct cause of 'Failed to fetch' in the browser." "Yellow"

    }

}
catch {

    Log "CORS test could not be completed: $($_.Exception.Message)" "Yellow"

}

# ---------------------------------------------------------
# CHECK AUTH LOGIN REACHABILITY
# ---------------------------------------------------------

Log "Testing auth endpoint reachability..." "Cyan"

try {

    $body = @{
        email = "diagnostic.invalid@example.com"
        password = "invalid"
    } | ConvertTo-Json

    $authResponse = Invoke-WebRequest `
        -Uri "http://localhost:8100/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing `
        -TimeoutSec 10 `
        -ErrorAction SilentlyContinue

    Log "Auth endpoint HTTP status: $($authResponse.StatusCode)" "Green"

}
catch {

    $status = $_.Exception.Response.StatusCode.value__

    if ($status) {

        Log "Auth endpoint responded HTTP $status." "Green"

    }
    else {

        throw "Auth endpoint is unreachable: $($_.Exception.Message)"
    }

}

# ---------------------------------------------------------
# RECREATE FRONTEND USING STANDALONE COMPOSE
# ---------------------------------------------------------

Log "Recreating ONLY reconciled frontend..." "Cyan"

$old = $ErrorActionPreference
$ErrorActionPreference = "Continue"

$restartOutput = & docker compose `
    -f $Compose `
    -p careeros-reconciled-ui `
    up -d `
    --build `
    --force-recreate `
    frontend 2>&1

$restartExit = $LASTEXITCODE

$ErrorActionPreference = $old

$restartOutput |
    Set-Content -LiteralPath (Join-Path $ResultDir "frontend-restart.txt") -Encoding UTF8

if ($restartExit -ne 0) {

    throw @"
Reconciled frontend restart FAILED.

See:
$(Join-Path $ResultDir "frontend-restart.txt")
"@
}

Log "Reconciled frontend restart: PASS" "Green"

# ---------------------------------------------------------
# WAIT FOR FRONTEND
# ---------------------------------------------------------

Log "Waiting for http://localhost:3100 ..." "Cyan"

$ready = $false

for ($i = 1; $i -le 30; $i++) {

    try {

        $response = Invoke-WebRequest `
            -Uri "http://localhost:3100/" `
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

if (-not $ready) {

    throw "Reconciled frontend did not become ready on port 3100."
}

Log "Frontend HTTP 200: PASS" "Green"

# ---------------------------------------------------------
# FINAL FRONTEND LOG
# ---------------------------------------------------------

$frontendLog = Join-Path $ResultDir "frontend.log"

& docker compose `
    -f $Compose `
    -p careeros-reconciled-ui `
    logs `
    frontend `
    --tail=250 |
    Set-Content -LiteralPath $frontendLog -Encoding UTF8

# ---------------------------------------------------------
# SHOW RESULT
# ---------------------------------------------------------

Log ""
Log "============================================" "Green"
Log "AUTH NETWORK DIAGNOSTIC COMPLETE" "Green"
Log "============================================" "Green"
Log "Report: $Report" "Cyan"
Log "Frontend log: $frontendLog" "Cyan"

Start-Process "http://localhost:3100"