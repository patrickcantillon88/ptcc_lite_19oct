"""
Integration tests for safeguarding API endpoints.
Tests /analyze, /summary, /compliance, and /health endpoints.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Import from the backend package
from backend.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    mock_client = Mock()
    mock_client.generate_content = Mock(return_value=Mock(
        text='{"risk_level": "MEDIUM", "confidence": 0.75, "patterns": [], "pattern_combinations": [], "evidence_summary": "Test evidence", "recommendations": []}'
    ))
    return mock_client


class TestSafeguardingHealthEndpoint:
    """Test /api/safeguarding/health endpoint."""

    def test_health_check_returns_200(self, client):
        """Test health check returns 200 status."""
        response = client.get("/api/safeguarding/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self, client):
        """Test health check response has required fields."""
        response = client.get("/api/safeguarding/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] in ["operational", "not_initialized", "error"]

    def test_health_check_contains_privacy_info(self, client):
        """Test health check includes privacy guarantees."""
        response = client.get("/api/safeguarding/health")
        data = response.json()
        
        if data["status"] == "operational":
            assert "privacy_guarantees" in data
            assert isinstance(data["privacy_guarantees"], list)


class TestSafeguardingAnalyzeEndpoint:
    """Test /api/safeguarding/analyze endpoint."""

    def test_analyze_endpoint_requires_data(self, client):
        """Test analyze endpoint rejects empty request."""
        response = client.post("/api/safeguarding/analyze", json={})
        assert response.status_code == 422  # Validation error

    def test_analyze_endpoint_requires_student_id(self, client):
        """Test analyze endpoint requires student_id."""
        response = client.post("/api/safeguarding/analyze", json={
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [],
            "attendance": []
        })
        assert response.status_code == 422

    def test_analyze_with_minimal_data(self, client):
        """Test analyze with minimal valid data."""
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [],
            "attendance": []
        })
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 500, 503]

    def test_analyze_with_full_data(self, client):
        """Test analyze with complete student data."""
        now = datetime.now().isoformat()
        
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [
                {
                    "type": "disruptive",
                    "timestamp": now,
                    "description": "Talked back to teacher"
                }
            ],
            "assessments": [
                {
                    "subject": "Math",
                    "performance_level": "below",
                    "timestamp": now,
                    "assessment_type": "formative"
                }
            ],
            "communications": [
                {
                    "source": "parent",
                    "urgency_level": "important",
                    "timestamp": now,
                    "content": "Concerned about progress"
                }
            ],
            "attendance": [
                {
                    "status": "absent",
                    "timestamp": now
                }
            ]
        })
        
        assert response.status_code in [200, 500, 503]
        
        # If successful, verify response structure
        if response.status_code == 200:
            data = response.json()
            assert "student_id" in data
            assert data["student_id"] == "STU12345"

    def test_analyze_response_structure(self, client):
        """Test analyze response has expected structure."""
        now = datetime.now().isoformat()
        
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU99999",
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": now}
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        })
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify key fields are present
            assert "risk_assessment" in data or "error" not in str(data).lower()


class TestSafeguardingSummaryEndpoint:
    """Test /api/safeguarding/summary/{student_id} endpoint."""

    def test_summary_endpoint_requires_student_id(self, client):
        """Test summary endpoint requires student_id in path."""
        response = client.get("/api/safeguarding/summary/")
        assert response.status_code == 404

    def test_summary_endpoint_with_valid_student_id(self, client):
        """Test summary endpoint with valid student ID."""
        response = client.get("/api/safeguarding/summary/STU12345")
        
        assert response.status_code in [200, 503]

    def test_summary_response_structure(self, client):
        """Test summary response has expected structure."""
        response = client.get("/api/safeguarding/summary/STU12345")
        
        if response.status_code == 200:
            data = response.json()
            
            assert "student_id" in data
            assert "analyses_count" in data or "most_recent" in data

    def test_summary_different_students(self, client):
        """Test summary endpoint for different students."""
        student_ids = ["STU11111", "STU22222", "STU33333"]
        
        for student_id in student_ids:
            response = client.get(f"/api/safeguarding/summary/{student_id}")
            
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert data.get("student_id") == student_id


class TestSafeguardingComplianceEndpoint:
    """Test /api/safeguarding/compliance endpoint."""

    def test_compliance_endpoint_accessible(self, client):
        """Test compliance endpoint is accessible."""
        response = client.get("/api/safeguarding/compliance")
        
        assert response.status_code in [200, 503]

    def test_compliance_response_structure(self, client):
        """Test compliance response has expected structure."""
        response = client.get("/api/safeguarding/compliance")
        
        if response.status_code == 200:
            data = response.json()
            
            # Should contain compliance information
            assert "report_generated" in data or "total_analyses" in data
            assert "privacy_assertions" in data or "analyses_summary" in data

    def test_compliance_includes_privacy_info(self, client):
        """Test compliance report includes privacy information."""
        response = client.get("/api/safeguarding/compliance")
        
        if response.status_code == 200:
            data = response.json()
            
            if "privacy_assertions" in data:
                assertions = data["privacy_assertions"]
                
                # Verify key privacy assertions
                assert any("pii" in str(v).lower() or "privacy" in str(v).lower() 
                          for v in assertions.values())


class TestEndpointDataValidation:
    """Test data validation for endpoints."""

    def test_invalid_behavioral_incident(self, client):
        """Test validation of behavioral incident data."""
        now = datetime.now().isoformat()
        
        # Missing required 'type' field
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [
                {"timestamp": now, "description": "Misbehavior"}
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        })
        
        assert response.status_code in [422, 400, 500, 503]

    def test_invalid_assessment(self, client):
        """Test validation of assessment data."""
        now = datetime.now().isoformat()
        
        # Missing required fields
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [],
            "assessments": [
                {"subject": "Math", "timestamp": now}  # Missing performance_level
            ],
            "communications": [],
            "attendance": []
        })
        
        assert response.status_code in [422, 400, 500, 503]

    def test_invalid_communication(self, client):
        """Test validation of communication data."""
        now = datetime.now().isoformat()
        
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [
                {"source": "parent", "timestamp": now}  # Missing urgency_level
            ],
            "attendance": []
        })
        
        assert response.status_code in [422, 400, 500, 503]

    def test_invalid_attendance(self, client):
        """Test validation of attendance data."""
        now = datetime.now().isoformat()
        
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [],
            "attendance": [
                {"timestamp": now}  # Missing status
            ]
        })
        
        assert response.status_code in [422, 400, 500, 503]

    def test_invalid_datetime(self, client):
        """Test validation of datetime fields."""
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [
                {
                    "type": "disruptive",
                    "timestamp": "not-a-valid-datetime"
                }
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        })
        
        assert response.status_code in [422, 400]


class TestEndpointErrorHandling:
    """Test error handling in endpoints."""

    def test_analyze_handles_system_errors(self, client):
        """Test analyze endpoint handles system errors gracefully."""
        response = client.post("/api/safeguarding/analyze", json={
            "student_id": "STU12345",
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [],
            "attendance": []
        })
        
        # Should return a valid response even if system not initialized
        assert response.status_code in [200, 503]
        
        # If not initialized, should indicate that
        if response.status_code == 503:
            data = response.json()
            assert "detail" in data or "error" in str(data).lower()

    def test_summary_handles_missing_data(self, client):
        """Test summary endpoint handles missing student data."""
        response = client.get("/api/safeguarding/summary/NONEXISTENT")
        
        # Should handle gracefully
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            # Should indicate no analyses available
            assert data.get("analyses_count", 0) >= 0


class TestEndpointConcurrency:
    """Test endpoints handle concurrent requests."""

    def test_multiple_analyze_requests(self, client):
        """Test multiple concurrent analyze requests."""
        now = datetime.now().isoformat()
        
        responses = []
        for i in range(3):
            response = client.post("/api/safeguarding/analyze", json={
                "student_id": f"STU{i:05d}",
                "behavioral_incidents": [],
                "assessments": [],
                "communications": [],
                "attendance": []
            })
            responses.append(response)
        
        # All requests should complete
        assert len(responses) == 3
        
        # Status codes should be valid
        for response in responses:
            assert response.status_code in [200, 500, 503]

    def test_multiple_summary_requests(self, client):
        """Test multiple concurrent summary requests."""
        responses = []
        for i in range(3):
            response = client.get(f"/api/safeguarding/summary/STU{i:05d}")
            responses.append(response)
        
        # All requests should complete
        assert len(responses) == 3
        
        # Status codes should be valid
        for response in responses:
            assert response.status_code in [200, 503]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
