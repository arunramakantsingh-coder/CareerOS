$ErrorActionPreference = "Continue"

function Write-Step {
    param([string]$Text)
    Write-Host ""
    Write-Host $Text -ForegroundColor Cyan
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " CareerOS v0.1 - Docker Engine Check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Step "[1] Project root"

$ProjectRoot = (Get-Location).Path

Write-Host $ProjectRoot -ForegroundColor White

if (-not (Test-Path ".\docker-compose.yml")) {
    Write-Host "WARNING: docker-compose.yml was not found in this directory." -ForegroundColor Yellow
}
else {
    Write-Host "docker-compose.yml: FOUND" -ForegroundColor Green
}

Write-Step "[2] Docker CLI"

$DockerCommand = Get-Command docker.exe -ErrorAction SilentlyContinue

if ($null -eq $DockerCommand) {
    Write-Host "FAIL: docker.exe is not available." -ForegroundColor Red
    Write-Host "PowerShell will remain open. No exit command is used." -ForegroundColor Yellow
    return
}

Write-Host "Docker executable: $($DockerCommand.Source)" -ForegroundColor Green
docker --version

Write-Step "[3] Docker Desktop process"

$DockerDesktop = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue

if ($null -eq $DockerDesktop) {

    Write-Host "Docker Desktop process is not running." -ForegroundColor Yellow

    $DesktopPath = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"

    if (Test-Path $DesktopPath) {

        Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow

        Start-Process -FilePath $DesktopPath

        Write-Host "Docker Desktop launch requested." -ForegroundColor Green
    }
    else {

        Write-Host "Docker Desktop executable was not found at:" -ForegroundColor Red
        Write-Host $DesktopPath -ForegroundColor Red

        Write-Host ""
        Write-Host "PowerShell will remain open." -ForegroundColor Yellow
        return
    }
}
else {
    Write-Host "Docker Desktop process is running." -ForegroundColor Green
}

Write-Step "[4] Waiting for Docker Linux Engine"

$DockerReady = $false

for ($i = 1; $i -le 60; $i++) {

    $DockerInfo = docker info 2>&1

    if ($LASTEXITCODE -eq 0) {

        $DockerReady = $true

        Write-Host ""
        Write-Host "Docker Engine is READY." -ForegroundColor Green
        break
    }

    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
}

Write-Host ""

if (-not $DockerReady) {

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host " DOCKER ENGINE: FAIL" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red

    Write-Host ""
    Write-Host "Docker Desktop process:" -ForegroundColor Yellow

    Get-Process "Docker Desktop" -ErrorAction SilentlyContinue |
        Select-Object Id, ProcessName, StartTime

    Write-Host ""
    Write-Host "Docker contexts:" -ForegroundColor Yellow
    docker context ls

    Write-Host ""
    Write-Host "Docker API result:" -ForegroundColor Yellow
    docker info

    Write-Host ""
    Write-Host "IMPORTANT:" -ForegroundColor Yellow
    Write-Host "The Docker Linux engine is not available yet." -ForegroundColor Yellow
    Write-Host "PowerShell will remain open." -ForegroundColor Yellow

    return
}

Write-Step "[5] Docker version"

docker version

Write-Step "[6] Docker Compose"

docker compose version

Write-Step "[7] Docker context"

docker context ls

Write-Step "[8] Docker Engine summary"

docker info --format "Server={{.ServerVersion}} | Containers={{.Containers}} | Images={{.Images}} | OS={{.OperatingSystem}}"

Write-Step "[9] CareerOS Compose validation"

if (Test-Path ".\docker-compose.yml") {

    docker compose config

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "CareerOS Compose configuration: PASS" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "CareerOS Compose configuration: FAIL" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " DOCKER CHECK COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "PowerShell terminal was NOT terminated." -ForegroundColor Green
Write-Host ""
