import React from 'react'

const Testing = ({ isDemoMode }) => {
  return (
    <div className="content-section">
      <h2>🧪 Testing</h2>

      <div className={`highlight-box ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🚀 Run All Tests</h3>
        <div className="code-block">
          <code>pytest tests/ -v</code>
        </div>
        <p>Executes all unit and integration tests with verbose output.</p>
      </div>

      <h3>🎯 Specific Testing Commands</h3>
      
      <div className="testing-commands">
        <div className="test-command">
          <h4>Run Specific Test File</h4>
          <div className="code-block">
            <code>pytest tests/test_llm_integration.py -v</code>
          </div>
          <p>Execute tests from a single file</p>
        </div>

        <div className="test-command">
          <h4>Run Single Test</h4>
          <div className="code-block">
            <code>pytest tests/test_llm_integration.py::test_function_name -v</code>
          </div>
          <p>Execute a specific test function</p>
        </div>

        <div className="test-command">
          <h4>System Integration Test</h4>
          <div className="code-block">
            <code>python test_system_integration.py</code>
          </div>
          <p>End-to-end system testing across all components</p>
        </div>

        <div className="test-command">
          <h4>Coverage Report</h4>
          <div className="code-block">
            <code>pytest tests/ --cov=backend --cov-report=html</code>
          </div>
          <p>Generate HTML coverage reports for backend code</p>
        </div>
      </div>

      <h3>📊 Test Categories</h3>
      
      <div className="test-categories">
        <div className="test-category">
          <h4>🔌 API Tests</h4>
          <ul>
            <li>Router endpoint validation</li>
            <li>Authentication and authorization</li>
            <li>Request/response schemas</li>
            <li>Error handling</li>
          </ul>
        </div>

        <div className="test-category">
          <h4>🤖 LLM Integration Tests</h4>
          <ul>
            <li>Provider abstraction layer</li>
            <li>Context window management</li>
            <li>Token counting</li>
            <li>Error handling for API failures</li>
          </ul>
        </div>

        <div className="test-category">
          <h4>🗄️ Database Tests</h4>
          <ul>
            <li>Model creation and relationships</li>
            <li>Migration scripts</li>
            <li>Session management</li>
            <li>Connection pooling</li>
          </ul>
        </div>

        <div className="test-category">
          <h4>🔍 Search & RAG Tests</h4>
          <ul>
            <li>Vector embedding generation</li>
            <li>Semantic search accuracy</li>
            <li>ChromaDB operations</li>
            <li>Query performance</li>
          </ul>
        </div>

        <div className="test-category">
          <h4>🛡️ Safeguarding Tests</h4>
          <ul>
            <li>Privacy anonymization</li>
            <li>Student identifier tokenization</li>
            <li>GDPR compliance</li>
            <li>Data retention policies</li>
          </ul>
        </div>
      </div>

      <div className={`testing-best-practices ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>✅ Testing Best Practices</h3>
        
        <div className="practice-item">
          <h4>🎯 Before Deployment</h4>
          <p>Always run the full test suite before deploying changes:</p>
          <div className="code-block">
            <code>pytest tests/ -v --cov=backend</code>
          </div>
        </div>

        <div className="practice-item">
          <h4>🔄 Continuous Testing</h4>
          <p>Run tests frequently during development to catch issues early.</p>
        </div>

        <div className="practice-item">
          <h4>📝 Test Data</h4>
          <p>Use anonymized test data that mirrors real student information structures.</p>
        </div>

        <div className="practice-item">
          <h4>🌐 Environment Isolation</h4>
          <p>Tests run against a separate test database to avoid data contamination.</p>
        </div>
      </div>

      <h3>📈 Performance Benchmarks</h3>
      
      <div className="performance-benchmarks">
        <div className="benchmark-item">
          <strong>Database Queries:</strong> &lt;100ms typical
        </div>
        <div className="benchmark-item">
          <strong>AI Agent Processing:</strong> &lt;2 seconds
        </div>
        <div className="benchmark-item">
          <strong>Semantic Search:</strong> &lt;500ms
        </div>
        <div className="benchmark-item">
          <strong>Frontend Load:</strong> &lt;3 seconds
        </div>
      </div>

      <h3>🔧 Test Configuration</h3>
      
      <p>Tests automatically configure:</p>
      <ul>
        <li>Test database isolation</li>
        <li>Mock LLM providers for offline testing</li>
        <li>Temporary file handling</li>
        <li>Network request mocking</li>
      </ul>
    </div>
  )
}

export default Testing