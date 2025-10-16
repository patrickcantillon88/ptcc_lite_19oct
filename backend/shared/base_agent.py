#!/usr/bin/env python3
"""
Shared base classes for agent interoperability across PTCC.

Provides enhanced agent communication with context awareness,
memory integration, and safety validation.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
import logging


class AgentInput:
    """Lightweight container for agent input parameters."""

    def __init__(self, text: str, task_type: str, metadata: Optional[Dict[str, Any]] = None):
        self.text = text
        self.task_type = task_type
        self.metadata = metadata or {}


class AgentOutput:
    """Lightweight container for agent outputs used by API responses."""

    def __init__(self, result: str, explanation: str, confidence: float, metadata: Optional[Dict[str, Any]] = None):
        self.result = result
        self.explanation = explanation
        self.confidence = confidence
        self.metadata = metadata or {}


class ContextAwareAgentInput(AgentInput):
    """Enhanced agent input with context awareness."""

    def __init__(
        self,
        text: str,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        context_layers: Optional[Dict[str, Any]] = None,
        user_profile_id: Optional[int] = None,
        memory_context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(text, task_type, metadata)
        self.context_layers = context_layers or {}
        self.user_profile_id = user_profile_id
        self.memory_context = memory_context or {}
        self.timestamp = datetime.utcnow()


class ContextAwareAgentOutput(AgentOutput):
    """Enhanced agent output with additional metadata."""

    def __init__(
        self,
        result: str,
        explanation: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None,
        context_used: Optional[List[str]] = None,
        memory_updated: bool = False,
        safety_validated: bool = False,
        reasoning_steps: Optional[List[str]] = None
    ):
        super().__init__(result, explanation, confidence, metadata)
        self.context_used = context_used or []
        self.memory_updated = memory_updated
        self.safety_validated = safety_validated
        self.reasoning_steps = reasoning_steps or []
        self.timestamp = datetime.utcnow()


class AgentCoordinator:
    """Coordinates multiple agents for complex tasks."""

    def __init__(self):
        self.logger = logging.getLogger("agent_coordinator")
        self.active_sessions = {}

    def create_coordination_session(self, session_id: str, agents: List[str]) -> Dict[str, Any]:
        """Create a new coordination session."""
        session = {
            "session_id": session_id,
            "agents": agents,
            "start_time": datetime.utcnow(),
            "status": "active",
            "messages": []
        }
        self.active_sessions[session_id] = session
        return session

    def route_task(self, task: Dict[str, Any], target_agent: str) -> Dict[str, Any]:
        """Route a task to a specific agent."""
        message = {
            "timestamp": datetime.utcnow(),
            "target_agent": target_agent,
            "task": task,
            "status": "routed"
        }
        return message

    def collect_results(self, session_id: str) -> List[Dict[str, Any]]:
        """Collect results from all agents in a session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        return session.get("messages", [])


class InterAgentCommunication:
    """Protocol for inter-agent communication."""

    @staticmethod
    def send_message(
        sender_id: str,
        receiver_id: str,
        message_type: str,
        content: Dict[str, Any],
        requires_response: bool = False
    ) -> Dict[str, Any]:
        """Send a message from one agent to another."""
        return {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message_type": message_type,
            "content": content,
            "requires_response": requires_response,
            "timestamp": datetime.utcnow()
        }

    @staticmethod
    def create_response(
        original_message: Dict[str, Any],
        response_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a response to a message."""
        return {
            "sender_id": original_message["receiver_id"],
            "receiver_id": original_message["sender_id"],
            "message_type": "response",
            "content": response_content,
            "in_response_to": original_message,
            "timestamp": datetime.utcnow()
        }


class MemoryAccessMixin:
    """Mixin for agents that need memory system access."""

    def get_user_profile(self, user_profile_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user profile from memory system."""
        # Will be implemented with memory system
        return None

    def get_context_layers(self, user_profile_id: int) -> Dict[str, Any]:
        """Retrieve context layers for a user."""
        # Will be implemented with context engine
        return {}

    def get_interaction_history(
        self,
        user_profile_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve recent interaction history."""
        # Will be implemented with memory system
        return []

    def update_memory(
        self,
        user_profile_id: int,
        interaction_data: Dict[str, Any]
    ) -> bool:
        """Update memory with new interaction."""
        # Will be implemented with memory system
        return False


class SafetyValidationMixin:
    """Mixin for agents that need safety validation."""

    def validate_input(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate input for safety concerns."""
        # Will be implemented with alignment system
        return {
            "is_safe": True,
            "concerns": [],
            "confidence": 1.0
        }

    def validate_output(
        self,
        output_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate output for safety, bias, and appropriateness."""
        # Will be implemented with alignment system
        return {
            "is_safe": True,
            "alignment_score": 1.0,
            "bias_detected": False,
            "cultural_sensitivity_score": 1.0,
            "educational_appropriateness": 1.0
        }

    def check_alignment(
        self,
        content: str,
        educational_values: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check content alignment with educational values."""
        # Will be implemented with alignment system
        return {
            "aligned": True,
            "score": 1.0,
            "recommendations": []
        }


class BaseContextAwareAgent(MemoryAccessMixin, SafetyValidationMixin):
    """Base class for context-aware agents."""

    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_id}")

    def process(
        self,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process input with context awareness and safety validation."""
        # This will be overridden by specific agents
        raise NotImplementedError("Subclasses must implement process()")

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return []

    def can_handle_task(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type."""
        return task_type in self.get_capabilities()


