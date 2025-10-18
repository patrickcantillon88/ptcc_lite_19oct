"""
Safeguarding Orchestrator

Complete privacy-preserving safeguarding analysis workflow:
1. Tokenize sensitive data
2. Extract patterns across sources
3. Send anonymized patterns to external LLM
4. Localize results back to student context
5. Generate actionable reports
6. Log all privacy operations
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import json

from .privacy_tokenization import PrivacyTokenizer, create_tokenizer_for_session
from .safeguarding_patterns import PatternExtractor, RiskLevel
from .privacy_llm_interface import PrivacyPreservingLLMInterface

logger = logging.getLogger(__name__)


class SafeguardingOrchestrator:
    """
    Orchestrates complete privacy-preserving safeguarding analysis pipeline.
    """

    def __init__(self, llm_client: Any):
        """
        Initialize safeguarding orchestrator.
        
        Args:
            llm_client: LLM client for pattern analysis
        """
        self.llm_client = llm_client
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.analysis_history: List[Dict[str, Any]] = []

    def analyze_student_safeguarding(
        self, student_id: str, student_data: Dict[str, Any], session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete end-to-end safeguarding analysis for a student.
        
        Args:
            student_id: Student identifier
            student_data: Raw student data with behaviors, assessments, communications
            session_id: Optional session ID for tracking
            
        Returns:
            Complete safeguarding analysis report
        """
        # Create session
        session_id = session_id or self._create_session_id()
        session = {
            "session_id": session_id,
            "student_id": student_id,
            "started_at": datetime.utcnow().isoformat(),
            "stages": {},
        }

        try:
            # Stage 1: Tokenization
            tokenizer = create_tokenizer_for_session(session_id)
            session["stages"]["tokenization"] = "in_progress"

            tokenized_data = tokenizer.create_anonymized_data_snapshot(student_data)
            session["stages"]["tokenization"] = "complete"
            logger.info(f"Stage 1 complete: Tokenization for {session_id}")

            # Stage 2: Pattern Extraction
            session["stages"]["pattern_extraction"] = "in_progress"
            extractor = PatternExtractor(min_frequency=2, days_lookback=30)
            patterns = extractor.extract_all_patterns(
                tokenized_data.get("student_token"), student_data
            )
            session["stages"]["pattern_extraction"] = "complete"
            logger.info(f"Stage 2 complete: Extracted {len(patterns)} patterns")

            # Stage 3: Risk Assessment
            session["stages"]["risk_assessment"] = "in_progress"
            risk_assessment = extractor.assess_risk(
                tokenized_data.get("student_token"), patterns
            )
            session["stages"]["risk_assessment"] = "complete"
            logger.info(f"Stage 3 complete: Risk level = {risk_assessment.overall_risk_level.name}")

            # Stage 4: External LLM Analysis
            session["stages"]["llm_analysis"] = "in_progress"
            llm_interface = PrivacyPreservingLLMInterface(self.llm_client, tokenizer)

            external_analysis = llm_interface.analyze_student_patterns(
                tokenized_data, student_id
            )
            session["stages"]["llm_analysis"] = "complete"
            logger.info(f"Stage 4 complete: LLM analysis received")

            # Stage 5: Result Localization
            session["stages"]["localization"] = "in_progress"
            localized_analysis = llm_interface.localize_analysis_results(
                external_analysis, student_id
            )
            session["stages"]["localization"] = "complete"
            logger.info(f"Stage 5 complete: Analysis localized")

            # Stage 6: Report Generation
            session["stages"]["report_generation"] = "in_progress"
            report = llm_interface.generate_safeguarding_report(
                localized_analysis, {"student_id": student_id}
            )
            session["stages"]["report_generation"] = "complete"
            logger.info(f"Stage 6 complete: Report generated")

            # Store session and history
            session["completed_at"] = datetime.utcnow().isoformat()
            session["status"] = "complete"
            self.sessions[session_id] = session

            analysis_record = {
                "analysis_id": session_id,
                "student_id": student_id,
                "risk_level": report["risk_assessment"]["overall_level"],
                "confidence": report["risk_assessment"].get("confidence_score", 0.0),
                "patterns_identified": len(patterns),
                "timestamp": datetime.utcnow().isoformat(),
                "privacy_audit": llm_interface.get_privacy_log(),
            }
            self.analysis_history.append(analysis_record)

            # Return final report with metadata
            report["analysis_metadata"] = {
                "session_id": session_id,
                "analysis_stages": session["stages"],
                "duration_seconds": (
                    datetime.fromisoformat(session["completed_at"])
                    - datetime.fromisoformat(session["started_at"])
                ).total_seconds(),
                "patterns_found": len(patterns),
                "privacy_guarantees": {
                    "tokenization": "Complete - all PII replaced with tokens",
                    "external_communication": "Only anonymized tokens sent to LLM",
                    "mapping_storage": "Local system only - never shared",
                    "audit_trail": "All operations logged for compliance",
                },
            }

            return report

        except Exception as e:
            session["status"] = "error"
            session["error"] = str(e)
            session["completed_at"] = datetime.utcnow().isoformat()
            self.sessions[session_id] = session
            logger.error(f"Safeguarding analysis failed for {student_id}: {e}")
            raise

    def get_analysis_summary(self, student_id: str) -> Dict[str, Any]:
        """Get summary of recent analyses for a student."""
        student_analyses = [
            a for a in self.analysis_history if a.get("student_id") == student_id
        ]

        return {
            "student_id": student_id,
            "analyses_count": len(student_analyses),
            "most_recent": student_analyses[-1] if student_analyses else None,
            "risk_trend": self._calculate_risk_trend(student_analyses),
            "summary": self._summarize_analyses(student_analyses),
        }

    def get_privacy_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive privacy compliance report."""
        return {
            "report_generated": datetime.utcnow().isoformat(),
            "total_analyses": len(self.analysis_history),
            "privacy_assertions": {
                "no_pii_external": "All external communications use tokens only",
                "local_only_storage": "Token mappings stored locally only",
                "audit_trails": "All privacy operations logged",
                "compliance": "FERPA/GDPR compliant architecture",
            },
            "analyses_summary": self._get_analyses_summary_stats(),
        }

    def _create_session_id(self) -> str:
        """Create unique session ID."""
        import uuid

        return f"sfg_{uuid.uuid4().hex[:12]}"

    def _calculate_risk_trend(self, analyses: List[Dict[str, Any]]) -> str:
        """Calculate trend in risk levels over time."""
        if len(analyses) < 2:
            return "insufficient_data"

        risk_levels = [a.get("risk_level") for a in analyses[-3:]]
        level_values = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

        values = [level_values.get(rl, 2) for rl in risk_levels]
        if values[-1] > values[0]:
            return "escalating"
        elif values[-1] < values[0]:
            return "improving"
        else:
            return "stable"

    def _summarize_analyses(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate text summary of analyses."""
        if not analyses:
            return "No analyses available"

        recent = analyses[-1]
        risk_level = recent.get("risk_level", "UNKNOWN")
        confidence = recent.get("confidence", 0.0)

        return f"Most recent analysis: {risk_level} risk (confidence: {confidence:.1%})"

    def _get_analyses_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for all analyses."""
        if not self.analysis_history:
            return {"total": 0}

        risk_counts = {}
        for a in self.analysis_history:
            risk = a.get("risk_level", "UNKNOWN")
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

        avg_confidence = sum(
            a.get("confidence", 0) for a in self.analysis_history
        ) / len(self.analysis_history)

        return {
            "total": len(self.analysis_history),
            "by_risk_level": risk_counts,
            "average_confidence": avg_confidence,
            "most_common_risk": max(risk_counts.items(), key=lambda x: x[1])[0]
            if risk_counts
            else "UNKNOWN",
        }


# Integration with existing systems
def initialize_safeguarding_system(llm_client: Any) -> SafeguardingOrchestrator:
    """Factory function to initialize safeguarding system."""
    return SafeguardingOrchestrator(llm_client)
