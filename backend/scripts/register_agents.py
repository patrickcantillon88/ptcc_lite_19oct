#!/usr/bin/env python3
"""
Register Existing Agents with PTCC Orchestrator

This script registers all existing teacher-tools agents with the
agent orchestration system, enabling them to use LLM integration,
memory, alignment, and governance features.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.agent_orchestrator import AgentOrchestrator
from backend.core.logging_config import get_logger

logger = get_logger("register_agents")


def register_teacher_tools_agents():
    """Register all teacher tools agents."""
    
    orchestrator = AgentOrchestrator()
    
    agents_to_register = [
        {
            "agent_id": "at_risk_identifier",
            "agent_name": "At-Risk Student Identifier",
            "agent_type": "educational_analysis",
            "capabilities": [
                "analyze_student",
                "analyze_class",
                "system_summary",
                "risk_assessment",
                "behavioral_analysis",
                "academic_trend_analysis"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-pro",
            "configuration": {
                "risk_weights": {
                    "high_support_level": 25,
                    "recent_negative_logs": 20,
                    "declining_assessments": 15,
                    "no_positive_interaction": 10,
                    "multiple_support_notes": 15,
                    "behavioral_patterns": 15
                },
                "analysis_window_days": 30
            }
        },
        {
            "agent_id": "behavior_manager",
            "agent_name": "Classroom Behavior Manager",
            "agent_type": "educational_management",
            "capabilities": [
                "analyze_behavior",
                "suggest_interventions",
                "track_patterns",
                "behavior_insights"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-pro",
            "configuration": {
                "intervention_strategies": True,
                "pattern_recognition": True
            }
        },
        {
            "agent_id": "learning_path_creator",
            "agent_name": "Personalized Learning Path Creator",
            "agent_type": "educational_planning",
            "capabilities": [
                "create_learning_path",
                "personalize_curriculum",
                "adapt_to_progress",
                "recommend_resources"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-pro",
            "configuration": {
                "adaptation_enabled": True,
                "resource_recommendations": True
            }
        }
    ]
    
    registered_count = 0
    
    for agent_config in agents_to_register:
        try:
            agent = orchestrator.register_agent(**agent_config)
            logger.info(f"✅ Registered: {agent_config['agent_name']}")
            registered_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to register {agent_config['agent_name']}: {e}")
    
    return registered_count, len(agents_to_register)


def register_core_agents():
    """Register core system agents."""
    
    orchestrator = AgentOrchestrator()
    
    core_agents = [
        {
            "agent_id": "lesson_planner",
            "agent_name": "Lesson Planning Assistant",
            "agent_type": "educational_planning",
            "capabilities": [
                "create_lesson_plan",
                "adapt_lesson",
                "suggest_activities",
                "align_standards"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-pro"
        },
        {
            "agent_id": "assessment_generator",
            "agent_name": "Assessment Generator",
            "agent_type": "educational_assessment",
            "capabilities": [
                "generate_questions",
                "create_rubric",
                "analyze_assessment",
                "suggest_improvements"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-pro"
        },
        {
            "agent_id": "feedback_composer",
            "agent_name": "Feedback Composer",
            "agent_type": "educational_communication",
            "capabilities": [
                "compose_feedback",
                "personalize_feedback",
                "suggest_next_steps",
                "encourage_growth"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-flash"  # Faster for feedback
        },
        {
            "agent_id": "curriculum_advisor",
            "agent_name": "Curriculum Advisor",
            "agent_type": "educational_planning",
            "capabilities": [
                "suggest_curriculum",
                "align_standards",
                "sequence_topics",
                "recommend_resources"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-pro"
        },
        {
            "agent_id": "differentiation_specialist",
            "agent_name": "Differentiation Specialist",
            "agent_type": "educational_planning",
            "capabilities": [
                "differentiate_instruction",
                "adapt_materials",
                "support_diverse_learners",
                "scaffold_learning"
            ],
            "model_provider": "gemini",
            "model_name": "gemini-1.5-pro"
        }
    ]
    
    registered_count = 0
    
    for agent_config in core_agents:
        try:
            agent = orchestrator.register_agent(**agent_config)
            logger.info(f"✅ Registered: {agent_config['agent_name']}")
            registered_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to register {agent_config['agent_name']}: {e}")
    
    return registered_count, len(core_agents)


def main():
    """Main registration process."""
    print("\n" + "="*60)
    print("PTCC Agent Registration")
    print("="*60 + "\n")
    
    # Register teacher tools agents
    print("📚 Registering Teacher Tools Agents...")
    teacher_success, teacher_total = register_teacher_tools_agents()
    print(f"   {teacher_success}/{teacher_total} teacher tools agents registered\n")
    
    # Register core agents
    print("🎯 Registering Core Educational Agents...")
    core_success, core_total = register_core_agents()
    print(f"   {core_success}/{core_total} core agents registered\n")
    
    # Summary
    total_success = teacher_success + core_success
    total_agents = teacher_total + core_total
    
    print("="*60)
    print("REGISTRATION SUMMARY")
    print("="*60)
    print(f"✅ Successfully registered: {total_success}/{total_agents} agents")
    
    if total_success == total_agents:
        print("\n🎉 All agents registered successfully!")
        print("\nNext steps:")
        print("1. Test agents with: python tests/test_agent_orchestrator.py")
        print("2. View registered agents in the database")
        print("3. Start using agents in your application")
    else:
        print(f"\n⚠️  {total_agents - total_success} agents failed to register")
        print("Check the logs above for details")
    
    print("")
    return total_success == total_agents


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
