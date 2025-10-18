"""
Safeguarding Pattern Extraction Engine

Identifies concerning patterns across multiple data sources (behavior, academic,
communication) while maintaining full privacy through tokenization.

Patterns extracted:
- Behavioral escalation patterns
- Academic performance correlations
- Communication urgency escalation
- Temporal clustering (multiple incidents close together)
- Cross-domain pattern correlations
- Risk factor combinations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Pattern:
    """Individual pattern identified"""
    pattern_type: str
    token: str
    severity: RiskLevel
    supporting_evidence: List[str]
    first_occurrence: datetime
    last_occurrence: datetime
    frequency: int
    temporal_trend: str  # escalating, persistent, scattered


@dataclass
class RiskAssessment:
    """Complete risk assessment for a student"""
    student_token: str
    overall_risk_level: RiskLevel
    confidence_score: float  # 0.0 - 1.0
    identified_patterns: List[Pattern]
    pattern_combinations: List[Tuple[str, str]]  # Combinations of patterns
    contributing_factors: List[str]
    assessment_timestamp: datetime
    time_window: str  # "recent", "month", "quarter"


class PatternExtractor:
    """
    Extracts meaningful patterns from tokenized student data
    for safeguarding analysis.
    """

    def __init__(self, min_frequency: int = 2, days_lookback: int = 30):
        """
        Initialize pattern extractor.
        
        Args:
            min_frequency: Minimum occurrences to consider a pattern
            days_lookback: Days of history to analyze
        """
        self.min_frequency = min_frequency
        self.days_lookback = days_lookback
        self.reference_date = datetime.utcnow()

    def extract_all_patterns(
        self, student_token: str, raw_data: Dict[str, Any]
    ) -> List[Pattern]:
        """
        Extract all patterns from student data.
        
        Args:
            student_token: Anonymized student token
            raw_data: Raw student data with timestamps and categories
            
        Returns:
            List of identified patterns
        """
        patterns = []

        # Behavioral patterns
        if "behavioral_incidents" in raw_data:
            patterns.extend(
                self._extract_behavioral_patterns(
                    student_token, raw_data["behavioral_incidents"]
                )
            )

        # Academic patterns
        if "assessments" in raw_data:
            patterns.extend(
                self._extract_academic_patterns(
                    student_token, raw_data["assessments"]
                )
            )

        # Communication patterns
        if "communications" in raw_data:
            patterns.extend(
                self._extract_communication_patterns(
                    student_token, raw_data["communications"]
                )
            )

        # Withdrawal patterns
        if "attendance" in raw_data:
            patterns.extend(
                self._extract_withdrawal_patterns(
                    student_token, raw_data["attendance"]
                )
            )

        return patterns

    def assess_risk(self, student_token: str, patterns: List[Pattern]) -> RiskAssessment:
        """
        Generate comprehensive risk assessment from patterns.
        
        Args:
            student_token: Anonymized student token
            patterns: List of identified patterns
            
        Returns:
            Risk assessment with overall level and recommendations
        """
        if not patterns:
            return RiskAssessment(
                student_token=student_token,
                overall_risk_level=RiskLevel.LOW,
                confidence_score=0.0,
                identified_patterns=[],
                pattern_combinations=[],
                contributing_factors=["No concerning patterns identified"],
                assessment_timestamp=datetime.utcnow(),
                time_window=self._categorize_timeframe(),
            )

        # Calculate overall risk level
        risk_levels = [p.severity for p in patterns]
        overall_risk = max(risk_levels, key=lambda x: x.value)

        # Identify pattern combinations
        pattern_combinations = self._identify_pattern_combinations(patterns)

        # Calculate confidence based on convergence
        confidence = self._calculate_confidence(patterns, pattern_combinations)

        # Extract contributing factors
        contributing_factors = self._extract_contributing_factors(
            patterns, pattern_combinations
        )

        return RiskAssessment(
            student_token=student_token,
            overall_risk_level=overall_risk,
            confidence_score=confidence,
            identified_patterns=patterns,
            pattern_combinations=pattern_combinations,
            contributing_factors=contributing_factors,
            assessment_timestamp=datetime.utcnow(),
            time_window=self._categorize_timeframe(),
        )

    def _extract_behavioral_patterns(
        self, student_token: str, incidents: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Extract behavioral patterns from incident data."""
        patterns = []

        # Group by behavior type
        behavior_groups: Dict[str, List[Dict[str, Any]]] = {}
        for incident in incidents:
            behavior_type = incident.get("type", "unknown")
            if behavior_type not in behavior_groups:
                behavior_groups[behavior_type] = []
            behavior_groups[behavior_type].append(incident)

        # Analyze each behavior type
        for behavior_type, incidents_of_type in behavior_groups.items():
            if len(incidents_of_type) < self.min_frequency:
                continue

            # Check if within lookback window
            recent_incidents = self._filter_recent(incidents_of_type)
            if not recent_incidents:
                continue

            timestamps = [
                incident.get("timestamp") for incident in recent_incidents
                if incident.get("timestamp")
            ]

            if len(timestamps) >= self.min_frequency:
                trend = self._analyze_temporal_trend(timestamps)
                severity = self._calculate_severity_from_frequency(len(timestamps))

                pattern_token = f"BEHAV_{behavior_type.upper().replace(' ', '_')}"
                pattern = Pattern(
                    pattern_type="behavioral",
                    token=pattern_token,
                    severity=severity,
                    supporting_evidence=[
                        f"{behavior_type} incident on {str(ts.date())}"
                        for ts in timestamps
                    ],
                    first_occurrence=min(timestamps),
                    last_occurrence=max(timestamps),
                    frequency=len(timestamps),
                    temporal_trend=trend,
                )
                patterns.append(pattern)

        return patterns

    def _extract_academic_patterns(
        self, student_token: str, assessments: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Extract academic performance patterns."""
        patterns = []

        # Check for consistent underperformance
        recent_assessments = self._filter_recent(assessments)
        if not recent_assessments:
            return patterns

        below_level_count = sum(
            1 for a in recent_assessments
            if a.get("performance_level") in ["below", "significantly_below"]
        )

        if below_level_count >= self.min_frequency:
            severity = self._calculate_severity_from_frequency(below_level_count)
            timestamps = [
                a.get("timestamp") for a in recent_assessments
                if a.get("timestamp")
            ]

            pattern = Pattern(
                pattern_type="academic",
                token="ACAD_BELOW_GRADE_LEVEL",
                severity=severity,
                supporting_evidence=[
                    f"Assessment below grade level in {a.get('subject')}"
                    for a in recent_assessments
                    if a.get("performance_level") in ["below", "significantly_below"]
                ],
                first_occurrence=min(timestamps) if timestamps else datetime.utcnow(),
                last_occurrence=max(timestamps) if timestamps else datetime.utcnow(),
                frequency=below_level_count,
                temporal_trend=self._analyze_temporal_trend(timestamps)
                if timestamps
                else "unknown",
            )
            patterns.append(pattern)

        # Check for subject-specific struggles
        subjects: Dict[str, List[Dict[str, Any]]] = {}
        for assessment in recent_assessments:
            subject = assessment.get("subject", "unknown")
            if subject not in subjects:
                subjects[subject] = []
            subjects[subject].append(assessment)

        for subject, subject_assessments in subjects.items():
            below_count = sum(
                1 for a in subject_assessments
                if a.get("performance_level") in ["below", "significantly_below"]
            )

            if len(subject_assessments) >= 2 and below_count >= 2:
                severity = self._calculate_severity_from_frequency(below_count)
                timestamps = [
                    a.get("timestamp") for a in subject_assessments
                    if a.get("timestamp")
                ]

                pattern = Pattern(
                    pattern_type="academic_subject",
                    token=f"ACAD_{subject.upper().replace(' ', '_')}_STRUGGLE",
                    severity=severity,
                    supporting_evidence=[
                        f"Consistent difficulty in {subject}"
                        for _ in range(below_count)
                    ],
                    first_occurrence=min(timestamps) if timestamps else datetime.utcnow(),
                    last_occurrence=max(timestamps) if timestamps else datetime.utcnow(),
                    frequency=below_count,
                    temporal_trend=self._analyze_temporal_trend(timestamps)
                    if timestamps
                    else "unknown",
                )
                patterns.append(pattern)

        return patterns

    def _extract_communication_patterns(
        self, student_token: str, communications: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Extract communication escalation patterns."""
        patterns = []

        # Filter recent communications
        recent_comms = self._filter_recent(communications)
        if not recent_comms:
            return patterns

        # Check for escalation in urgency
        urgent_count = sum(
            1 for c in recent_comms
            if c.get("urgency_level") in ["urgent", "high_priority"]
        )

        if urgent_count >= self.min_frequency:
            severity = self._calculate_severity_from_frequency(urgent_count)
            timestamps = [c.get("timestamp") for c in recent_comms if c.get("timestamp")]

            trend = self._analyze_temporal_trend(timestamps)

            pattern = Pattern(
                pattern_type="communication_escalation",
                token="COMM_ESCALATING_CONCERNS",
                severity=severity,
                supporting_evidence=[
                    f"High-priority communication from {c.get('source')}"
                    for c in recent_comms
                    if c.get("urgency_level") in ["urgent", "high_priority"]
                ],
                first_occurrence=min(timestamps) if timestamps else datetime.utcnow(),
                last_occurrence=max(timestamps) if timestamps else datetime.utcnow(),
                frequency=urgent_count,
                temporal_trend=trend,
            )
            patterns.append(pattern)

        # Check for multi-source concerns
        sources = set(c.get("source") for c in recent_comms if c.get("source"))
        if len(sources) >= 2:
            pattern = Pattern(
                pattern_type="multi_source_concern",
                token="COMM_MULTI_SOURCE",
                severity=RiskLevel.MEDIUM,
                supporting_evidence=[
                    f"Concerns raised by: {', '.join(sources)}"
                ],
                first_occurrence=min(
                    c.get("timestamp") for c in recent_comms if c.get("timestamp")
                ),
                last_occurrence=max(
                    c.get("timestamp") for c in recent_comms if c.get("timestamp")
                ),
                frequency=len(sources),
                temporal_trend="convergence",
            )
            patterns.append(pattern)

        return patterns

    def _extract_withdrawal_patterns(
        self, student_token: str, attendance_data: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Extract withdrawal and isolation patterns."""
        patterns = []

        # Check for attendance decline
        recent_attendance = self._filter_recent(attendance_data)
        if not recent_attendance:
            return patterns

        absent_count = sum(
            1 for a in recent_attendance if a.get("status") == "absent"
        )
        present_count = sum(
            1 for a in recent_attendance if a.get("status") == "present"
        )
        total_possible = len(recent_attendance)

        if total_possible > 0:
            attendance_rate = present_count / total_possible

            if attendance_rate < 0.85:  # Below 85% threshold
                severity = (
                    RiskLevel.HIGH
                    if attendance_rate < 0.70
                    else RiskLevel.MEDIUM
                )
                timestamps = [
                    a.get("timestamp") for a in recent_attendance
                    if a.get("timestamp") and a.get("status") == "absent"
                ]

                pattern = Pattern(
                    pattern_type="attendance_decline",
                    token="ATTEND_DECLINING",
                    severity=severity,
                    supporting_evidence=[
                        f"Attendance: {int(attendance_rate*100)}% (below target)"
                    ],
                    first_occurrence=min(timestamps) if timestamps else datetime.utcnow(),
                    last_occurrence=max(timestamps) if timestamps else datetime.utcnow(),
                    frequency=absent_count,
                    temporal_trend=self._analyze_temporal_trend(timestamps)
                    if timestamps
                    else "unknown",
                )
                patterns.append(pattern)

        return patterns

    def _identify_pattern_combinations(
        self, patterns: List[Pattern]
    ) -> List[Tuple[str, str]]:
        """
        Identify concerning combinations of patterns.
        The presence of multiple pattern types together indicates higher risk.
        """
        combinations = []

        pattern_types = [p.pattern_type for p in patterns]
        pattern_tokens = [p.token for p in patterns]

        # Check for common concerning combinations
        type_set = set(pattern_types)

        if "behavioral" in type_set and "academic" in type_set:
            combinations.append(("behavioral_struggle", "academic_struggle"))

        if "behavioral" in type_set and "communication_escalation" in type_set:
            combinations.append(("behavioral_issues", "escalating_concerns"))

        if "academic" in type_set and "attendance_decline" in type_set:
            combinations.append(("academic_difficulty", "withdrawal_pattern"))

        if "communication_escalation" in type_set and "attendance_decline" in type_set:
            combinations.append(("escalating_concerns", "withdrawal_pattern"))

        # Multi-pattern convergence (3+ patterns)
        if len(pattern_types) >= 3:
            combinations.append(("multi_factor_concern", "convergence"))

        return combinations

    def _calculate_confidence(
        self, patterns: List[Pattern], combinations: List[Tuple[str, str]]
    ) -> float:
        """
        Calculate confidence score for risk assessment.
        Based on:
        - Number of patterns (convergence)
        - Frequency of incidents
        - Pattern combinations
        - Temporal consistency
        """
        confidence = 0.5  # Base confidence

        # Add for convergence
        confidence += min(0.2, len(patterns) * 0.05)

        # Add for frequency
        total_frequency = sum(p.frequency for p in patterns)
        confidence += min(0.15, total_frequency * 0.02)

        # Add for pattern combinations
        confidence += min(0.15, len(combinations) * 0.05)

        # Cap at 1.0
        return min(1.0, confidence)

    def _extract_contributing_factors(
        self, patterns: List[Pattern], combinations: List[Tuple[str, str]]
    ) -> List[str]:
        """Extract human-readable contributing factors."""
        factors = []

        for pattern in patterns:
            if pattern.pattern_type == "behavioral":
                factors.append(
                    f"Multiple behavioral incidents (escalating pattern over {pattern.temporal_trend} period)"
                )
            elif pattern.pattern_type == "academic":
                factors.append(
                    f"Consistent academic underperformance in {pattern.frequency} recent assessments"
                )
            elif pattern.pattern_type == "communication_escalation":
                factors.append(
                    f"Escalating concerns from multiple sources ({pattern.frequency} communications)"
                )
            elif pattern.pattern_type == "attendance_decline":
                factors.append(
                    f"Declining attendance ({pattern.frequency} absences in recent period)"
                )

        for combo_type, intensity in combinations:
            if combo_type == "behavioral_struggle":
                factors.append(
                    "Behavioral issues appearing alongside academic difficulties - suggesting frustration"
                )
            elif combo_type == "multi_factor_concern":
                factors.append(
                    "Multiple concerns converging across different areas - indicates systemic issue"
                )

        return factors if factors else ["No specific contributing factors identified"]

    def _filter_recent(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter items within lookback window."""
        cutoff_date = self.reference_date - timedelta(days=self.days_lookback)
        return [
            item
            for item in items
            if item.get("timestamp") and item.get("timestamp") >= cutoff_date
        ]

    def _analyze_temporal_trend(self, timestamps: List[datetime]) -> str:
        """Analyze trend of events over time."""
        if len(timestamps) < 2:
            return "single_event"

        sorted_timestamps = sorted(timestamps)
        total_days = (sorted_timestamps[-1] - sorted_timestamps[0]).days

        if total_days == 0:
            return "clustered"
        elif total_days <= 7:
            return "escalating"
        elif total_days <= 30:
            return "persistent"
        else:
            return "scattered"

    def _calculate_severity_from_frequency(self, frequency: int) -> RiskLevel:
        """Convert frequency to risk severity level."""
        if frequency >= 5:
            return RiskLevel.CRITICAL
        elif frequency >= 4:
            return RiskLevel.HIGH
        elif frequency >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _categorize_timeframe(self) -> str:
        """Categorize assessment timeframe."""
        return "recent" if self.days_lookback <= 30 else (
            "monthly" if self.days_lookback <= 90 else "quarterly"
        )
