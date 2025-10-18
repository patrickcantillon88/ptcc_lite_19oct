"""
Unit tests for privacy components:
- Tokenization
- Pattern extraction
- Risk assessment
"""

import pytest
from datetime import datetime, timedelta
from core.privacy_tokenization import PrivacyTokenizer, create_tokenizer_for_session
from core.safeguarding_patterns import PatternExtractor, RiskLevel, RiskAssessment


class TestPrivacyTokenizer:
    """Test privacy tokenization functionality."""

    def test_tokenizer_creation(self):
        """Test creating a tokenizer for a session."""
        session_id = "test_session_123"
        tokenizer = create_tokenizer_for_session(session_id)
        
        assert tokenizer is not None
        assert isinstance(tokenizer, PrivacyTokenizer)
        assert tokenizer.namespace == f"ptcc_{session_id}"

    def test_student_id_tokenization(self):
        """Test student ID tokenization."""
        tokenizer = create_tokenizer_for_session("session_1")
        student_id = "STU12345"
        
        token = tokenizer.tokenize_student_id(student_id)
        
        assert token is not None
        assert token != student_id  # Should be different
        assert token.startswith("TOKEN_")

    def test_student_id_consistent_tokenization(self):
        """Test that same student ID gets same token in same session."""
        tokenizer = create_tokenizer_for_session("session_2")
        student_id = "STU12345"
        
        token1 = tokenizer.tokenize_student_id(student_id)
        token2 = tokenizer.tokenize_student_id(student_id)
        
        assert token1 == token2  # Should be consistent

    def test_different_sessions_different_tokens(self):
        """Test that different sessions produce different tokens for same student."""
        student_id = "STU12345"
        
        tokenizer1 = create_tokenizer_for_session("session_1")
        tokenizer2 = create_tokenizer_for_session("session_2")
        
        token1 = tokenizer1.tokenize_student_id(student_id)
        token2 = tokenizer2.tokenize_student_id(student_id)
        
        assert token1 != token2  # Different sessions = different tokens

    def test_anonymized_snapshot_no_pii(self):
        """Test that anonymized snapshot contains no PII."""
        tokenizer = create_tokenizer_for_session("session_3")
        
        student_data = {
            "name": "John Smith",
            "email": "john@example.com",
            "student_id": "STU12345",
            "assessments": [
                {
                    "subject": "Math",
                    "performance_level": "below",
                    "type": "formative"
                }
            ]
        }
        
        anonymized = tokenizer.create_anonymized_data_snapshot(student_data)
        
        # Check that anonymized data doesn't contain PII
        anonymized_str = str(anonymized).lower()
        assert "john" not in anonymized_str
        assert "smith" not in anonymized_str
        assert "john@example.com" not in anonymized_str
        assert "stu12345" not in anonymized_str
        
        # Check that anonymized data contains tokens
        assert "token_" in anonymized_str.lower()

    def test_timestamp_tokenization(self):
        """Test timestamp tokenization."""
        tokenizer = create_tokenizer_for_session("session_4")
        
        timestamp = datetime.now()
        token = tokenizer.tokenize_temporal_data(timestamp)
        
        assert token is not None
        assert token.startswith("TIME_")

    def test_behavior_tokenization(self):
        """Test behavior type tokenization."""
        tokenizer = create_tokenizer_for_session("session_5")
        
        behavior = "disruptive"
        token = tokenizer.tokenize_behavior(behavior)
        
        assert token is not None
        assert token != behavior
        assert token.startswith("BEHAV_")


class TestPatternExtractor:
    """Test pattern extraction functionality."""

    @pytest.fixture
    def extractor(self):
        """Create pattern extractor instance."""
        return PatternExtractor(min_frequency=1, days_lookback=30)
    
    def _convert_iso_to_datetime(self, iso_string: str) -> datetime:
        """Convert ISO string to datetime object."""
        # Handle both formats: with and without microseconds
        if '.' in iso_string:
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        else:
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))

    def test_behavioral_pattern_extraction(self, extractor):
        """Test extraction of behavioral patterns."""
        student_token = "TOKEN_STU_123"
        now = datetime.now()
        
        student_data = {
            "behavioral_incidents": [
                {
                    "type": "disruptive",
                    "timestamp": now,  # Use datetime object
                    "description": "Talking back"
                },
                {
                    "type": "disruptive",
                    "timestamp": (now - timedelta(days=2)),  # Use datetime object
                    "description": "Not following instructions"
                }
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        
        assert len(patterns) > 0
        assert any("BEHAV" in str(p) for p in patterns)

    def test_academic_pattern_extraction(self, extractor):
        """Test extraction of academic patterns."""
        student_token = "TOKEN_STU_456"
        now = datetime.now()
        
        student_data = {
            "behavioral_incidents": [],
            "assessments": [
                {
                    "subject": "Math",
                    "performance_level": "below",
                    "timestamp": now,
                    "type": "formative"
                },
                {
                    "subject": "Math",
                    "performance_level": "below",
                    "timestamp": (now - timedelta(days=5)),
                    "type": "formative"
                }
            ],
            "communications": [],
            "attendance": []
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        
        assert len(patterns) > 0

    def test_communication_pattern_extraction(self, extractor):
        """Test extraction of communication patterns."""
        student_token = "TOKEN_STU_789"
        now = datetime.now()
        
        student_data = {
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [
                {
                    "source": "parent",
                    "urgency_level": "urgent",
                    "timestamp": now,
                    "content": "Concern about progress"
                }
            ],
            "attendance": []
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        
        assert len(patterns) > 0

    def test_attendance_pattern_extraction(self, extractor):
        """Test extraction of attendance patterns."""
        student_token = "TOKEN_STU_999"
        now = datetime.now()
        
        student_data = {
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [],
            "attendance": [
                {
                    "status": "absent",
                    "timestamp": now
                },
                {
                    "status": "absent",
                    "timestamp": (now - timedelta(days=1))
                },
                {
                    "status": "late",
                    "timestamp": (now - timedelta(days=3))
                }
            ]
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        
        assert len(patterns) > 0

    def test_risk_assessment(self, extractor):
        """Test risk assessment."""
        student_token = "TOKEN_STU_111"
        now = datetime.now()
        
        # Create student data with multiple concerning patterns
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": now},
                {"type": "disruptive", "timestamp": (now - timedelta(days=1))}
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now},
                {"subject": "English", "performance_level": "below", "timestamp": now}
            ],
            "communications": [
                {"source": "parent", "urgency_level": "urgent", "timestamp": now}
            ],
            "attendance": [
                {"status": "absent", "timestamp": now}
            ]
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        assessment = extractor.assess_risk(student_token, patterns)
        
        assert assessment is not None
        assert isinstance(assessment, RiskAssessment)
        assert assessment.overall_risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert 0.0 <= assessment.confidence_score <= 1.0

    def test_low_risk_assessment(self, extractor):
        """Test low risk assessment with minimal data."""
        student_token = "TOKEN_STU_222"
        
        student_data = {
            "behavioral_incidents": [],
            "assessments": [
                {"subject": "Math", "performance_level": "at", "timestamp": datetime.now()}
            ],
            "communications": [],
            "attendance": [
                {"status": "present", "timestamp": datetime.now()}
            ]
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        assessment = extractor.assess_risk(student_token, patterns)
        
        assert assessment.overall_risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]

    def test_high_risk_assessment(self, extractor):
        """Test high risk assessment with multiple concerning factors."""
        student_token = "TOKEN_STU_333"
        now = datetime.now()
        
        # Create highly concerning data
        student_data = {
            "behavioral_incidents": [
                {"type": "disruptive", "timestamp": (now - timedelta(days=i))}
                for i in range(5)
            ],
            "assessments": [
                {"subject": "Math", "performance_level": "below", "timestamp": now},
                {"subject": "English", "performance_level": "below", "timestamp": now},
                {"subject": "Science", "performance_level": "below", "timestamp": now}
            ],
            "communications": [
                {"source": "parent", "urgency_level": "urgent", "timestamp": now},
                {"source": "teacher", "urgency_level": "important", "timestamp": now}
            ],
            "attendance": [
                {"status": "absent", "timestamp": (now - timedelta(days=i))}
                for i in range(7)
            ]
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        assessment = extractor.assess_risk(student_token, patterns)
        
        assert assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def test_temporal_pattern_detection(self, extractor):
        """Test detection of temporal patterns."""
        student_token = "TOKEN_STU_444"
        now = datetime.now()
        
        # Create a pattern over time
        student_data = {
            "behavioral_incidents": [
                {
                    "type": "disruptive",
                    "timestamp": (now - timedelta(days=i))
                }
                for i in range(10)  # 10 days of incidents
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        }
        
        patterns = extractor.extract_all_patterns(student_token, student_data)
        
        # Should detect temporal pattern
        assert len(patterns) > 0


class TestAnonymityValidation:
    """Test anonymity validation in the system."""

    def test_no_student_names_in_anonymized_data(self):
        """Verify student names are not exposed in anonymized data."""
        tokenizer = create_tokenizer_for_session("test_anon_1")
        
        student_data = {
            "name": "Michael Johnson",
            "student_id": "STU99999",
            "email": "michael.johnson@school.edu",
            "behavioral_incidents": [
                {
                    "type": "disruptive",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "assessments": [],
            "communications": [],
            "attendance": []
        }
        
        anonymized = tokenizer.create_anonymized_data_snapshot(student_data)
        
        # Convert to string for comprehensive checking
        data_str = str(anonymized).lower()
        
        # Verify PII is not present
        assert "michael" not in data_str
        assert "johnson" not in data_str
        assert "michael.johnson" not in data_str
        assert "@school.edu" not in data_str

    def test_no_email_in_anonymized_data(self):
        """Verify email addresses are not exposed."""
        tokenizer = create_tokenizer_for_session("test_anon_2")
        
        student_data = {
            "student_id": "STU88888",
            "email": "john.doe@example.com",
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [
                {
                    "source": "parent",
                    "urgency_level": "routine",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "attendance": []
        }
        
        anonymized = tokenizer.create_anonymized_data_snapshot(student_data)
        
        data_str = str(anonymized)
        
        # Verify email is tokenized
        assert "@example.com" not in data_str
        assert "john.doe" not in data_str

    def test_token_mapping_not_exposed(self):
        """Verify token-to-ID mapping is not exposed in snapshot."""
        tokenizer = create_tokenizer_for_session("test_anon_3")
        
        student_id = "STU77777"
        student_data = {
            "student_id": student_id,
            "behavioral_incidents": [],
            "assessments": [],
            "communications": [],
            "attendance": []
        }
        
        anonymized = tokenizer.create_anonymized_data_snapshot(student_data)
        
        # The original student ID should not be in the anonymized data
        assert student_id not in str(anonymized)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
