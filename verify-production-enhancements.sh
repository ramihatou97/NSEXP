#!/bin/bash
# Production Enhancement Verification Script
# Verifies all production enhancements are in place

set -e

echo "=============================================="
echo "🔍 NSEXP Production Enhancement Verification"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $2 - MISSING${NC}"
        ((FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $2 - MISSING${NC}"
        ((FAILED++))
    fi
}

check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✅ $3${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  $3 - NOT FOUND${NC}"
        ((WARNINGS++))
    fi
}

echo "📦 Phase 1: Testing Infrastructure"
echo "-----------------------------------"
check_dir "backend/tests/unit" "Unit tests directory"
check_dir "backend/tests/integration" "Integration tests directory"
check_dir "backend/tests/e2e" "E2E tests directory"
check_file "backend/tests/unit/test_ai_service.py" "AI service tests"
check_file "backend/tests/unit/test_chapter_service.py" "Chapter service tests"
check_file "backend/tests/e2e/test_complete_workflows.py" "E2E workflow tests"
check_file "frontend/jest.config.js" "Jest configuration"
check_file "frontend/jest.setup.js" "Jest setup"
check_file "frontend/__tests__/services/api.test.ts" "Frontend API tests"
check_content "backend/pytest.ini" "e2e" "E2E marker in pytest.ini"
echo ""

echo "🔄 Phase 2: CI/CD Pipeline"
echo "-----------------------------------"
check_file ".github/workflows/ci.yml" "CI/CD workflow"
check_content ".github/workflows/ci.yml" "backend-tests" "Backend tests job"
check_content ".github/workflows/ci.yml" "frontend-tests" "Frontend tests job"
check_content ".github/workflows/ci.yml" "docker-build" "Docker build job"
check_content ".github/workflows/ci.yml" "integration-tests" "Integration tests job"
check_content ".github/workflows/ci.yml" "security-scan" "Security scanning job"
echo ""

echo "📦 Phase 3: Dependencies"
echo "-----------------------------------"
check_content "backend/requirements_simplified.txt" "uvicorn\[standard\]==0.25.0" "uvicorn 0.25.0"
check_content "backend/requirements_simplified.txt" "openai>=1.6.0" "openai 1.6.0+"
check_content "backend/requirements_simplified.txt" "anthropic>=0.8.0" "anthropic 0.8.0+"
check_content "backend/requirements_simplified.txt" "httpx==0.26.0" "httpx 0.26.0"
check_content "backend/requirements_simplified.txt" "pytest-cov" "pytest-cov"
check_content "frontend/package.json" '"next": "14.1.0"' "Next.js 14.1.0"
check_content "frontend/package.json" '"react": "18.3.1"' "React 18.3.1"
check_content "frontend/package.json" '"axios": "\^1.6.5"' "axios 1.6.5"
echo ""

echo "🗑️  Phase 4: Bundle Optimization"
echo "-----------------------------------"
if ! grep -q "cornerstone-core" frontend/package.json 2>/dev/null; then
    echo -e "${GREEN}✅ cornerstone-core removed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ cornerstone-core still present${NC}"
    ((FAILED++))
fi

if ! grep -q "dicom-parser" frontend/package.json 2>/dev/null; then
    echo -e "${GREEN}✅ dicom-parser removed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ dicom-parser still present${NC}"
    ((FAILED++))
fi

if ! grep -q '"three":' frontend/package.json 2>/dev/null; then
    echo -e "${GREEN}✅ three.js removed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ three.js still present${NC}"
    ((FAILED++))
fi
echo ""

echo "🔒 Phase 5: Security"
echo "-----------------------------------"
check_file "backend/core/exceptions.py" "Custom exceptions"
check_file "backend/middleware/security_middleware.py" "Security middleware"
check_content "backend/core/exceptions.py" "NSEXPException" "NSEXPException class"
check_content "backend/core/exceptions.py" "ChapterNotFoundError" "ChapterNotFoundError"
check_content "backend/middleware/security_middleware.py" "SecurityHeadersMiddleware" "Security headers"
check_content "backend/middleware/security_middleware.py" "RateLimitMiddleware" "Rate limiting"
check_content "backend/middleware/security_middleware.py" "InputSanitizationMiddleware" "Input sanitization"
check_content "backend/main_simplified.py" "SecurityHeadersMiddleware" "Security integrated"
check_content "backend/main_simplified.py" "RateLimitMiddleware" "Rate limit integrated"
echo ""

echo "📊 Phase 6: Performance Monitoring"
echo "-----------------------------------"
check_file "backend/middleware/metrics_middleware.py" "Metrics middleware"
check_content "backend/middleware/metrics_middleware.py" "PerformanceMetrics" "Performance metrics class"
check_content "backend/middleware/metrics_middleware.py" "PerformanceMiddleware" "Performance middleware"
check_content "backend/middleware/metrics_middleware.py" "HealthCheckMiddleware" "Health check middleware"
check_content "backend/main_simplified.py" "PerformanceMiddleware" "Performance integrated"
echo ""

echo "💾 Phase 7: Database Optimization"
echo "-----------------------------------"
check_content "backend/models/database_simplified.py" "idx_chapter_status" "Status index"
check_content "backend/models/database_simplified.py" "idx_chapter_created_at" "Created_at index"
check_content "backend/models/database_simplified.py" "idx_chapter_updated_at" "Updated_at index"
check_content "backend/models/database_simplified.py" "idx_chapter_evidence_level" "Evidence level index"
echo ""

echo "🛠️  Phase 8: Developer Tools"
echo "-----------------------------------"
check_file ".pre-commit-config.yaml" "Pre-commit hooks"
check_file "backend/pyproject.toml" "Python tool config"
check_content ".pre-commit-config.yaml" "black" "Black formatter hook"
check_content ".pre-commit-config.yaml" "isort" "isort hook"
check_content ".pre-commit-config.yaml" "flake8" "flake8 hook"
check_content ".pre-commit-config.yaml" "prettier" "Prettier hook"
check_content "backend/pyproject.toml" "\\[tool.black\\]" "Black configuration"
check_content "backend/pyproject.toml" "\\[tool.isort\\]" "isort configuration"
check_content "backend/pyproject.toml" "\\[tool.pytest.ini_options\\]" "Pytest configuration"
echo ""

echo "📚 Phase 9: Documentation"
echo "-----------------------------------"
check_file "PRODUCTION_DEPLOYMENT.md" "Production deployment guide"
check_file "PRODUCTION_ENHANCEMENTS_COMPLETE.md" "Enhancement completion summary"
check_content "README.md" "2.1.0-production-ready" "README updated with version"
check_content "README.md" "Testing & Quality Assurance" "Testing section in README"
check_content "README.md" "CI/CD Pipeline" "CI/CD section in README"
check_content "PRODUCTION_DEPLOYMENT.md" "Quick Start" "Quick start guide"
check_content "PRODUCTION_DEPLOYMENT.md" "Security Configuration" "Security guide"
check_content "PRODUCTION_DEPLOYMENT.md" "Monitoring" "Monitoring guide"
echo ""

echo "🎯 Phase 10: Integration"
echo "-----------------------------------"
check_content "backend/main_simplified.py" "from core.exceptions import NSEXPException" "Exception import"
check_content "backend/main_simplified.py" "exception_handler(NSEXPException)" "Exception handler"
check_content "backend/main_simplified.py" "2.1.0-production-ready" "Version updated"
echo ""

echo "=============================================="
echo "📊 Verification Summary"
echo "=============================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
fi
echo ""

TOTAL=$((PASSED + WARNINGS + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo "Overall: $PASSED/$TOTAL checks passed ($PERCENTAGE%)"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical checks passed! System is production-ready.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Review the output above.${NC}"
    exit 1
fi
