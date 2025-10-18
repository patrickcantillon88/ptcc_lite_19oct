import React from 'react'

const ProjectOverview = ({ isDemoMode }) => {
  return (
    <div className="content-section">
      <h2>🏫 Project Overview</h2>
      
      <div className={`highlight-box ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>What is PTCC?</h3>
        <p>
          <strong>PTCC (Personal Teaching Command Center)</strong> is a local-first, AI-powered information 
          management system designed for specialist teachers managing 400+ students across multiple campuses.
        </p>
      </div>

      <h3>🏗️ System Architecture</h3>
      <div className="architecture-overview">
        <div className="component-card">
          <h4>🖥️ Desktop Dashboard (Streamlit)</h4>
          <p>Teacher-facing interface for comprehensive student management</p>
          <ul>
            <li>Port: 8501</li>
            <li>Main entry point for teachers</li>
            <li>Sidebar navigation with links to all features</li>
          </ul>
        </div>

        <div className="component-card">
          <h4>📱 Mobile PWA (React/Vite)</h4>
          <p>In-lesson quick-logging interface</p>
          <ul>
            <li>Port: 5174</li>
            <li>Two main views: Logger & AI Agents</li>
            <li>Responsive design with device mode toggle</li>
          </ul>
        </div>

        <div className="component-card">
          <h4>⚡ Backend API (FastAPI)</h4>
          <p>Core business logic and safeguarding</p>
          <ul>
            <li>Port: 8001</li>
            <li>9 specialized routers</li>
            <li>Privacy-preserving AI integration</li>
          </ul>
        </div>
      </div>

      <div className={`privacy-section ${isDemoMode ? 'demo-highlight' : ''}`}>
        <h3>🔒 Privacy & Security</h3>
        <div className="privacy-features">
          <div className="privacy-item">
            <strong>Local-First:</strong> All data stored locally in SQLite
          </div>
          <div className="privacy-item">
            <strong>No Cloud Storage:</strong> No external cloud storage of sensitive data
          </div>
          <div className="privacy-item">
            <strong>Safeguarding:</strong> Anonymizes/tokenizes student identifiers
          </div>
          <div className="privacy-item">
            <strong>GDPR Compliant:</strong> Data export and deletion capabilities
          </div>
        </div>
      </div>

      <h3>🎯 Key Features</h3>
      <div className="features-grid">
        <div className="feature-item">
          <h4>🤖 AI Teacher Tools</h4>
          <p>At-risk identifier, behavior manager, learning path generator</p>
        </div>
        <div className="feature-item">
          <h4>📊 Daily Briefings</h4>
          <p>AI-generated daily teacher briefings with key insights</p>
        </div>
        <div className="feature-item">
          <h4>🔍 Semantic Search</h4>
          <p>ChromaDB-powered search across all documents and data</p>
        </div>
        <div className="feature-item">
          <h4>🏃‍♂️ Workflow Engine</h4>
          <p>Automated workflow orchestration for common tasks</p>
        </div>
        <div className="feature-item">
          <h4>👥 Student Management</h4>
          <p>Comprehensive student data management across campuses</p>
        </div>
        <div className="feature-item">
          <h4>💬 Parent Communication</h4>
          <p>Guardian communication tools with safeguarding compliance</p>
        </div>
      </div>
    </div>
  )
}

export default ProjectOverview