"""
Personal Teaching Command Center (PTCC) Backend
FastAPI application for the RAG school system
"""

import logging
import time
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .api.briefing import router as briefing_router
from .api.search import router as search_router
from .api.students import router as students_router
from .api.file_import import router as import_router
from .api.agents_api import router as agents_api_router
from .api.chat import router as chat_router
from .api.orchestration import router as orchestration_router
from .api.workflows import router as workflows_router, init_workflow_engine
from .api.classroom_tools import router as classroom_tools_router
from .api.cca import router as cca_router
from .api.digital_citizenship import router as digital_citizenship_router
from .api.quiz_analytics import router as quiz_analytics_router
from .api.behavior_management import router as behavior_management_router
from .api.documents import router as documents_router
from .api.safeguarding import router as safeguarding_router
from .api.teacher_assistant import router as teacher_assistant_router
from .api.staff_router import router as staff_router
from .api.timetable_router import router as timetable_router
from .api.accommodations_router import router as accommodations_router
from .api.lite_endpoints import router as lite_router
from .core.agent_orchestrator import AgentOrchestrator
from .core.config import get_settings
from .core.database import create_tables, get_db
from .core.logging_config import setup_logging
from .core.safeguarding_orchestrator import initialize_safeguarding_system


# Setup logging
# Get settings before setting up logging
settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)


def validate_environment():
    """
    Validate critical environment variables and configuration on startup.
    Logs clear warnings if issues found.
    """
    issues = []
    
    # Check JWT_SECRET
    jwt_secret = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
    if jwt_secret == 'dev-secret-key-change-in-production':
        issues.append("⚠️  JWT_SECRET using default dev value - change in production")
    
    # Check GEMINI_API_KEY
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    if not gemini_key or len(gemini_key) <= 5:
        logger.warning("⚠️  GEMINI_API_KEY not configured - AI features will be disabled")
    elif gemini_key.startswith('sk-') or 'test' in gemini_key.lower():
        issues.append("⚠️  GEMINI_API_KEY looks malformed or is a test key")
    else:
        logger.info("✓ GEMINI_API_KEY configured")
    
    if issues:
        for issue in issues:
            logger.warning(issue)
    
    return True


def get_allowed_origins():
    """
    Get CORS allowed origins from config or environment.
    Fallback to safe defaults.
    """
    # Try to get from env var first
    env_origins = os.getenv('CORS_ORIGINS', '')
    if env_origins:
        return env_origins.split(',')
    
    # Default safe origins (localhost and common test IPs)
    return [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",  # Mobile PWA
        "http://localhost:5175",  # Classroom Tools
        "http://localhost:5176",  # CCA Comments
        "http://localhost:5177",  # Behaviour Management
        "http://localhost:5178",  # Intervention Priority
        "http://localhost:5179",  # Progress Dashboard
        "http://localhost:5180",  # Seating Chart
        "http://localhost:5181",  # Group Formation
        "http://localhost:5182",  # Differentiation
        "http://localhost:5183",  # Quiz Upload
        "http://localhost:5184",  # Performance Trends
        "http://localhost:5185",  # Progress Levels
        "http://localhost:5186",  # At-Risk Students
        "http://localhost:5187",  # Assessment Analytics Overview
        "http://localhost:8501",  # Streamlit Dashboard
        "http://localhost:8502",
        # Add network-specific IPs if needed via .env
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting PTCC backend...")
    
    # Validate environment on startup
    validate_environment()

    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")

    # Initialize workflow engine (needed by /api/workflows)
    try:
        orchestrator = AgentOrchestrator()
        init_workflow_engine(orchestrator)
        logger.info("Workflow engine initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize workflow engine: {e}")

    # Initialize safeguarding system (privacy-preserving student analysis)
    # Set to None by default - will be initialized lazily if needed
    app.state.safeguarding = None
    
    try:
        import os
        api_key = os.getenv('GEMINI_API_KEY', '')
        
        if not api_key or len(api_key) <= 5:
            logger.info("GEMINI_API_KEY not configured - AI features will be disabled")
        else:
            logger.info("Gemini API key found - will initialize on first use")
    except Exception as e:
        logger.warning(f"Error checking Gemini API key: {e}")

    # Initialize RAG engine and ChromaDB collections (deferred for faster startup)
    try:
        # Don't initialize RAG engine immediately to speed up startup
        # It will be initialized on first use
        logger.info("RAG engine initialization deferred")
    except Exception as e:
        logger.warning(f"Failed to defer RAG engine initialization: {e}")

    logger.info("PTCC backend started successfully")
    yield

    logger.info("Shutting down PTCC backend...")


# Create FastAPI application
app = FastAPI(
    title="Personal Teaching Command Center",
    description="Local-first AI-powered information management system for teachers",
    version="1.0.0",
    lifespan=lifespan,
)


# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(briefing_router, prefix="/api/briefing", tags=["briefing"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(students_router, prefix="/api/students", tags=["students"])
app.include_router(import_router, prefix="/api/import", tags=["import"])
app.include_router(agents_api_router)
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(orchestration_router)
app.include_router(workflows_router)
app.include_router(classroom_tools_router, prefix="/api/classroom-tools", tags=["classroom-tools"])
app.include_router(cca_router, prefix="/api/cca", tags=["cca"])
app.include_router(digital_citizenship_router, prefix="/api/digital-citizenship", tags=["digital-citizenship"])
app.include_router(quiz_analytics_router, prefix="/api/quiz-analytics", tags=["quiz-analytics"])
app.include_router(behavior_management_router, prefix="/api/behavior-management", tags=["behavior-management"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(safeguarding_router, prefix="/api/safeguarding", tags=["safeguarding"])
app.include_router(teacher_assistant_router)  # No prefix - uses /api/teacher-assistant from router

# Include context routers (Phase 1 APIs)
app.include_router(staff_router)
app.include_router(timetable_router)
app.include_router(accommodations_router)

# Include PTCC Lite endpoints (YOUR ICT CLASSES ONLY)
app.include_router(lite_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic API information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PTCC - Personal Teaching Command Center</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .api-info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .endpoint { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏫 Personal Teaching Command Center</h1>
                <p>Local-first AI-powered information management system for teachers</p>
            </div>

            <div class="api-info">
                <h2>🚀 Quick Start</h2>
                <div class="endpoint">
                    <strong>CLI Briefing:</strong> <code>python cli.py briefing</code>
                </div>
                <div class="endpoint">
                    <strong>Search:</strong> <code>python cli.py search "your query"</code>
                </div>
            </div>

            <div class="api-info">
                <h2>📚 API Endpoints</h2>
                <div class="endpoint">
                    <strong>GET /api/briefing/today</strong> - Get today's briefing
                </div>
                <div class="endpoint">
                    <strong>GET /api/search?q=query</strong> - Semantic search across documents
                </div>
                <div class="endpoint">
                    <strong>GET /api/students</strong> - List all students
                </div>
            </div>

            <div class="api-info">
                <h2>⚙️ Configuration</h2>
                <p>Edit <code>config/config.yaml</code> to customize school settings, file paths, and system behavior.</p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = next(get_db())
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db.close()
        except Exception as e:
            db.close()
            raise e

        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="System unhealthy")


@app.get("/api/health")
async def api_health_check():
    """Health check endpoint (API prefix for frontend compatibility)"""
    try:
        db = next(get_db())
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db.close()
        except Exception as e:
            db.close()
            raise e

        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="System unhealthy")


@app.get("/api/status")
async def system_status():
    """
    Get detailed system status including configuration and health.
    
    Returns:
    - Backend status
    - Database connection
    - LLM provider and model
    - Configuration status
    - Environment warnings
    """
    from .core.config import get_gemini_model
    
    # Check environment
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    gemini_configured = bool(gemini_key and len(gemini_key) > 5)
    jwt_secret = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
    
    # Check database
    try:
        db = next(get_db())
        db_status = "connected"
        db.close()
    except Exception as e:
        db_status = "disconnected"
        logger.error(f"Database status check failed: {e}")
    
    # Gather warnings
    warnings = []
    if jwt_secret == 'dev-secret-key-change-in-production':
        warnings.append("JWT_SECRET using default dev value")
    if not gemini_configured:
        warnings.append("GEMINI_API_KEY not configured - AI features disabled")
    
    return {
        "status": "operational",
        "timestamp": time.time(),
        "components": {
            "backend": "connected",
            "database": db_status,
            "llm_provider": "gemini" if gemini_configured else "disabled",
            "llm_model": get_gemini_model() if gemini_configured else None,
        },
        "configuration": {
            "gemini_api_key_configured": gemini_configured,
            "jwt_secret_is_default": jwt_secret == 'dev-secret-key-change-in-production',
            "cors_origins": len(get_allowed_origins()),
        },
        "warnings": warnings if warnings else None,
        "version": "1.0.0"
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disabled to avoid import errors during module changes
        log_level="info"
    )
