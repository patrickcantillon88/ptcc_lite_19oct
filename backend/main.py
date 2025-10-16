"""
Personal Teaching Command Center (PTCC) Backend
FastAPI application for the RAG school system
"""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .api.briefing import router as briefing_router
from .api.search import router as search_router
from .api.students import router as students_router
from .api.file_import import router as import_router
from .api.agents import router as agents_router
from .api.chat import router as chat_router
from .api.orchestration import router as orchestration_router
from .api.workflows import router as workflows_router, init_workflow_engine
from .api.classroom_tools import router as classroom_tools_router
from .api.cca import router as cca_router
from .api.guardian import router as guardian_router
from .api.quiz_analytics import router as quiz_analytics_router
from .api.ict_behavior import router as ict_behavior_router
from .api.documents import router as documents_router
from .core.agent_orchestrator import AgentOrchestrator
from .core.config import get_settings
from .core.database import create_tables, get_db
from .core.logging_config import setup_logging


# Setup logging
# Get settings before setting up logging
settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting PTCC backend...")

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
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8502",
        "http://localhost:5173",
        "http://localhost:5174",  # Project Guardian React app
        "http://172.16.28.76:5173",  # Mobile PWA network access
        "http://172.16.28.76:5174",  # Network access alternate port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(briefing_router, prefix="/api/briefing", tags=["briefing"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(students_router, prefix="/api/students", tags=["students"])
app.include_router(import_router, prefix="/api/import", tags=["import"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(orchestration_router)
app.include_router(workflows_router)
app.include_router(classroom_tools_router, prefix="/api/classroom-tools", tags=["classroom-tools"])
app.include_router(cca_router, prefix="/api/cca", tags=["cca"])
app.include_router(guardian_router, prefix="/api/guardian", tags=["guardian"])
app.include_router(quiz_analytics_router, prefix="/api/quiz-analytics", tags=["quiz-analytics"])
app.include_router(ict_behavior_router, prefix="/api/ict-behavior", tags=["ict-behavior"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])


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




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )