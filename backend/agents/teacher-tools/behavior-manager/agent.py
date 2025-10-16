#!/usr/bin/env python3
"""
Classroom Behavior Management Agent for PTCC

Helps teachers optimize classroom seating arrangements and implement behavior interventions
based on student behavior patterns and interaction data.

Features:
- Analyzes student behavior patterns and interactions
- Suggests optimal seating arrangements
- Recommends behavior intervention strategies
- Identifies positive peer relationships
- Tracks behavior improvement over time
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
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
    from backend.models.database_models import Student, QuickLog
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
class StudentBehaviorProfile:
    """Behavior profile for a single student"""
    student_id: int
    student_name: str
    class_code: str
    behavior_score: float  # -100 to 100, negative = challenging, positive = cooperative
    interaction_patterns: Dict[str, int]  # student_id -> interaction_count
    preferred_peers: List[int]  # student_ids of preferred peers
    challenging_peers: List[int]  # student_ids that cause issues
    behavior_trends: List[str]  # recent behavior trends
    support_needs: List[str]  # identified support needs

@dataclass
class SeatingRecommendation:
    """Seating arrangement recommendation"""
    arrangement_name: str
    description: str
    seating_plan: Dict[str, List[int]]  # row -> list of student_ids
    rationale: List[str]
    expected_benefits: List[str]
    potential_challenges: List[str]
    implementation_tips: List[str]

@dataclass
class BehaviorIntervention:
    """Behavior intervention recommendation"""
    intervention_type: str
    target_students: List[int]
    description: str
    expected_outcomes: List[str]
    implementation_steps: List[str]
    monitoring_metrics: List[str]
    timeline: str

class ClassroomBehaviorManager:
    """Agent for managing classroom behavior and seating arrangements"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.behavior_weights = {
            'positive_log': 10,
            'negative_log': -15,
            'neutral_log': 0,
            'peer_interaction': 5,
            'support_level': -20,
            'recent_improvement': 15
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger("behavior_manager")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def analyze_class_behavior(self, class_code: str) -> Dict[str, Any]:
        """Analyze behavior patterns for all students in a class"""
        if not PTCC_MODULES_AVAILABLE:
            self.logger.error("PTCC modules not available - cannot analyze class behavior")
            return {}

        try:
            db = next(get_db())

            # Get all students in class
            students = db.query(Student).filter(Student.class_code == class_code).all()

            behavior_profiles = {}
            class_summary = {
                'class_code': class_code,
                'total_students': len(students),
                'behavior_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'average_behavior_score': 0,
                'peer_interaction_network': {},
                'recommended_interventions': [],
                'seating_recommendations': []
            }

            total_score = 0

            for student in students:
                profile = self._analyze_student_behavior(student.id, db)
                if profile:
                    behavior_profiles[student.id] = profile
                    total_score += profile.behavior_score

                    # Update class summary
                    if profile.behavior_score > 10:
                        class_summary['behavior_distribution']['positive'] += 1
                    elif profile.behavior_score < -10:
                        class_summary['behavior_distribution']['negative'] += 1
                    else:
                        class_summary['behavior_distribution']['neutral'] += 1

            class_summary['average_behavior_score'] = total_score / len(students) if students else 0

            # Generate peer interaction network
            class_summary['peer_interaction_network'] = self._analyze_peer_interactions(behavior_profiles)

            # Generate recommendations
            class_summary['recommended_interventions'] = self._generate_interventions(behavior_profiles)
            class_summary['seating_recommendations'] = self._generate_seating_recommendations(behavior_profiles, class_code)

            return class_summary

        except Exception as e:
            self.logger.error(f"Error analyzing class behavior for {class_code}: {e}")
            return {}

    def _analyze_student_behavior(self, student_id: int, db) -> Optional[StudentBehaviorProfile]:
        """Analyze individual student behavior patterns"""
        try:
            # Get student info
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return None

            # Analyze behavior logs
            thirty_days_ago = datetime.now() - timedelta(days=30)
            behavior_logs = db.query(QuickLog).filter(
                QuickLog.student_id == student_id,
                QuickLog.timestamp >= thirty_days_ago
            ).all()

            behavior_score = 0
            interaction_patterns = defaultdict(int)
            behavior_trends = []
            support_needs = []

            # Calculate behavior score based on logs
            for log in behavior_logs:
                if log.log_type == "positive":
                    behavior_score += self.behavior_weights['positive_log']
                    behavior_trends.append("positive_behavior")
                elif log.log_type == "negative":
                    behavior_score += self.behavior_weights['negative_log']
                    behavior_trends.append("challenging_behavior")
                else:
                    behavior_score += self.behavior_weights['neutral_log']

                # Track interactions if mentioned
                if log.note and any(peer in log.note.lower() for peer in ['peer', 'friend', 'group', 'partner']):
                    interaction_patterns['peer_interaction'] += 1

            # Adjust for support level
            if student.support_level >= 2:
                behavior_score += self.behavior_weights['support_level']
                support_needs.append(f"High support level ({student.support_level})")

            # Identify preferred and challenging peers based on interaction patterns
            preferred_peers, challenging_peers = self._identify_peer_relationships(student_id, behavior_logs, db)

            return StudentBehaviorProfile(
                student_id=student_id,
                student_name=student.name,
                class_code=student.class_code,
                behavior_score=min(max(behavior_score, -100), 100),  # Clamp to -100 to 100
                interaction_patterns=dict(interaction_patterns),
                preferred_peers=preferred_peers,
                challenging_peers=challenging_peers,
                behavior_trends=list(set(behavior_trends)),  # Remove duplicates
                support_needs=support_needs
            )

        except Exception as e:
            self.logger.error(f"Error analyzing student {student_id}: {e}")
            return None

    def _identify_peer_relationships(self, student_id: int, behavior_logs: List, db) -> Tuple[List[int], List[int]]:
        """Identify positive and challenging peer relationships"""
        preferred_peers = []
        challenging_peers = []

        # This is a simplified analysis - in practice, you'd analyze log content
        # for mentions of specific peers and their context

        # For now, we'll use a basic heuristic based on log frequency and type
        peer_mention_count = defaultdict(lambda: {'positive': 0, 'negative': 0})

        for log in behavior_logs:
            if log.note:
                # Simple keyword-based analysis (would be more sophisticated in practice)
                note_lower = log.note.lower()
                if any(pos_word in note_lower for pos_word in ['helped', 'worked well', 'positive', 'friend']):
                    peer_mention_count['positive_context']['count'] = peer_mention_count['positive_context'].get('count', 0) + 1
                elif any(neg_word in note_lower for neg_word in ['conflict', 'argument', 'issue', 'problem']):
                    peer_mention_count['negative_context']['count'] = peer_mention_count['negative_context'].get('count', 0) + 1

        # Convert context counts to peer preferences (simplified)
        if peer_mention_count['positive_context'].get('count', 0) > peer_mention_count['negative_context'].get('count', 0):
            preferred_peers.append(-1)  # Placeholder for positive peer relationships
        elif peer_mention_count['negative_context'].get('count', 0) > 0:
            challenging_peers.append(-1)  # Placeholder for challenging peer relationships

        return preferred_peers, challenging_peers

    def _analyze_peer_interactions(self, behavior_profiles: Dict[int, StudentBehaviorProfile]) -> Dict[str, Any]:
        """Analyze peer interaction patterns across the class"""
        interaction_network = {
            'strong_positive_relationships': [],
            'potential_conflicts': [],
            'isolated_students': [],
            'social_butterflies': []
        }

        # Identify students with many positive interactions
        for profile in behavior_profiles.values():
            if profile.behavior_score > 20:
                interaction_network['strong_positive_relationships'].append({
                    'student_id': profile.student_id,
                    'student_name': profile.student_name,
                    'interaction_count': sum(profile.interaction_patterns.values())
                })

            # Identify potentially isolated students
            if sum(profile.interaction_patterns.values()) < 2 and profile.behavior_score < 0:
                interaction_network['isolated_students'].append({
                    'student_id': profile.student_id,
                    'student_name': profile.student_name,
                    'behavior_score': profile.behavior_score
                })

        return interaction_network

    def _generate_interventions(self, behavior_profiles: Dict[int, StudentBehaviorProfile]) -> List[BehaviorIntervention]:
        """Generate behavior intervention recommendations"""
        interventions = []

        # Identify students needing interventions
        challenging_students = [
            profile for profile in behavior_profiles.values()
            if profile.behavior_score < -20
        ]

        if challenging_students:
            interventions.append(BehaviorIntervention(
                intervention_type="individual_behavior_support",
                target_students=[s.student_id for s in challenging_students],
                description=f"Individual behavior support for {len(challenging_students)} students with challenging behavior patterns",
                expected_outcomes=[
                    "Improved behavior scores",
                    "Better peer interactions",
                    "Increased engagement in class activities"
                ],
                implementation_steps=[
                    "Schedule one-on-one meetings with identified students",
                    "Create individual behavior tracking sheets",
                    "Implement daily check-in routines",
                    "Establish clear behavior expectations and consequences"
                ],
                monitoring_metrics=[
                    "Daily behavior log entries",
                    "Peer interaction frequency",
                    "Academic engagement indicators"
                ],
                timeline="2-4 weeks for initial improvements"
            ))

        # Group interventions for students with similar needs
        high_support_students = [
            profile for profile in behavior_profiles.values()
            if profile.support_needs
        ]

        if high_support_students:
            interventions.append(BehaviorIntervention(
                intervention_type="peer_buddy_system",
                target_students=[s.student_id for s in high_support_students],
                description="Pair high-support students with positive peer buddies for mutual support",
                expected_outcomes=[
                    "Improved social integration",
                    "Increased positive peer interactions",
                    "Enhanced self-confidence"
                ],
                implementation_steps=[
                    "Identify positive peer buddies for each high-support student",
                    "Train peer buddies in supportive communication",
                    "Establish regular buddy check-in times",
                    "Monitor and celebrate successful pairings"
                ],
                monitoring_metrics=[
                    "Buddy interaction frequency",
                    "Student confidence ratings",
                    "Reduction in negative incidents"
                ],
                timeline="Ongoing with monthly reviews"
            ))

        return interventions

    def _generate_seating_recommendations(self, behavior_profiles: Dict[int, StudentBehaviorProfile], class_code: str) -> List[SeatingRecommendation]:
        """Generate seating arrangement recommendations"""
        recommendations = []

        # Strategy 1: Separate challenging students
        challenging_students = [
            (sid, profile) for sid, profile in behavior_profiles.items()
            if profile.behavior_score < -10
        ]

        if len(challenging_students) >= 2:
            recommendations.append(SeatingRecommendation(
                arrangement_name="Dispersed Challenging Students",
                description="Spread students with challenging behavior patterns throughout the classroom",
                seating_plan=self._create_dispersed_seating(behavior_profiles, challenging_students),
                rationale=[
                    "Reduces peer conflicts and distractions",
                    "Allows better teacher monitoring",
                    "Prevents clustering of negative behaviors"
                ],
                expected_benefits=[
                    "Reduced classroom disruptions",
                    "Improved focus and engagement",
                    "Better academic outcomes"
                ],
                potential_challenges=[
                    "May require adjustment period",
                    "Some students may resist changes"
                ],
                implementation_tips=[
                    "Explain the rationale to students",
                    "Implement gradually over 2-3 days",
                    "Monitor for 1-2 weeks before making further changes"
                ]
            ))

        # Strategy 2: Group positive influencers
        positive_students = [
            (sid, profile) for sid, profile in behavior_profiles.items()
            if profile.behavior_score > 20
        ]

        if positive_students:
            recommendations.append(SeatingRecommendation(
                arrangement_name="Positive Influence Clusters",
                description="Group positive behavior students to create influence zones",
                seating_plan=self._create_influence_clusters(behavior_profiles, positive_students),
                rationale=[
                    "Positive peers can influence behavior",
                    "Creates supportive micro-environments",
                    "Enhances overall classroom climate"
                ],
                expected_benefits=[
                    "Improved overall behavior",
                    "Better peer support systems",
                    "Enhanced learning environment"
                ],
                potential_challenges=[
                    "May isolate some students",
                    "Requires careful balance"
                ],
                implementation_tips=[
                    "Ensure no student feels excluded",
                    "Rotate groupings periodically",
                    "Monitor all students' progress"
                ]
            ))

        return recommendations

    def _create_dispersed_seating(self, behavior_profiles: Dict, challenging_students: List) -> Dict[str, List[int]]:
        """Create seating plan with challenging students dispersed"""
        # Simplified seating plan - in practice, this would consider classroom layout
        all_students = list(behavior_profiles.keys())
        challenging_ids = [sid for sid, _ in challenging_students]

        # Simple alternating pattern
        row1 = []
        row2 = []

        for i, student_id in enumerate(all_students):
            if student_id in challenging_ids and i % 3 == 0:
                # Place challenging students with space between them
                if i % 2 == 0:
                    row1.append(student_id)
                else:
                    row2.append(student_id)
            else:
                # Place other students normally
                if i % 2 == 0:
                    row1.append(student_id)
                else:
                    row2.append(student_id)

        return {
            "front_row": row1[:8],  # Assuming 8 seats per row
            "back_row": row2[:8]
        }

    def _create_influence_clusters(self, behavior_profiles: Dict, positive_students: List) -> Dict[str, List[int]]:
        """Create seating plan with positive influence clusters"""
        all_students = list(behavior_profiles.keys())
        positive_ids = [sid for sid, _ in positive_students]

        # Create clusters around positive students
        cluster_centers = positive_ids[:2]  # Use top 2 positive students as centers

        row1 = cluster_centers[:1] + [sid for sid in all_students if sid not in cluster_centers][:7]
        row2 = cluster_centers[1:] + [sid for sid in all_students if sid not in cluster_centers and sid not in row1][:7]

        return {
            "front_row": row1,
            "back_row": row2
        }

    def get_behavior_insights(self, class_code: str) -> Dict[str, Any]:
        """Get behavioral insights and trends for a class"""
        try:
            db = next(get_db())

            # Get behavior logs for the class
            thirty_days_ago = datetime.now() - timedelta(days=30)
            class_logs = db.query(QuickLog).filter(
                QuickLog.class_code == class_code,
                QuickLog.timestamp >= thirty_days_ago
            ).all()

            insights = {
                'class_code': class_code,
                'total_logs': len(class_logs),
                'behavior_trends': self._analyze_behavior_trends(class_logs),
                'peak_behavior_times': self._identify_peak_behavior_times(class_logs),
                'common_behavior_patterns': self._identify_common_patterns(class_logs),
                'improvement_opportunities': self._identify_improvement_opportunities(class_logs)
            }

            return insights

        except Exception as e:
            self.logger.error(f"Error generating behavior insights for {class_code}: {e}")
            return {}

    def _analyze_behavior_trends(self, logs: List) -> Dict[str, Any]:
        """Analyze behavior trends over time"""
        if not logs:
            return {'trend': 'insufficient_data'}

        # Group logs by day
        daily_logs = defaultdict(list)
        for log in logs:
            day = log.timestamp.date()
            daily_logs[day].append(log)

        # Calculate daily behavior scores
        daily_scores = {}
        for day, day_logs in daily_logs.items():
            positive = sum(1 for log in day_logs if log.log_type == "positive")
            negative = sum(1 for log in day_logs if log.log_type == "negative")
            daily_scores[day] = positive - negative

        # Determine trend
        if len(daily_scores) >= 7:
            recent_scores = list(daily_scores.values())[-7:]
            older_scores = list(daily_scores.values())[:-7]

            if older_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)

                if recent_avg > older_avg + 1:
                    trend = "improving"
                elif recent_avg < older_avg - 1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_history"
        else:
            trend = "insufficient_data"

        return {
            'trend': trend,
            'daily_scores': daily_scores,
            'average_daily_score': sum(daily_scores.values()) / len(daily_scores) if daily_scores else 0
        }

    def _identify_peak_behavior_times(self, logs: List) -> Dict[str, Any]:
        """Identify times when behavior issues are most common"""
        if not logs:
            return {'peak_times': []}

        # Group by hour
        hourly_logs = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        for log in logs:
            hour = log.timestamp.hour
            hourly_logs[hour][log.log_type] += 1

        # Find peak negative behavior hours
        peak_hours = []
        for hour, counts in hourly_logs.items():
            negative_ratio = counts['negative'] / max(sum(counts.values()), 1)
            if negative_ratio > 0.3:  # More than 30% negative logs
                peak_hours.append({
                    'hour': hour,
                    'negative_ratio': negative_ratio,
                    'total_logs': sum(counts.values())
                })

        peak_hours.sort(key=lambda x: x['negative_ratio'], reverse=True)

        return {
            'peak_times': peak_hours,
            'recommendation': f"Monitor behavior closely during hour(s): {[h['hour'] for h in peak_hours[:2]]}"
        }

    def _identify_common_patterns(self, logs: List) -> List[str]:
        """Identify common behavior patterns"""
        patterns = []

        if not logs:
            return patterns

        # Analyze log categories and notes for patterns
        category_count = defaultdict(int)
        for log in logs:
            if log.category:
                category_count[log.category] += 1

        # Identify most common categories
        if category_count:
            most_common = max(category_count.items(), key=lambda x: x[1])
            patterns.append(f"Most common behavior category: {most_common[0]} ({most_common[1]} incidents)")

        # Analyze timing patterns
        negative_logs = [log for log in logs if log.log_type == "negative"]
        if len(negative_logs) >= 5:
            patterns.append(f"{len(negative_logs)} negative behavior incidents in analysis period")

        return patterns

    def _identify_improvement_opportunities(self, logs: List) -> List[str]:
        """Identify opportunities for behavior improvement"""
        opportunities = []

        if not logs:
            return opportunities

        # Calculate improvement metrics
        positive_logs = [log for log in logs if log.log_type == "positive"]
        negative_logs = [log for log in logs if log.log_type == "negative"]

        if negative_logs and not positive_logs:
            opportunities.append("Implement positive reinforcement system")
        elif len(negative_logs) > len(positive_logs) * 2:
            opportunities.append("Increase positive behavior recognition")
        else:
            opportunities.append("Current behavior management strategies appear effective")

        # Check for patterns that suggest specific interventions
        if len(logs) < 10:
            opportunities.append("Increase behavior observation frequency")

        return opportunities

    def _generate_ai_enhanced_behavior_analysis(self, analysis: Dict[str, Any], class_code: str, user_query: str) -> str:
        """Generate AI-enhanced behavior analysis using Gemini"""
        try:
            # Prepare context data for Gemini
            context_data = {
                "class_code": class_code,
                "total_students": analysis.get('total_students', 0),
                "average_behavior_score": analysis.get('average_behavior_score', 0),
                "behavior_distribution": analysis.get('behavior_distribution', {}),
                "school_context": "BIS HCMC (British International School Ho Chi Minh City)",
                "interventions": [
                    {
                        "type": intervention.intervention_type,
                        "description": intervention.description,
                        "target_students": len(intervention.target_students),
                        "expected_outcomes": intervention.expected_outcomes,
                        "implementation_steps": intervention.implementation_steps[:2]  # Limit for token efficiency
                    }
                    for intervention in analysis.get('recommended_interventions', [])
                ],
                "seating_recommendations": [
                    {
                        "name": rec.arrangement_name,
                        "description": rec.description,
                        "rationale": rec.rationale[:2],  # Limit for token efficiency
                        "expected_benefits": rec.expected_benefits[:2],
                        "implementation_tips": rec.implementation_tips[:2]
                    }
                    for rec in analysis.get('seating_recommendations', [])
                ]
            }

            # Create prompt for Gemini
            prompt = f"""
            You are an expert classroom behavior specialist at BIS HCMC analyzing classroom behavior patterns.

            Class Context:
            - Class: {context_data['class_code']}
            - Total Students: {context_data['total_students']}
            - Average Behavior Score: {context_data['average_behavior_score']:.1f}
            - Behavior Distribution: Positive: {context_data['behavior_distribution'].get('positive', 0)}, Neutral: {context_data['behavior_distribution'].get('neutral', 0)}, Negative: {context_data['behavior_distribution'].get('negative', 0)}

            Recommended Interventions:
            {chr(10).join([f"- {int['type']}: {int['description']} (Targets: {int['target_students']} students)" for int in context_data['interventions']])}

            Seating Recommendations:
            {chr(10).join([f"- {rec['name']}: {rec['description']}" for rec in context_data['seating_recommendations']])}

            Teacher's Query: "{user_query}"

            Provide a comprehensive, context-aware behavior analysis that:
            1. Summarizes the current classroom behavior climate
            2. Explains behavior patterns and their potential causes
            3. Evaluates the effectiveness of recommended interventions
            4. Suggests specific implementation strategies for BIS HCMC environment
            5. Considers cultural and contextual factors relevant to Vietnam/International school setting
            6. Recommends monitoring and adjustment strategies

            Format your response professionally, focusing on practical, actionable recommendations for teachers.
            """

            if hasattr(self, 'gemini_client') and self.gemini_client and self.gemini_client.is_available():
                ai_response = self.gemini_client.generate_agent_response("behavior-manager", context_data, user_query)
                if ai_response:
                    return ai_response
                else:
                    # Fallback to basic analysis
                    return self._generate_basic_behavior_analysis(analysis, class_code)
            else:
                # Fallback to basic analysis if AI not available
                return self._generate_basic_behavior_analysis(analysis, class_code)

        except Exception as e:
            self.logger.error(f"AI-enhanced behavior analysis failed: {e}")
            return self._generate_basic_behavior_analysis(analysis, class_code)

    def _generate_basic_behavior_analysis(self, analysis: Dict[str, Any], class_code: str) -> str:
        """Generate basic behavior analysis when AI is not available"""
        result_text = f"Classroom Behavior Analysis for {class_code}:\n\n"
        result_text += f"**Total Students:** {analysis.get('total_students', 0)}\n"
        result_text += f"**Average Behavior Score:** {analysis.get('average_behavior_score', 0):.1f}\n\n"

        behavior_dist = analysis.get('behavior_distribution', {})
        result_text += "**Behavior Distribution:**\n"
        result_text += f"- Positive: {behavior_dist.get('positive', 0)} students\n"
        result_text += f"- Neutral: {behavior_dist.get('neutral', 0)} students\n"
        result_text += f"- Negative: {behavior_dist.get('negative', 0)} students\n\n"

        if analysis.get('recommended_interventions'):
            result_text += "**Recommended Interventions:**\n"
            for intervention in analysis['recommended_interventions'][:2]:
                result_text += f"- **{intervention.intervention_type.replace('_', ' ').title()}**: {intervention.description}\n"
                result_text += f"  *Expected Outcomes:* {', '.join(intervention.expected_outcomes[:2])}\n\n"

        if analysis.get('seating_recommendations'):
            result_text += "**Seating Recommendations:**\n"
            for recommendation in analysis['seating_recommendations'][:1]:
                result_text += f"- **{recommendation.arrangement_name}**: {recommendation.description}\n"
                result_text += f"  *Expected Benefits:* {', '.join(recommendation.expected_benefits[:2])}\n\n"

        result_text += "*Note: This analysis is based on available behavior data. Consider additional classroom observations and student feedback.*"

        return result_text

# Agent interface for PTCC integration
class ClassroomBehaviorAgent:
    """Main agent class for PTCC integration"""

    def __init__(self):
        self.manager = ClassroomBehaviorManager()
        self.logger = self.manager.logger

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
            task_type = input_data.get('task_type', 'analyze_class')
            metadata = input_data.get('metadata', {})
        else:
            text = input_data.text if hasattr(input_data, 'text') else str(input_data)
            task_type = getattr(input_data, 'task_type', 'analyze_class')
            metadata = getattr(input_data, 'metadata', {})

        # Determine action based on task type
        if task_type == 'analyze_class' and 'class_code' in metadata:
            class_code = metadata['class_code']
            analysis = self.manager.analyze_class_behavior(class_code)

            # Use Gemini for enhanced analysis if available
            if hasattr(self, 'gemini_client') and self.gemini_client and self.gemini_client.is_available():
                result_text = self._generate_ai_enhanced_behavior_analysis(analysis, class_code, text)
            else:
                # Fallback to basic analysis
                result_text = f"Classroom Behavior Analysis for {class_code}:\n"
                result_text += f"Total Students: {analysis.get('total_students', 0)}\n"
                result_text += f"Average Behavior Score: {analysis.get('average_behavior_score', 0):.1f}\n"

                behavior_dist = analysis.get('behavior_distribution', {})
                result_text += f"Behavior Distribution: Positive: {behavior_dist.get('positive', 0)}, "
                result_text += f"Neutral: {behavior_dist.get('neutral', 0)}, "
                result_text += f"Negative: {behavior_dist.get('negative', 0)}\n"

                if analysis.get('recommended_interventions'):
                    result_text += f"\nRecommended Interventions: {len(analysis['recommended_interventions'])}\n"
                    for intervention in analysis['recommended_interventions'][:2]:  # Show top 2
                        result_text += f"- {intervention.intervention_type}: {intervention.description}\n"

                if analysis.get('seating_recommendations'):
                    result_text += f"\nSeating Recommendations: {len(analysis['seating_recommendations'])}\n"
                    for recommendation in analysis['seating_recommendations'][:1]:  # Show top recommendation
                        result_text += f"- {recommendation.arrangement_name}: {recommendation.description}\n"

        elif task_type == 'behavior_insights' and 'class_code' in metadata:
            class_code = metadata['class_code']
            insights = self.manager.get_behavior_insights(class_code)

            result_text = f"Behavior Insights for {class_code}:\n"
            result_text += f"Total Logs Analyzed: {insights.get('total_logs', 0)}\n"

            trends = insights.get('behavior_trends', {})
            result_text += f"Behavior Trend: {trends.get('trend', 'unknown')}\n"

            peak_times = insights.get('peak_behavior_times', {})
            if peak_times.get('peak_times'):
                result_text += f"Peak Behavior Times: {peak_times['recommendation']}\n"

            patterns = insights.get('common_behavior_patterns', [])
            if patterns:
                result_text += "\nCommon Patterns:\n"
                for pattern in patterns:
                    result_text += f"- {pattern}\n"

        else:
            result_text = "Classroom Behavior Management Agent\n"
            result_text += "Available task types: analyze_class, behavior_insights\n"
            result_text += "Include class_code in metadata"

        # Create output
        return {
            "result": result_text,
            "explanation": f"Behavior analysis completed for task type: {task_type}",
            "confidence": 0.85,
            "metadata": {
                'task_type': task_type,
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_type': 'behavior_manager',
                'ai_enhanced': hasattr(self, 'gemini_client') and self.gemini_client and self.gemini_client.is_available()
            }
        }

# Standalone testing
if __name__ == "__main__":
    print("🎯 Classroom Behavior Management Agent")
    print("=" * 50)

    agent = ClassroomBehaviorAgent()

    # Test class analysis
    print("Testing class behavior analysis...")
    test_input = {
        "text": "Analyze classroom behavior patterns",
        "task_type": "analyze_class",
        "metadata": {"class_code": "7B"}
    }

    result = agent.process(test_input)
    print("Result:", result.result[:300] + "..." if len(result.result) > 300 else result.result)

    print("\n✅ Agent test completed!")