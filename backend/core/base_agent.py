"""
Base agent class for context-aware AI agents.
Provides shared infrastructure for behavior prediction and intervention agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class StudentContext:
    """Complete context for a student at a specific time."""
    student_id: int
    student_name: str
    class_code: str
    
    # Current period/time
    current_day: str  # Monday, Tuesday, etc.
    current_period: int
    current_time: datetime
    
    # Current activities
    current_subject: str
    lesson_type: str
    specialist_name: Optional[str]
    
    # Staff present
    class_teacher: str
    ta_present: bool
    specialist_present: bool
    
    # Recent context
    recent_logs: List[Dict[str, Any]]  # Last 5 quick logs
    behavior_flags: List[str]  # [ANXIETY], [AT-RISK], [BEHAVIOR-CONCERN], etc.
    
    # Accommodations
    active_accommodations: List[Dict[str, str]]
    
    # Timetable info
    next_period_subject: Optional[str]
    is_transition_period: bool
    time_since_last_break: int  # minutes


@dataclass
class AgentOutput:
    """Structured output from an agent."""
    agent_name: str
    timestamp: datetime
    student_id: int
    
    # Main content
    title: str
    message: str
    
    # Metadata
    priority: str  # 'low', 'medium', 'high', 'critical'
    intervention_type: str  # 'preventive', 'reactive', 'enrichment'
    action_required: bool
    
    # Recommendations
    recommended_actions: List[str]
    
    # Context
    reasoning: str  # Explain why this output was generated


class BaseAgent(ABC):
    """
    Base class for all context-aware agents.
    
    Agents analyze student context and generate:
    - Proactive briefings
    - Behavior predictions
    - Intervention recommendations
    - Enrichment suggestions
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agents.{name}")
    
    @abstractmethod
    def analyze(self, context: StudentContext) -> AgentOutput:
        """
        Analyze student context and generate output.
        
        Args:
            context: Complete student context at current time
            
        Returns:
            AgentOutput with analysis and recommendations
        """
        pass
    
    def _format_briefing(
        self,
        title: str,
        alerts: List[str],
        accommodations: List[str],
        recommendations: List[str]
    ) -> str:
        """Format a structured briefing."""
        lines = [f"\n🎓 {title}\n"]
        
        if alerts:
            lines.append("⚠️ ATTENTION ALERTS:")
            for alert in alerts:
                lines.append(f"• {alert}")
            lines.append("")
        
        if accommodations:
            lines.append("✅ ACCOMMODATIONS ACTIVE:")
            for acc in accommodations:
                lines.append(f"• {acc}")
            lines.append("")
        
        if recommendations:
            lines.append("💡 RECOMMENDATIONS:")
            for rec in recommendations:
                lines.append(f"• {rec}")
        
        return "\n".join(lines)
    
    def _get_student_flag_type(self, flags: List[str]) -> Optional[str]:
        """Determine primary concern type from flags."""
        flag_priority = {
            '[SAFEGUARDING]': 'critical',
            '[AT-RISK]': 'high',
            '[ANXIETY]': 'high',
            '[BEHAVIOR-CONCERN]': 'medium',
            '[COMMUNICATION-NEED]': 'medium',
            '[SENSORY-NEED]': 'low',
        }
        
        for flag in flags:
            if flag in flag_priority:
                return flag
        
        return None
    
    def _generate_json_output(self, output: AgentOutput) -> Dict[str, Any]:
        """Convert AgentOutput to JSON-serializable dict."""
        return {
            'agent': output.agent_name,
            'timestamp': output.timestamp.isoformat(),
            'student_id': output.student_id,
            'title': output.title,
            'message': output.message,
            'priority': output.priority,
            'intervention_type': output.intervention_type,
            'action_required': output.action_required,
            'recommended_actions': output.recommended_actions,
            'reasoning': output.reasoning,
        }


class AgentOrchestrator:
    """
    Manages multiple agents and coordinates their outputs.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agents.orchestrator")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent."""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def analyze_all(self, context: StudentContext) -> List[AgentOutput]:
        """
        Run all registered agents on the same context.
        
        Returns:
            List of AgentOutputs, sorted by priority
        """
        outputs = []
        
        for agent in self.agents.values():
            try:
                output = agent.analyze(context)
                outputs.append(output)
            except Exception as e:
                self.logger.error(f"Agent {agent.name} failed: {e}")
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        outputs.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        return outputs
    
    def get_critical_alerts(self, context: StudentContext) -> List[str]:
        """Get only critical/high-priority alerts."""
        outputs = self.analyze_all(context)
        critical = [o for o in outputs if o.priority in ['critical', 'high']]
        return [o.title for o in critical]
