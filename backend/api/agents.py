#!/usr/bin/env python3
"""
Teacher Tools Agents API for PTCC

API endpoints for teacher-focused AI agents that integrate with PTCC's
student management and briefing systems.

Features:
- At-Risk Student Identification
- Classroom Behavior Management
- Personalized Learning Path Creation
- Assessment Analytics
- Lesson Planning Support
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import json

from ..core.database import get_db
from ..core.logging_config import get_logger

logger = get_logger("api.agents")
router = APIRouter()

# Import teacher tools agents with robust path resolution
def load_teacher_tools_agents():
    """Load teacher tools agents with robust path resolution"""
    try:
        import sys
        import os

        # Get current file location and find agents directory
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        agents_dir = os.path.join(current_dir, '..', 'agents', 'teacher-tools')

        if not os.path.exists(agents_dir):
            logger.warning(f"Agents directory not found: {agents_dir}")
            return None

        # Add agents directory to path
        agents_path = os.path.abspath(agents_dir)
        if agents_path not in sys.path:
            sys.path.insert(0, agents_path)

        # Import agents with fallback handling
        try:
            from at_risk_identifier.agent import AtRiskStudentAgent
        except ImportError:
            logger.warning("AtRiskStudentAgent not found, using placeholder")
            AtRiskStudentAgent = None

        try:
            from behavior_manager.agent import ClassroomBehaviorAgent
        except ImportError:
            logger.warning("ClassroomBehaviorAgent not found, using placeholder")
            ClassroomBehaviorAgent = None

        try:
            from learning_path.agent import PersonalizedLearningPathAgent
        except ImportError:
            logger.warning("PersonalizedLearningPathAgent not found, using placeholder")
            PersonalizedLearningPathAgent = None

        # Check if all agents were loaded successfully
        if AtRiskStudentAgent and ClassroomBehaviorAgent and PersonalizedLearningPathAgent:
            logger.info("✅ All teacher tools agents loaded successfully")
            return {
                'at_risk': AtRiskStudentAgent,
                'behavior': ClassroomBehaviorAgent,
                'learning_path': PersonalizedLearningPathAgent
            }
        else:
            logger.warning("Some agents failed to load, using placeholders for missing ones")
            return None

        logger.info("✅ Teacher tools agents loaded successfully")
        return {
            'at_risk': AtRiskStudentAgent,
            'behavior': ClassroomBehaviorAgent,
            'learning_path': PersonalizedLearningPathAgent
        }

    except ImportError as e:
        logger.warning(f"Teacher tools agents not found: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading teacher tools agents: {e}")
        return None

# Load agents
loaded_agents = load_teacher_tools_agents()

if loaded_agents:
    AtRiskStudentAgent = loaded_agents['at_risk']
    ClassroomBehaviorAgent = loaded_agents['behavior']
    PersonalizedLearningPathAgent = loaded_agents['learning_path']
else:
    # Create placeholder agents for when modules aren't available
    logger.warning("Using placeholder agents - modules not available")

    class PlaceholderAgent:
        def process(self, input_data):
            return {
                "result": "Agent not available - modules not found",
                "explanation": "Agent modules could not be imported",
                "confidence": 0.0,
                "metadata": {"error": "Agent modules not available"}
            }

    AtRiskStudentAgent = PlaceholderAgent
    ClassroomBehaviorAgent = PlaceholderAgent
    PersonalizedLearningPathAgent = PlaceholderAgent

# Initialize agents
at_risk_agent = AtRiskStudentAgent()
behavior_agent = ClassroomBehaviorAgent()
learning_path_agent = PersonalizedLearningPathAgent()

# Pydantic models
class AgentRequest(BaseModel):
    """Request model for agent processing"""
    text: str
    task_type: str
    metadata: Optional[Dict[str, Any]] = {}

class AgentResponse(BaseModel):
    """Response model for agent processing"""
    result: str
    explanation: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class AtRiskAnalysisRequest(BaseModel):
    """Request for at-risk student analysis"""
    student_id: Optional[int] = None
    class_code: Optional[str] = None
    analysis_type: str = "individual"  # individual, class, system

class BehaviorAnalysisRequest(BaseModel):
    """Request for behavior analysis"""
    class_code: str
    analysis_type: str = "comprehensive"  # comprehensive, trends, insights

class LearningPathRequest(BaseModel):
    """Request for learning path creation"""
    student_id: Optional[int] = None
    class_code: Optional[str] = None
    path_type: str = "individual"  # individual, class

# Agent endpoints
@router.post("/at-risk/analyze", response_model=AgentResponse)
async def analyze_at_risk_students(request: AtRiskAnalysisRequest, db: Session = Depends(get_db)):
    """Analyze students for at-risk indicators"""
    try:
        # Create agent input
        if request.analysis_type == "individual" and request.student_id:
            input_data = {
                "text": f"Analyze student {request.student_id} for risk factors",
                "task_type": "analyze_student",
                "metadata": {"student_id": request.student_id}
            }
        elif request.analysis_type == "class" and request.class_code:
            input_data = {
                "text": f"Analyze class {request.class_code} for at-risk students",
                "task_type": "analyze_class",
                "metadata": {"class_code": request.class_code}
            }
        else:
            input_data = {
                "text": "Analyze system for at-risk students",
                "task_type": "system_summary",
                "metadata": {}
            }

        # Process with agent
        result = at_risk_agent.process(input_data)

        # Normalize output (supports dict or object-like)
        if isinstance(result, dict):
            return AgentResponse(
                result=result.get("result", ""),
                explanation=result.get("explanation", ""),
                confidence=float(result.get("confidence", 0.0)),
                metadata=result.get("metadata")
            )
        else:
            return AgentResponse(
                result=getattr(result, "result", ""),
                explanation=getattr(result, "explanation", ""),
                confidence=float(getattr(result, "confidence", 0.0)),
                metadata=getattr(result, "metadata", None)
            )

    except Exception as e:
        logger.error(f"Error in at-risk analysis: {e}")
        raise HTTPException(status_code=500, detail=f"At-risk analysis failed: {str(e)}")

@router.post("/behavior/analyze", response_model=AgentResponse)
async def analyze_classroom_behavior(request: BehaviorAnalysisRequest, db: Session = Depends(get_db)):
    """Analyze classroom behavior patterns"""
    try:
        # Create agent input
        try:
            from ...shared.base_agent import AgentInput, AgentOutput
        except ImportError:
            # Create simple fallback classes
            class AgentInput:
                def __init__(self, text, task_type, metadata=None):
                    self.text = text
                    self.task_type = task_type
                    self.metadata = metadata or {}

            class AgentOutput:
                def __init__(self, result, explanation, confidence, metadata=None):
                    self.result = result
                    self.explanation = explanation
                    self.confidence = confidence
                    self.metadata = metadata

        if request.analysis_type == "comprehensive":
            input_data = {
                "text": f"Analyze classroom behavior for {request.class_code}",
                "task_type": "analyze_class",
                "metadata": {"class_code": request.class_code}
            }
        else:  # insights
            input_data = {
                "text": f"Get behavior insights for {request.class_code}",
                "task_type": "behavior_insights",
                "metadata": {"class_code": request.class_code}
            }

        # Process with agent
        result = behavior_agent.process(input_data)

        # Normalize output (supports dict or object-like)
        if isinstance(result, dict):
            return AgentResponse(
                result=result.get("result", ""),
                explanation=result.get("explanation", ""),
                confidence=float(result.get("confidence", 0.0)),
                metadata=result.get("metadata")
            )
        else:
            return AgentResponse(
                result=getattr(result, "result", ""),
                explanation=getattr(result, "explanation", ""),
                confidence=float(getattr(result, "confidence", 0.0)),
                metadata=getattr(result, "metadata", None)
            )

    except Exception as e:
        logger.error(f"Error in behavior analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Behavior analysis failed: {str(e)}")

@router.post("/learning-path/create", response_model=AgentResponse)
async def create_learning_path(request: LearningPathRequest, db: Session = Depends(get_db)):
    """Create personalized learning path"""
    try:
        # Create agent input
        try:
            from ..shared.base_agent import AgentInput
        except ImportError:
            # Create simple fallback class
            class AgentInput:
                def __init__(self, text, task_type, metadata=None):
                    self.text = text
                    self.task_type = task_type
                    self.metadata = metadata or {}

        if request.path_type == "individual" and request.student_id:
            input_data = {
                "text": f"Create personalized learning path for student {request.student_id}",
                "task_type": "create_path",
                "metadata": {"student_id": request.student_id}
            }
        else:  # class analysis
            input_data = {
                "text": f"Analyze learning paths for class {request.class_code}",
                "task_type": "analyze_class",
                "metadata": {"class_code": request.class_code}
            }

        # Process with agent
        result = learning_path_agent.process(input_data)

        # Normalize output (supports dict or object-like)
        if isinstance(result, dict):
            return AgentResponse(
                result=result.get("result", ""),
                explanation=result.get("explanation", ""),
                confidence=float(result.get("confidence", 0.0)),
                metadata=result.get("metadata")
            )
        else:
            return AgentResponse(
                result=getattr(result, "result", ""),
                explanation=getattr(result, "explanation", ""),
                confidence=float(getattr(result, "confidence", 0.0)),
                metadata=getattr(result, "metadata", None)
            )

    except Exception as e:
        logger.error(f"Error in learning path creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Learning path creation failed: {str(e)}")

@router.get("/available")
async def list_available_agents(db: Session = Depends(get_db)):
    """List all available agents from the database (data-driven classroom management only)"""
    try:
        # Import AgentRegistry model
        from ..models.agent_models import AgentRegistry
        
        # Only show data-driven classroom management agents
        allowed_agents = [
            "at_risk_identifier",
            "behavior_manager",
            "learning_path_creator"
        ]
        
        # Query database for active agents
        db_agents = db.query(AgentRegistry).filter(
            AgentRegistry.is_active == True,
            AgentRegistry.is_enabled == True,
            AgentRegistry.agent_id.in_(allowed_agents)
        ).all()
        
        # Map old agent IDs to maintain compatibility
        agent_id_map = {
            "at_risk_identifier": "at-risk-identifier",
            "behavior_manager": "behavior-manager",
            "learning_path_creator": "learning-path-creator"
        }
        
        # Endpoint mapping for known agents
        endpoint_map = {
            "at_risk_identifier": [{"method": "POST", "path": "/api/agents/at-risk/analyze", "description": "Analyze students for at-risk indicators"}],
            "behavior_manager": [{"method": "POST", "path": "/api/agents/behavior/analyze", "description": "Analyze classroom behavior"}],
            "learning_path_creator": [{"method": "POST", "path": "/api/agents/learning-path/create", "description": "Create personalized learning path"}]
        }
        
        # Build agent list
        agents = []
        for db_agent in db_agents:
            # Map to frontend-compatible ID
            agent_id = agent_id_map.get(db_agent.agent_id, db_agent.agent_id)
            
            # Determine category from agent type
            category_map = {
                "educational_analysis": "Student Support",
                "educational_management": "Classroom Management",
                "educational_planning": "Academic Planning",
                "educational_assessment": "Assessment",
                "educational_communication": "Communication"
            }
            category = category_map.get(db_agent.agent_type, "Other")
            
            # Get endpoints if available
            endpoints = endpoint_map.get(db_agent.agent_id, [])
            
            agents.append({
                "id": agent_id,
                "name": db_agent.agent_name,
                "description": f"{db_agent.agent_name} - {db_agent.agent_type}",
                "category": category,
                "endpoints": endpoints,
                "capabilities": db_agent.capabilities,
                "model": f"{db_agent.model_provider}/{db_agent.model_name}"
            })
        
        return {"agents": agents, "total": len(agents)}
        
    except Exception as e:
        logger.error(f"Error loading agents from database: {e}")
        # Fallback to hardcoded legacy agents
        agents = [
            {
                "id": "at-risk-identifier",
                "name": "At-Risk Student Identifier",
                "description": "Identify students who may need additional academic or behavioral support",
                "category": "Student Support",
                "endpoints": [{"method": "POST", "path": "/api/agents/at-risk/analyze", "description": "Analyze students"}]
            },
            {
                "id": "behavior-manager",
                "name": "Classroom Behavior Manager",
                "description": "Analyze classroom behavior patterns",
                "category": "Classroom Management",
                "endpoints": [{"method": "POST", "path": "/api/agents/behavior/analyze", "description": "Analyze behavior"}]
            },
            {
                "id": "learning-path-creator",
                "name": "Personalized Learning Path Creator",
                "description": "Create individualized learning paths",
                "category": "Academic Support",
                "endpoints": [{"method": "POST", "path": "/api/agents/learning-path/create", "description": "Create learning path"}]
            }
        ]
        return {"agents": agents, "total": len(agents)}

@router.get("/categories")
async def get_agent_categories():
    """Get agent categories for organization"""
    categories = {
        "Student Support": [
            "At-Risk Student Identifier",
            "Student Progress Tracker",
            "Intervention Strategy Agent"
        ],
        "Classroom Management": [
            "Classroom Behavior Manager",
            # Parent Communication Assistant removed
        ],
        "Academic Support": [
            "Personalized Learning Path Creator",
            "Assessment Analytics Agent",
            "Lesson Planning Assistant"
        ]
    }

    return {"categories": categories}

@router.get("/health")
async def check_agents_health():
    """Check health status of all agents"""
    health_status = {}

    try:
        # Test at-risk agent
        test_input = {'text': 'test', 'task_type': 'test', 'metadata': {}}
        at_risk_agent.process(test_input)
        health_status['at_risk_identifier'] = "healthy"
    except Exception as exc:
        health_status['at_risk_identifier'] = f"error: {str(exc)}"

    try:
        # Test behavior agent
        behavior_agent.process(test_input)
        health_status['behavior_manager'] = "healthy"
    except Exception as exc:
        health_status['behavior_manager'] = f"error: {str(exc)}"

    try:
        # Test learning path agent
        learning_path_agent.process(test_input)
        health_status['learning_path_creator'] = "healthy"
    except Exception as exc:
        health_status['learning_path_creator'] = f"error: {str(exc)}"

    return {
        "status": "operational",
        "agents": health_status,
        "total_agents": len(health_status),
        "healthy_agents": len([s for s in health_status.values() if s == "healthy"])
    }