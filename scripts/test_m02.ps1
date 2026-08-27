# ============================================================
# M02 — Identity & Career Intake — Test Commands
# 
# Run these commands in order to test M02 functionality
# ============================================================

Write-Host "🧪 M02 — Identity & Career Intake — Test Suite" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# ============================================================
# 1. DATABASE MIGRATION
# ============================================================

Write-Host "`n📋 1. Database Migration" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Check current Alembic version
Write-Host "`n   Checking Alembic version..." -ForegroundColor Cyan
docker compose run --rm backend alembic current

# Run migration
Write-Host "`n   Running migration..." -ForegroundColor Cyan
docker compose run --rm backend alembic upgrade head

# Verify tables
Write-Host "`n   Verifying M02 tables..." -ForegroundColor Cyan
docker compose exec postgres psql -U careeros -d careeros -c "\dt" | findstr "external_identities\|candidate_profiles\|professional_experiences\|candidate_skills\|candidate_certifications\|candidate_educations\|documents\|extraction_results\|extraction_fields"

Write-Host "`n   ✅ Migration complete!" -ForegroundColor Green

# ============================================================
# 2. BACKEND SERVICES
# ============================================================

Write-Host "`n📋 2. Backend Services" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Check containers
Write-Host "`n   Checking container status..." -ForegroundColor Cyan
docker compose ps

# Health check
Write-Host "`n   Health check..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing
    Write-Host "✅ Health: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed" -ForegroundColor Red
}

# ============================================================
# 3. AUTHENTICATION
# ============================================================

Write-Host "`n📋 3. Authentication" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Test Registration
Write-Host "`n   Testing Registration..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$registerBody = @{
    email = "test_m02_$timestamp@careeros.com"
    password = "TestPassword123!"
    name = "M02 Test User"
    tenant_name = "M02-Test"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    Write-Host "✅ Registration: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
    $regData = $response.Content | ConvertFrom-Json
    $userId = $regData.id
    $tenantId = $regData.tenant_id
} catch {
    Write-Host "❌ Registration failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test Login
Write-Host "`n   Testing Login..." -ForegroundColor Cyan
$loginBody = @{
    email = "test_m02_$timestamp@careeros.com"
    password = "TestPassword123!"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
    Write-Host "✅ Login: HTTP $($response.StatusCode)" -ForegroundColor Green
    $loginData = $response.Content | ConvertFrom-Json
    $token = $loginData.access_token
    Write-Host "   Token: $($token.Substring(0, 30))..." -ForegroundColor White
} catch {
    Write-Host "❌ Login failed" -ForegroundColor Red
}

# Test Get Current User
Write-Host "`n   Testing Get Current User..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/me" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Get User: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Get User failed" -ForegroundColor Red
}

# ============================================================
# 4. CANDIDATE PROFILE
# ============================================================

Write-Host "`n📋 4. Candidate Profile" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Test Create Profile
Write-Host "`n   Testing Create Profile..." -ForegroundColor Cyan
$profileBody = @{
    user_id = $userId
    full_name = "M02 Test User"
    primary_email = "test_m02_$timestamp@careeros.com"
    title = "Senior Test Architect"
    location = "New York, NY"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/" -Method POST -Body $profileBody -ContentType "application/json" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Create Profile: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
    $profileData = $response.Content | ConvertFrom-Json
    $profileId = $profileData.id
} catch {
    Write-Host "❌ Create Profile failed" -ForegroundColor Red
}

# Test Get Profile
Write-Host "`n   Testing Get Profile..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Get Profile: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Profile failed" -ForegroundColor Red
}

# Test Update Profile
Write-Host "`n   Testing Update Profile..." -ForegroundColor Cyan
$updateBody = @{
    full_name = "M02 Test User Updated"
    title = "Principal Test Architect"
    summary = "Test profile summary"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/" -Method PUT -Body $updateBody -ContentType "application/json" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Update Profile: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Update Profile failed" -ForegroundColor Red
}

# Test Profile Completeness
Write-Host "`n   Testing Profile Completeness..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/completeness" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Profile Completeness: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Profile Completeness failed" -ForegroundColor Red
}

# ============================================================
# 5. PROFESSIONAL EXPERIENCE
# ============================================================

Write-Host "`n📋 5. Professional Experience" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Test Add Experience
Write-Host "`n   Testing Add Experience..." -ForegroundColor Cyan
$expBody = @{
    candidate_id = $profileId
    company = "Test Company Inc."
    title = "Senior Test Architect"
    location = "New York, NY"
    start_date = "2022-01-01"
    is_current = $true
    responsibilities = @("Designed test architecture", "Led test team")
    achievements = @("Achieved 100% test coverage")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/experiences" -Method POST -Body $expBody -ContentType "application/json" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Add Experience: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Add Experience failed" -ForegroundColor Red
}

# Test Get Experiences
Write-Host "`n   Testing Get Experiences..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/experiences" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Get Experiences: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Experiences failed" -ForegroundColor Red
}

# ============================================================
# 6. SKILLS
# ============================================================

Write-Host "`n📋 6. Skills" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Test Add Skill
Write-Host "`n   Testing Add Skill..." -ForegroundColor Cyan
$skillBody = @{
    candidate_id = $profileId
    name = "Kubernetes"
    category = "Technical"
    proficiency = "Advanced"
    years_experience = 5
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/skills" -Method POST -Body $skillBody -ContentType "application/json" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Add Skill: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Add Skill failed" -ForegroundColor Red
}

# Test Get Skills
Write-Host "`n   Testing Get Skills..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/profile/skills" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Get Skills: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Skills failed" -ForegroundColor Red
}

# ============================================================
# 7. DOCUMENTS
# ============================================================

Write-Host "`n📋 7. Documents" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Test Get Documents (empty initially)
Write-Host "`n   Testing Get Documents..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/documents/" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Get Documents: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Documents failed" -ForegroundColor Red
}

# Test Document Categories
Write-Host "`n   Testing Document Categories..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/documents/categories" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Document Categories: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Document Categories failed" -ForegroundColor Red
}

# ============================================================
# 8. EXTRACTION
# ============================================================

Write-Host "`n📋 8. Extraction" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Test Extraction Summary (empty initially)
Write-Host "`n   Testing Extraction Summary..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/extraction/summary" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing
    Write-Host "✅ Extraction Summary: HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Extraction Summary failed" -ForegroundColor Red
}

# ============================================================
# 9. FRONTEND ROUTES
# ============================================================

Write-Host "`n📋 9. Frontend Routes" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────────────────" -ForegroundColor Yellow

# Test Login Page
Write-Host "`n   Testing Login Page..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/login" -UseBasicParsing
    Write-Host "✅ Login Page: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Login Page failed" -ForegroundColor Red
}

# Test Register Page
Write-Host "`n   Testing Register Page..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/register" -UseBasicParsing
    Write-Host "✅ Register Page: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Register Page failed" -ForegroundColor Red
}

# Test Onboarding Page (requires auth - may redirect)
Write-Host "`n   Testing Onboarding Page..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/onboarding" -UseBasicParsing
    Write-Host "✅ Onboarding Page: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Onboarding Page failed" -ForegroundColor Red
}

# Test Profile Page (requires auth - may redirect)
Write-Host "`n   Testing Profile Page..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/profile" -UseBasicParsing
    Write-Host "✅ Profile Page: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Profile Page failed" -ForegroundColor Red
}

# Test Documents Page (requires auth - may redirect)
Write-Host "`n   Testing Documents Page..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/documents" -UseBasicParsing
    Write-Host "✅ Documents Page: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Documents Page failed" -ForegroundColor Red
}

# ============================================================
# 10. SUMMARY
# ============================================================

Write-Host "`n📋 10. Test Summary" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ M02 Test Suite Complete" -ForegroundColor Green
Write-Host "   - Database Migration: Check output above" -ForegroundColor Yellow
Write-Host "   - Authentication: Check output above" -ForegroundColor Yellow
Write-Host "   - Profile: Check output above" -ForegroundColor Yellow
Write-Host "   - Experiences: Check output above" -ForegroundColor Yellow
Write-Host "   - Skills: Check output above" -ForegroundColor Yellow
Write-Host "   - Documents: Check output above" -ForegroundColor Yellow
Write-Host "   - Extraction: Check output above" -ForegroundColor Yellow
Write-Host "   - Frontend Routes: Check output above" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
