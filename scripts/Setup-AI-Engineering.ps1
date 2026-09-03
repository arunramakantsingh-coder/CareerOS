param(
    [switch]$InstallOllama,
    [switch]$PullStarterModel
)

$ErrorActionPreference = 'Stop'

Write-Host "CareerOS AI Engineering Bootstrap" -ForegroundColor Cyan
Write-Host "This script installs/configures developer tooling only. It does not modify application source code." -ForegroundColor DarkGray

function Test-Command {
    param([Parameter(Mandatory=$true)][string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

Write-Host "`n[1/6] Checking Git..." -ForegroundColor Yellow
if (Test-Command git) {
    git --version
} else {
    Write-Warning "Git is not available in PATH. Install Git for Windows before continuing with repository work."
}

Write-Host "`n[2/6] Checking VS Code CLI..." -ForegroundColor Yellow
if (Test-Command code) {
    code --version | Select-Object -First 1

    Write-Host "Installing/updating Cline VS Code extension..." -ForegroundColor Yellow
    code --install-extension saoudrizwan.claude-dev --force
} else {
    Write-Warning "The 'code' command is not available in PATH. In VS Code, enable/install the shell command or install Cline manually from Extensions."
}

Write-Host "`n[3/6] Checking Docker..." -ForegroundColor Yellow
if (Test-Command docker) {
    docker --version
    try {
        docker info | Out-Null
        Write-Host "Docker engine reachable." -ForegroundColor Green
    } catch {
        Write-Warning "Docker CLI exists but the engine is not reachable. Start Docker Desktop before running containerized project services or OpenHands."
    }
} else {
    Write-Warning "Docker is not available in PATH. CareerOS may already depend on Docker for its runtime; install/start Docker Desktop separately if required."
}

Write-Host "`n[4/6] Checking Ollama..." -ForegroundColor Yellow
if (-not (Test-Command ollama) -and $InstallOllama) {
    Write-Host "Installing Ollama using the official Windows installer command..." -ForegroundColor Yellow
    irm https://ollama.com/install.ps1 | iex
}

if (Test-Command ollama) {
    ollama --version
} else {
    Write-Warning "Ollama is not installed. Cline can still be configured with another provider. Re-run with -InstallOllama if you want local models."
}

Write-Host "`n[5/6] Optional starter model..." -ForegroundColor Yellow
if ($PullStarterModel) {
    if (Test-Command ollama) {
        Write-Host "No model is pulled automatically by default because model choice must match RAM/VRAM."
        Write-Host "Choose a current coding/agent model appropriate to this machine, then run: ollama pull <model-name>" -ForegroundColor Cyan
    } else {
        Write-Warning "Cannot pull a model because Ollama is not installed."
    }
}

Write-Host "`n[6/6] Repository safety check..." -ForegroundColor Yellow
if (Test-Command git) {
    try {
        $root = git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Repository: $root" -ForegroundColor Green
            Write-Host "Branch: $(git branch --show-current)" -ForegroundColor Green
            git status --short
        } else {
            Write-Warning "Run this script from inside a Git working tree for repository-specific status checks."
        }
    } catch {
        Write-Warning "Could not read repository status."
    }
}

Write-Host "`nBootstrap complete." -ForegroundColor Green
Write-Host "Next: open the repository in VS Code, open Cline, configure Ollama (http://localhost:11434) or another provider, and start with .ai/CLINE_STARTER_PROMPT.md." -ForegroundColor Cyan
Write-Host "Do not enable broad auto-approval until the workflow has been validated on a disposable or dedicated task branch." -ForegroundColor Yellow
