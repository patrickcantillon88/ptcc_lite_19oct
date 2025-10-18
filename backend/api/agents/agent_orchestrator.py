"""
AgentOrchestrator: Coordinates all behavior prediction agents.

Manages agent registration, execution, and result aggregation for:
- PeriodBriefingAgent (pre-lesson context)
- CCAEngagementAgent (enrichment opportunities)
- AccommodationComplianceAgent (accessibility/support verification)

Provides unified output combining all agent analyses.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.core.base_agent import StudentContext, AgentOutput
from backend.api.agents.period_briefing_agent import PeriodBriefingAgent
from backend.api.agents.cca_engagement_agent import CCAEngagementAgent
from backend.api.agents.accommodation_compliance_agent import AccommodationComplianceAgent


class AgentOrchestrator:
    """
    Central coordinator for behavior prediction agents.
    
    Manages:
    - Agent registration and initialization
    - Parallel agent analysis execution
    - Result aggregation and prioritization
    - Output formatting for different interfaces
    """
    
    def __init__(self):
        """Initialize orchestrator and register agents."""
        self.agents = {}
        self._register_agents()
    
    def _register_agents(self) -> None:
        """Register all available agents."""
        # Period briefing agent (pre-lesson context)
        self.agents['period_briefing'] = PeriodBriefingAgent()
        
        # CCA engagement agent (enrichment recommendations)
        self.agents['cca_engagement'] = CCAEngagementAgent()
        
        # Accommodation compliance agent (accessibility verification)
        self.agents['accommodation_compliance'] = AccommodationComplianceAgent()
    
    def analyze_student(
        self,
        context: StudentContext,
        agent_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze student using specified agents (or all agents if not specified).
        
        Args:
            context: StudentContext with all relevant data
            agent_names: List of agent names to run, or None for all
        
        Returns:
            Dict with aggregated results from all agents
        """
        # Determine which agents to run
        agents_to_run = agent_names or list(self.agents.keys())
        
        # Execute agents
        results = {}
        for agent_name in agents_to_run:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                try:
                    output = agent.analyze(context)
                    results[agent_name] = output
                except Exception as e:
                    results[agent_name] = {
                        'error': str(e),
                        'agent_name': agent_name
                    }
        
        # Aggregate results
        return self._aggregate_results(context, results)
    
    def _aggregate_results(self, context: StudentContext, results: Dict) -> Dict[str, Any]:
        """Aggregate agent results with priorities and summary."""
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_agents = sorted(
            results.items(),
            key=lambda x: priority_order.get(
                x[1].get('priority', 'low') if isinstance(x[1], dict) and 'priority' in x[1] else 'low'
            )
        )
        
        # Generate summary
        summary = self._generate_summary(context, results)
        
        return {
            'student_id': context.student_id,
            'student_name': context.student_name,
            'class_code': context.class_code,
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'agents': {name: output for name, output in sorted_agents},
            'total_agents': len(results),
            'high_priority_count': sum(
                1 for r in results.values()
                if isinstance(r, dict) and r.get('priority') == 'high'
            )
        }
    
    def _generate_summary(self, context: StudentContext, results: Dict) -> str:
        """Generate executive summary of analysis."""
        lines = [
            f"\n🎓 BEHAVIOR CONTEXT ANALYSIS SUMMARY",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Student: {context.student_name}",
            f"Class: {context.class_code}",
            f"Analysis Time: {datetime.now().strftime('%H:%M:%S')}",
            ""
        ]
        
        # Student profile
        if context.behavior_flags:
            lines.append("📊 STUDENT PROFILE:")
            for flag in context.behavior_flags:
                lines.append(f"  {flag}")
            lines.append("")
        
        # High-priority alerts
        high_priority_alerts = []
        for agent_name, output in results.items():
            if isinstance(output, dict) and output.get('priority') == 'high':
                if 'title' in output:
                    high_priority_alerts.append(output['title'])
        
        if high_priority_alerts:
            lines.append("🚨 HIGH PRIORITY ALERTS:")
            for alert in high_priority_alerts:
                lines.append(f"  ⚠️  {alert}")
            lines.append("")
        
        # Agent status
        lines.append(f"✅ ANALYSIS STATUS: {len(results)}/{len(results)} agents completed")
        lines.append("")
        
        return "\n".join(lines)
    
    def format_for_display(self, aggregated: Dict) -> str:
        """Format aggregated results for display."""
        lines = [aggregated['summary']]
        
        # Add each agent's full output
        for agent_name, output in aggregated['agents'].items():
            if isinstance(output, dict) and 'message' in output:
                lines.append("\n" + "="*50)
                lines.append(output.get('title', agent_name.upper()))
                lines.append("="*50)
                lines.append(output['message'])
        
        return "\n".join(lines)
    
    def format_for_api(self, aggregated: Dict) -> Dict[str, Any]:
        """Format aggregated results for API response."""
        formatted = {
            'student_id': aggregated['student_id'],
            'student_name': aggregated['student_name'],
            'class_code': aggregated['class_code'],
            'timestamp': aggregated['timestamp'],
            'summary': aggregated['summary'],
            'high_priority_count': aggregated['high_priority_count'],
            'agents': {}
        }
        
        for agent_name, output in aggregated['agents'].items():
            if isinstance(output, dict):
                formatted['agents'][agent_name] = {
                    'agent_name': output.get('agent_name', agent_name),
                    'title': output.get('title', ''),
                    'priority': output.get('priority', 'low'),
                    'action_required': output.get('action_required', False),
                    'intervention_type': output.get('intervention_type', ''),
                    'recommended_actions': output.get('recommended_actions', []),
                    'reasoning': output.get('reasoning', '')
                }
        
        return formatted
    
    def get_agent(self, name: str):
        """Get specific agent by name."""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self.agents.keys())


# Export orchestrator
__all__ = ['AgentOrchestrator']
