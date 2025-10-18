import React, { useState } from 'react'
import './App.css'
import TableOfContents from './components/TableOfContents'
import ProjectOverview from './components/ProjectOverview'
import QuickStart from './components/QuickStart'
import Testing from './components/Testing'
import Development from './components/Development'
import Architecture from './components/Architecture'
import Debugging from './components/Debugging'
import RagWorkflow from './components/RagWorkflow'
import SearchBar from './components/SearchBar'

const sections = [
  { id: 'overview', title: 'Project Overview', component: ProjectOverview },
  { id: 'quickstart', title: 'Quick Start', component: QuickStart },
  { id: 'ragworkflow', title: 'RAG Workflow', component: RagWorkflow },
  { id: 'testing', title: 'Testing', component: Testing },
  { id: 'development', title: 'Development', component: Development },
  { id: 'architecture', title: 'Architecture', component: Architecture },
  { id: 'debugging', title: 'Debugging & Performance', component: Debugging }
]

function App() {
  const [activeSection, setActiveSection] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [isDemoMode, setIsDemoMode] = useState(false)

  const ActiveComponent = sections.find(s => s.id === activeSection)?.component || ProjectOverview

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>🏫 PTCC System Documentation</h1>
            <p className="subtitle">Personal Teaching Command Center - Local-first AI for Education</p>
          </div>
          <div className="header-controls">
            <button 
              className={`demo-toggle ${isDemoMode ? 'active' : ''}`}
              onClick={() => setIsDemoMode(!isDemoMode)}
              title="Highlight demo features"
            >
              🎭 Demo Mode
            </button>
            <SearchBar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
          </div>
        </div>
      </header>

      <div className="app-body">
        <nav className="sidebar">
          <TableOfContents 
            sections={sections} 
            activeSection={activeSection}
            setActiveSection={setActiveSection}
          />
          
          <div className="quick-links">
            <h4>🔗 Quick Access</h4>
            <a href="http://localhost:8501" target="_blank" rel="noopener noreferrer" className="external-link">
              🖥️ Desktop Dashboard
            </a>
            <a href="http://localhost:5173" target="_blank" rel="noopener noreferrer" className="external-link">
              📱 Mobile PWA
            </a>
            <a href="http://localhost:8001/docs" target="_blank" rel="noopener noreferrer" className="external-link">
              📋 API Documentation
            </a>
            <a href="http://localhost:8001/health" target="_blank" rel="noopener noreferrer" className="external-link">
              💚 System Health
            </a>
          </div>
        </nav>

        <main className="content">
          <ActiveComponent 
            searchTerm={searchTerm} 
            isDemoMode={isDemoMode}
          />
        </main>
      </div>
    </div>
  )
}

export default App