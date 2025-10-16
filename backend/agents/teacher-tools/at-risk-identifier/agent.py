#!/usr/bin/env python3
"""
At-Risk Student Identification Agent for PTCC

Analyzes student data patterns to identify students who may need additional support.
Integrates with PTCC's student database to provide teachers with actionable insights.

Features:
- Analyzes support levels and behavioral patterns
- Identifies students with concerning trends
- Provides risk assessment scores
- Suggests intervention strategies
- Integrates with PTCC briefing system
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

# PTCC Integration
import sys
import os

# More robust path resolution for PTCC backend modules
def find_ptcc_backend():
    """Find PTCC backend directory and add to path"""
    try:
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)

        # Try multiple possible paths to find PTCC backend
        possible_paths = [
            # Path when run as agent: agent -> teacher-tools -> agents -> backend -> ptcc
            os.path.join(current_dir, '..', '..', '..', '..', 'backend'),
            # Path when imported by API: agent -> teacher-tools -> agents -> backend
            os.path.join(current_dir, '..', '..', '..', 'backend'),
            # Alternative path structure
            os.path.join(current_dir, '..', '..', '..', '..', '..', 'backend'),
        ]

        for ptcc_backend in possible_paths:
            if os.path.exists(ptcc_backend):
                backend_path = os.path.abspath(ptcc_backend)
                if backend_path not in sys.path:
                    sys.path.insert(0, backend_path)
                return True
        return False
    except Exception:
        return False

# Try to locate PTCC backend modules
ptcc_backend_found = find_ptcc_backend()

try:
    from backend.core.database import get_db
    from backend.models.database_models import Student, QuickLog, Assessment
    from backend.core.logging_config import get_logger
    from backend.core.gemini_client import create_gemini_client_from_config
    from backend.core.config import get_settings
    PTCC_MODULES_AVAILABLE = True
except ImportError as e:
    PTCC_MODULES_AVAILABLE = False
    print(f"Warning: PTCC database modules not found: {e}")
    print("Warning: Running in standalone mode - database features will not work")

    # Create fallback mock modules for when PTCC modules aren't available
    class MockDB:
        def query(self, model):
            return MockQuery([])
        def close(self):
            pass

    class MockQuery:
        def __init__(self, results):
            self.results = results
        def filter(self, *args):
            return self
        def first(self):
            return None
        def all(self):
            return self.results
        def order_by(self, *args):
            return self
        def limit(self, n):
            return self

    class MockModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    # Create mock database function
    def get_db():
        return [MockDB()]

    # Create mock models
    Student = MockModel
    Assessment = MockModel
    QuickLog = MockModel

    # Create mock logger
    def get_logger(name):
        import logging
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        return logger

    # Create mock Gemini client
    def create_gemini_client_from_config(settings):
        class MockGeminiClient:
            def is_available(self):
                return False
            def generate_agent_response(self, *args):
                return None
        return MockGeminiClient()

    # Create mock settings
    def get_settings():
        class MockSettings:
            def __init__(self):
                pass
        return MockSettings()

@dataclass
class RiskFactor:
    """Individual risk factor for a student"""
    factor_type: str
    severity: str  # low, medium, high
    description: str
    data_points: List[str]
    recommendation: str

@dataclass
class StudentRiskAssessment:
    """Risk assessment for a single student"""
    student_id: int
    student_name: str
    class_code: str
    overall_risk_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    risk_factors: List[RiskFactor]
    positive_factors: List[str]
    recommended_actions: List[str]
    last_updated: datetime

class AtRiskStudentIdentifier:
    """Agent for identifying students at risk of academic or behavioral challenges"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.risk_weights = {
            'high_support_level': 25,
            'recent_negative_logs': 20,
            'declining_assessments': 15,
            'no_positive_interaction': 10,
            'multiple_support_notes': 15,
            'behavioral_patterns': 15
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger("at_risk_identifier")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def analyze_student(self, student_id: int) -> Optional[StudentRiskAssessment]:
        """Analyze a single student for risk factors"""
        if not PTCC_MODULES_AVAILABLE:
            self.logger.error("PTCC modules not available - cannot analyze student")
            return None

        try:
            db = next(get_db())

            # Get student information
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                self.logger.error(f"Student {student_id} not found")
                return None

            risk_factors = []
            positive_factors = []
            risk_score = 0

            # Analyze support level
            support_risk = self._analyze_support_level(student)
            if support_risk:
                risk_factors.append(support_risk)
                risk_score += self.risk_weights.get('high_support_level', 0)

            # Analyze recent behavior logs
            behavior_risk = self._analyze_behavior_logs(student_id, db)
            if behavior_risk:
                risk_factors.append(behavior_risk)
                risk_score += self.risk_weights.get('recent_negative_logs', 0)

            # Analyze assessment trends
            assessment_risk = self._analyze_assessment_trends(student_id, db)
            if assessment_risk:
                risk_factors.append(assessment_risk)
                risk_score += self.risk_weights.get('declining_assessments', 0)

            # Analyze positive interactions
            positive_analysis = self._analyze_positive_interactions(student_id, db)
            positive_factors.extend(positive_analysis)

            # Analyze support notes
            notes_risk = self._analyze_support_notes(student)
            if notes_risk:
                risk_factors.append(notes_risk)
                risk_score += self.risk_weights.get('multiple_support_notes', 0)

            # Determine overall risk level
            risk_level = self._calculate_risk_level(risk_score)

            # Generate recommended actions
            recommended_actions = self._generate_recommendations(risk_factors, positive_factors)

            return StudentRiskAssessment(
                student_id=student_id,
                student_name=student.name,
                class_code=student.class_code,
                overall_risk_score=min(risk_score, 100),
                risk_level=risk_level,
                risk_factors=risk_factors,
                positive_factors=positive_factors,
                recommended_actions=recommended_actions,
                last_updated=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Error analyzing student {student_id}: {e}")
            return None

    def _analyze_support_level(self, student) -> Optional[RiskFactor]:
        """Analyze student's support level"""
        if student.support_level >= 2:
            severity = "high" if student.support_level >= 3 else "medium"

            return RiskFactor(
                factor_type="high_support_level",
                severity=severity,
                description=f"Student has support level {student.support_level}",
                data_points=[f"Support level: {student.support_level}"],
                recommendation=f"Review and update support plan for {student.name}"
            )
        return None

    def _analyze_behavior_logs(self, student_id: int, db) -> Optional[RiskFactor]:
        """Analyze recent behavior logs for negative patterns"""
        two_weeks_ago = datetime.now() - timedelta(days=14)

        # Count negative logs in last 2 weeks
        negative_logs = db.query(QuickLog).filter(
            QuickLog.student_id == student_id,
            QuickLog.log_type == "negative",
            QuickLog.timestamp >= two_weeks_ago
        ).count()

        if negative_logs >= 3:
            return RiskFactor(
                factor_type="recent_negative_logs",
                severity="high" if negative_logs >= 5 else "medium",
                description=f"{negative_logs} negative behavior logs in last 2 weeks",
                data_points=[f"Negative logs: {negative_logs}"],
                recommendation="Consider behavior intervention plan"
            )
        elif negative_logs >= 2:
            return RiskFactor(
                factor_type="recent_negative_logs",
                severity="medium",
                description=f"{negative_logs} negative behavior logs in last 2 weeks",
                data_points=[f"Negative logs: {negative_logs}"],
                recommendation="Monitor behavior patterns closely"
            )

        return None

    def _analyze_assessment_trends(self, student_id: int, db) -> Optional[RiskFactor]:
        """Analyze assessment trends for declining performance"""
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Get recent assessments
        recent_assessments = db.query(Assessment).filter(
            Assessment.student_id == student_id,
            Assessment.date >= thirty_days_ago
        ).order_by(Assessment.date.desc()).limit(5).all()

        if len(recent_assessments) >= 3:
            # Calculate trend
            scores = [a.percentage for a in recent_assessments if a.percentage]
            if len(scores) >= 3:
                # Check for declining trend
                declining_count = 0
                for i in range(1, len(scores)):
                    if scores[i] < scores[i-1] - 5:  # 5% decline threshold
                        declining_count += 1

                if declining_count >= 2:
                    avg_score = sum(scores) / len(scores)
                    return RiskFactor(
                        factor_type="declining_assessments",
                        severity="high" if avg_score < 60 else "medium",
                        description=f"Declining assessment trend: {declining_count} declines detected",
                        data_points=[f"Average score: {avg_score:.1f}%", f"Declines: {declining_count}"],
                        recommendation="Review learning objectives and provide additional support"
                    )

        return None

    def _analyze_positive_interactions(self, student_id: int, db) -> List[str]:
        """Analyze positive interactions and factors"""
        positive_factors = []
        two_weeks_ago = datetime.now() - timedelta(days=14)

        # Check for recent positive logs
        positive_logs = db.query(QuickLog).filter(
            QuickLog.student_id == student_id,
            QuickLog.log_type == "positive",
            QuickLog.timestamp >= two_weeks_ago
        ).count()

        if positive_logs >= 2:
            positive_factors.append(f"{positive_logs} positive behavior logs in last 2 weeks")

        # Check for recent assessments with good scores
        good_assessments = db.query(Assessment).filter(
            Assessment.student_id == student_id,
            Assessment.percentage >= 80,
            Assessment.date >= two_weeks_ago
        ).count()

        if good_assessments >= 1:
            positive_factors.append(f"{good_assessments} high-scoring assessment(s) recently")

        return positive_factors

    def _analyze_support_notes(self, student) -> Optional[RiskFactor]:
        """Analyze support notes for concerning patterns"""
        if student.support_notes:
            notes_lower = student.support_notes.lower()
            concerning_keywords = ['struggling', 'difficult', 'concern', 'worry', 'issue', 'problem']

            concerning_count = sum(1 for keyword in concerning_keywords if keyword in notes_lower)

            if concerning_count >= 2:
                return RiskFactor(
                    factor_type="multiple_support_notes",
                    severity="medium",
                    description="Multiple concerning keywords found in support notes",
                    data_points=[f"Support notes: {student.support_notes}"],
                    recommendation="Review support notes and consider additional interventions"
                )

        return None

    def _calculate_risk_level(self, risk_score: float) -> str:
        """Calculate overall risk level based on score"""
        if risk_score >= 70:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 30:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, risk_factors: List[RiskFactor], positive_factors: List[str]) -> List[str]:
        """Generate recommended actions based on risk factors"""
        recommendations = []

        # Base recommendations on risk factors
        for factor in risk_factors:
            if factor.factor_type == "high_support_level":
                recommendations.append("Schedule one-on-one meeting with student")
                recommendations.append("Review and update Individual Education Plan (IEP)")

            if factor.factor_type == "recent_negative_logs":
                recommendations.append("Implement behavior tracking system")
                recommendations.append("Consider peer mentoring program")

            if factor.factor_type == "declining_assessments":
                recommendations.append("Provide additional academic support")
                recommendations.append("Schedule parent-teacher conference")

        # Consider positive factors for balanced approach
        if positive_factors:
            recommendations.append("Build on positive behaviors and achievements")

        # General recommendations based on overall risk
        if len(risk_factors) >= 3:
            recommendations.append("Consider multi-disciplinary team review")
        elif len(risk_factors) >= 2:
            recommendations.append("Implement targeted intervention strategies")

        return list(set(recommendations))  # Remove duplicates

    def _generate_ai_enhanced_analysis(self, assessment: StudentRiskAssessment, user_query: str) -> str:
        """Generate AI-enhanced analysis using Gemini"""
        try:
            # Prepare context data for Gemini
            context_data = {
                "student_name": assessment.student_name,
                "class_code": assessment.class_code,
                "risk_level": assessment.risk_level,
                "risk_score": assessment.overall_risk_score,
                "risk_factors": [
                    {
                        "type": factor.factor_type,
                        "severity": factor.severity,
                        "description": factor.description,
                        "recommendation": factor.recommendation
                    }
                    for factor in assessment.risk_factors
                ],
                "positive_factors": assessment.positive_factors,
                "recommended_actions": assessment.recommended_actions,
                "school_context": "BIS HCMC (British International School Ho Chi Minh City)"
            }

            # Create prompt for Gemini
            prompt = f"""
            You are an expert educational psychologist at BIS HCMC analyzing student risk assessment data.

            Student Context:
            - Name: {context_data['student_name']}
            - Class: {context_data['class_code']}
            - Current Risk Level: {context_data['risk_level'].upper()} ({context_data['risk_score']:.1f}/100)

            Risk Factors Identified:
            {chr(10).join([f"- {factor['type']}: {factor['description']} (Severity: {factor['severity']})" for factor in context_data['risk_factors']])}

            Positive Factors:
            {chr(10).join([f"- {factor}" for factor in context_data['positive_factors']]) if context_data['positive_factors'] else "None identified"}

            Current Recommendations:
            {chr(10).join([f"- {action}" for action in context_data['recommended_actions']])}

            Teacher's Query: "{user_query}"

            Provide a comprehensive, context-aware analysis that:
            1. Summarizes the student's current situation
            2. Explains the risk factors in educational context
            3. Suggests specific, actionable interventions for BIS HCMC environment
            4. Considers cultural and contextual factors relevant to Vietnam/International school setting
            5. Recommends monitoring and follow-up strategies

            Format your response professionally, focusing on actionable insights for teachers.
            """

            if hasattr(self, 'gemini_client') and self.gemini_client and self.gemini_client.is_available():
                ai_response = self.gemini_client.generate_agent_response("at-risk-identifier", context_data, user_query)
                if ai_response:
                    return ai_response
                else:
                    # Fallback to basic analysis if AI fails
                    return self._generate_basic_analysis(assessment)
            else:
                # Fallback to basic analysis if AI not available
                return self._generate_basic_analysis(assessment)

        except Exception as e:
            self.logger.error(f"AI-enhanced analysis failed: {e}")
            return self._generate_basic_analysis(assessment)

    def _generate_basic_analysis(self, assessment: StudentRiskAssessment) -> str:
        """Generate basic analysis when AI is not available"""
        result_text = f"Risk Assessment for {assessment.student_name} (Class {assessment.class_code}):\n\n"
        result_text += f"**Risk Level: {assessment.risk_level.upper()}** ({assessment.overall_risk_score:.1f}/100)\n\n"

        if assessment.risk_factors:
            result_text += "**Key Risk Factors:**\n"
            for factor in assessment.risk_factors:
                result_text += f"- **{factor.factor_type.replace('_', ' ').title()}**: {factor.description}\n"
                result_text += f"  *Severity: {factor.severity.upper()}*\n"
                result_text += f"  *Recommendation: {factor.recommendation}*\n\n"

        if assessment.positive_factors:
            result_text += "**Positive Factors:**\n"
            for factor in assessment.positive_factors:
                result_text += f"- {factor}\n"
            result_text += "\n"

        if assessment.recommended_actions:
            result_text += "**Recommended Actions:**\n"
            for action in assessment.recommended_actions:
                result_text += f"- {action}\n"
            result_text += "\n"

        result_text += "*Note: This analysis is based on available data patterns. Consider additional context and professional judgment.*"

        return result_text

    def analyze_class(self, class_code: str) -> List[StudentRiskAssessment]:
        """Analyze all students in a class"""
        try:
            db = next(get_db())

            # Get all students in class
            students = db.query(Student).filter(Student.class_code == class_code).all()

            assessments = []
            for student in students:
                assessment = self.analyze_student(student.id)
                if assessment:
                    assessments.append(assessment)

            # Sort by risk score (highest first)
            assessments.sort(key=lambda x: x.overall_risk_score, reverse=True)

            self.logger.info(f"Analyzed {len(assessments)} students in class {class_code}")
            return assessments

        except Exception as e:
            self.logger.error(f"Error analyzing class {class_code}: {e}")
            return []

    def get_system_risk_summary(self) -> Dict[str, Any]:
        """Get system-wide risk summary"""
        try:
            db = next(get_db())

            # Get all students
            all_students = db.query(Student).all()

            risk_summary = {
                'total_students': len(all_students),
                'critical_risk': 0,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0,
                'risk_distribution': {},
                'common_risk_factors': {},
                'last_updated': datetime.now().isoformat()
            }

            for student in all_students:
                assessment = self.analyze_student(student.id)
                if assessment:
                    risk_summary[f'{assessment.risk_level}_risk'] += 1

                    # Track risk distribution by class
                    class_code = assessment.class_code
                    if class_code not in risk_summary['risk_distribution']:
                        risk_summary['risk_distribution'][class_code] = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                    risk_summary['risk_distribution'][class_code][assessment.risk_level] += 1

                    # Track common risk factors
                    for factor in assessment.risk_factors:
                        factor_type = factor.factor_type
                        if factor_type not in risk_summary['common_risk_factors']:
                            risk_summary['common_risk_factors'][factor_type] = 0
                        risk_summary['common_risk_factors'][factor_type] += 1

            return risk_summary

        except Exception as e:
            self.logger.error(f"Error generating system risk summary: {e}")
            return {}

# Agent interface for PTCC integration
class AtRiskStudentAgent:
    """Main agent class for PTCC integration"""

    def __init__(self):
        self.identifier = AtRiskStudentIdentifier()
        self.logger = self.identifier.logger

        # Initialize Gemini client for AI-powered analysis
        try:
            settings = get_settings()
            self.gemini_client = create_gemini_client_from_config(settings)
        except Exception as e:
            self.logger.warning(f"Failed to initialize Gemini client: {e}")
            self.gemini_client = None

    def process(self, input_data):
        """Process input request"""
        # Parse input - handle both object and dict formats
        if isinstance(input_data, dict):
            text = input_data.get('text', str(input_data))
            task_type = input_data.get('task_type', 'analyze')
            metadata = input_data.get('metadata', {})
        else:
            text = input_data.text if hasattr(input_data, 'text') else str(input_data)
            task_type = getattr(input_data, 'task_type', 'analyze')
            metadata = getattr(input_data, 'metadata', {})

        # Determine action based on task type
        if task_type == 'analyze_student' and 'student_id' in metadata:
            student_id = metadata['student_id']
            assessment = self.identifier.analyze_student(student_id)

            if assessment:
                # Use Gemini for enhanced analysis if available
                if hasattr(self, 'gemini_client') and self.gemini_client and self.gemini_client.is_available():
                    result_text = self._generate_ai_enhanced_analysis(assessment, text)
                else:
                    # Fallback to basic analysis
                    result_text = f"Risk Assessment for {assessment.student_name}:\n"
                    result_text += f"Risk Level: {assessment.risk_level.upper()} ({assessment.overall_risk_score:.1f}/100)\n"
                    result_text += f"Risk Factors: {len(assessment.risk_factors)}\n"
                    result_text += f"Positive Factors: {len(assessment.positive_factors)}\n"
                    result_text += f"Recommended Actions: {len(assessment.recommended_actions)}\n"

                    if assessment.risk_factors:
                        result_text += "\nKey Risk Factors:\n"
                        for factor in assessment.risk_factors[:3]:  # Show top 3
                            result_text += f"- {factor.factor_type}: {factor.description}\n"

                    if assessment.recommended_actions:
                        result_text += "\nRecommended Actions:\n"
                        for action in assessment.recommended_actions[:3]:  # Show top 3
                            result_text += f"- {action}\n"
            else:
                result_text = f"Could not analyze student {student_id}"

        elif task_type == 'analyze_class' and 'class_code' in metadata:
            class_code = metadata['class_code']
            assessments = self.identifier.analyze_class(class_code)

            result_text = f"Class Risk Analysis for {class_code}:\n"
            result_text += f"Students Analyzed: {len(assessments)}\n"

            risk_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            for assessment in assessments:
                risk_counts[assessment.risk_level] += 1

            result_text += f"Risk Distribution: Critical: {risk_counts['critical']}, High: {risk_counts['high']}, Medium: {risk_counts['medium']}, Low: {risk_counts['low']}\n"

            if assessments:
                top_risks = assessments[:5]  # Show top 5 at-risk students
                result_text += "\nStudents Needing Attention:\n"
                for assessment in top_risks:
                    if assessment.risk_level in ['critical', 'high']:
                        result_text += f"- {assessment.student_name}: {assessment.risk_level} risk ({assessment.overall_risk_score:.1f})\n"

        elif task_type == 'system_summary':
            summary = self.identifier.get_system_risk_summary()

            result_text = "System-Wide Risk Summary:\n"
            result_text += f"Total Students: {summary.get('total_students', 0)}\n"
            result_text += f"Critical Risk: {summary.get('critical_risk', 0)}\n"
            result_text += f"High Risk: {summary.get('high_risk', 0)}\n"
            result_text += f"Medium Risk: {summary.get('medium_risk', 0)}\n"
            result_text += f"Low Risk: {summary.get('low_risk', 0)}\n"

        else:
            result_text = "At-Risk Student Identification Agent\n"
            result_text += "Available task types: analyze_student, analyze_class, system_summary\n"
            result_text += "Include student_id or class_code in metadata"

        # Create output
        return {
            "result": result_text,
            "explanation": f"Risk analysis completed for task type: {task_type}",
            "confidence": 0.9,
            "metadata": {
                'task_type': task_type,
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_type': 'at_risk_identifier',
                'ai_enhanced': self.gemini_client and self.gemini_client.is_available()
            }
        }

# Standalone testing
if __name__ == "__main__":
    print("🛡️ At-Risk Student Identification Agent")
    print("=" * 50)

    agent = AtRiskStudentAgent()

    # Test student analysis
    print("Testing student analysis...")
    test_input = {
        "text": "Analyze student for risk factors",
        "task_type": "analyze_student",
        "metadata": {"student_id": 1}
    }

    result = agent.process(test_input)
    print("Result:", result.result[:200] + "..." if len(result.result) > 200 else result.result)

    print("\n✅ Agent test completed!")