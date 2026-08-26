[CmdletBinding()]
param(
    [switch]$NoBuild,
    [switch]$ShowLogs
)

$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Compose = Join-Path $Root 'docker-compose.yml'
$Results = Join-Path $Root 'test-results\V01-UI-AND-SMOKE'
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Run = Join-Path $Results $Stamp
New-Item -ItemType Directory -Force -Path $Run | Out-Null

function Step([string]$Text) { Write-Host "[$(Get-Date -Format HH:mm:ss)] $Text" -ForegroundColor Cyan }
function Pass([string]$Text) { Write-Host "PASS: $Text" -ForegroundColor Green }
function Fail([string]$Text) { Write-Host "FAIL: $Text" -ForegroundColor Red; $script:Failed = $true }
function Run-Docker([string[]]$Args) {
    & docker @Args 2>&1 | Tee-Object -FilePath (Join-Path $Run 'docker-command.log')
    return $LASTEXITCODE
}

$script:Failed = $false
Step 'CareerOS v0.1 consolidated build + smoke test'
Write-Host "Root: $Root"
Write-Host "Compose project: careeros-v01"
Write-Host "Results: $Run"

Step 'Checking Docker Desktop / Docker Engine'
& docker version 2>&1 | Tee-Object -FilePath (Join-Path $Run 'docker-version.txt') | Out-Null
if ($LASTEXITCODE -ne 0) { Fail 'Docker is not available. Start Docker Desktop and run this script again.'; exit 1 }
Pass 'Docker is available.'

Step 'Validating compose file'
Run-Docker @('compose','-p','careeros-v01','-f',$Compose,'config') | Out-Null
if ($LASTEXITCODE -eq 0) { Pass 'docker-compose.yml is valid.' } else { Fail 'docker-compose.yml validation failed.'; exit 1 }

Step 'Removing ONLY the v0.1 frontend/backend containers'
Run-Docker @('compose','-p','careeros-v01','-f',$Compose,'rm','-sfv','frontend','backend') | Out-Null

$FrontendNext = Join-Path $Root 'frontend\.next'
if (Test-Path $FrontendNext) { Remove-Item -Recurse -Force $FrontendNext -ErrorAction SilentlyContinue }
Pass 'Frontend .next cache cleared.'

if (-not $NoBuild) {
    Step 'Building v0.1 frontend and backend images'
    Run-Docker @('compose','-p','careeros-v01','-f',$Compose,'build','frontend','backend') | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail 'Docker image build failed.'; exit 1 }
    Pass 'Docker images built.'
}

Step 'Starting PostgreSQL, backend and frontend for v0.1 only'
Run-Docker @('compose','-p','careeros-v01','-f',$Compose,'up','-d','postgres','backend','frontend') | Out-Null
if ($LASTEXITCODE -ne 0) { Fail 'v0.1 services failed to start.'; exit 1 }

Step 'Waiting for backend health'
$backendOk = $false
for ($i=1; $i -le 30; $i++) {
    try {
        $r = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/health' -TimeoutSec 5
        ($r | ConvertTo-Json -Depth 10) | Set-Content (Join-Path $Run 'backend-health.json')
        if ($r.status -eq 'healthy') { $backendOk = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}
if ($backendOk) { Pass 'Backend health endpoint is healthy.' } else { Fail 'Backend health endpoint did not become healthy.' }

Step 'Checking frontend HTTP endpoint'
try {
    $fr = Invoke-WebRequest -Uri 'http://localhost:3000/' -UseBasicParsing -TimeoutSec 15
    "HTTP $($fr.StatusCode)" | Set-Content (Join-Path $Run 'frontend-http.txt')
    if ($fr.StatusCode -ge 200 -and $fr.StatusCode -lt 500) { Pass "Frontend responded with HTTP $($fr.StatusCode)." } else { Fail "Frontend returned HTTP $($fr.StatusCode)." }
} catch {
    Fail "Frontend did not respond: $($_.Exception.Message)"
}

Step 'Checking required UI routes'
$routes = @('/login','/onboarding','/','/career-vault','/personas','/jobs','/applications','/application-studio','/company-intelligence','/interviews','/live-interview','/global-mobility','/analytics','/settings')
$routeResults = @()
foreach ($route in $routes) {
    try {
        $x = Invoke-WebRequest -Uri ("http://localhost:3000" + $route) -UseBasicParsing -TimeoutSec 10
        $routeResults += [pscustomobject]@{ Route=$route; Status=$x.StatusCode; Result='PASS' }
    } catch {
        $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
        $routeResults += [pscustomobject]@{ Route=$route; Status=$status; Result='FAIL' }
        $script:Failed = $true
    }
}
$routeResults | Format-Table -AutoSize | Tee-Object -FilePath (Join-Path $Run 'ui-routes.txt')
if (($routeResults | Where-Object Result -eq 'FAIL').Count -eq 0) { Pass 'All required UI routes responded.' } else { Fail 'One or more required UI routes failed.' }

Step 'Saving service status'
Run-Docker @('compose','-p','careeros-v01','-f',$Compose,'ps') | Tee-Object -FilePath (Join-Path $Run 'compose-ps.txt') | Out-Null

if ($ShowLogs -or $script:Failed) {
    Step 'Collecting v0.1 service logs'
    Run-Docker @('compose','-p','careeros-v01','-f',$Compose,'logs','--tail','250','backend','frontend') | Tee-Object -FilePath (Join-Path $Run 'service-logs.txt') | Out-Null
}

Write-Host ''
if ($script:Failed) {
    Write-Host 'V0.1 RESULT: FAIL' -ForegroundColor Red
    Write-Host "Review: $Run" -ForegroundColor Yellow
    exit 1
}
Write-Host 'V0.1 RESULT: PASS' -ForegroundColor Green
Write-Host 'UI: http://localhost:3000' -ForegroundColor Cyan
Write-Host 'API: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host "Results: $Run" -ForegroundColor Cyan
exit 0
