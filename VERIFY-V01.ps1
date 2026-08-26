$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
Write-Host '=== CareerOS v0.1 Verification ===' -ForegroundColor Cyan
docker compose config | Out-Null
Write-Host '[PASS] Compose configuration valid.'
docker compose up -d --build
Write-Host '[INFO] Waiting for services...'
Start-Sleep -Seconds 8
Invoke-RestMethod http://localhost:8000/api/v1/health | ConvertTo-Json -Depth 5
docker compose exec backend alembic upgrade head
docker compose exec backend pytest -q
docker compose exec backend python -m compileall -q /app
Write-Host '[PASS] Backend checks completed.'
Write-Host 'Open http://localhost:3000 for the GUI and http://localhost:8000/docs for the API.' -ForegroundColor Green
