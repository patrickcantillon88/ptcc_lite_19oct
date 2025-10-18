"""
CCAEngagementAgent: Recommends CCAs and tracks engagement for enrichment & behavior.

Identifies students who would benefit from CCA participation by analyzing:
- Current CCA enrollments vs. recommendations
- Attendance patterns in existing CCAs
- Behavior flags and optimal activity types
- At-risk identification and engagement opportunities
- Leadership/mentorship potential
"""

from datetime import datetime
from typing import List, Dict, Any
from backend.core.base_agent import BaseAgent, StudentContext, AgentOutput


class CCAEngagementAgent(BaseAgent):
    """
    Co-curricular activities engagement agent.
    
    Analyzes CCA participation and recommends activities based on:
    - Student behavior profile and flags
    - Current CCA enrollments
    - Engagement patterns
    - At-risk identification
    - Enrichment opportunities
    """
    
    # CCA type recommendations by behavior profile
    CCA_RECOMMENDATIONS = {
        '[BEHAVIOR-CONCERN]': {
            'sports': 'Physical outlet for energy management',
            'leadership': 'Structure and responsibility',
            'robotics': 'Problem-solving focus'
        },
        '[ANXIETY]': {
            'arts': 'Creative expression and confidence building',
            'drama': 'Confidence and social skills in structured setting',
            'music': 'Calming and emotional outlet'
        },
        '[AT-RISK]': {
            'sports': 'Social engagement and belonging',
            'coding': 'Problem-solving and achievement',
            'drama': 'Self-worth and voice'
        },
        'general': {
            'sports': 'Team skills and physical health',
            'arts': 'Creative development',
            'STEM': 'Problem-solving and critical thinking',
            'leadership': 'Responsibility and advocacy'
        }
    }
    
    def __init__(self):
        super().__init__("CCAEngagementAgent")
    
    def analyze(self, context: StudentContext) -> AgentOutput:
        """Analyze CCA engagement and generate recommendations."""
        
        # Analyze current situation
        at_risk = '[AT-RISK]' in context.behavior_flags
        has_concerns = any(flag in context.behavior_flags for flag in ['[BEHAVIOR-CONCERN]', '[ANXIETY]'])
        
        # Determine priority and message
        if at_risk:
            priority = 'high'
            title_insight = "AT-RISK - CCA Engagement Critical"
            action_required = True
        elif has_concerns:
            priority = 'medium'
            title_insight = "Support Needed - CCA Recommended"
            action_required = True
        else:
            priority = 'low'
            title_insight = "Engagement Monitoring"
            action_required = False
        
        # Generate recommendations
        recommendations = self._generate_recommendations(context)
        
        # Format message
        message = self._format_message(context, priority, recommendations)
        
        return AgentOutput(
            agent_name=self.name,
            timestamp=datetime.now(),
            student_id=context.student_id,
            title=f"🎯 CCA ENGAGEMENT - {title_insight}",
            message=message,
            priority=priority,
            intervention_type='enrichment',
            action_required=action_required,
            recommended_actions=recommendations,
            reasoning=f"Student profile: {', '.join(context.behavior_flags) or 'positive'}"
        )
    
    def _format_message(self, context: StudentContext, priority: str, recommendations: List[str]) -> str:
        """Format engagement analysis message."""
        lines = []
        lines.append(f"\n🎯 CCA ENGAGEMENT ANALYSIS")
        lines.append(f"Student: {context.student_name} | Class: {context.class_code} | Time: {context.current_time.strftime('%H:%M')}\n")
        
        if context.behavior_flags:
            lines.append("Student Profile:")
            for flag in context.behavior_flags:
                lines.append(f"  {flag}")
            lines.append("")
        
        lines.append("Engagement Strategy:")
        for rec in recommendations:
            lines.append(f"  ✓ {rec}")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, context: StudentContext) -> List[str]:
        """Generate CCA enrollment recommendations."""
        recommendations = []
        
        # Identify primary behavior flags
        primary_flags = [flag for flag in context.behavior_flags if flag in self.CCA_RECOMMENDATIONS]
        
        if not primary_flags:
            primary_flags = ['general']
        
        # Get recommendations for each flag
        for flag in primary_flags:
            rec_dict = self.CCA_RECOMMENDATIONS.get(flag, {})
            for cca_type, reason in rec_dict.items():
                recommendations.append(
                    f"Consider: {cca_type.title()} CCA ({reason})"
                )
        
        # Add general enrichment suggestions
        if not recommendations:
            recommendations = [
                "Encourage participation in at least one CCA",
                "Recommend activity matching student interests",
                "Monitor for engagement and attendance"
            ]
        
        return recommendations[:3]  # Limit to top 3
    
    def _determine_priority(self, context: StudentContext, alerts: List[str]) -> str:
        """Determine priority based on engagement risk."""
        
        if '[AT-RISK]' in context.behavior_flags and len(alerts) > 0:
            return 'high'
        
        if len(alerts) >= 2:
            return 'high'
        
        if any(flag in context.behavior_flags for flag in ['[ANXIETY]', '[BEHAVIOR-CONCERN]']):
            return 'medium'
        
        return 'low'
    
    def _format_analysis(
        self,
        context: StudentContext,
        alerts: List[str],
        recommendations: List[str]
    ) -> str:
        """Format engagement analysis."""
        lines = [f"\n🎯 CCA ENGAGEMENT ANALYSIS\n"]
        lines.append(f"Student: {context.student_name} | Class: {context.class_code}\n")
        
        # Flags
        if context.behavior_flags:
            lines.append("Student Profile:")
            for flag in context.behavior_flags:
                lines.append(f"  {flag}")
            lines.append("")
        
        # Alerts
        if alerts:
            lines.append("🚨 ENGAGEMENT STATUS:")
            for alert in alerts:
                lines.append(f"  • {alert}")
            lines.append("")
        
        # Recommendations
        lines.append("💡 RECOMMENDATIONS:")
        for rec in recommendations:
            lines.append(f"  ✓ {rec}")
        lines.append("")
        
        # Engagement strategy
        lines.append("📋 ENGAGEMENT STRATEGY:")
        if '[AT-RISK]' in context.behavior_flags:
            lines.append("  1. Enroll in CCA matching interests (immediate)")
            lines.append("  2. Assign CCA mentor/peer buddy")
            lines.append("  3. Monitor attendance closely (weekly)")
        elif '[BEHAVIOR-CONCERN]' in context.behavior_flags:
            lines.append("  1. Enroll in high-energy activity (sports, robotics)")
            lines.append("  2. Position as student leader if engaged")
            lines.append("  3. Track behavior improvements post-CCA")
        elif '[ANXIETY]' in context.behavior_flags:
            lines.append("  1. Offer choice of creative or structured CCA")
            lines.append("  2. Start with low-pressure trial (2-week commitment)")
            lines.append("  3. Build confidence through success experiences")
        else:
            lines.append("  1. Encourage participation in preferred activity")
            lines.append("  2. Support peer relationships through CCA")
            lines.append("  3. Monitor for leadership opportunities")
        
        return "\n".join(lines)
    
    def _generate_reasoning(self, context: StudentContext, alerts: List[str]) -> str:
        """Explain reasoning for recommendations."""
        reasons = []
        
        if '[AT-RISK]' in context.behavior_flags:
            reasons.append("At-risk students benefit significantly from structured CCA engagement")
        
        if '[BEHAVIOR-CONCERN]' in context.behavior_flags:
            reasons.append("Energy-outlet CCAs provide positive behavior channel")
        
        if '[ANXIETY]' in context.behavior_flags:
            reasons.append("Creative CCAs build confidence and emotional resilience")
        
        if len(alerts) > 0:
            reasons.append(f"Multiple engagement factors identified ({len(alerts)} alerts)")
        
        return "; ".join(reasons) if reasons else "Routine CCA engagement check"


# Export agent
__all__ = ['CCAEngagementAgent']
