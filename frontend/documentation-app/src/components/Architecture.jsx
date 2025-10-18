import React from 'react'

const Architecture = ({ isDemoMode }) => {
  return (
    <div className="content-section">
      <h2>🏗️ System Architecture</h2>

      <div className={`highlight-box ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🔧 Three-Layer Architecture</h3>
        <pre className="architecture-diagram">
{`┌──────────────────────────────────────────┐
│     User Interfaces                      │
├──────────────────────────────────────────┤
│  Desktop (Streamlit)  │  Mobile PWA (React)
└────────────┬──────────┴──────────────┬───┘
             │ API Calls               │
             └────────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ API Routes │  │ AI Agents  │  │ Safeguard  │
    │ (9 routers)│  │ & LLM      │  │ System     │
    └────┬───────┘  └────┬───────┘  └────┬───────┘
         │                │               │
         └────────────────┼───────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          ┌─────────┐ ┌─────────┐ ┌─────────┐
          │ SQLite  │ │ ChromaDB│ │ Gemini  │
          │ Database│ │ Vectors │ │ API     │
          └─────────┘ └─────────┘ └─────────┘`}
        </pre>
      </div>

      <h3>🛤️ API Router Organization</h3>
      
      <div className="api-routers">
        <div className="router-item">
          <h4>📊 briefing</h4>
          <p>Daily teacher briefings with AI-generated insights</p>
        </div>
        
        <div className="router-item">
          <h4>🔍 search</h4>
          <p>Semantic search across documents using ChromaDB</p>
        </div>
        
        <div className="router-item">
          <h4>👥 students</h4>
          <p>Student data management and CRUD operations</p>
        </div>
        
        <div className="router-item">
          <h4>🤖 agents</h4>
          <p>AI teacher tools: at-risk identifier, behavior manager, learning paths</p>
        </div>
        
        <div className="router-item">
          <h4>💬 chat</h4>
          <p>Conversational interface with context-aware responses</p>
        </div>
        
        <div className="router-item">
          <h4>🔄 workflows</h4>
          <p>Workflow orchestration and automation</p>
        </div>
        
        <div className="router-item">
          <h4>🏫 classroom-tools</h4>
          <p>Classroom-specific features and utilities</p>
        </div>
        
        <div className="router-item">
          <h4>🎯 cca</h4>
          <p>Co-curricular activities management</p>
        </div>
        
        <div className="router-item">
          <h4>👨‍👩‍👧‍👦 guardian</h4>
          <p>Parent communication and engagement tools</p>
        </div>
      </div>

      <div className={`core-components ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>⚙️ Core Components</h3>
        
        <div className="components-grid">
          <div className="component-item">
            <h4>🗄️ database.py</h4>
            <p>SQLite connection, session management, health checks</p>
          </div>
          
          <div className="component-item">
            <h4>⚙️ config.py</h4>
            <p>YAML-based configuration with defaults</p>
          </div>
          
          <div className="component-item">
            <h4>🧠 llm_integration.py</h4>
            <p>LLM provider abstraction (Gemini, Claude, Ollama)</p>
          </div>
          
          <div className="component-item">
            <h4>🔍 rag_engine.py</h4>
            <p>Semantic search using ChromaDB</p>
          </div>
          
          <div className="component-item">
            <h4>📋 briefing_engine.py</h4>
            <p>Daily briefing generation</p>
          </div>
          
          <div className="component-item">
            <h4>🛡️ safeguarding_orchestrator.py</h4>
            <p>Privacy-preserving compliance checks</p>
          </div>
          
          <div className="component-item">
            <h4>🤖 agent_orchestrator.py</h4>
            <p>Multi-agent coordination</p>
          </div>
          
          <div className="component-item">
            <h4>🔄 workflow_engine.py</h4>
            <p>Workflow execution</p>
          </div>
        </div>
      </div>

      <h3>📐 Key Architectural Patterns</h3>
      
      <div className="patterns-section">
        <div className="pattern-item">
          <h4>🔧 Configuration Management</h4>
          <ul>
            <li>YAML-based config in <code>config/config.yaml</code></li>
            <li>Fallback to defaults in <code>backend/core/config.py</code></li>
            <li>Environment variables in <code>.env</code></li>
          </ul>
        </div>

        <div className="pattern-item">
          <h4>🗄️ Database Access</h4>
          <ul>
            <li>SQLAlchemy ORM with SQLite</li>
            <li>Generator-based session management in <code>get_db()</code></li>
            <li>Single connection pool (StaticPool for SQLite)</li>
          </ul>
        </div>

        <div className="pattern-item">
          <h4>🧠 LLM Integration</h4>
          <ul>
            <li>Provider-agnostic abstraction layer</li>
            <li>Supports Gemini (cloud), Claude, and Ollama (local)</li>
            <li>Context window and token management</li>
          </ul>
        </div>

        <div className="pattern-item">
          <h4>🚨 Error Handling</h4>
          <ul>
            <li>FastAPI HTTPException for API errors</li>
            <li>Logging via <code>logging_config.py</code></li>
            <li>Health checks on critical components</li>
          </ul>
        </div>
      </div>

      <div className={`data-flow ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>📁 Data Directories</h3>
        
        <div className="directory-structure">
          <div className="dir-item">
            <strong>data/school.db</strong> - Main SQLite database
          </div>
          <div className="dir-item">
            <strong>data/chroma/</strong> - Vector embeddings for semantic search
          </div>
          <div className="dir-item">
            <strong>data/processed/</strong> - Processed data files
          </div>
          <div className="dir-item">
            <strong>data/backups/</strong> - Automatic database backups
          </div>
        </div>
      </div>

      <h3>🔒 Privacy Architecture</h3>
      
      <div className="privacy-architecture">
        <div className="privacy-layer">
          <h4>🏠 Local-First Design</h4>
          <p>All data processing and storage happens locally, ensuring complete data sovereignty</p>
        </div>
        
        <div className="privacy-layer">
          <h4>🎭 Anonymization Layer</h4>
          <p>Student identifiers are tokenized before any AI processing</p>
        </div>
        
        <div className="privacy-layer">
          <h4>🔐 Encryption Options</h4>
          <p>Optional database encryption for additional security</p>
        </div>
        
        <div className="privacy-layer">
          <h4>📋 GDPR Compliance</h4>
          <p>Built-in data export and deletion capabilities</p>
        </div>
      </div>

      <h3>⚡ Performance Characteristics</h3>
      
      <div className="performance-metrics">
        <div className="metric-item">
          <strong>Database queries:</strong> typically &lt;100ms
        </div>
        <div className="metric-item">
          <strong>AI agent processing:</strong> &lt;2 seconds
        </div>
        <div className="metric-item">
          <strong>Semantic search:</strong> &lt;500ms
        </div>
        <div className="metric-item">
          <strong>Frontend load:</strong> &lt;3 seconds
        </div>
        <div className="metric-item">
          <strong>Vector embeddings:</strong> cached in ChromaDB
        </div>
      </div>
    </div>
  )
}

export default Architecture