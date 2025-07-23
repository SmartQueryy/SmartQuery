

import requests
import json
import time
from typing import Dict, Any

# Backend API base URL
API_BASE_URL = "http://localhost:8000"

class TestProjectIntegration:
    """Test project integration between frontend API client and backend"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = API_BASE_URL
        self.headers = {"Content-Type": "application/json"}
        
    def test_backend_health_check(self):
        """Test that backend is running and healthy"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        # Check if we get a proper health response
        try:
            data = response.json()
            # Should have success field or be a health status
            assert "success" in data or "status" in data, f"Invalid health response: {data}"
        except json.JSONDecodeError:
            # If no JSON, at least check it responds
            assert response.status_code == 200
    
    def test_root_endpoint(self):
        """Test root endpoint returns expected format"""
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, f"Root response missing success: {data}"
        assert "data" in data, f"Root response missing data field: {data}"
        assert data["data"]["message"] == "SmartQuery API is running", f"Unexpected message: {data}"
        assert data["data"]["status"] == "healthy", f"Unexpected status: {data}"
    
    def test_project_endpoints_structure(self):
        """Test that project endpoints are available (even if auth required)"""
        # Test GET /projects
        response = requests.get(f"{self.base_url}/projects")
        # Should return 401 (auth required) or 200, not 404
        assert response.status_code in [200, 401, 403], f"Projects GET unexpected status: {response.status_code}"
        
        # Test POST /projects  
        response = requests.post(f"{self.base_url}/projects", json={})
        # Should return 401 (auth required) or 422 (validation error), not 404
        assert response.status_code in [401, 403, 422], f"Projects POST unexpected status: {response.status_code}"
    
    def test_auth_endpoints_structure(self):
        """Test that auth endpoints are available"""
        # Test GET /auth/me
        response = requests.get(f"{self.base_url}/auth/me")
        # Should return 401 (auth required), not 404
        assert response.status_code in [401, 403], f"Auth me unexpected status: {response.status_code}"
        
        # Test POST /auth/logout
        response = requests.post(f"{self.base_url}/auth/logout")
        # Should return 401 (auth required) or handle gracefully, not 404
        assert response.status_code in [200, 401, 403], f"Auth logout unexpected status: {response.status_code}"
    
    def test_api_response_format(self):
        """Test that API responses follow expected format"""
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200, f"API format test failed: {response.status_code}"
        
        data = response.json()
        # Check API response structure matches frontend expectations
        assert isinstance(data, dict), f"Response not a dict: {type(data)}"
        assert "success" in data, f"Response missing success field: {data}"
        assert isinstance(data["success"], bool), f"Success field not boolean: {data['success']}"
        
        if "data" in data:
            assert isinstance(data["data"], dict), f"Data field not a dict: {type(data['data'])}"
    
    def test_cors_headers(self):
        """Test that CORS is properly configured for frontend"""
        # Test preflight request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        
        response = requests.options(f"{self.base_url}/projects", headers=headers)
        
        # Should handle CORS or at least not fail completely
        # Accept 200 (CORS enabled) or 405 (method not allowed, but server responds)
        assert response.status_code in [200, 405], f"CORS test failed: {response.status_code}"
    
    def test_mock_auth_mode(self):
        """Test if mock auth mode is working for development"""
        # Try to access endpoints that might work in mock mode
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200, f"Health check failed in mock auth test: {response.status_code}"
        
        # Check if backend is configured for development
        try:
            # Some endpoints might be accessible in mock mode
            response = requests.get(f"{self.base_url}/projects", headers=self.headers)
            
            if response.status_code == 200:
                # Mock mode working - verify response structure
                data = response.json()
                assert "success" in data or "items" in data or isinstance(data, list), f"Invalid mock response: {data}"
            else:
                # Auth required - expected in production mode
                assert response.status_code in [401, 403], f"Unexpected auth status: {response.status_code}"
        except requests.exceptions.ConnectionError:
            raise Exception("Backend not accessible - ensure it's running on localhost:8000")
    
    def test_error_handling_format(self):
        """Test that error responses follow expected format"""
        # Test invalid endpoint
        response = requests.get(f"{self.base_url}/invalid-endpoint")
        assert response.status_code == 404, f"Invalid endpoint should return 404: {response.status_code}"
        
        # Test malformed request
        response = requests.post(
            f"{self.base_url}/projects",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return proper error status
        assert response.status_code in [400, 401, 403, 422], f"Malformed request unexpected status: {response.status_code}"
    
    def test_api_documentation_available(self):
        """Test that API documentation is accessible"""
        # Test OpenAPI docs
        response = requests.get(f"{self.base_url}/docs")
        assert response.status_code == 200, f"API docs not accessible: {response.status_code}"
        
        # Test OpenAPI spec
        response = requests.get(f"{self.base_url}/openapi.json")
        assert response.status_code == 200, f"OpenAPI spec not accessible: {response.status_code}"
        
        # Verify it's valid JSON
        data = response.json()
        assert "openapi" in data or "info" in data, f"Invalid OpenAPI spec: {data}"

def run_all_tests():
    """Run all integration tests"""
    test = TestProjectIntegration()
    test.setup_method()
    
    tests = [
        ("Backend Health Check", test.test_backend_health_check),
        ("Root Endpoint", test.test_root_endpoint),
        ("Project Endpoints Structure", test.test_project_endpoints_structure),
        ("Auth Endpoints Structure", test.test_auth_endpoints_structure),
        ("API Response Format", test.test_api_response_format),
        ("CORS Headers", test.test_cors_headers),
        ("Mock Auth Mode", test.test_mock_auth_mode),
        ("Error Handling Format", test.test_error_handling_format),
        ("API Documentation", test.test_api_documentation_available),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check backend is running on localhost:8000")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 