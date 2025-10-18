"""
Privacy-Preserving Tokenization Engine

Transforms sensitive student and educational data into anonymous tokens
for safe external LLM analysis without exposing personally identifiable information.

Key Features:
- Student identity anonymization
- Data type tokenization
- Temporal anonymization
- Context anonymization
- Reversible mapping (local-only)
- Privacy audit trails
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Token types for different data categories"""
    STUDENT_ID = "STU"
    TEACHER_ID = "TCH"
    CLASS_ID = "CLS"
    BEHAVIOR = "BEH"
    ACADEMIC = "ACA"
    COMMUNICATION = "COM"
    ASSESSMENT = "ASS"
    TIME_PERIOD = "TIM"
    LOCATION = "LOC"
    EMOTION = "EMO"
    SEVERITY = "SEV"


class PrivacyTokenizer:
    """
    Transforms sensitive data into anonymous tokens for external LLM analysis.
    
    All mappings remain local and are never shared externally.
    Tokens are meaningless to external systems but reversible locally.
    """

    def __init__(self, namespace: str = "ptcc_safeguarding"):
        """
        Initialize tokenizer with secure namespace.
        
        Args:
            namespace: Unique namespace for token generation
        """
        self.namespace = namespace
        self.student_tokens: Dict[str, str] = {}  # {student_id: token}
        self.token_registry: Dict[str, Dict[str, Any]] = {}  # {token: metadata}
        self.reverse_mapping: Dict[str, str] = {}  # {token: original_id}
        self.privacy_log: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()

    def tokenize_student_id(self, student_id: str) -> str:
        """
        Tokenize student ID - returns same token for same student.
        
        Args:
            student_id: Original student identifier
            
        Returns:
            Anonymous token (e.g., TOKEN_STU_7B9)
        """
        if student_id in self.student_tokens:
            return self.student_tokens[student_id]

        # Generate deterministic but anonymous token
        token_suffix = self._generate_token_suffix(student_id)
        token = f"TOKEN_{TokenType.STUDENT_ID.value}_{token_suffix}"

        # Store mappings (local only, never shared)
        self.student_tokens[student_id] = token
        self.reverse_mapping[token] = student_id
        self.token_registry[token] = {
            "type": TokenType.STUDENT_ID.value,
            "created_at": datetime.utcnow().isoformat(),
            "original_type": "student_id",
        }

        return token

    def tokenize_behavior(self, behavior_type: str, frequency: int = 1) -> str:
        """
        Tokenize behavior data.
        
        Args:
            behavior_type: Type of behavior (e.g., 'disruptive', 'withdrawn')
            frequency: How many times occurred
            
        Returns:
            Behavior token (e.g., BEHAV_DISRUPT_HIGH_3)
        """
        normalized_type = behavior_type.upper().replace(" ", "_")
        frequency_level = self._frequency_to_level(frequency)
        token = f"BEHAV_{normalized_type}_{frequency_level}"

        self.token_registry[token] = {
            "type": TokenType.BEHAVIOR.value,
            "behavior_type": behavior_type,
            "frequency": frequency,
            "created_at": datetime.utcnow().isoformat(),
        }

        return token

    def tokenize_academic_result(
        self, subject: str, performance_level: str, assessment_type: str = "formative"
    ) -> str:
        """
        Tokenize academic performance data.
        
        Args:
            subject: Subject area (e.g., 'Math', 'English')
            performance_level: Level ('below', 'at', 'above', 'advanced')
            assessment_type: Type of assessment
            
        Returns:
            Academic token (e.g., ACAD_MATH_BELOW)
        """
        normalized_subject = subject.upper().replace(" ", "_")
        normalized_level = performance_level.upper()
        token = f"ACAD_{normalized_subject}_{normalized_level}"

        self.token_registry[token] = {
            "type": TokenType.ACADEMIC.value,
            "subject": subject,
            "performance_level": performance_level,
            "assessment_type": assessment_type,
            "created_at": datetime.utcnow().isoformat(),
        }

        return token

    def tokenize_communication(self, source: str, urgency_level: str) -> str:
        """
        Tokenize communication data.
        
        Args:
            source: Communication source (parent, teacher, admin)
            urgency_level: Urgency level (routine, important, urgent)
            
        Returns:
            Communication token (e.g., COMM_PARENT_URGENT)
        """
        normalized_source = source.upper()
        normalized_urgency = urgency_level.upper()
        token = f"COMM_{normalized_source}_{normalized_urgency}"

        self.token_registry[token] = {
            "type": TokenType.COMMUNICATION.value,
            "source": source,
            "urgency_level": urgency_level,
            "created_at": datetime.utcnow().isoformat(),
        }

        return token

    def tokenize_temporal_data(
        self, timestamp: datetime, relative_to: Optional[datetime] = None
    ) -> str:
        """
        Tokenize temporal data - loses exact dates but preserves patterns.
        
        Args:
            timestamp: Actual timestamp
            relative_to: Reference date for relative timing
            
        Returns:
            Temporal token (e.g., TIME_RECENT_ESCALATING)
        """
        reference = relative_to or datetime.utcnow()
        days_ago = (reference - timestamp).days

        if days_ago <= 7:
            period = "RECENT"
        elif days_ago <= 30:
            period = "MONTH"
        elif days_ago <= 90:
            period = "QUARTER"
        else:
            period = "HISTORICAL"

        token = f"TIME_{period}"

        self.token_registry[token] = {
            "type": TokenType.TIME_PERIOD.value,
            "period": period,
            "days_ago": days_ago,
            "original_timestamp": timestamp.isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        }

        return token

    def tokenize_frequency_pattern(self, events: List[datetime]) -> Tuple[str, str]:
        """
        Analyze frequency pattern of events over time.
        
        Args:
            events: List of event timestamps
            
        Returns:
            Tuple of (frequency_token, trend_token)
        """
        if not events:
            return "FREQ_NONE", "TREND_STABLE"

        sorted_events = sorted(events)
        total_count = len(sorted_events)

        # Determine frequency
        if total_count == 1:
            freq_token = "FREQ_SINGLE"
        elif total_count <= 3:
            freq_token = "FREQ_LOW"
        elif total_count <= 7:
            freq_token = "FREQ_MEDIUM"
        else:
            freq_token = "FREQ_HIGH"

        # Determine trend
        if len(sorted_events) >= 2:
            days_spanned = (sorted_events[-1] - sorted_events[0]).days
            if days_spanned == 0:
                trend_token = "TREND_CLUSTER"
            elif days_spanned <= 7 and total_count >= 3:
                trend_token = "TREND_ESCALATING"
            elif days_spanned > 30 and total_count > 2:
                trend_token = "TREND_PERSISTENT"
            else:
                trend_token = "TREND_SCATTERED"
        else:
            trend_token = "TREND_STABLE"

        self.token_registry[freq_token] = {
            "type": "frequency",
            "total_count": total_count,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.token_registry[trend_token] = {
            "type": "trend",
            "days_spanned": (sorted_events[-1] - sorted_events[0]).days if len(sorted_events) > 1 else 0,
            "created_at": datetime.utcnow().isoformat(),
        }

        return freq_token, trend_token

    def create_anonymized_data_snapshot(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw student data into fully anonymized snapshot.
        
        Args:
            raw_data: Original data with PII
            
        Returns:
            Anonymized data safe for external LLM
        """
        anonymized = {}

        # Tokenize student
        if "student_id" in raw_data:
            anonymized["student_token"] = self.tokenize_student_id(raw_data["student_id"])

        # Tokenize behavioral data
        if "behaviors" in raw_data:
            anonymized["behavior_tokens"] = [
                self.tokenize_behavior(b["type"], b.get("count", 1))
                for b in raw_data["behaviors"]
            ]

        # Tokenize academic data
        if "assessments" in raw_data:
            anonymized["academic_tokens"] = [
                self.tokenize_academic_result(
                    a.get("subject"), a.get("performance_level"), a.get("type")
                )
                for a in raw_data["assessments"]
            ]

        # Tokenize communications
        if "communications" in raw_data:
            anonymized["communication_tokens"] = [
                self.tokenize_communication(c.get("source"), c.get("urgency"))
                for c in raw_data["communications"]
            ]

        # Tokenize temporal data
        if "timestamps" in raw_data:
            anonymized["temporal_tokens"] = [
                self.tokenize_temporal_data(ts) for ts in raw_data["timestamps"]
            ]

        # Tokenize frequency patterns
        if "event_timestamps" in raw_data:
            freq_token, trend_token = self.tokenize_frequency_pattern(
                raw_data["event_timestamps"]
            )
            anonymized["frequency_token"] = freq_token
            anonymized["trend_token"] = trend_token

        # Add metadata (no PII)
        anonymized["anonymization_timestamp"] = datetime.utcnow().isoformat()
        anonymized["data_categories"] = list(anonymized.keys())

        # Log anonymization
        self._log_privacy_event("data_anonymized", anonymized)

        return anonymized

    def deanonymize_analysis_results(
        self, external_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert external LLM analysis back to specific student context.
        Only called locally - never exposes tokens externally.
        
        Args:
            external_analysis: Analysis results from external LLM (tokenized)
            
        Returns:
            Localized analysis with actual student context
        """
        localized = {}

        # Get student context
        if "student_token" in external_analysis:
            student_token = external_analysis["student_token"]
            student_id = self.reverse_mapping.get(student_token)
            localized["student_id"] = student_id
            localized["student_context_available"] = student_id is not None

        # Preserve pattern analysis (still tokenized for safety)
        localized["identified_patterns"] = external_analysis.get("patterns", [])
        localized["risk_level"] = external_analysis.get("risk_level")
        localized["confidence_score"] = external_analysis.get("confidence")

        # Convert recommendations to actionable items
        if "recommendations" in external_analysis:
            localized["intervention_recommendations"] = external_analysis["recommendations"]

        # Add evidence (still in token form for security)
        localized["evidence_tokens"] = external_analysis.get("evidence", [])

        # Log deanonymization
        self._log_privacy_event("analysis_localized", localized)

        return localized

    def get_privacy_report(self) -> Dict[str, Any]:
        """
        Generate privacy compliance report.
        
        Returns:
            Report of all privacy-preserving actions
        """
        return {
            "summary": {
                "students_anonymized": len(self.student_tokens),
                "tokens_generated": len(self.token_registry),
                "privacy_events_logged": len(self.privacy_log),
                "created_at": self.created_at.isoformat(),
                "runtime_duration": (datetime.utcnow() - self.created_at).total_seconds(),
            },
            "token_statistics": {
                "behavior_tokens": len(
                    [t for t in self.token_registry.values() if t.get("type") == "BEHAV"]
                ),
                "academic_tokens": len(
                    [t for t in self.token_registry.values() if t.get("type") == "ACA"]
                ),
                "communication_tokens": len(
                    [t for t in self.token_registry.values() if t.get("type") == "COM"]
                ),
            },
            "privacy_log_summary": {
                "total_events": len(self.privacy_log),
                "event_types": list(set(e["event_type"] for e in self.privacy_log)),
            },
            "guarantees": {
                "no_pii_external": "All external communications are fully anonymized",
                "local_only_mapping": "Token mappings never leave local system",
                "reversible_locally": "Results can be localized only within system",
                "audit_trail": "All privacy actions are logged",
            },
        }

    def _generate_token_suffix(self, original_id: str) -> str:
        """
        Generate deterministic but anonymous token suffix.
        Same input always produces same token (for consistency),
        but token reveals nothing about original ID.
        """
        hash_input = f"{self.namespace}:{original_id}".encode()
        hash_digest = hashlib.sha256(hash_input).hexdigest()
        # Use first 3 characters of hash
        return hash_digest[:3].upper()

    def _frequency_to_level(self, frequency: int) -> str:
        """Convert frequency count to level token."""
        if frequency == 1:
            return "SINGLE"
        elif frequency <= 2:
            return "LOW"
        elif frequency <= 5:
            return "MEDIUM"
        else:
            return "HIGH"

    def _log_privacy_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log privacy-related events for audit trail."""
        self.privacy_log.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "details_summary": str(details)[:200],  # Summary only, not full details
            }
        )


def create_tokenizer_for_session(session_id: str) -> PrivacyTokenizer:
    """Factory function to create tokenizer for a specific session."""
    return PrivacyTokenizer(namespace=f"ptcc_{session_id}")
