"""
Teacher Assistant Lazy Initialization

Provides endpoint to enable Teacher Assistant (Gemini AI) on-demand.
This avoids startup delays and warnings - features only initialize when teacher clicks button.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/teacher-assistant", tags=["teacher-assistant"])


@router.post("/enable")
async def enable_teacher_assistant(req: Request, api_key: str = None) -> Dict[str, Any]:
    """
    Enable Teacher Assistant (AI features) on demand.
    
    Called when user clicks "Enable Teacher Assistant" button.
    Initializes Gemini connection and safeguarding system lazily.
    
    Args:
        api_key: Optional Gemini API key passed from frontend
    
    Returns:
        Status of Teacher Assistant activation
    """
    try:
        import os
        from backend.core.gemini_client import GeminiClient, GeminiConfig
        from backend.core.safeguarding_orchestrator import initialize_safeguarding_system
        
        # Check if already initialized
        if hasattr(req.app.state, "safeguarding") and req.app.state.safeguarding is not None:
            return {
                "status": "already_enabled",
                "message": "Teacher Assistant is already enabled",
                "features": [
                    "Smart Student Analysis",
                    "At-Risk Detection",
                    "Behavior Pattern Recognition",
                    "Learning Path Suggestions"
                ]
            }
        
        # Get API key from parameter or environment
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY', '')
        
        if not api_key or len(api_key) <= 5:
            return {
                "status": "error",
                "message": "Teacher Assistant API key not configured. Please contact system administrator.",
                "code": "MISSING_API_KEY"
            }
        
        try:
            # Initialize Gemini client
            logger.info("Initializing Gemini client for Teacher Assistant...")
            gemini_config = GeminiConfig(
                api_key=api_key,
                model="gemini-2.5-flash-lite",
                temperature=0.7,
                max_tokens=2048
            )
            
            gemini_client = GeminiClient(gemini_config)
            
            if not gemini_client.is_available():
                return {
                    "status": "error",
                    "message": "Failed to connect to AI provider. Please try again.",
                    "code": "AI_CONNECTION_FAILED"
                }
            
            # Initialize safeguarding system
            logger.info("Initializing safeguarding system...")
            safeguarding_orchestrator = initialize_safeguarding_system(gemini_client)
            req.app.state.safeguarding = safeguarding_orchestrator
            
            logger.info("✓ Teacher Assistant enabled successfully")
            
            return {
                "status": "success",
                "message": "Teacher Assistant activated! Smart features are now available.",
                "features": [
                    "Smart Student Analysis - Get AI insights about student performance",
                    "At-Risk Detection - Automatically identify students who need support",
                    "Behavior Pattern Recognition - Find patterns in student behavior",
                    "Learning Path Suggestions - Get personalized learning recommendations"
                ],
                "activated_at": __import__('datetime').datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize Teacher Assistant: {e}")
            return {
                "status": "error",
                "message": f"Failed to activate Teacher Assistant: {str(e)}",
                "code": "INITIALIZATION_ERROR"
            }
    
    except Exception as e:
        logger.error(f"Unexpected error enabling Teacher Assistant: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enable Teacher Assistant: {str(e)}"
        )


@router.get("/status")
async def get_teacher_assistant_status(req: Request) -> Dict[str, Any]:
    """
    Get current Teacher Assistant status.
    
    Returns:
        Current status and available features
    """
    try:
        is_enabled = (
            hasattr(req.app.state, "safeguarding") 
            and req.app.state.safeguarding is not None
        )
        
        return {
            "status": "enabled" if is_enabled else "disabled",
            "message": "Teacher Assistant is " + ("enabled" if is_enabled else "disabled"),
            "features_available": is_enabled,
            "available_features": [
                "Smart Student Analysis",
                "At-Risk Detection",
                "Behavior Pattern Recognition",
                "Learning Path Suggestions"
            ] if is_enabled else []
        }
    
    except Exception as e:
        logger.error(f"Error checking Teacher Assistant status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check status: {str(e)}"
        )


@router.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """
    Get available Teacher Assistant capabilities.
    
    Returns:
        List of capabilities and their descriptions
    """
    return {
        "status": "available",
        "capabilities": {
            "smart_student_analysis": {
                "name": "Smart Student Analysis",
                "description": "Get AI-powered insights about individual student performance and needs",
                "endpoint": "/api/safeguarding/analyze"
            },
            "at_risk_detection": {
                "name": "At-Risk Detection",
                "description": "Automatically identify students who may need additional support",
                "endpoint": "/api/agents/at-risk-analysis"
            },
            "behavior_patterns": {
                "name": "Behavior Pattern Recognition",
                "description": "Discover patterns in student behavior across time",
                "endpoint": "/api/search"
            },
            "learning_recommendations": {
                "name": "Learning Path Suggestions",
                "description": "Get AI recommendations for personalized learning paths",
                "endpoint": "/api/agents/learning-path"
            }
        },
        "note": "Use /api/teacher-assistant/enable to activate these features"
    }
