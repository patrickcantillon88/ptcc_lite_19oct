"""
Example PTCC API Client

Demonstrates how to use the PTCC API for agent orchestration,
lesson planning, assessments, and feedback generation.
"""

import requests
from typing import Dict, List, Optional, Any
import json


class PTCCClient:
    """Python client for PTCC API."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    # Agent Management
    
    def list_agents(self) -> List[Dict]:
        """Get list of all available agents."""
        response = self.session.get(f"{self.base_url}/api/orchestration/agents")
        response.raise_for_status()
        return response.json()
    
    def get_agent(self, agent_id: str) -> Dict:
        """Get details about a specific agent."""
        response = self.session.get(f"{self.base_url}/api/orchestration/agents/{agent_id}")
        response.raise_for_status()
        return response.json()
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        model_provider: str = "gemini",
        model_name: str = "gemini-1.5-pro"
    ) -> Dict:
        """Register a new agent."""
        data = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "agent_type": agent_type,
            "capabilities": capabilities,
            "model_provider": model_provider,
            "model_name": model_name
        }
        response = self.session.post(
            f"{self.base_url}/api/orchestration/agents/register",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    # Task Execution
    
    def execute_task(
        self,
        agent_id: str,
        task_type: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        enable_memory: bool = True,
        enable_alignment: bool = True,
        enable_governance: bool = True
    ) -> Dict:
        """Execute an agent task."""
        data = {
            "agent_id": agent_id,
            "task_type": task_type,
            "input_data": input_data,
            "user_id": user_id,
            "enable_memory": enable_memory,
            "enable_alignment": enable_alignment,
            "enable_governance": enable_governance
        }
        response = self.session.post(
            f"{self.base_url}/api/orchestration/tasks/execute",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_task_history(self, agent_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get task execution history."""
        params = {"limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        
        response = self.session.get(
            f"{self.base_url}/api/orchestration/tasks/history",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict:
        """Get details about a specific task."""
        response = self.session.get(f"{self.base_url}/api/orchestration/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    # Quick Actions
    
    def create_lesson_plan(
        self,
        grade: str,
        subject: str,
        topic: str,
        duration: str = "45 minutes",
        user_id: Optional[str] = None
    ) -> Dict:
        """Quick method to create a lesson plan."""
        params = {
            "grade": grade,
            "subject": subject,
            "topic": topic,
            "duration": duration
        }
        if user_id:
            params["user_id"] = user_id
        
        response = self.session.post(
            f"{self.base_url}/api/orchestration/quick/lesson-plan",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def generate_assessment(
        self,
        topic: str,
        grade: str,
        question_count: int = 5,
        user_id: Optional[str] = None
    ) -> Dict:
        """Quick method to generate assessment questions."""
        params = {
            "topic": topic,
            "grade": grade,
            "question_count": question_count
        }
        if user_id:
            params["user_id"] = user_id
        
        response = self.session.post(
            f"{self.base_url}/api/orchestration/quick/assessment",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def compose_feedback(
        self,
        student_name: str,
        assignment: str,
        score: int,
        strengths: List[str],
        improvements: List[str],
        user_id: Optional[str] = None
    ) -> Dict:
        """Quick method to compose student feedback."""
        params = {
            "student_name": student_name,
            "assignment": assignment,
            "score": score,
            "strengths": strengths,
            "improvements": improvements
        }
        if user_id:
            params["user_id"] = user_id
        
        response = self.session.post(
            f"{self.base_url}/api/orchestration/quick/feedback",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    # Statistics
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        response = self.session.get(f"{self.base_url}/api/orchestration/stats/overview")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


# Example usage
def main():
    """Demonstrate API usage."""
    print("=" * 60)
    print("PTCC API Client Example")
    print("=" * 60)
    
    # Create client
    client = PTCCClient()
    
    try:
        # 1. Health check
        print("\n1. Health Check")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Database: {health['database']}")
        
        # 2. List agents
        print("\n2. Available Agents")
        agents = client.list_agents()
        print(f"   Found {len(agents)} agents:")
        for agent in agents[:3]:  # Show first 3
            print(f"   - {agent['name']} ({agent['agent_id']})")
        
        # 3. Get statistics
        print("\n3. System Statistics")
        stats = client.get_stats()
        print(f"   Total Tasks: {stats['total_tasks']}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   Total Cost: ${stats['total_cost']:.4f}")
        
        # 4. Create a lesson plan
        print("\n4. Creating Lesson Plan...")
        lesson = client.create_lesson_plan(
            grade="5th",
            subject="Science",
            topic="Solar System",
            user_id="teacher_demo"
        )
        print("   ✓ Lesson plan created!")
        print(f"   Preview: {lesson['lesson_plan'][:150]}...")
        
        # 5. Generate assessment
        print("\n5. Generating Assessment...")
        assessment = client.generate_assessment(
            topic="Solar System",
            grade="5th",
            question_count=3,
            user_id="teacher_demo"
        )
        print("   ✓ Assessment generated!")
        print(f"   Preview: {assessment['questions'][:150]}...")
        
        # 6. Compose feedback
        print("\n6. Composing Feedback...")
        feedback = client.compose_feedback(
            student_name="Alex",
            assignment="Solar System Project",
            score=88,
            strengths=["Creative presentation", "Good research"],
            improvements=["Add more details", "Include diagrams"],
            user_id="teacher_demo"
        )
        print("   ✓ Feedback composed!")
        print(f"   Preview: {feedback['feedback'][:150]}...")
        
        # 7. View recent tasks
        print("\n7. Recent Task History")
        history = client.get_task_history(limit=5)
        print(f"   Last {len(history)} tasks:")
        for task in history:
            print(f"   - {task['task_type']}: {task['status']} ({task['execution_time_ms']}ms)")
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to PTCC API")
        print("   Make sure the server is running:")
        print("   python backend/main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
