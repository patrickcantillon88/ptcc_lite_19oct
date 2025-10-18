import React from 'react'

const Development = ({ isDemoMode }) => {
  return (
    <div className="content-section">
      <h2>⚙️ Development</h2>

      <div className={`highlight-box ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🛠️ Code Quality & Linting</h3>
        <div className="linting-commands">
          <div className="lint-section">
            <h4>Python Linting</h4>
            <div className="code-block">
              <code>flake8 backend/ --max-line-length=120</code><br/>
              <code>black backend/ --check</code><br/>
              <code>mypy backend/</code><br/>
              <code>isort backend/ --check-only</code>
            </div>
          </div>
          
          <div className="lint-section">
            <h4>Auto-format Code</h4>
            <div className="code-block">
              <code>black backend/</code><br/>
              <code>isort backend/</code>
            </div>
          </div>

          <div className="lint-section">
            <h4>Frontend Linting</h4>
            <div className="code-block">
              <code>cd frontend/mobile-pwa</code><br/>
              <code>npm run lint</code>
            </div>
          </div>
        </div>
      </div>

      <h3>🗄️ Database Management</h3>
      
      <div className="database-commands">
        <div className="db-command">
          <h4>Initialize Database</h4>
          <div className="code-block">
            <code>python scripts/simplified_migration.py</code>
          </div>
          <p>Sets up initial database schema and tables</p>
        </div>

        <div className="db-command">
          <h4>Check Database Health</h4>
          <div className="code-block">
            <code>curl http://localhost:8001/health</code>
          </div>
          <p>Verify database connectivity and API status</p>
        </div>

        <div className="db-command">
          <h4>Backup Database</h4>
          <div className="code-block">
            <code>python -c "from backend.core.database import backup_database; backup_database()"</code>
          </div>
          <p>Create backup of current database state</p>
        </div>

        <div className="db-command">
          <h4>Query Database Directly</h4>
          <div className="code-block">
            <code>sqlite3 data/school.db ".tables"</code><br/>
            <code>sqlite3 data/school.db "SELECT COUNT(*) FROM students;"</code>
          </div>
          <p>Direct database access for debugging</p>
        </div>
      </div>

      <h3>🏗️ Development Workflow</h3>
      
      <div className="workflow-section">
        <div className="workflow-step">
          <div className="step-number">1</div>
          <div className="step-content">
            <h4>Environment Setup</h4>
            <p>Configure .env from template, set up virtual environment, install dependencies</p>
          </div>
        </div>

        <div className="workflow-step">
          <div className="step-number">2</div>
          <div className="step-content">
            <h4>Feature Development</h4>
            <p>Create feature branch, develop in appropriate component (API/Desktop/Mobile)</p>
          </div>
        </div>

        <div className="workflow-step">
          <div className="step-number">3</div>
          <div className="step-content">
            <h4>Testing & Quality</h4>
            <p>Run tests, lint code, verify functionality across all components</p>
          </div>
        </div>

        <div className="workflow-step">
          <div className="step-number">4</div>
          <div className="step-content">
            <h4>Integration</h4>
            <p>Test full system integration, verify API contracts, check UI/UX</p>
          </div>
        </div>
      </div>

      <div className={`file-organization ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>📁 File Organization Standards</h3>
        
        <div className="org-structure">
          <div className="org-item">
            <strong>backend/api/</strong> - Each file handles one domain
          </div>
          <div className="org-item">
            <strong>backend/core/</strong> - Shared infrastructure only
          </div>
          <div className="org-item">
            <strong>backend/models/</strong> - Database schemas only
          </div>
          <div className="org-item">
            <strong>backend/ingestion/</strong> - Data parsing and import
          </div>
          <div className="org-item">
            <strong>tests/</strong> - Unit and integration tests
          </div>
          <div className="org-item">
            <strong>scripts/</strong> - Setup and utility scripts
          </div>
          <div className="org-item">
            <strong>config/</strong> - Configuration files
          </div>
        </div>
      </div>

      <h3>🔧 Common Development Tasks</h3>
      
      <div className="dev-tasks">
        <div className="task-item">
          <h4>Add New API Endpoint</h4>
          <ol>
            <li>Create route function in appropriate <code>backend/api/*.py</code> file</li>
            <li>Import router in <code>backend/main.py</code></li>
            <li>Include router in app with <code>app.include_router()</code></li>
          </ol>
        </div>

        <div className="task-item">
          <h4>Add Database Table</h4>
          <ol>
            <li>Define SQLAlchemy model in <code>backend/models/database_models.py</code></li>
            <li>Model automatically included in <code>create_tables()</code></li>
            <li>Run <code>python backend/migrations/create_comprehensive_ptcc_schema.py</code></li>
          </ol>
        </div>

        <div className="task-item">
          <h4>Use LLM API</h4>
          <div className="code-block">
            <code>from backend.core.llm_integration import LLMIntegration</code><br/>
            <code>llm = LLMIntegration()</code><br/>
            <code>response = llm.generate(prompt="Your prompt", provider="gemini")</code>
          </div>
        </div>

        <div className="task-item">
          <h4>Query Student Data</h4>
          <div className="code-block">
            <code>from backend.core.database import SessionLocal</code><br/>
            <code>from backend.models.database_models import Student</code><br/>
            <code>db = SessionLocal()</code><br/>
            <code>students = db.query(Student).filter(...).all()</code>
          </div>
        </div>

        <div className="task-item">
          <h4>Semantic Search</h4>
          <div className="code-block">
            <code>from backend.core.rag_engine import RAGEngine</code><br/>
            <code>rag = RAGEngine()</code><br/>
            <code>results = rag.search("query text", top_k=5)</code>
          </div>
        </div>
      </div>

      <h3>🔗 Integration Points</h3>
      
      <div className="integration-points">
        <div className="integration-item">
          <h4>Desktop (Streamlit) ↔ Backend</h4>
          <ul>
            <li>Streamlit app on port 8501 makes REST calls to <code>http://localhost:8001/api/*</code></li>
            <li>CORS configured in <code>backend/main.py</code> for port 8501</li>
            <li>Sidebar includes link to Mobile PWA for seamless navigation</li>
          </ul>
        </div>

        <div className="integration-item">
          <h4>Mobile PWA (React) ↔ Backend</h4>
          <ul>
            <li>React app on port 5174 makes REST calls to <code>http://localhost:8001/api/*</code></li>
            <li>CORS configured for port 5174</li>
            <li>Accessible from Streamlit sidebar via "📱 Apps" section</li>
            <li>Device Mode Toggle: Built-in responsive design switcher</li>
          </ul>
        </div>

        <div className="integration-item">
          <h4>Safeguarding System</h4>
          <ul>
            <li>Runs on startup in <code>backend/main.py</code> lifespan</li>
            <li>Provides privacy-preserving student analysis</li>
            <li>Integrated with AI agents for risk assessment</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Development