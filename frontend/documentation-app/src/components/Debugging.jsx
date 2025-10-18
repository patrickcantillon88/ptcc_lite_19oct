import React from 'react'

const Debugging = ({ isDemoMode }) => {
  return (
    <div className="content-section">
      <h2>🔧 Debugging & Performance</h2>

      <div className={`highlight-box ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🔍 Backend Debugging</h3>
        <div className="debug-section">
          <h4>Log Files</h4>
          <div className="code-block">
            <code>tail -f .ptcc_logs/backend.log</code>
          </div>
          <p>Monitor real-time backend activity and errors</p>
        </div>

        <div className="debug-section">
          <h4>Enable Debug Mode</h4>
          <div className="code-block">
            <code>DEBUG=true</code>
          </div>
          <p>Set in .env file for verbose logging and error details</p>
        </div>

        <div className="debug-section">
          <h4>API Documentation</h4>
          <p><a href="http://localhost:8001/docs" target="_blank" rel="noopener noreferrer">http://localhost:8001/docs</a> - Interactive Swagger UI</p>
        </div>

        <div className="debug-section">
          <h4>Health Endpoint</h4>
          <p><a href="http://localhost:8001/health" target="_blank" rel="noopener noreferrer">http://localhost:8001/health</a> - System status and diagnostics</p>
        </div>
      </div>

      <h3>🖥️ Frontend Debugging</h3>
      
      <div className="frontend-debug">
        <div className="debug-item">
          <h4>Desktop Dashboard Logs</h4>
          <div className="code-block">
            <code>tail -f .ptcc_logs/dashboard.log</code>
          </div>
          <p>Streamlit application logs and errors</p>
        </div>

        <div className="debug-item">
          <h4>PWA Logs</h4>
          <div className="code-block">
            <code>tail -f .ptcc_logs/pwa.log</code>
          </div>
          <p>React/Vite mobile PWA logs</p>
        </div>

        <div className="debug-item">
          <h4>Browser Dev Tools</h4>
          <p>Press F12 in desktop/mobile apps for client-side debugging</p>
        </div>
      </div>

      <div className={`css-debugging ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🎨 CSS Responsive Design Issues</h3>
        
        <div className="debug-problem">
          <h4>🚨 Common Problem</h4>
          <p>Dynamic CSS class switching works in JavaScript but container dimensions don't change visually.</p>
        </div>

        <div className="debug-cause">
          <h4>🔍 Root Cause</h4>
          <p>CSS specificity conflicts when multiple stylesheets contain competing rules.</p>
        </div>

        <div className="debug-symptoms">
          <h4>📋 Symptoms</h4>
          <ul>
            <li>State changes correctly (buttons show active states)</li>
            <li>CSS classes apply to DOM elements</li>
            <li>Container width/layout remains unchanged</li>
          </ul>
        </div>

        <div className="debug-steps">
          <h4>🔬 Diagnostic Steps</h4>
          <div className="diagnostic-step">
            <strong>1. Check for conflicting CSS rules:</strong>
            <div className="code-block">
              <code>grep -r "max-width\|width:" frontend/ --include="*.css" --include="*.scss"</code>
            </div>
          </div>
          
          <div className="diagnostic-step">
            <strong>2. Browser DevTools inspection:</strong>
            <ul>
              <li>Inspect element and check Computed styles</li>
              <li>Look for crossed-out CSS rules (overridden)</li>
              <li>Verify CSS classes are being applied</li>
            </ul>
          </div>
        </div>

        <div className="debug-solutions">
          <h4>✅ Solutions</h4>
          
          <div className="solution-item">
            <h5>3. CSS Specificity Override</h5>
            <p>Use <code>!important</code> to force styles:</p>
            <div className="code-block">
              <code>
                {`/* Example: Device mode classes */
.container.mobile { width: 375px !important; max-width: 375px !important; }
.container.tablet { width: 1024px !important; max-width: 1024px !important; }
.container.desktop { width: 100vw !important; max-width: 100vw !important; }`}
              </code>
            </div>
          </div>

          <div className="solution-item">
            <h5>4. Visual Debugging</h5>
            <p>Add colored borders during development:</p>
            <div className="code-block">
              <code>
                {`.container.mobile { border: 5px solid #ff0000 !important; }
.container.tablet { border: 5px solid #00ff00 !important; }
.container.desktop { border: 5px solid #0000ff !important; }`}
              </code>
            </div>
          </div>

          <div className="solution-item">
            <h5>5. Browser Cache</h5>
            <p>Hard refresh to ensure latest CSS loads:</p>
            <ul>
              <li>Chrome/Safari: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows)</li>
              <li>Or disable cache in DevTools Network tab</li>
            </ul>
          </div>
        </div>

        <div className="debug-prevention">
          <h4>🛡️ Prevention</h4>
          <ul>
            <li>Use CSS-in-JS libraries (styled-components, emotion) for scoped styles</li>
            <li>Implement CSS naming conventions (BEM, CSS Modules)</li>
            <li>Keep responsive breakpoints in a single stylesheet</li>
          </ul>
        </div>
      </div>

      <h3>🗄️ Database Debugging</h3>
      
      <div className="database-debug">
        <div className="db-debug-item">
          <h4>List Tables</h4>
          <div className="code-block">
            <code>sqlite3 data/school.db ".tables"</code>
          </div>
        </div>

        <div className="db-debug-item">
          <h4>Query Counts</h4>
          <div className="code-block">
            <code>sqlite3 data/school.db "SELECT COUNT(*) FROM students;"</code>
          </div>
        </div>

        <div className="db-debug-item">
          <h4>Schema Information</h4>
          <div className="code-block">
            <code>sqlite3 data/school.db ".schema students"</code>
          </div>
        </div>

        <div className="db-debug-item">
          <h4>Recent Records</h4>
          <div className="code-block">
            <code>sqlite3 data/school.db "SELECT * FROM students ORDER BY created_at DESC LIMIT 5;"</code>
          </div>
        </div>
      </div>

      <div className={`performance-monitoring ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>📊 Performance Monitoring</h3>
        
        <div className="perf-metrics">
          <div className="metric-section">
            <h4>Expected Performance</h4>
            <div className="perf-item">
              <strong>Database queries:</strong> typically &lt;100ms
            </div>
            <div className="perf-item">
              <strong>AI agent processing:</strong> &lt;2 seconds
            </div>
            <div className="perf-item">
              <strong>Semantic search:</strong> &lt;500ms
            </div>
            <div className="perf-item">
              <strong>Frontend load:</strong> &lt;3 seconds
            </div>
          </div>

          <div className="metric-section">
            <h4>Performance Optimization</h4>
            <ul>
              <li>Vector embeddings cached in ChromaDB</li>
              <li>Database connection pooling</li>
              <li>LLM response caching</li>
              <li>Frontend code splitting</li>
            </ul>
          </div>
        </div>
      </div>

      <h3>🚨 Common Issues & Solutions</h3>
      
      <div className="common-issues">
        <div className="issue-item">
          <h4>🔌 API Connection Issues</h4>
          <ul>
            <li>Check if backend is running on port 8001</li>
            <li>Verify CORS configuration</li>
            <li>Test with <code>curl http://localhost:8001/health</code></li>
          </ul>
        </div>

        <div className="issue-item">
          <h4>🤖 LLM Provider Errors</h4>
          <ul>
            <li>Check API key configuration in .env</li>
            <li>Verify provider availability (Gemini, Claude, Ollama)</li>
            <li>Review token limits and context windows</li>
          </ul>
        </div>

        <div className="issue-item">
          <h4>🗄️ Database Lock Issues</h4>
          <ul>
            <li>Ensure only one process accesses SQLite</li>
            <li>Check for hanging database connections</li>
            <li>Restart backend if database is locked</li>
          </ul>
        </div>

        <div className="issue-item">
          <h4>📱 Frontend Loading Issues</h4>
          <ul>
            <li>Clear browser cache</li>
            <li>Check console for JavaScript errors</li>
            <li>Verify API endpoints are reachable</li>
          </ul>
        </div>
      </div>

      <h3>📝 Debug Logging Configuration</h3>
      
      <p>All components use structured logging with configurable levels:</p>
      <ul>
        <li><strong>INFO:</strong> Normal operations</li>
        <li><strong>DEBUG:</strong> Detailed execution flow</li>
        <li><strong>WARNING:</strong> Potential issues</li>
        <li><strong>ERROR:</strong> Errors with stack traces</li>
      </ul>
    </div>
  )
}

export default Debugging