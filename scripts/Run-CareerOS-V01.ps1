# CareerOS v0.1 - One-Command Build / Fix / Test Runner
# Run this script FROM the CareerOS v0.1 project root.
# It performs safe, repeatable diagnostics and fixes without requiring
# the user to manually jump between multiple commands.

[CmdletBinding()]
param(
    [switch]$Rebuild,
    [switch]$CleanV01Volume,
    [switch]$RunFrontendBuild,
    [switch]$RunAuthSmokeTest
)

$ErrorActionPreference = 'Stop'
$Root = (Get-Location).Path
$Compose = Join-Path $Root 'docker-compose.yml'
$ReportDir = Join-Path $Root 'test-results'
$Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Report = Join-Path $ReportDir "CareerOS-V01-$Timestamp.txt"
$ComposeBackup = Join-Path $Root "docker-compose.yml.backup-$Timestamp"

New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null

function Log([string]$Message) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $Message"
    Write-Host $line
    Add-Content -LiteralPath $Report -Value $line
}

function Section([string]$Title) {
    Log ''
    Log ('=' * 78)
    Log $Title
    Log ('=' * 78)
}

function Run-Step {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][scriptblock]$Action,
        [switch]$ContinueOnError
    )

    Section $Name
    try {
        & $Action 2>&1 | Tee-Object -FilePath $Report -Append
        if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
            throw "Exit code $LASTEXITCODE"
        }
        Log "PASS: $Name"
        return $true
    }
    catch {
        Log "FAIL: $Name -- $($_.Exception.Message)"
        if (-not $ContinueOnError) { throw }
        return $false
    }
}

if ((Split-Path -Leaf $Root) -ne 'CareerOS-v0.1') {
    throw "Run this script from the CareerOS-v0.1 project root. Current root: $Root"
}

if (-not (Test-Path $Compose)) {
    throw "docker-compose.yml was not found at $Root"
}

Section 'CareerOS v0.1 One-Command Validation'
Log "Project root: $Root"
Log "Report: $Report"

Run-Step 'Repository structure check' {
    $required = @('.devcontainer','.vscode','backend','database','docker','docs','frontend','Lovable','nginx','scripts','tests','AGENTS.md','docker-compose.yml','README.md')
    foreach ($item in $required) {
        if (-not (Test-Path (Join-Path $Root $item))) { throw "Missing required path: $item" }
    }
    $files = Get-ChildItem $Root -Recurse -File -Force
    Log "File count: $($files.Count)"
    Log "Source size MB: $([math]::Round((($files | Measure-Object Length -Sum).Sum / 1MB),2))"
}

Run-Step 'Docker daemon check' {
    docker info | Out-Null
}

Run-Step 'Compose collision-safe fix' {
    Copy-Item -LiteralPath $Compose -Destination $ComposeBackup -Force
    $text = Get-Content -LiteralPath $Compose -Raw
    # Remove hard-coded container_name entries so Compose can generate project-scoped names.
    $fixed = [regex]::Replace($text, '(?m)^\s*container_name:\s*.*\r?\n', '')
    if ($fixed -ne $text) {
        Set-Content -LiteralPath $Compose -Value $fixed -Encoding UTF8
        Log "Removed hard-coded container_name values. Backup: $ComposeBackup"
    } else {
        Log 'No hard-coded container_name entries found.'
    }
}

Run-Step 'Compose configuration validation' {
    docker compose config | Tee-Object -FilePath $Report -Append | Out-Null
}

if ($CleanV01Volume) {
    Run-Step 'Optional v0.1 clean volume reset' {
        docker compose down --remove-orphans --volumes
    }
} else {
    Run-Step 'Stop any partial v0.1 stack' {
        docker compose down --remove-orphans
    }
}

$buildArgs = @('compose','up','-d')
if ($Rebuild) { $buildArgs += '--build' }
else { $buildArgs += '--build' }

Run-Step 'Build and start v0.1 stack' {
    & docker @buildArgs
}

Run-Step 'Container status' {
    docker compose ps
}

Run-Step 'PostgreSQL readiness' {
    $ok = $false
    for ($i=1; $i -le 18; $i++) {
        try {
            docker compose exec -T postgres pg_isready -U careeros -d careeros
            $ok = $true
            break
        } catch {
            Start-Sleep -Seconds 5
        }
    }
    if (-not $ok) { throw 'PostgreSQL did not become ready within 90 seconds.' }
}

Run-Step 'Alembic migrations' {
    docker compose exec -T backend alembic upgrade head
}

Run-Step 'Alembic current/head comparison' {
    Log 'Current migration:'
    docker compose exec -T backend alembic current
    Log 'Migration heads:'
    docker compose exec -T backend alembic heads
}

Run-Step 'Backend Python compilation' {
    docker compose exec -T backend python -m compileall -q /app
}

Run-Step 'Backend test suite' {
    docker compose exec -T backend pytest -q
}

Run-Step 'API root' {
    $r = Invoke-RestMethod 'http://localhost:8000/'
    $r | ConvertTo-Json -Depth 10 | Tee-Object -FilePath $Report -Append
}

Run-Step 'API health' {
    $r = Invoke-RestMethod 'http://localhost:8000/api/v1/health'
    $r | ConvertTo-Json -Depth 10 | Tee-Object -FilePath $Report -Append
}

Run-Step 'OpenAPI availability' {
    $r = Invoke-WebRequest 'http://localhost:8000/openapi.json' -UseBasicParsing
    if ($r.StatusCode -ne 200) { throw "OpenAPI returned $($r.StatusCode)" }
    Log "OpenAPI status: $($r.StatusCode)"
}

Run-Step 'Frontend HTTP availability' {
    $r = Invoke-WebRequest 'http://localhost:3000' -UseBasicParsing
    if ($r.StatusCode -lt 200 -or $r.StatusCode -ge 400) { throw "Frontend returned $($r.StatusCode)" }
    Log "Frontend status: $($r.StatusCode)"
}

if ($RunFrontendBuild) {
    Run-Step 'Frontend production build' {
        docker compose exec -T frontend npm run build
    } -ContinueOnError
}

if ($RunAuthSmokeTest) {
    Run-Step 'Authentication smoke test' {
        $email = "careeros.test.$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())@example.invalid"
        $password = 'CareerOS-Test-2026!'
        $body = @{
            email = $email
            password = $password
            name = 'CareerOS Automated Test User'
            tenant_name = 'CareerOS Automated Test Tenant'
        } | ConvertTo-Json

        $reg = Invoke-RestMethod 'http://localhost:8000/api/v1/auth/register' -Method Post -ContentType 'application/json' -Body $body
        Log ('Register response: ' + ($reg | ConvertTo-Json -Depth 10 -Compress))

        $loginBody = @{ email = $email; password = $password } | ConvertTo-Json
        $login = Invoke-RestMethod 'http://localhost:8000/api/v1/auth/login' -Method Post -ContentType 'application/json' -Body $loginBody
        if (-not $login.access_token) { throw 'Login response did not contain access_token.' }

        $headers = @{ Authorization = "Bearer $($login.access_token)" }
        $me = Invoke-RestMethod 'http://localhost:8000/api/v1/auth/me' -Headers $headers
        Log ('/auth/me response: ' + ($me | ConvertTo-Json -Depth 10 -Compress))
    } -ContinueOnError
}

Section 'Database snapshot'
try {
    docker compose exec -T postgres psql -U careeros -d careeros -c '\dt' 2>&1 | Tee-Object -FilePath $Report -Append
    docker compose exec -T postgres psql -U careeros -d careeros -c 'SELECT version_num FROM alembic_version;' 2>&1 | Tee-Object -FilePath $Report -Append
} catch {
    Log "WARN: database snapshot failed: $($_.Exception.Message)"
}

Section 'Recent container logs'
docker compose logs --no-color --tail=60 2>&1 | Tee-Object -FilePath $Report -Append

Section 'Security / dependency findings'
try {
    $pkg = Get-Content (Join-Path $Root 'frontend/package.json') -Raw | ConvertFrom-Json
    Log "Next.js version: $($pkg.dependencies.next)"
} catch {
    Log "WARN: unable to read frontend/package.json"
}
Log 'Frontend npm audit is intentionally REPORT-ONLY; this script does not blindly run npm audit fix --force.'

Section 'Final result'
Log "Detailed report: $Report"
Log "Compose backup: $ComposeBackup"
Log "Open GUI: http://localhost:3000"
Log "Open API docs: http://localhost:8000/docs"
Log "If any PASS/FAIL above is unexpected, send this entire report file to ChatGPT."
Write-Host ''
Write-Host 'CAREEROS v0.1 TEST RUN COMPLETE' -ForegroundColor Cyan
Write-Host "REPORT: $Report" -ForegroundColor Green
