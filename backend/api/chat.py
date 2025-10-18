#!/usr/bin/env python3
"""
AI Chat API for PTCC
Provides conversational AI interface for teachers with Gemini integration,
agent calling, and context-aware responses.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import json
import logging

from ..core.database import get_db
from ..core.gemini_client import create_gemini_client_from_config, GeminiClient
from ..core.config import get_settings
from ..core.logging_config import get_logger

logger = get_logger("api.chat")
router = APIRouter()

# Initialize Gemini client
settings = get_settings()
gemini_client = create_gemini_client_from_config(settings)

def generate_fallback_response(message: str, context_data: Dict[str, Any]) -> str:
    """
    Generate a helpful response when Gemini is unavailable.
    This response makes it clear that the AI is in a limited, fallback mode.
    """
    # This is the primary message to inform the user about the state.
    main_message = (
        "**The AI Assistant is currently in fallback mode.**\n\n"
        "To unlock intelligent, conversational responses, please enable the AI features by providing a valid "
        "Gemini API key in the activation section on the Teacher Assistant page."
    )

    # Add some contextual hints based on the query.
    msg_lower = message.lower()
    contextual_hint = ""

    if any(word in msg_lower for word in ["performance", "grades", "assessment", "progress"]):
        contextual_hint = "\n\n*Hint: Once enabled, you can ask me to 'analyze the performance of class 8A'.*"
    elif any(word in msg_lower for word in ["alert", "risk", "concern", "problem"]):
        contextual_hint = "\n\n*Hint: Once enabled, you can ask me to 'identify at-risk students in my classes'.*"
    elif "student" in msg_lower:
        contextual_hint = "\n\n*Hint: Once enabled, you can ask me for a 'summary of a student\'s recent progress'.*"
    elif "capital of vietnam" in msg_lower: # Example from user's screenshot
         contextual_hint = "\n\n*Note: My primary function is to assist with teaching-related tasks and student data, not general knowledge questions.*"

    return main_message + contextual_hint

# Pydantic models
class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    """Request model for chat conversation"""
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    context_data: Optional[Dict[str, Any]] = {}
    enable_agents: bool = True
    enable_search: bool = True

class ChatResponse(BaseModel):
    """Response model for chat conversation"""
    response: str
    conversation_id: Optional[str] = None
    agents_used: List[str] = []
    search_performed: bool = False
    context_references: List[Dict[str, Any]] = []
    suggestions: List[str] = []

class QuickAction(BaseModel):
    """Quick action button model"""
    label: str
    query: str
    description: str

# Context gathering functions
def get_current_briefing_context(db: Session) -> Dict[str, Any]:
    """Get current briefing data for context"""
    try:
        from ..api.briefing import get_today_briefing
        from ..core.briefing_engine import generate_daily_briefing
        from datetime import date
        
        # Use the briefing engine directly to avoid async issues
        briefing_date = date.today()
        briefing = generate_daily_briefing(briefing_date)
        briefing_data = briefing.to_dict()
        
        return {
            "date": briefing_data.get("date"),
            "schedule": briefing_data.get("schedule", []),
            "student_alerts": briefing_data.get("student_alerts", {}),
            "insights": briefing_data.get("insights", []),
            "classes_today": briefing_data.get("metadata", {}).get("classes_today", 0),
            "total_students": briefing_data.get("metadata", {}).get("total_students", 0)
        }
    except Exception as e:
        logger.warning(f"Failed to get briefing context: {e}")
        return {}

def get_student_context(db: Session, student_name: Optional[str] = None) -> Dict[str, Any]:
    """Get student-related context"""
    try:
        from ..models.database_models import Student
        query = db.query(Student)

        if student_name:
            # Try to find student by name
            student = query.filter(Student.name.ilike(f"%{student_name}%")).first()
            if student:
                return {
                    "student_info": {
                        "id": student.id,
                        "name": student.name,
                        "class_code": student.class_code,
                        "year_group": student.year_group,
                        "campus": student.campus,
                        "support_level": student.support_level,
                        "support_notes": student.support_notes
                    }
                }

        # Return general student stats
        total_students = query.count()
        class_distribution = {}
        for cls in ["3A", "4B", "5C", "6A"]:
            count = query.filter(Student.class_code == cls).count()
            if count > 0:
                class_distribution[cls] = count

        return {
            "student_stats": {
                "total_students": total_students,
                "class_distribution": class_distribution
            }
        }
    except Exception as e:
        logger.warning(f"Failed to get student context: {e}")
        return {}

def get_agent_tools() -> Dict[str, Any]:
    """Get available agent tools for chat"""
    return {
        "at_risk_identifier": {
            "description": "Analyze students for at-risk indicators",
            "parameters": {
                "student_id": "optional student ID",
                "class_code": "optional class code",
                "analysis_type": "individual, class, or system"
            }
        },
        "behavior_manager": {
            "description": "Analyze classroom behavior patterns",
            "parameters": {
                "class_code": "required class code",
                "analysis_type": "comprehensive or insights"
            }
        },
        "learning_path": {
            "description": "Create personalized learning paths",
            "parameters": {
                "student_id": "optional student ID",
                "class_code": "optional class code",
                "path_type": "individual or class"
            }
        }
    }

def perform_search(query: str, db: Session) -> Dict[str, Any]:
    """Perform search and return results"""
    try:
        from ..api.search import search_all
        search_results = search_all(query, limit=5, db=db)
        return {
            "performed": True,
            "results": search_results.get("results", [])[:3],  # Limit to top 3
            "total_found": search_results.get("total_count", 0)
        }
    except Exception as e:
        logger.warning(f"Search failed: {e}")
        return {"performed": False, "error": str(e)}

def call_agent(agent_name: str, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Call a specific agent with parameters"""
    try:
        if agent_name == "at_risk_identifier":
            from ..api.agents import at_risk_agent
            input_data = {
                "text": f"Analyze {parameters.get('analysis_type', 'system')} for at-risk indicators",
                "task_type": "analyze_student" if parameters.get('student_id') else "analyze_class" if parameters.get('class_code') else "system_summary",
                "metadata": parameters
            }
            result = at_risk_agent.process(input_data)
            # Handle both dict and object responses
            if isinstance(result, dict):
                return {"success": True, "result": result.get("result", ""), "confidence": result.get("confidence", 0.0)}
            else:
                return {"success": True, "result": getattr(result, "result", ""), "confidence": getattr(result, "confidence", 0.0)}

        elif agent_name == "behavior_manager":
            from ..api.agents import behavior_agent
            input_data = {
                "text": f"Analyze behavior for class {parameters.get('class_code')}",
                "task_type": "analyze_class" if parameters.get('analysis_type') == 'comprehensive' else "behavior_insights",
                "metadata": parameters
            }
            result = behavior_agent.process(input_data)
            # Handle both dict and object responses
            if isinstance(result, dict):
                return {"success": True, "result": result.get("result", ""), "confidence": result.get("confidence", 0.0)}
            else:
                return {"success": True, "result": getattr(result, "result", ""), "confidence": getattr(result, "confidence", 0.0)}

        elif agent_name == "learning_path":
            from ..api.agents import learning_path_agent
            input_data = {
                "text": f"Create learning path for {parameters.get('path_type', 'individual')}",
                "task_type": "create_path" if parameters.get('student_id') else "analyze_class",
                "metadata": parameters
            }
            result = learning_path_agent.process(input_data)
            # Handle both dict and object responses
            if isinstance(result, dict):
                return {"success": True, "result": result.get("result", ""), "confidence": result.get("confidence", 0.0)}
            else:
                return {"success": True, "result": getattr(result, "result", ""), "confidence": getattr(result, "confidence", 0.0)}

        else:
            return {"success": False, "error": f"Unknown agent: {agent_name}"}

    except Exception as e:
        logger.error(f"Agent call failed: {e}")
        return {"success": False, "error": str(e)}

def build_system_prompt(context_data: Dict[str, Any]) -> str:
    """Build system prompt with BIS HCMC context"""
    prompt = """You are an AI assistant for teachers at BIS HCMC (British International School Ho Chi Minh City).
You have access to student data, class schedules, assessment results, and behavior logs.

Current Context:
"""

    # Add briefing context
    briefing = context_data.get("briefing", {})
    if briefing:
        prompt += f"""
- Today's date: {briefing.get('date', 'Unknown')}
- Classes today: {briefing.get('classes_today', 0)}
- Total students: {briefing.get('total_students', 0)}
- Schedule: {len(briefing.get('schedule', []))} periods
"""

        # Add student alerts
        alerts = briefing.get('student_alerts', {})
        if alerts:
            prompt += f"- Student alerts in {len(alerts)} classes\n"

    # Add student context
    student_info = context_data.get("student_info", {})
    if student_info:
        prompt += f"""
Specific Student: {student_info.get('name')} (Class {student_info.get('class_code')})
- Year Group: {student_info.get('year_group')}
- Campus: {student_info.get('campus')}
- Support Level: {student_info.get('support_level')}
"""

    # Add available tools
    prompt += """
Available Tools:
- Search student data, logs, and assessments
- Call AI agents: at-risk-identifier, behavior-manager, learning-path
- Access current briefing information

Guidelines:
- Be helpful, professional, and supportive
- Reference specific students, classes, or data when relevant
- Suggest actionable recommendations
- If you need more information, ask specific questions
- Use tools when appropriate to provide accurate, data-driven responses

"""

    return prompt

def analyze_query_for_tools(message: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze user query to determine if tools should be used"""
    analysis_prompt = f"""
Analyze this teacher query and determine what tools or actions to take:

Query: "{message}"

Available tools:
- search: For finding specific information about students, assessments, logs
- at_risk_identifier: For analyzing student risk factors
- behavior_manager: For classroom behavior analysis
- learning_path: For creating personalized learning plans

Context: {json.dumps(context_data, indent=2)}

Respond with JSON:
{{
    "needs_search": true/false,
    "search_query": "search terms if needed",
    "needs_agent": true/false,
    "agent_name": "agent name if needed",
    "agent_params": {{"param": "value"}},
    "response_type": "direct/informational/analytical/actionable"
}}
"""

    response = gemini_client.generate_text(analysis_prompt, temperature=0.3, max_tokens=512)
    if not response:
        return {"needs_search": False, "needs_agent": False}

    try:
        # Extract JSON from response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response[start:end]
            return json.loads(json_str)
    except Exception as e:
        logger.warning(f"Failed to parse tool analysis: {e}")

    return {"needs_search": False, "needs_agent": False}

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint for AI conversation"""
    try:
        # Gather context data
        context_data = {
            "briefing": get_current_briefing_context(db),
            "student_info": get_student_context(db, request.context_data.get("student_name")),
            "available_tools": get_agent_tools()
        }

        # Analyze query for tool usage
        tool_analysis = analyze_query_for_tools(request.message, context_data)

        agents_used = []
        search_results = None
        context_references = []

        # Perform search if needed
        if tool_analysis.get("needs_search", False) and request.enable_search:
            search_query = tool_analysis.get("search_query", request.message)
            search_results = perform_search(search_query, db)
            if search_results.get("performed"):
                context_data["search_results"] = search_results
                context_references.extend([{
                    "type": "search_result",
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:100] + "..."
                } for r in search_results.get("results", [])])

        # Call agent if needed
        if tool_analysis.get("needs_agent", False) and request.enable_agents:
            agent_name = tool_analysis.get("agent_name")
            agent_params = tool_analysis.get("agent_params", {})
            agent_result = call_agent(agent_name, agent_params, db)
            if agent_result.get("success"):
                agents_used.append(agent_name)
                context_data[f"{agent_name}_result"] = agent_result
                context_references.append({
                    "type": "agent_result",
                    "agent": agent_name,
                    "result": agent_result.get("result", "")[:200] + "..."
                })

        # Build conversation context
        conversation_context = ""
        if request.conversation_history:
            # Include last few messages for context
            recent_messages = request.conversation_history[-4:]  # Last 4 messages
            conversation_context = "\n".join([
                f"{msg.role}: {msg.content}" for msg in recent_messages
            ])

        # Build system prompt
        system_prompt = build_system_prompt(context_data)

        # Build full prompt for Gemini
        full_prompt = f"""{system_prompt}

Conversation History:
{conversation_context}

Current User Query: {request.message}

Please provide a helpful, context-aware response. Reference specific data when relevant and suggest actionable next steps."""

        # Get AI response (with fallback if Gemini unavailable)
        ai_response = gemini_client.generate_text(
            full_prompt,
            temperature=0.7,
            max_tokens=1024
        )

        # Use fallback response if AI unavailable
        if not ai_response:
            logger.info("AI service unavailable, using fallback response generator")
            ai_response = generate_fallback_response(request.message, context_data)

        # Generate suggestions based on context
        suggestions = []
        if context_data.get("briefing", {}).get("student_alerts"):
            suggestions.append("Check student alerts for today's classes")
        if agents_used:
            suggestions.append("Review agent analysis results above")
        if search_results and search_results.get("results"):
            suggestions.append("See search results for additional details")

        return ChatResponse(
            response=ai_response,
            agents_used=agents_used,
            search_performed=search_results is not None,
            context_references=context_references,
            suggestions=suggestions
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Chat API error: {e}\n{traceback.format_exc()}")
        # Return proper ChatResponse model for error cases
        return ChatResponse(
            response=f"I encountered an error processing your request. Please try again or contact support. Error: {str(e)[:100]}",
            agents_used=[],
            search_performed=False,
            context_references=[],
            suggestions=["Try rephrasing your question", "Check your internet connection", "Contact system administrator if issue persists"]
        )

@router.get("/quick-actions")
async def get_quick_actions() -> List[QuickAction]:
    """Get quick action buttons for common teacher queries"""
    return [
        QuickAction(
            label="📊 Class Performance",
            query="Show me the performance trends for my classes this week",
            description="Get overview of assessment results and student progress"
        ),
        QuickAction(
            label="🚨 Student Alerts",
            query="What student alerts do I need to address today?",
            description="Review urgent student issues and behavioral concerns"
        ),
        QuickAction(
            label="📅 Schedule Check",
            query="What's my schedule for today and any special notes?",
            description="Review today's classes and important reminders"
        ),
        QuickAction(
            label="🎯 At-Risk Students",
            query="Identify students who might need additional support",
            description="AI analysis of students showing risk indicators"
        ),
        QuickAction(
            label="📚 Learning Paths",
            query="Create learning plans for students who need them",
            description="Personalized learning recommendations"
        ),
        QuickAction(
            label="🔍 Search Students",
            query="Help me find information about a specific student",
            description="Search student records, assessments, and logs"
        )
    ]

@router.get("/context")
async def get_chat_context(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current context data for chat initialization"""
    return {
        "briefing": get_current_briefing_context(db),
        "student_stats": get_student_context(db),
        "available_agents": list(get_agent_tools().keys()),
        "capabilities": [
            "student_data_access",
            "agent_calling",
            "search_functionality",
            "briefing_context",
            "educational_knowledge"
        ]
    }