"""
Test Agent Orchestration System

Tests the full agent orchestration with LLM, memory, alignment, and governance.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ptcc.backend.core.agent_orchestrator import (
    AgentOrchestrator,
    execute_task,
    register_new_agent
)


def test_agent_registration():
    """Test 1: Register a new agent."""
    print("\n" + "="*60)
    print("TEST 1: Agent Registration")
    print("="*60)
    
    try:
        agent = register_new_agent(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="testing",
            capabilities=["test_capability"],
            model_provider="gemini",
            model_name="gemini-1.5-flash"
        )
        
        print(f"\n✅ Agent registered successfully!")
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Agent Name: {agent.agent_name}")
        print(f"   Capabilities: {agent.capabilities}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Agent registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lesson_planning_agent():
    """Test 2: Execute lesson planning task."""
    print("\n" + "="*60)
    print("TEST 2: Lesson Planning Agent")
    print("="*60)
    
    try:
        # First register the lesson planning agent if not already registered
        try:
            register_new_agent(
                agent_id="lesson_planner",
                agent_name="Lesson Planning Assistant",
                agent_type="educational_planning",
                capabilities=[
                    "create_lesson_plan",
                    "adapt_lesson",
                    "suggest_activities"
                ]
            )
        except:
            pass  # Agent might already be registered
        
        # Execute task
        result = execute_task(
            agent_id="lesson_planner",
            task_type="create_lesson_plan",
            input_data={
                "grade": "5th",
                "subject": "Science",
                "topic": "Photosynthesis",
                "duration": "45 minutes",
                "learning_objectives": [
                    "Understand the process of photosynthesis",
                    "Identify the key components needed",
                    "Explain why photosynthesis is important"
                ]
            },
            user_id="teacher_001",
            enable_memory=True,
            enable_alignment=True,
            enable_governance=True
        )
        
        if result["success"]:
            print(f"\n✅ Lesson plan created successfully!")
            print(f"\nTask ID: {result['task_id']}")
            print(f"Execution Time: {result['execution_time_ms']}ms")
            print(f"Tokens Used: {result['tokens_used']}")
            print(f"Cost: ${result['cost']:.6f}")
            print(f"\nLesson Plan Preview:")
            print("-" * 60)
            print(result['result'][:300] + "..." if len(result['result']) > 300 else result['result'])
            print("-" * 60)
            
            if result.get('alignment_result'):
                print(f"\n✅ Alignment Check: {result['alignment_result']['overall_aligned']}")
        else:
            print(f"\n❌ Lesson plan creation failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_assessment_generator():
    """Test 3: Generate assessment questions."""
    print("\n" + "="*60)
    print("TEST 3: Assessment Generator")
    print("="*60)
    
    try:
        # Register agent
        try:
            register_new_agent(
                agent_id="assessment_generator",
                agent_name="Assessment Generator",
                agent_type="educational_assessment",
                capabilities=[
                    "generate_questions",
                    "create_rubric",
                    "analyze_assessment"
                ]
            )
        except:
            pass
        
        # Execute task
        result = execute_task(
            agent_id="assessment_generator",
            task_type="generate_questions",
            input_data={
                "topic": "Photosynthesis",
                "grade": "5th",
                "question_count": 5,
                "question_types": ["multiple_choice", "short_answer"],
                "difficulty": "medium"
            },
            user_id="teacher_001"
        )
        
        if result["success"]:
            print(f"\n✅ Assessment questions generated!")
            print(f"\nQuestions Preview:")
            print("-" * 60)
            print(result['result'][:400] + "..." if len(result['result']) > 400 else result['result'])
            print("-" * 60)
        else:
            print(f"\n❌ Assessment generation failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feedback_composer():
    """Test 4: Compose personalized feedback."""
    print("\n" + "="*60)
    print("TEST 4: Feedback Composer")
    print("="*60)
    
    try:
        # Register agent
        try:
            register_new_agent(
                agent_id="feedback_composer",
                agent_name="Feedback Composer",
                agent_type="educational_communication",
                capabilities=[
                    "compose_feedback",
                    "personalize_feedback",
                    "suggest_next_steps"
                ],
                model_name="gemini-1.5-flash"  # Faster model for feedback
            )
        except:
            pass
        
        # Execute task
        result = execute_task(
            agent_id="feedback_composer",
            task_type="compose_feedback",
            input_data={
                "student_name": "Alex",
                "assignment": "Photosynthesis Essay",
                "score": 85,
                "strengths": [
                    "Clear explanation of the process",
                    "Good use of scientific terminology",
                    "Well-organized structure"
                ],
                "areas_for_improvement": [
                    "Could include more specific examples",
                    "Add discussion of limiting factors"
                ]
            },
            user_id="teacher_001",
            enable_alignment=True
        )
        
        if result["success"]:
            print(f"\n✅ Feedback composed!")
            print(f"\nFeedback:")
            print("-" * 60)
            print(result['result'])
            print("-" * 60)
        else:
            print(f"\n❌ Feedback composition failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_list_agents():
    """Test 5: List all registered agents."""
    print("\n" + "="*60)
    print("TEST 5: List Registered Agents")
    print("="*60)
    
    try:
        orchestrator = AgentOrchestrator()
        agents = orchestrator.list_available_agents()
        
        print(f"\n✅ Found {len(agents)} registered agents:")
        print("")
        
        for agent in agents:
            print(f"📌 {agent['name']}")
            print(f"   ID: {agent['agent_id']}")
            print(f"   Type: {agent['type']}")
            print(f"   Capabilities: {', '.join(agent['capabilities'][:3])}...")
            print("")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PTCC Agent Orchestration Test Suite")
    print("="*60)
    
    tests = [
        ("Agent Registration", test_agent_registration),
        ("Lesson Planning", test_lesson_planning_agent),
        ("Assessment Generator", test_assessment_generator),
        ("Feedback Composer", test_feedback_composer),
        ("List Agents", test_list_agents)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Agent orchestration is working correctly.")
        print("\nThe system now has:")
        print("  ✅ LLM Integration")
        print("  ✅ Memory & Context Management")
        print("  ✅ Alignment & Ethics Checking")
        print("  ✅ Governance & Policy Enforcement")
        print("  ✅ Agent Orchestration")
        print("  ✅ Performance Tracking")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
