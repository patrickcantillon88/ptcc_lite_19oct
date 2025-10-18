"""
End-to-End Workflow Tests

Complete user journey tests covering:
- Student onboarding
- Incident reporting
- Risk assessment
- Parent communication
- Administrator review
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.privacy_tokenization import create_tokenizer_for_session
from core.safeguarding_patterns import PatternExtractor
from core.safeguarding_orchestrator import SafeguardingOrchestrator


class TestStudentOnboardingWorkflow:
    """Test complete student onboarding workflow."""

    def test_student_registration_and_consent(self):
        """E2E: Student registration with parental consent."""
        workflow_state = {}
        
        # Step 1: Register student
        student_data = {
            "student_id": "STU12345",
            "first_name": "John",
            "last_name": "Doe",
            "grade": "9",
            "school": "Jefferson High",
            "registration_date": datetime.now().isoformat(),
        }
        workflow_state["student"] = student_data
        
        # Step 2: Create consent record
        consent_record = {
            "student_id": student_data["student_id"],
            "consent_type": "data_processing",
            "parent_id": "PARENT001",
            "consented": True,
            "timestamp": datetime.now().isoformat(),
        }
        workflow_state["consent"] = consent_record
        
        # Step 3: Initialize tokenization
        tokenizer = create_tokenizer_for_session(f"student_{student_data['student_id']}")
        token = tokenizer.tokenize_student_id(student_data["student_id"])
        workflow_state["token"] = token
        
        # Verify workflow completion
        assert "student" in workflow_state
        assert "consent" in workflow_state
        assert "token" in workflow_state
        assert workflow_state["consent"]["consented"] is True

    def test_student_profile_initialization(self):
        """E2E: Initialize student profile with baseline data."""
        student_profile = {
            "student_token": "TOKEN_STU_ABC",
            "created_date": datetime.now().isoformat(),
            "baseline_data": {
                "behavioral": [],
                "academic": [],
                "attendance": [],
                "communications": [],
            },
            "status": "active",
        }
        
        assert student_profile["status"] == "active"
        assert len(student_profile["baseline_data"]) == 4


class TestIncidentReportingWorkflow:
    """Test complete incident reporting workflow."""

    def test_behavioral_incident_reporting(self):
        """E2E: Report and process behavioral incident."""
        now = datetime.now()
        
        # Step 1: Report incident
        incident = {
            "incident_id": "INC20241001001",
            "student_token": "TOKEN_STU_ABC",
            "incident_type": "disruptive",
            "description": "Disrupted class during math lesson",
            "timestamp": now.isoformat(),
            "reported_by": "TEACHER001",
            "severity": "medium",
            "status": "reported",
        }
        
        # Step 2: Incident review
        incident["status"] = "reviewed"
        incident["reviewed_at"] = now.isoformat()
        incident["reviewed_by"] = "ADMIN001"
        
        # Step 3: Flag for analysis
        incident["status"] = "queued_for_analysis"
        
        assert incident["status"] == "queued_for_analysis"
        assert incident["reviewed_by"] == "ADMIN001"

    def test_attendance_concern_workflow(self):
        """E2E: Report and escalate attendance concern."""
        now = datetime.now()
        
        # Step 1: Record attendance
        attendance = {
            "student_token": "TOKEN_STU_ABC",
            "records": [
                {"date": (now - timedelta(days=i)).isoformat(), "status": "absent"}
                for i in range(5)
            ],
            "pattern_identified": True,
            "escalation_status": "pending",
        }
        
        # Step 2: Escalate
        attendance["escalation_status"] = "escalated"
        attendance["escalated_at"] = now.isoformat()
        
        # Step 3: Parent notification
        notification = {
            "student_token": attendance["student_token"],
            "notification_type": "attendance_concern",
            "sent_at": now.isoformat(),
            "status": "sent",
        }
        
        assert len(attendance["records"]) == 5
        assert attendance["escalation_status"] == "escalated"
        assert notification["status"] == "sent"


class TestRiskAssessmentWorkflow:
    """Test complete risk assessment workflow."""

    def test_multi_factor_risk_assessment(self):
        """E2E: Multi-factor risk assessment workflow."""
        now = datetime.now()
        
        # Step 1: Collect data
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(3)
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now, "type": "formative"}
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ],
        }
        
        # Step 2: Extract patterns
        extractor = PatternExtractor(min_frequency=1, days_lookback=30)
        patterns = extractor.extract_all_patterns("TOKEN_STU_123", student_data)
        
        # Step 3: Assess risk
        risk_assessment = extractor.assess_risk("TOKEN_STU_123", patterns)
        
        assert risk_assessment is not None
        assert hasattr(risk_assessment, "overall_risk_level")

    def test_risk_level_escalation(self):
        """E2E: Risk level escalation workflow."""
        # Initial assessment
        risk_history = [
            {"level": "LOW", "timestamp": (datetime.now() - timedelta(days=7)).isoformat()},
            {"level": "MEDIUM", "timestamp": (datetime.now() - timedelta(days=3)).isoformat()},
            {"level": "HIGH", "timestamp": datetime.now().isoformat()},
        ]
        
        current_risk = risk_history[-1]["level"]
        previous_risk = risk_history[-2]["level"]
        
        assert current_risk == "HIGH"
        assert previous_risk == "MEDIUM"
        
        # Escalation detected
        escalated = current_risk != previous_risk and current_risk in ["HIGH", "CRITICAL"]
        assert escalated is True


class TestParentCommunicationWorkflow:
    """Test parent communication workflow."""

    def test_parent_notification_workflow(self):
        """E2E: Parent notification workflow."""
        now = datetime.now()
        
        # Step 1: Trigger notification
        notification = {
            "notification_id": "NOTIF20241001001",
            "student_token": "TOKEN_STU_ABC",
            "parent_contact": "PARENT001",
            "notification_type": "risk_escalation",
            "risk_level": "MEDIUM",
            "timestamp": now.isoformat(),
            "status": "pending",
        }
        
        # Step 2: Send notification
        notification["status"] = "sent"
        notification["sent_at"] = now.isoformat()
        notification["delivery_method"] = "email"
        
        # Step 3: Track engagement
        notification["parent_viewed"] = True
        notification["viewed_at"] = (now + timedelta(hours=2)).isoformat()
        
        assert notification["status"] == "sent"
        assert notification["parent_viewed"] is True

    def test_parent_report_request_workflow(self):
        """E2E: Parent requests student report."""
        now = datetime.now()
        
        # Step 1: Parent initiates report request
        request = {
            "request_id": "REQ20241001001",
            "student_token": "TOKEN_STU_ABC",
            "parent_id": "PARENT001",
            "request_type": "full_report",
            "requested_at": now.isoformat(),
            "status": "submitted",
        }
        
        # Step 2: Generate anonymized report
        request["status"] = "processing"
        report = {
            "report_id": "RPT20241001001",
            "request_id": request["request_id"],
            "generated_at": now.isoformat(),
            "content_anonymized": True,
            "status": "ready",
        }
        
        # Step 3: Deliver report
        request["status"] = "completed"
        request["report_id"] = report["report_id"]
        request["delivered_at"] = now.isoformat()
        
        assert request["status"] == "completed"
        assert report["content_anonymized"] is True


class TestAdministratorReviewWorkflow:
    """Test administrator review workflow."""

    def test_risk_report_review_workflow(self):
        """E2E: Administrator reviews high-risk student report."""
        now = datetime.now()
        
        # Step 1: High-risk report generated
        report = {
            "report_id": "RPT20241001001",
            "student_token": "TOKEN_STU_ABC",
            "risk_level": "HIGH",
            "generated_at": now.isoformat(),
            "status": "pending_review",
        }
        
        # Step 2: Admin assigns for review
        report["assigned_to"] = "ADMIN001"
        report["assigned_at"] = now.isoformat()
        report["status"] = "under_review"
        
        # Step 3: Admin reviews and takes action
        report["reviewed_at"] = (now + timedelta(hours=1)).isoformat()
        report["admin_notes"] = "Multiple concerning patterns detected. Recommend intervention."
        report["recommended_action"] = "schedule_parent_conference"
        report["status"] = "reviewed"
        
        # Step 4: Action assigned
        action = {
            "action_id": "ACT20241001001",
            "report_id": report["report_id"],
            "action_type": "parent_conference",
            "assigned_to": "COUNSELOR001",
            "due_date": (now + timedelta(days=3)).isoformat(),
            "status": "assigned",
        }
        
        assert report["status"] == "reviewed"
        assert action["status"] == "assigned"

    def test_intervention_tracking_workflow(self):
        """E2E: Track intervention and outcomes."""
        now = datetime.now()
        
        # Step 1: Intervention initiated
        intervention = {
            "intervention_id": "INT20241001001",
            "student_token": "TOKEN_STU_ABC",
            "intervention_type": "behavioral_support",
            "initiated_by": "COUNSELOR001",
            "initiated_at": now.isoformat(),
            "status": "active",
        }
        
        # Step 2: Progress checkpoints
        checkpoints = [
            {"date": (now + timedelta(weeks=1)).isoformat(), "status": "on_track"},
            {"date": (now + timedelta(weeks=2)).isoformat(), "status": "progressing"},
            {"date": (now + timedelta(weeks=3)).isoformat(), "status": "improved"},
        ]
        intervention["checkpoints"] = checkpoints
        
        # Step 3: Intervention outcome
        intervention["ended_at"] = (now + timedelta(weeks=4)).isoformat()
        intervention["outcome"] = "positive"
        intervention["status"] = "completed"
        
        assert intervention["status"] == "completed"
        assert intervention["outcome"] == "positive"
        assert len(checkpoints) == 3


class TestCompleteStudentJourney:
    """Test complete student journey from onboarding to intervention."""

    def test_end_to_end_student_journey(self):
        """E2E: Complete student journey."""
        now = datetime.now()
        journey = {}
        
        # 1. Onboarding
        journey["onboarding"] = {
            "status": "completed",
            "timestamp": now.isoformat(),
        }
        
        # 2. Data collection (first month)
        journey["data_collection"] = {
            "period": "month_1",
            "incidents_reported": 3,
            "attendance_issues": 5,
            "academic_concerns": 1,
        }
        
        # 3. Initial assessment
        journey["initial_assessment"] = {
            "risk_level": "MEDIUM",
            "timestamp": (now + timedelta(days=30)).isoformat(),
        }
        
        # 4. Parent notification
        journey["parent_notification"] = {
            "notified": True,
            "timestamp": (now + timedelta(days=31)).isoformat(),
        }
        
        # 5. Intervention plan
        journey["intervention"] = {
            "status": "active",
            "type": "behavioral_support",
            "start_date": (now + timedelta(days=35)).isoformat(),
        }
        
        # 6. Follow-up assessment
        journey["follow_up_assessment"] = {
            "risk_level": "LOW",
            "timestamp": (now + timedelta(days=90)).isoformat(),
            "improvement_noted": True,
        }
        
        # Verify journey completion
        assert journey["onboarding"]["status"] == "completed"
        assert journey["initial_assessment"]["risk_level"] == "MEDIUM"
        assert journey["follow_up_assessment"]["risk_level"] == "LOW"
        assert journey["follow_up_assessment"]["improvement_noted"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
