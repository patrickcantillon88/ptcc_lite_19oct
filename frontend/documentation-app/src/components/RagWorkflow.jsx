import React, { useState } from 'react'

const RagWorkflow = ({ isDemoMode, searchTerm }) => {
  const [selectedQuery, setSelectedQuery] = useState('')
  const [showDemo, setShowDemo] = useState(false)

  const demoQueries = {
    "Show me Sophie Chen's profile": {
      retrieved: "Student Database → Sophie Chen (4B), Assessment Records → 78% Computing, Behavioral Logs → Excellent progress",
      response: "**Sophie Chen (4B)** - Support Level 2\n• Computing: 78% (Excellent progress in Scratch)\n• Recent: Improved engagement with pair programming\n• Works well with visual learning aids"
    },
    "What's today's assembly time?": {
      retrieved: "School Calendar → Assembly 8:30-8:45 AM, Weekly Schedule → Guest speaker Dr. Sarah Chen",
      response: "**Morning Assembly:** 8:30 AM - 8:45 AM (Main Hall)\n**Today's Guest:** Dr. Sarah Chen on 'Digital Citizenship'\n**Note:** All Year groups attend morning assembly"
    },
    "Students with recent incidents": {
      retrieved: "Behavioral Logs → Marcus Thompson (3A), David Kim (6A), Incident Reports → Last 7 days",
      response: "**Recent Incidents (Last 7 Days):**\n• Marcus Thompson (3A) - Off-task behavior, resolved with calm corner\n• David Kim (6A) - Assembly disruption, follow-up successful\n• Most issues resolved with early intervention"
    }
  }

  const handleRunDemo = () => {
    if (selectedQuery) {
      setShowDemo(true)
    }
  }

  // Filter content based on search term
  const content = `rag workflow retrieval augmented generation vector embeddings chromadb similarity search ai llm semantic search documents indexing query processing`.toLowerCase()
  const isVisible = !searchTerm || content.includes(searchTerm.toLowerCase()) || 
                   "RAG Workflow".toLowerCase().includes(searchTerm.toLowerCase())

  if (!isVisible) return null

  return (
    <div className="content-section">
      <div className={`ascii-header ${isDemoMode ? 'demo-highlight' : ''}`}>
        <pre className="ascii-title">
{`╔════════════════════════════════════════════════════════════════════════════╗
║                         RAG WORKFLOW PROCESS                                ║
╚════════════════════════════════════════════════════════════════════════════╝`}
        </pre>
      </div>

      <div className="visual-diagram">
        <h3>📊 Visual RAG Workflow</h3>
        <div className="diagram-container">
          <img 
            src="/rag-diagram.png" 
            alt="RAG Workflow Diagram showing the complete process from documents to response"
            className="rag-diagram-image"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextElementSibling.style.display = 'block';
            }}
          />
          <div className="diagram-fallback" style={{display: 'none'}}>
            <p>📋 <strong>RAG Diagram:</strong> Save your RAG workflow diagram as <code>rag-diagram.png</code> in the <code>public/</code> directory to display it here.</p>
          </div>
        </div>
      </div>

      <div className="ascii-diagram">
        <h3>🔧 ASCII Technical Flow</h3>
        <pre className="workflow-ascii">
{`
 ┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
 │   1. Encode         │      │   2. Index          │      │   3. Encode         │
 │   Documents         │─────▶│   & Store           │      │   Query             │
 │                     │      │                     │      │                     │
 │  Text → Embedding   │      │  Vectors → Database │      │  Query → Embedding  │
 └─────────────────────┘      └─────────────────────┘      └─────────────────────┘
                                       │                             │
                                       │                             │
                                       └──────────┬──────────────────┘
                                                  │
                                                  ▼
 ┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
 │   6. Generate       │      │   5. Augment        │      │   4. Similarity     │
 │   Response          │◀─────│   Prompt            │◀─────│   Search            │
 │                     │      │                     │      │                     │
 │  LLM → Output       │      │  Query + Context    │      │  Database → Docs    │
 └─────────────────────┘      └─────────────────────┘      └─────────────────────┘
`}
        </pre>
      </div>

      <div className="components-section">
        <pre className="ascii-components">
{`╔════════════════════════════════════════════════════════════════════════════╗
║  COMPONENTS:                                                                ║
║  • Embedding Model: Converts text to vector representations                ║
║  • Vector Database: Stores and indexes document vectors                    ║
║  • Similarity Search: Finds most relevant documents                        ║
║  • LLM: Generates final response from augmented prompt                     ║
╚════════════════════════════════════════════════════════════════════════════╝`}
        </pre>
      </div>

      <div className="detailed-flow">
        <pre className="ascii-flow">
{`┌─────────────────────────────────────────────────────────────────────────────┐
│ DETAILED FLOW:                                                               │
│                                                                              │
│ Setup Phase (Steps 1-2):                                                    │
│   • Documents are converted to vectors via embedding model                  │
│   • Vectors are indexed and stored in vector database                       │
│                                                                              │
│ Query Phase (Steps 3-6):                                                    │
│   • User query is converted to vector via same embedding model              │
│   • Vector database searches for most similar document vectors              │
│   • Retrieved documents are combined with original query                    │
│   • LLM generates response using augmented prompt                           │
└─────────────────────────────────────────────────────────────────────────────┘`}
        </pre>
      </div>

      <div className={`demo-section ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🎮 Try It Live: Sample RAG Query</h3>
        
        <div className="demo-controls">
          <label htmlFor="query-select">Choose a sample query:</label>
          <select 
            id="query-select"
            value={selectedQuery} 
            onChange={(e) => setSelectedQuery(e.target.value)}
            className="query-selector"
          >
            <option value="">Select a query...</option>
            {Object.keys(demoQueries).map(query => (
              <option key={query} value={query}>{query}</option>
            ))}
          </select>
          
          <button 
            onClick={handleRunDemo}
            disabled={!selectedQuery}
            className="demo-button"
          >
            🔍 Run RAG Demo
          </button>
        </div>

        {showDemo && selectedQuery && (
          <div className="demo-results">
            <h4>🔍 Step-by-Step RAG Process</h4>
            <div className="demo-step">
              <strong>📝 Original Query:</strong> <code>{selectedQuery}</code>
            </div>
            <div className="demo-step">
              <strong>🎯 Documents Retrieved:</strong> {demoQueries[selectedQuery].retrieved}
            </div>
            <div className="demo-step">
              <strong>🤖 AI Response Generated:</strong>
              <div className="demo-response">
                {demoQueries[selectedQuery].response.split('\n').map((line, index) => (
                  <div key={index}>{line}</div>
                ))}
              </div>
            </div>
            
            <div className="demo-explanation">
              <h5>💡 What Just Happened:</h5>
              <ol>
                <li>Your query was converted to a vector</li>
                <li>Similar documents were found in our database</li>
                <li>Context was sent to the AI (without student names externally)</li>
                <li>AI generated a helpful, contextual response</li>
              </ol>
            </div>
          </div>
        )}
      </div>

      <div className="technical-details">
        <h3>🔧 Technical Implementation</h3>
        <div className="tech-grid">
          <div className="tech-item">
            <h4>Vector Database</h4>
            <p>ChromaDB for fast similarity search</p>
          </div>
          <div className="tech-item">
            <h4>Embedding Model</h4>
            <p>Converts text to numerical vectors</p>
          </div>
          <div className="tech-item">
            <h4>LLM Integration</h4>
            <p>Gemini, Claude, or local Ollama</p>
          </div>
          <div className="tech-item">
            <h4>Privacy First</h4>
            <p>All processing happens locally</p>
          </div>
        </div>
      </div>

      <div className="benefits-section">
        <h3>✨ Benefits of RAG</h3>
        <div className="benefits-grid">
          <div className="benefit-item">
            <strong>🎯 Contextual Responses:</strong> AI has access to your specific school data
          </div>
          <div className="benefit-item">
            <strong>⚡ Fast Retrieval:</strong> Sub-second search across all documents
          </div>
          <div className="benefit-item">
            <strong>🔒 Privacy Preserved:</strong> No external access to student data
          </div>
          <div className="benefit-item">
            <strong>📚 Always Current:</strong> Uses your latest uploaded documents
          </div>
        </div>
      </div>
    </div>
  )
}

export default RagWorkflow