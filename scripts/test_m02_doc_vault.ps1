# ============================================================
# M02-DOC-01 — Document Vault + Mobile Connectivity Tests
# ============================================================

Write-Host "🧪 M02-DOC-01 — Document Vault + Mobile Connectivity Tests" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n📋 1. Health Check:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing
    Write-Host "✅ HTTP $($response.StatusCode): $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Migration Status
Write-Host "`n📋 2. Migration Status:" -ForegroundColor Yellow
docker compose run --rm backend alembic current 2>&1 | Select-String "head"

# 3. Document Upload (Single)
Write-Host "`n📋 3. Document Upload (Single):" -ForegroundColor Yellow
Write-Host "   Manual test required: http://localhost:3000/documents" -ForegroundColor Cyan

# 4. Mobile Access Test
Write-Host "`n📋 4. Mobile Access Test:" -ForegroundColor Yellow
Write-Host "   Desktop: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Mobile: http://<YOUR-IP>:3000" -ForegroundColor Cyan
Write-Host "   Backend: http://<YOUR-IP>:8000/api/v1/health" -ForegroundColor Cyan

# 5. API Base URL
Write-Host "`n📋 5. API Base URL:" -ForegroundColor Yellow
$apiClient = Get-Content "frontend/src/lib/api/client.ts" | Select-String -Pattern "API_BASE_URL"
$apiClient | ForEach-Object { Write-Host "   $_" -ForegroundColor White }

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ M02-DOC-01 Tests Complete" -ForegroundColor Green
