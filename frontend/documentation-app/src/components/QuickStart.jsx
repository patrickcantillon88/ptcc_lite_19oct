import React from 'react'

const QuickStart = ({ isDemoMode }) => {
  return (
    <div className="content-section">
      <h2>🚀 Quick Start</h2>

      <div className={`highlight-box ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>⚡ Fast Start (Recommended)</h3>
        <div className="code-block">
          <code>./start-ptcc-fast.sh</code>
        </div>
        <p>
          This launches all components sequentially with automatic health checks.
          Skips pip install if dependencies already exist, reducing startup time significantly.
        </p>
      </div>

      <h3>🔄 Complete Start</h3>
      <div className="code-block">
        <code>./start-ptcc.sh</code>
      </div>
      <p>Alternative launcher that installs/updates all dependencies before starting services.</p>

      <h3>🎯 What Gets Started</h3>
      <div className="startup-sequence">
        <div className="startup-step">
          <div className="step-number">1</div>
          <div className="step-content">
            <h4>Backend API</h4>
            <p>Port 8001 - Core business logic and safeguarding</p>
            <div className="step-detail">Automatic health check ensures API is ready</div>
          </div>
        </div>

        <div className="startup-step">
          <div className="step-number">2</div>
          <div className="step-content">
            <h4>Mobile PWA</h4>
            <p>Port 5174 - In-lesson quick-logging interface</p>
            <div className="step-detail">Accessible via Streamlit sidebar link</div>
          </div>
        </div>

        <div className="startup-step">
          <div className="step-number">3</div>
          <div className="step-content">
            <h4>Desktop Dashboard</h4>
            <p>Port 8501 - Main entry point for teachers</p>
            <div className="step-detail">Opens automatically in your browser</div>
          </div>
        </div>
      </div>

      <h3>🔧 Individual Component Startup</h3>
      
      <div className="component-startup">
        <div className="component-section">
          <h4>Backend API Only</h4>
          <div className="code-block">
            <code>cd backend</code><br/>
            <code>pip install -r requirements.txt</code><br/>
            <code>python -m backend.main</code>
          </div>
          <p>Runs on <a href="http://localhost:8001" target="_blank" rel="noopener noreferrer">http://localhost:8001</a></p>
        </div>

        <div className="component-section">
          <h4>Desktop Dashboard Only</h4>
          <div className="code-block">
            <code>cd frontend/desktop-web</code><br/>
            <code>pip install -r requirements.txt</code><br/>
            <code>python run.py</code>
          </div>
          <p>Runs on <a href="http://localhost:8501" target="_blank" rel="noopener noreferrer">http://localhost:8501</a></p>
        </div>

        <div className="component-section">
          <h4>Mobile PWA Only</h4>
          <div className="code-block">
            <code>cd frontend/mobile-pwa</code><br/>
            <code>npm install</code><br/>
            <code>npm run dev</code>
          </div>
          <p>Runs on <a href="http://localhost:5174" target="_blank" rel="noopener noreferrer">http://localhost:5174</a></p>
        </div>
      </div>

      <div className={`environment-setup ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🔐 Environment Setup</h3>
        <ol>
          <li>
            <strong>Copy environment template:</strong>
            <div className="code-block">
              <code>cp .env.template .env</code>
            </div>
          </li>
          <li>
            <strong>Configure required variables:</strong>
            <ul>
              <li><code>GEMINI_API_KEY</code> - Your Google Gemini API key</li>
              <li><code>DEFAULT_LLM_PROVIDER</code> - Set to "gemini" for cloud, "ollama" for local</li>
              <li><code>JWT_SECRET</code> - Change from default in production</li>
            </ul>
          </li>
          <li>
            <strong>Activate virtual environment:</strong>
            <div className="code-block">
              <code>python3 -m venv venv</code><br/>
              <code>source venv/bin/activate  # macOS/Linux</code><br/>
              <code># or: venv\\Scripts\\activate  # Windows</code>
            </div>
          </li>
        </ol>
      </div>

      <h3>✅ Verification</h3>
      <div className="verification-checklist">
        <div className="check-item">
          <strong>API Health:</strong> <a href="http://localhost:8001/health" target="_blank" rel="noopener noreferrer">http://localhost:8001/health</a>
        </div>
        <div className="check-item">
          <strong>API Docs:</strong> <a href="http://localhost:8001/docs" target="_blank" rel="noopener noreferrer">http://localhost:8001/docs</a>
        </div>
        <div className="check-item">
          <strong>Desktop App:</strong> <a href="http://localhost:8501" target="_blank" rel="noopener noreferrer">http://localhost:8501</a>
        </div>
        <div className="check-item">
          <strong>Mobile PWA:</strong> <a href="http://localhost:5174" target="_blank" rel="noopener noreferrer">http://localhost:5174</a>
        </div>
      </div>
    </div>
  )
}

export default QuickStart