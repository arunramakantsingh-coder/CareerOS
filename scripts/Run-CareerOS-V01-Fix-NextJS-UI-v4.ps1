#requires -Version 5.1
$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\Projects\CareerOS-v0.1-Personal-Job-Interview-Copilot-FINAL\CareerOS-v0.1"
Set-Location $ProjectRoot

$ResultsRoot = Join-Path $ProjectRoot ("test-results\UI-FIX-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Path $ResultsRoot -Force | Out-Null
$Report = Join-Path $ResultsRoot "UI-FIX-REPORT.txt"

function Log {
    param([string]$Text, [string]$Color = "White")
    $line = "$(Get-Date -Format 'HH:mm:ss') $Text"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $Report -Value $line
}

@"
CareerOS v0.1 - Next.js UI Fix v4
Project: $ProjectRoot
Started: $(Get-Date)
"@ | Set-Content -LiteralPath $Report -Encoding UTF8

$Compose = Join-Path $ProjectRoot "docker-compose.yml"
$Backup = Join-Path $ResultsRoot "docker-compose.yml.before-ui-fix-v4"
Copy-Item $Compose $Backup -Force

$txt = Get-Content $Compose -Raw

if ($txt -match '(?m)^\s*-\s*/app/\.next\s*$') {
    $txt = ($txt -split "`r?`n" | Where-Object { $_ -notmatch '^\s*-\s*/app/\.next\s*$' }) -join [Environment]::NewLine
    Set-Content $Compose $txt -Encoding UTF8
    Log "Removed /app/.next volume." "Green"
}

$txt = Get-Content $Compose -Raw
$txt = $txt.Replace('command: npm run dev','command: sh -c "rm -rf /app/.next && npm run dev"')
Set-Content $Compose $txt -Encoding UTF8
Log "Configured clean Next.js startup." "Green"

# Docker commands are executed through cmd.exe and output is written to files,
# avoiding PowerShell NativeCommandError on Docker progress output.
function Invoke-DockerCmd {
    param(
        [string]$Args,
        [string]$LogPath
    )

    $cmdFile = Join-Path $ResultsRoot "docker-command.cmd"
    $safeArgs = $Args.Replace('"','\"')
    @"
@echo off
docker $Args
exit /b %ERRORLEVEL%
"@ | Set-Content $cmdFile -Encoding ASCII

    $out = & cmd.exe /c "`"$cmdFile`"" 2>&1
    $out | Tee-Object -FilePath $LogPath -Append | ForEach-Object { Add-Content -LiteralPath $Report -Value $_ }
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        throw "Docker command failed with exit code $exitCode}: docker $Args"
    }
}

Log "Validating Compose..." "Cyan"
Invoke-DockerCmd "compose config" (Join-Path $ResultsRoot "compose-config.log")
Log "Compose validation PASS." "Green"

Log "Stopping frontend..." "Cyan"
try {
    Invoke-DockerCmd "compose stop frontend" (Join-Path $ResultsRoot "frontend-stop.log")
} catch {
    Log "Frontend stop returned non-zero; continuing to removal." "Yellow"
}

Log "Removing frontend container/anonymous volumes..." "Cyan"
try {
    Invoke-DockerCmd "compose rm -sfv frontend" (Join-Path $ResultsRoot "frontend-rm.log")
} catch {
    Log "Frontend removal returned non-zero; continuing." "Yellow"
}

$hostNext = Join-Path $ProjectRoot "frontend\.next"
if (Test-Path $hostNext) {
    Remove-Item $hostNext -Recurse -Force
    Log "Removed frontend\.next." "Green"
}

Log "Building frontend image..." "Cyan"
Invoke-DockerCmd "compose build frontend" (Join-Path $ResultsRoot "frontend-build.log")
Log "Frontend build PASS." "Green"

Log "Starting frontend..." "Cyan"
Invoke-DockerCmd "compose up -d --force-recreate frontend" (Join-Path $ResultsRoot "frontend-start.log")
Log "Frontend container start command PASS." "Green"

Start-Sleep -Seconds 6

Log "Frontend status:" "Cyan"
$status = & cmd.exe /c "docker compose ps frontend" 2>&1
$status | Tee-Object -FilePath (Join-Path $ResultsRoot "frontend-status.log") | ForEach-Object {
    Add-Content -LiteralPath $Report -Value $_
    Write-Host $_
}

Log "Waiting for UI..." "Cyan"
$ready = $false
for ($i=1; $i -le 20; $i++) {
    try {
        $r = Invoke-WebRequest "http://localhost:3000/" -UseBasicParsing -TimeoutSec 8
        if ($r.StatusCode -eq 200) { $ready=$true; break }
    } catch {
        Start-Sleep 3
    }
}

if ($ready) { Log "[PASS] / -> HTTP 200" "Green" }
else { Log "[FAIL] / did not return HTTP 200" "Red" }

$routes = @(
"/","/login","/onboarding","/career-vault","/personas","/jobs",
"/applications","/application-studio","/company-intelligence",
"/interviews","/live-interview","/global-mobility","/analytics","/settings"
)

$fail = 0
foreach ($route in $routes) {
    try {
        $r = Invoke-WebRequest ("http://localhost:3000" + $route) -UseBasicParsing -TimeoutSec 15
        if ($r.StatusCode -eq 200) {
            Log "[PASS] $route -> HTTP 200" "Green"
        } else {
            Log "[FAIL] $route -> HTTP $($r.StatusCode)" "Red"
            $fail++
        }
    } catch {
        Log "[FAIL] $route -> $($_.Exception.Message)" "Red"
        $fail++
    }
}

$finalLog = Join-Path $ResultsRoot "frontend-final.log"
& cmd.exe /c "docker compose logs frontend --tail=300" 2>&1 |
    Set-Content -LiteralPath $finalLog -Encoding UTF8

if ($ready -and $fail -eq 0) {
    Log "=== UI STARTUP + ALL ROUTES PASS ===" "Green"
    Log "Open http://localhost:3000 for visual UI inspection." "Green"
    exit 0
}

Log "=== UI STILL FAILING ===" "Red"
Log "Report: $Report" "Yellow"
Log "Frontend log: $finalLog" "Yellow"
exit 1

