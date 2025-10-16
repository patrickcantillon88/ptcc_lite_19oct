#!/usr/bin/env python3
"""
Personalized Learning Path Agent for PTCC

Creates individualized learning paths for students based on their assessment data,
learning patterns, and identified strengths and weaknesses.

Features:
- Analyzes assessment results and trends
- Identifies learning gaps and strengths
- Creates personalized learning objectives
- Suggests targeted interventions and resources
- Tracks progress toward learning goals
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

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
    from backend.models.database_models import Student, Assessment, QuickLog
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
class LearningGap:
    """Identified learning gap for a student"""
    subject: str
    skill_area: str
    current_level: str
    target_level: str
    gap_size: str  # small, medium, large
    priority: str  # low, medium, high
    suggested_interventions: List[str]
    estimated_timeframe: str

@dataclass
class LearningStrength:
    """Identified learning strength for a student"""
    subject: str
    skill_area: str
    strength_level: str
    leverage_opportunities: List[str]
    extension_activities: List[str]

@dataclass
class LearningObjective:
    """Specific learning objective for a student"""
    objective_id: str
    subject: str
    skill_area: str
    description: str
    success_criteria: List[str]
    target_date: datetime
    priority: str
    resources_needed: List[str]
    progress_indicators: List[str]

@dataclass
class PersonalizedLearningPath:
    """Complete personalized learning path for a student"""
    student_id: int
    student_name: str
    class_code: str
    assessment_date: datetime
    learning_gaps: List[LearningGap]
    learning_strengths: List[LearningStrength]
    learning_objectives: List[LearningObjective]
    overall_recommendations: List[str]
    monitoring_schedule: Dict[str, str]
    expected_progress_timeline: Dict[str, str]

class LearningPathBuilder:
    """Builds personalized learning paths from database data"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.subject_areas = {
            'math': ['numbers', 'algebra', 'geometry', 'data', 'measurement'],
            'english': ['reading', 'writing', 'grammar', 'vocabulary', 'comprehension'],
            'science': ['biology', 'chemistry', 'physics', 'earth_science', 'investigation']
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger("learning_path_agent")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def create_learning_path(self, student_id: int) -> Optional[PersonalizedLearningPath]:
        """Create a personalized learning path for a student"""
        if not PTCC_MODULES_AVAILABLE:
            self.logger.error("PTCC modules not available - cannot create learning path")
            return None

        try:
            db = next(get_db())

            # Get student information
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                self.logger.error(f"Student {student_id} not found")
                return None

            # Analyze recent assessments
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_assessments = db.query(Assessment).filter(
                Assessment.student_id == student_id,
                Assessment.date >= thirty_days_ago
            ).order_by(Assessment.date.desc()).all()

            # Analyze all assessments for trends
            all_assessments = db.query(Assessment).filter(
                Assessment.student_id == student_id
            ).order_by(Assessment.date.desc()).all()

            # Identify learning gaps
            learning_gaps = self._identify_learning_gaps(student, recent_assessments)

            # Identify learning strengths
            learning_strengths = self._identify_learning_strengths(student, all_assessments)

            # Create learning objectives
            learning_objectives = self._create_learning_objectives(student, learning_gaps, learning_strengths)

            # Generate overall recommendations
            overall_recommendations = self._generate_overall_recommendations(learning_gaps, learning_strengths)

            # Create monitoring schedule
            monitoring_schedule = self._create_monitoring_schedule(learning_objectives)

            # Create progress timeline
            expected_timeline = self._create_progress_timeline(learning_objectives)

            return PersonalizedLearningPath(
                student_id=student_id,
                student_name=student.name,
                class_code=student.class_code,
                assessment_date=datetime.now(),
                learning_gaps=learning_gaps,
                learning_strengths=learning_strengths,
                learning_objectives=learning_objectives,
                overall_recommendations=overall_recommendations,
                monitoring_schedule=monitoring_schedule,
                expected_progress_timeline=expected_timeline
            )

        except Exception as e:
            self.logger.error(f"Error creating learning path for student {student_id}: {e}")
            return None

    def _identify_learning_gaps(self, student, assessments: List) -> List[LearningGap]:
        """Identify areas where student needs improvement"""
        gaps = []

        if not assessments:
            return gaps

        # Group assessments by subject
        subject_assessments = defaultdict(list)
        for assessment in assessments:
            if assessment.subject:
                subject_assessments[assessment.subject.lower()].append(assessment)

        # Analyze each subject for gaps
        for subject, subject_tests in subject_assessments.items():
            if len(subject_tests) >= 2:
                # Calculate average performance
                scores = [a.percentage for a in subject_tests if a.percentage]
                if scores:
                    avg_score = sum(scores) / len(scores)

                    # Identify gaps based on score thresholds
                    if avg_score < 60:
                        gap_size = "large"
                        priority = "high"
                    elif avg_score < 75:
                        gap_size = "medium"
                        priority = "medium"
                    else:
                        gap_size = "small"
                        priority = "low"

                    if avg_score < 80:  # Only create gaps for scores below 80%
                        gaps.append(LearningGap(
                            subject=subject,
                            skill_area=self._identify_skill_area(subject, scores),
                            current_level=self._determine_current_level(avg_score),
                            target_level=self._determine_target_level(subject, avg_score),
                            gap_size=gap_size,
                            priority=priority,
                            suggested_interventions=self._suggest_interventions(subject, gap_size),
                            estimated_timeframe=self._estimate_timeframe(gap_size, priority)
                        ))

        return gaps

    def _identify_learning_strengths(self, student, assessments: List) -> List[LearningStrength]:
        """Identify areas where student excels"""
        strengths = []

        if not assessments:
            return strengths

        # Group assessments by subject
        subject_assessments = defaultdict(list)
        for assessment in assessments:
            if assessment.subject:
                subject_assessments[assessment.subject.lower()].append(assessment)

        # Identify strengths based on high performance
        for subject, subject_tests in subject_assessments.items():
            scores = [a.percentage for a in subject_tests if a.percentage]
            if scores:
                avg_score = sum(scores) / len(scores)

                if avg_score >= 85:  # High performance threshold
                    strength_level = "exceptional" if avg_score >= 95 else "strong"

                    strengths.append(LearningStrength(
                        subject=subject,
                        skill_area=self._identify_skill_area(subject, scores),
                        strength_level=strength_level,
                        leverage_opportunities=self._suggest_leverage_opportunities(subject, strength_level),
                        extension_activities=self._suggest_extension_activities(subject, strength_level)
                    ))

        return strengths

    def _identify_skill_area(self, subject: str, scores: List[float]) -> str:
        """Identify specific skill area within a subject"""
        # Simplified skill area identification
        avg_score = sum(scores) / len(scores)

        skill_areas = {
            'math': ['numbers', 'algebra', 'geometry', 'data', 'measurement'],
            'english': ['reading', 'writing', 'grammar', 'vocabulary', 'comprehension'],
            'science': ['biology', 'chemistry', 'physics', 'earth_science', 'investigation']
        }

        areas = skill_areas.get(subject.lower(), ['general'])
        return areas[0]  # Return first area for now

    def _determine_current_level(self, avg_score: float) -> str:
        """Determine current performance level"""
        if avg_score >= 90:
            return "advanced"
        elif avg_score >= 75:
            return "proficient"
        elif avg_score >= 60:
            return "developing"
        else:
            return "beginning"

    def _determine_target_level(self, subject: str, current_score: float) -> str:
        """Determine appropriate target level"""
        # Set realistic targets based on current performance
        if current_score >= 85:
            return "advanced"
        elif current_score >= 70:
            return "proficient"
        elif current_score >= 50:
            return "developing"
        else:
            return "beginning"

    def _suggest_interventions(self, subject: str, gap_size: str) -> List[str]:
        """Suggest interventions based on subject and gap size"""
        interventions = {
            'math': {
                'small': ['Peer tutoring', 'Online math games', 'Extra practice worksheets'],
                'medium': ['Small group instruction', 'Math manipulatives', 'Visual aids'],
                'large': ['One-on-one tutoring', 'Intensive intervention program', 'Modified curriculum']
            },
            'english': {
                'small': ['Reading buddies', 'Vocabulary building apps', 'Writing journals'],
                'medium': ['Reading intervention program', 'Writing workshops', 'Phonics support'],
                'large': ['Intensive reading support', 'Speech therapy referral', 'Modified English program']
            },
            'science': {
                'small': ['Hands-on experiments', 'Science kits', 'Field trips'],
                'medium': ['Small group experiments', 'Visual demonstrations', 'Simplified concepts'],
                'large': ['Concrete learning materials', 'Multi-sensory approach', 'Extended time']
            }
        }

        return interventions.get(subject.lower(), {}).get(gap_size, ['General academic support'])

    def _estimate_timeframe(self, gap_size: str, priority: str) -> str:
        """Estimate timeframe for improvement"""
        if priority == "high":
            if gap_size == "large":
                return "6-8 weeks intensive support"
            else:
                return "4-6 weeks targeted intervention"
        elif priority == "medium":
            return "8-10 weeks sustained support"
        else:
            return "10-12 weeks ongoing monitoring"

    def _suggest_leverage_opportunities(self, subject: str, strength_level: str) -> List[str]:
        """Suggest ways to leverage student strengths"""
        opportunities = {
            'math': [
                'Peer tutoring in math',
                'Math club leadership',
                'Competition preparation'
            ],
            'english': [
                'Writing club participation',
                'School newspaper contribution',
                'Reading buddy program'
            ],
            'science': [
                'Science fair projects',
                'Laboratory assistance',
                'Science club activities'
            ]
        }

        return opportunities.get(subject.lower(), ['Peer mentoring opportunities'])

    def _suggest_extension_activities(self, subject: str, strength_level: str) -> List[str]:
        """Suggest extension activities for advanced students"""
        activities = {
            'math': [
                'Advanced problem solving',
                'Math competitions',
                'Independent research projects'
            ],
            'english': [
                'Creative writing projects',
                'Literature analysis',
                'Public speaking opportunities'
            ],
            'science': [
                'Independent experiments',
                'Research projects',
                'Science fair leadership'
            ]
        }

        return activities.get(subject.lower(), ['Advanced independent study'])

    def _create_learning_objectives(self, student, learning_gaps: List[LearningGap], learning_strengths: List[LearningStrength]) -> List[LearningObjective]:
        """Create specific learning objectives"""
        objectives = []

        # Create objectives based on learning gaps
        for i, gap in enumerate(learning_gaps[:3]):  # Limit to top 3 gaps
            objectives.append(LearningObjective(
                objective_id=f"obj_{student.id}_{i+1}",
                subject=gap.subject,
                skill_area=gap.skill_area,
                description=f"Improve {gap.skill_area} skills in {gap.subject}",
                success_criteria=[
                    f"Achieve {gap.target_level} level performance",
                    "Demonstrate consistent improvement in assessments",
                    "Show confidence in applying skills"
                ],
                target_date=datetime.now() + timedelta(weeks=self._weeks_for_timeframe(gap.estimated_timeframe)),
                priority=gap.priority,
                resources_needed=gap.suggested_interventions[:2],
                progress_indicators=[
                    "Weekly assessment scores",
                    "Class participation",
                    "Homework completion rates"
                ]
            ))

        # Create objectives to leverage strengths
        for i, strength in enumerate(learning_strengths[:2]):  # Limit to top 2 strengths
            objectives.append(LearningObjective(
                objective_id=f"obj_{student.id}_strength_{i+1}",
                subject=strength.subject,
                skill_area=strength.skill_area,
                description=f"Leverage {strength.skill_area} strengths in {strength.subject}",
                success_criteria=[
                    "Successfully complete extension activities",
                    "Demonstrate leadership in strength area",
                    "Help peers in area of expertise"
                ],
                target_date=datetime.now() + timedelta(weeks=8),
                priority="medium",
                resources_needed=strength.extension_activities[:2],
                progress_indicators=[
                    "Extension activity completion",
                    "Peer mentoring instances",
                    "Leadership role participation"
                ]
            ))

        return objectives

    def _weeks_for_timeframe(self, timeframe: str) -> int:
        """Convert timeframe string to weeks"""
        if "intensive" in timeframe or "4-6 weeks" in timeframe:
            return 6
        elif "8-10 weeks" in timeframe:
            return 9
        elif "10-12 weeks" in timeframe:
            return 11
        else:
            return 8

    def _generate_overall_recommendations(self, learning_gaps: List[LearningGap], learning_strengths: List[LearningStrength]) -> List[str]:
        """Generate overall recommendations for the student"""
        recommendations = []

        # Gap-based recommendations
        if learning_gaps:
            high_priority_gaps = [g for g in learning_gaps if g.priority == "high"]
            if high_priority_gaps:
                recommendations.append(f"Focus on {len(high_priority_gaps)} high-priority learning gaps")
                recommendations.append("Consider multi-disciplinary team review")

        # Strength-based recommendations
        if learning_strengths:
            recommendations.append(f"Leverage {len(learning_strengths)} identified strengths for motivation")
            recommendations.append("Use strength areas for peer mentoring opportunities")

        # General recommendations
        if len(learning_gaps) > len(learning_strengths):
            recommendations.append("Implement intensive support program")
        elif len(learning_strengths) > len(learning_gaps):
            recommendations.append("Build confidence through strength-based activities")

        recommendations.append("Schedule regular progress monitoring meetings")

        return recommendations

    def _create_monitoring_schedule(self, objectives: List[LearningObjective]) -> Dict[str, str]:
        """Create monitoring schedule for learning objectives"""
        schedule = {}

        for objective in objectives:
            if objective.priority == "high":
                schedule[objective.objective_id] = "Weekly monitoring"
            elif objective.priority == "medium":
                schedule[objective.objective_id] = "Bi-weekly monitoring"
            else:
                schedule[objective.objective_id] = "Monthly monitoring"

        return schedule

    def _create_progress_timeline(self, objectives: List[LearningObjective]) -> Dict[str, str]:
        """Create expected progress timeline"""
        timeline = {}

        for objective in objectives:
            weeks = self._weeks_for_timeframe("8-10 weeks")  # Default timeframe
            target_date = datetime.now() + timedelta(weeks=weeks)

            timeline[objective.objective_id] = target_date.strftime("%Y-%m-%d")

        return timeline

    def analyze_class_learning_paths(self, class_code: str) -> Dict[str, Any]:
        """Analyze learning paths for all students in a class"""
        try:
            db = next(get_db())

            # Get all students in class
            students = db.query(Student).filter(Student.class_code == class_code).all()

            class_analysis = {
                'class_code': class_code,
                'total_students': len(students),
                'students_with_paths': 0,
                'common_learning_gaps': defaultdict(int),
                'common_strengths': defaultdict(int),
                'overall_class_needs': [],
                'individual_paths': []
            }

            for student in students:
                learning_path = self.create_learning_path(student.id)
                if learning_path:
                    class_analysis['students_with_paths'] += 1

                    # Aggregate common gaps and strengths
                    for gap in learning_path.learning_gaps:
                        class_analysis['common_learning_gaps'][f"{gap.subject}_{gap.skill_area}"] += 1

                    for strength in learning_path.learning_strengths:
                        class_analysis['common_strengths'][f"{strength.subject}_{strength.skill_area}"] += 1

                    class_analysis['individual_paths'].append({
                        'student_id': student.id,
                        'student_name': student.name,
                        'gap_count': len(learning_path.learning_gaps),
                        'strength_count': len(learning_path.learning_strengths),
                        'high_priority_objectives': len([obj for obj in learning_path.learning_objectives if obj.priority == "high"])
                    })

            # Identify overall class needs
            class_analysis['overall_class_needs'] = self._identify_class_needs(class_analysis)

            return class_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing class learning paths for {class_code}: {e}")
            return {}

    def _identify_class_needs(self, class_analysis: Dict[str, Any]) -> List[str]:
        """Identify overall needs for the class"""
        needs = []

        # Find most common learning gaps
        if class_analysis['common_learning_gaps']:
            most_common_gaps = sorted(
                class_analysis['common_learning_gaps'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            for gap, count in most_common_gaps:
                if count >= class_analysis['total_students'] * 0.3:  # Affects 30%+ of students
                    needs.append(f"Class-wide support needed for {gap} ({count} students)")

        # General class recommendations
        if class_analysis['students_with_paths'] < class_analysis['total_students'] * 0.7:
            needs.append("Conduct class-wide academic screening")

        return needs

    def _generate_ai_enhanced_learning_path(self, learning_path: PersonalizedLearningPath, user_query: str) -> str:
        """Generate AI-enhanced learning path analysis using Gemini"""
        try:
            # Prepare context data for Gemini
            context_data = {
                "student_name": learning_path.student_name,
                "class_code": learning_path.class_code,
                "school_context": "BIS HCMC (British International School Ho Chi Minh City)",
                "learning_gaps": [
                    {
                        "subject": gap.subject,
                        "skill_area": gap.skill_area,
                        "current_level": gap.current_level,
                        "target_level": gap.target_level,
                        "gap_size": gap.gap_size,
                        "priority": gap.priority,
                        "interventions": gap.suggested_interventions,
                        "timeframe": gap.estimated_timeframe
                    }
                    for gap in learning_path.learning_gaps
                ],
                "learning_strengths": [
                    {
                        "subject": strength.subject,
                        "skill_area": strength.skill_area,
                        "strength_level": strength.strength_level,
                        "leverage_opportunities": strength.leverage_opportunities,
                        "extension_activities": strength.extension_activities
                    }
                    for strength in learning_path.learning_strengths
                ],
                "learning_objectives": [
                    {
                        "description": obj.description,
                        "subject": obj.subject,
                        "skill_area": obj.skill_area,
                        "priority": obj.priority,
                        "target_date": obj.target_date.strftime("%Y-%m-%d"),
                        "success_criteria": obj.success_criteria,
                        "resources": obj.resources_needed
                    }
                    for obj in learning_path.learning_objectives
                ],
                "overall_recommendations": learning_path.overall_recommendations,
                "monitoring_schedule": learning_path.monitoring_schedule,
                "progress_timeline": learning_path.expected_progress_timeline
            }

            # Create prompt for Gemini
            prompt = f"""
            You are an expert educational psychologist and learning specialist at BIS HCMC analyzing a personalized learning path for a student.

            Student Context:
            - Name: {context_data['student_name']}
            - Class: {context_data['class_code']}
            - School: BIS HCMC (British International School Ho Chi Minh City)

            Learning Gaps Identified:
            {chr(10).join([f"- {gap['subject']} ({gap['skill_area']}): {gap['gap_size']} gap, {gap['priority']} priority, current: {gap['current_level']}, target: {gap['target_level']}" for gap in context_data['learning_gaps']])}

            Learning Strengths Identified:
            {chr(10).join([f"- {strength['subject']} ({strength['skill_area']}): {strength['strength_level']} level" for strength in context_data['learning_strengths']])}

            Current Learning Objectives:
            {chr(10).join([f"- {obj['description']} (Priority: {obj['priority']}, Target: {obj['target_date']})" for obj in context_data['learning_objectives']])}

            Teacher's Query: "{user_query}"

            Provide a comprehensive, context-aware learning path analysis that:
            1. Summarizes the student's current learning profile and needs
            2. Explains the identified gaps and strengths in educational context
            3. Evaluates the appropriateness and sequencing of learning objectives
            4. Suggests specific implementation strategies for BIS HCMC environment
            5. Considers cultural, linguistic, and contextual factors relevant to Vietnam/International school setting
            6. Recommends differentiation strategies and progress monitoring approaches
            7. Suggests ways to leverage strengths while addressing gaps

            Format your response professionally, focusing on practical, actionable recommendations for teachers and individualized learning support.
            """

            if hasattr(self, 'gemini_client') and self.gemini_client and self.gemini_client.is_available():
                ai_response = self.gemini_client.generate_agent_response("learning-path-creator", context_data, user_query)
                if ai_response:
                    return ai_response
                else:
                    # Fallback to basic analysis
                    return self._generate_basic_learning_path(learning_path)
            else:
                # Fallback to basic analysis if AI not available
                return self._generate_basic_learning_path(learning_path)

        except Exception as e:
            self.logger.error(f"AI-enhanced learning path analysis failed: {e}")
            return self._generate_basic_learning_path(learning_path)

    def _generate_basic_learning_path(self, learning_path: PersonalizedLearningPath) -> str:
        """Generate basic learning path analysis when AI is not available"""
        result_text = f"Personalized Learning Path for {learning_path.student_name} (Class {learning_path.class_code}):\n\n"
        result_text += f"**Learning Gaps:** {len(learning_path.learning_gaps)}\n"
        result_text += f"**Learning Strengths:** {len(learning_path.learning_strengths)}\n"
        result_text += f"**Learning Objectives:** {len(learning_path.learning_objectives)}\n\n"

        if learning_path.learning_gaps:
            result_text += "**Priority Learning Gaps:**\n"
            for gap in learning_path.learning_gaps[:3]:
                result_text += f"- **{gap.subject}** ({gap.skill_area}): {gap.gap_size} gap, {gap.priority} priority\n"
                result_text += f"  *Current Level:* {gap.current_level} | *Target Level:* {gap.target_level}\n"
                result_text += f"  *Suggested Interventions:* {', '.join(gap.suggested_interventions[:2])}\n\n"

        if learning_path.learning_strengths:
            result_text += "**Key Learning Strengths:**\n"
            for strength in learning_path.learning_strengths[:2]:
                result_text += f"- **{strength.subject}** ({strength.skill_area}): {strength.strength_level} level\n"
                result_text += f"  *Leverage Opportunities:* {', '.join(strength.leverage_opportunities[:2])}\n\n"

        if learning_path.learning_objectives:
            result_text += "**Current Learning Objectives:**\n"
            for objective in learning_path.learning_objectives[:3]:
                result_text += f"- **{objective.description}**\n"
                result_text += f"  *Priority:* {objective.priority} | *Target Date:* {objective.target_date.strftime('%Y-%m-%d')}\n"
                result_text += f"  *Success Criteria:* {', '.join(objective.success_criteria[:2])}\n\n"

        if learning_path.overall_recommendations:
            result_text += "**Overall Recommendations:**\n"
            for rec in learning_path.overall_recommendations[:3]:
                result_text += f"- {rec}\n"
            result_text += "\n"

        result_text += "*Note: This learning path is based on available assessment data. Regular monitoring and adjustment is recommended.*"

        return result_text

# Agent interface for PTCC integration
class PersonalizedLearningPathAgent:
    """Main agent class for PTCC integration"""

    def __init__(self):
        self.path_creator = LearningPathBuilder()
        self.logger = self.path_creator.logger

        # Initialize Gemini client for AI-powered analysis
        try:
            settings = get_settings()
            self.gemini_client = create_gemini_client_from_config(settings)
        except Exception as e:
            self.logger.warning(f"Failed to initialize Gemini client: {e}")
            self.gemini_client = None

    def process(self, input_data):
        """Process input request"""
        # Parse input
        if isinstance(input_data, dict):
            text = input_data.get('text', str(input_data))
            task_type = input_data.get('task_type', 'create_path')
            metadata = input_data.get('metadata', {})
        else:
            text = input_data.text if hasattr(input_data, 'text') else str(input_data)
            task_type = getattr(input_data, 'task_type', 'create_path')
            metadata = getattr(input_data, 'metadata', {})

        # Determine action based on task type
        if task_type == 'create_path' and 'student_id' in metadata:
            student_id = metadata['student_id']
            learning_path = self.path_creator.create_learning_path(student_id)

            if learning_path:
                # Use Gemini for enhanced analysis if available
                if hasattr(self, 'gemini_client') and self.gemini_client and self.gemini_client.is_available():
                    result_text = self._generate_ai_enhanced_learning_path(learning_path, text)
                else:
                    # Fallback to basic analysis
                    result_text = f"Personalized Learning Path for {learning_path.student_name}:\n"
                    result_text += f"Learning Gaps: {len(learning_path.learning_gaps)}\n"
                    result_text += f"Learning Strengths: {len(learning_path.learning_strengths)}\n"
                    result_text += f"Learning Objectives: {len(learning_path.learning_objectives)}\n"

                    if learning_path.learning_gaps:
                        result_text += "\nPriority Learning Gaps:\n"
                        for gap in learning_path.learning_gaps[:3]:
                            result_text += f"- {gap.subject} ({gap.skill_area}): {gap.gap_size} gap, {gap.priority} priority\n"

                    if learning_path.learning_objectives:
                        result_text += "\nKey Learning Objectives:\n"
                        for objective in learning_path.learning_objectives[:3]:
                            result_text += f"- {objective.description} (Target: {objective.target_date.strftime('%Y-%m-%d')})\n"

                    if learning_path.overall_recommendations:
                        result_text += "\nOverall Recommendations:\n"
                        for rec in learning_path.overall_recommendations[:3]:
                            result_text += f"- {rec}\n"
            else:
                result_text = f"Could not create learning path for student {student_id}"

        elif task_type == 'analyze_class' and 'class_code' in metadata:
            class_code = metadata['class_code']
            class_analysis = self.path_creator.analyze_class_learning_paths(class_code)

            result_text = f"Class Learning Path Analysis for {class_code}:\n"
            result_text += f"Students Analyzed: {class_analysis.get('students_with_paths', 0)}/{class_analysis.get('total_students', 0)}\n"

            common_gaps = class_analysis.get('common_learning_gaps', {})
            if common_gaps:
                most_common = sorted(common_gaps.items(), key=lambda x: x[1], reverse=True)[:3]
                result_text += "\nMost Common Learning Gaps:\n"
                for gap, count in most_common:
                    result_text += f"- {gap}: {count} students\n"

            class_needs = class_analysis.get('overall_class_needs', [])
            if class_needs:
                result_text += "\nClass-wide Needs:\n"
                for need in class_needs:
                    result_text += f"- {need}\n"

        else:
            result_text = "Personalized Learning Path Agent\n"
            result_text += "Available task types: create_path, analyze_class\n"
            result_text += "Include student_id or class_code in metadata"

        # Create output
        return {
            "result": result_text,
            "explanation": f"Learning path analysis completed for task type: {task_type}",
            "confidence": 0.9,
            "metadata": {
                'task_type': task_type,
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_type': 'learning_path',
                'ai_enhanced': self.gemini_client and self.gemini_client.is_available()
            }
        }

# Standalone testing
if __name__ == "__main__":
    print("🎯 Personalized Learning Path Agent")
    print("=" * 50)

    agent = PersonalizedLearningPathAgent()

    # Test learning path creation
    print("Testing learning path creation...")
    test_input = {
        "text": "Create personalized learning path",
        "task_type": "create_path",
        "metadata": {"student_id": 1}
    }

    result = agent.process(test_input)
    print("Result:", result.result[:300] + "..." if len(result.result) > 300 else result.result)

    print("\n✅ Agent test completed!")