$ErrorActionPreference = "Stop"

Set-Location "C:\Projects\CareerOS"

git fetch --all --prune

$Branch = (git branch --show-current).Trim()
$Local = (git rev-parse HEAD).Trim()
$OriginMain = (git rev-parse origin/main).Trim()
$Dirty = @(git status --porcelain).Count

Write-Host ""
Write-Host "=== CareerOS Repository Synchronization ==="
Write-Host "Repository: C:\Projects\CareerOS"
Write-Host "Branch: $Branch"
Write-Host "Local HEAD: $Local"
Write-Host "origin/main: $OriginMain"

if ($Dirty -gt 0) {
    Write-Host "Working tree: DIRTY"
    git status --short
    exit 2
}
else {
    Write-Host "Working tree: CLEAN"
}

$Ahead = [int](git rev-list --count origin/main..HEAD)
$Behind = [int](git rev-list --count HEAD..origin/main)

if ($Branch -eq "main" -and $Local -eq $OriginMain) {
    Write-Host "Synchronization: SYNCED"
    Write-Host "Result: SAFE TO REVIEW"
    exit 0
}

if ($Ahead -gt 0 -and $Behind -gt 0) {
    Write-Host "Synchronization: DIVERGED"
    exit 3
}

if ($Ahead -gt 0) {
    Write-Host "Synchronization: AHEAD"
    exit 4
}

if ($Behind -gt 0) {
    Write-Host "Synchronization: BEHIND"
    exit 5
}

Write-Host "Synchronization: DIFFERENT BRANCH OR BASELINE"
exit 6
