"""
System Functionality Test Script
Tests core functionality of the simplified neurosurgical knowledge system
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))


async def test_database_models():
    """Test database models can be imported"""
    print("Testing database models...")
    try:
        from models.database_simplified import (
            Chapter, Reference, Citation, SurgicalProcedure,
            UserPreferences, BehavioralPattern, QASession
        )
        print("[OK] Database models imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Database models error: {e}")
        return False


async def test_services():
    """Test service modules can be imported"""
    print("\nTesting service modules...")
    try:
        from services.ai_service import AIService
        from services.pdf_service import PDFProcessor
        from services.synthesis_service import SynthesisService
        from services.qa_service import QAService

        print("[OK] Service modules imported successfully")

        # Test AI service instantiation
        ai_service = AIService()
        print("[OK] AI Service instantiated")

        # Test PDF processor instantiation
        pdf_processor = PDFProcessor()
        print("[OK] PDF Processor instantiated")

        # Test synthesis service instantiation
        synthesis_service = SynthesisService()
        print("[OK] Synthesis Service instantiated")

        # Test QA service instantiation
        qa_service = QAService()
        print("[OK] QA Service instantiated")

        return True
    except Exception as e:
        print(f"[FAIL] Service modules error: {e}")
        return False


async def test_main_app():
    """Test main FastAPI app can be imported"""
    print("\nTesting main application...")
    try:
        from main_simplified import app
        print("[OK] Main FastAPI app imported successfully")
        print(f"[OK] App title: {app.title}")

        # Check routes
        routes = [route.path for route in app.routes]
        print(f"[OK] Total routes: {len(routes)}")

        # Check key endpoints
        key_endpoints = [
            "/api/v1/chapters",
            "/api/v1/references",
            "/api/v1/synthesis/generate",
            "/api/v1/qa/ask"
        ]

        for endpoint in key_endpoints:
            if any(endpoint in route for route in routes):
                print(f"[OK] Endpoint found: {endpoint}")
            else:
                print(f"[WARN] Endpoint not found: {endpoint}")

        return True
    except Exception as e:
        print(f"[FAIL] Main app error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_config():
    """Test configuration can be loaded"""
    print("\nTesting configuration...")
    try:
        from config.settings_simplified import Settings
        settings = Settings()
        print(f"[OK] Settings loaded: {settings.APP_NAME}")
        print(f"[OK] Version: {settings.VERSION}")
        print(f"[OK] Debug mode: {settings.DEBUG}")
        return True
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        return False


async def test_ai_mock_response():
    """Test AI service mock responses"""
    print("\nTesting AI service mock response...")
    try:
        from services.ai_service import AIService

        ai_service = AIService()
        result = await ai_service.generate_with_gpt4(
            "Test prompt for neurosurgical synthesis"
        )

        print(f"[OK] AI response received")
        print(f"[OK] Model: {result['model']}")
        print(f"[OK] Response length: {len(result['text'])} chars")

        return True
    except Exception as e:
        print(f"[FAIL] AI service test error: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Neurosurgical Knowledge System - Functionality Test")
    print("=" * 60)

    results = []

    # Run tests
    results.append(await test_database_models())
    results.append(await test_services())
    results.append(await test_config())
    results.append(await test_main_app())
    results.append(await test_ai_mock_response())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests

    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")

    if failed_tests == 0:
        print("\nAll tests passed! System is ready.")
    else:
        print(f"\n{failed_tests} test(s) failed. Review errors above.")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())