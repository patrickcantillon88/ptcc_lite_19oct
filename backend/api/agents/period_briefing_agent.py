"""
PeriodBriefingAgent: Generates context-aware pre-lesson briefings.

Provides teachers with actionable intelligence 5 minutes before each lesson:
- Student behavior alerts
- Accommodation reminders
- Staff context
- Transition warnings
- Recommended proactive actions
"""

from datetime import datetime
from typing import List, Dict, Any
from backend.core.base_agent import BaseAgent, StudentContext, AgentOutput


class PeriodBriefingAgent(BaseAgent):
    """
    Pre-lesson intelligence agent.
    
    Analyzes:
    - Student's behavior flags and recent incidents
    - Active accommodations for this period
    - Time since last break (movement break predictor)
    - Specialist lesson context
    - Staff availability
    - Transition risk factors
    """
    
    def __init__(self):
        super().__init__("PeriodBriefingAgent")
    
    def analyze(self, context: StudentContext) -> AgentOutput:
        """Generate pre-lesson briefing."""
        
        # Collect alerts
        alerts = self._generate_alerts(context)
        
        # Collect accommodation reminders
        accommodations = self._format_accommodations(context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(context, alerts)
        
        # Determine priority
        priority = self._determine_priority(context, alerts)
        
        # Format briefing message
        message = self._format_briefing(
            title=f"⚠️ PERIOD BRIEFING - {context.current_time.strftime('%H:%M')} {context.current_subject}",
            alerts=alerts,
            accommodations=accommodations,
            recommendations=recommendations
        )
        
        # Add context details to message
        message += self._add_context_details(context)
        
        return AgentOutput(
            agent_name=self.name,
            timestamp=datetime.now(),
            student_id=context.student_id,
            title=f"PERIOD BRIEFING - {context.current_time.strftime('%H:%M')} {context.current_subject}",
            message=message,
            priority=priority,
            intervention_type='preventive',
            action_required=priority in ['critical', 'high'],
            recommended_actions=recommendations,
            reasoning=self._generate_reasoning(context, alerts)
        )
    
    def _generate_alerts(self, context: StudentContext) -> List[str]:
        """Generate behavioral and contextual alerts."""
        alerts = []
        
        # Movement break alert (key predictor of behavior)
        if context.time_since_last_break >= 60:
            minutes = context.time_since_last_break
            alerts.append(
                f"{context.student_name}: No break for {minutes}min - offer movement break at {self._suggest_break_time(context)}"
            )
        
        # Specialist lesson risk (unknown instructor)
        if context.lesson_type == 'Specialist' and context.specialist_name == 'Unknown':
            alerts.append("Specialist instructor not confirmed - verify before lesson")
        
        # Recent negative incidents
        recent_negatives = [
            log for log in context.recent_logs
            if log.get('log_type') == 'negative'
        ]
        if len(recent_negatives) >= 2:
            alerts.append(
                f"{context.student_name}: {len(recent_negatives)} negative incidents in last 2 periods - heightened monitoring recommended"
            )
        
        # Transition period flag
        if context.is_transition_period:
            alerts.append("Transition period detected - elevated behavior risk")
        
        # Behavior concern flags
        if '[BEHAVIOR-CONCERN]' in context.behavior_flags:
            alerts.append(
                f"{context.student_name}: Known behavior concern - establish clear expectations at lesson start"
            )
        
        # Anxiety flag
        if '[ANXIETY]' in context.behavior_flags:
            alerts.append(
                f"{context.student_name}: Anxiety management needed - provide reassurance and clear structure"
            )
        
        # At-risk flag
        if '[AT-RISK]' in context.behavior_flags:
            alerts.append(
                f"{context.student_name}: At-risk student - check-in on emotional state before lesson"
            )
        
        # TA absence during high-need lesson
        if not context.ta_present and context.lesson_type == 'Specialist':
            alerts.append("TA not present for specialist lesson - ensure close proximity to student")
        
        # No positive recent logs
        recent_positives = [
            log for log in context.recent_logs
            if log.get('log_type') == 'positive'
        ]
        if not recent_positives and len(context.recent_logs) >= 2:
            alerts.append(
                f"{context.student_name}: No positive incidents recorded - focus on catching good behaviors"
            )
        
        return alerts if alerts else ["No specific alerts - baseline briefing"]
    
    def _format_accommodations(self, context: StudentContext) -> List[str]:
        """Format active accommodations for this period."""
        if not context.active_accommodations:
            return []
        
        accommodations = []
        for acc in context.active_accommodations:
            acc_type = acc.get('accommodation_type', 'unknown')
            desc = acc.get('description', '')
            
            if acc_type == 'sensory':
                accommodations.append(f"Sensory: {desc}")
            elif acc_type == 'behavioral':
                accommodations.append(f"Behavioral: {desc}")
            elif acc_type == 'social':
                accommodations.append(f"Social: {desc}")
            elif acc_type == 'communication':
                accommodations.append(f"Communication: {desc}")
            else:
                accommodations.append(f"{acc_type}: {desc}")
        
        return accommodations
    
    def _generate_recommendations(
        self,
        context: StudentContext,
        alerts: List[str]
    ) -> List[str]:
        """Generate proactive actions for teacher."""
        recommendations = []
        
        # Movement break
        if context.time_since_last_break >= 60:
            recommendations.append(
                f"Offer {context.student_name} a movement break at {self._suggest_break_time(context)}"
            )
        
        # Behavior expectation setting
        if '[BEHAVIOR-CONCERN]' in context.behavior_flags:
            recommendations.append(
                f"Start lesson with brief behavior expectations review for {context.student_name}"
            )
        
        # Anxiety management
        if '[ANXIETY]' in context.behavior_flags:
            recommendations.append(
                f"Have reassurance buddy or TA assigned to {context.student_name} for check-ins"
            )
        
        # TA positioning
        if not context.ta_present and '[BEHAVIOR-CONCERN]' in context.behavior_flags:
            recommendations.append(
                f"Position another adult nearby to monitor {context.student_name}"
            )
        
        # Specialist lesson prep
        if context.lesson_type == 'Specialist':
            recommendations.append(
                f"Brief {context.student_name} on specialist lesson expectations (new instructor context)"
            )
        
        # Positive behavior catching
        if not any(log.get('log_type') == 'positive' for log in context.recent_logs):
            recommendations.append(
                f"Focus on catching and rewarding positive behaviors from {context.student_name}"
            )
        
        # Accommodation prep
        if context.active_accommodations:
            recommendations.append(
                f"Review accommodations before lesson: {', '.join([a.get('accommodation_type') for a in context.active_accommodations])}"
            )
        
        return recommendations if recommendations else ["Standard lesson approach - no specific interventions needed"]
    
    def _determine_priority(self, context: StudentContext, alerts: List[str]) -> str:
        """Determine briefing priority."""
        
        # Critical flags
        if '[SAFEGUARDING]' in context.behavior_flags:
            return 'critical'
        
        # High-priority combinations
        if '[AT-RISK]' in context.behavior_flags and len(alerts) >= 3:
            return 'high'
        
        if '[BEHAVIOR-CONCERN]' in context.behavior_flags and context.time_since_last_break >= 90:
            return 'high'
        
        if len(alerts) >= 3:
            return 'high'
        
        # Medium priority
        if any(flag in context.behavior_flags for flag in ['[ANXIETY]', '[BEHAVIOR-CONCERN]', '[AT-RISK]']):
            return 'medium'
        
        if context.time_since_last_break >= 60:
            return 'medium'
        
        # Low priority
        return 'low'
    
    def _suggest_break_time(self, context: StudentContext) -> str:
        """Suggest optimal break time during period."""
        # Default: midway through period (assuming 45-min periods)
        midpoint_minutes = 22
        
        # Calculate suggestion based on lesson type
        if context.lesson_type == 'Specialist':
            # Shorter attention span for new environments
            midpoint_minutes = 15
        
        # Add minutes and handle hour rollover
        new_minute = context.current_time.minute + midpoint_minutes
        new_hour = context.current_time.hour
        
        if new_minute >= 60:
            new_hour += 1
            new_minute -= 60
        
        suggested_time = context.current_time.replace(
            hour=new_hour,
            minute=new_minute
        )
        
        return suggested_time.strftime('%H:%M')
    
    def _add_context_details(self, context: StudentContext) -> str:
        """Add contextual details to briefing."""
        lines = []
        
        # Timetable context
        lines.append(f"\n📍 CONTEXT:")
        lines.append(f"• Class: {context.class_code}")
        lines.append(f"• Lesson Type: {context.lesson_type}")
        if context.specialist_name and context.specialist_name != 'Unknown':
            lines.append(f"• Specialist: {context.specialist_name}")
        lines.append(f"• Class Teacher: {context.class_teacher}")
        lines.append(f"• TA Present: {'✓ Yes' if context.ta_present else '✗ No'}")
        
        # Time context
        lines.append(f"\n⏱️ TIME CONTEXT:")
        lines.append(f"• Time Since Last Break: {context.time_since_last_break}min")
        if context.next_period_subject:
            lines.append(f"• Next: {context.next_period_subject}")
        
        return "\n".join(lines)
    
    def _generate_reasoning(self, context: StudentContext, alerts: List[str]) -> str:
        """Explain why this briefing was generated."""
        reasons = []
        
        if context.behavior_flags:
            reasons.append(f"Student has flags: {', '.join(context.behavior_flags)}")
        
        if context.time_since_last_break >= 60:
            reasons.append(f"High break timer ({context.time_since_last_break}min) increases behavior risk")
        
        if context.lesson_type == 'Specialist':
            reasons.append("Specialist lesson requires contextual awareness")
        
        if len(alerts) > 1:
            reasons.append(f"Multiple alerts ({len(alerts)}) indicate heightened needs")
        
        if not context.ta_present and context.active_accommodations:
            reasons.append("Without TA, accommodations require extra attention")
        
        return "; ".join(reasons) if reasons else "Routine pre-lesson briefing"


# Example usage / testing
if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    # Test context: Marcus Thompson before ICT specialist lesson
    test_context = StudentContext(
        student_id=1,
        student_name="Marcus Thompson",
        class_code="3A",
        current_day="Monday",
        current_period=3,
        current_time=datetime(2025, 10, 17, 9, 45),
        current_subject="ICT",
        lesson_type="Specialist",
        specialist_name="Unknown",
        class_teacher="Ms Elena Rodriguez",
        ta_present=True,
        specialist_present=False,
        recent_logs=[
            {"log_type": "negative", "category": "off_task", "time": "09:30"},
            {"log_type": "positive", "category": "good_effort", "time": "09:15"},
        ],
        behavior_flags=["[BEHAVIOR-CONCERN]"],
        active_accommodations=[
            {
                "accommodation_type": "behavioral",
                "description": "Impulsivity, attention-seeking, responds well to movement breaks"
            }
        ],
        next_period_subject="Break",
        is_transition_period=False,
        time_since_last_break=75,
    )
    
    agent = PeriodBriefingAgent()
    output = agent.analyze(test_context)
    
    print(f"Agent: {output.agent_name}")
    print(f"Priority: {output.priority}")
    print(f"Title: {output.title}")
    print(f"\n{output.message}")
    print(f"\nRecommended Actions:")
    for action in output.recommended_actions:
        print(f"  • {action}")
    print(f"\nReasoning: {output.reasoning}")
