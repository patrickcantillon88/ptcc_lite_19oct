import { useState, useEffect } from 'react'
import { useDeviceMode } from '../shared/DeviceToggle.jsx'
import '../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('assessment-analytics-overview')
  const [overviewData, setOverviewData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOverviewData()
  }, [])

  const fetchOverviewData = async () => {
    try {
      const response = await fetch('/api/quiz-analytics/analytics/overview?days=90')
      if (response.ok) {
        const data = await response.json()
        setOverviewData(data)
      }
    } catch (error) {
      console.error('Error fetching overview data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>📊 Assessment Analytics</h1>
            <p>Professional quiz analytics suite with dedicated apps for each analysis type</p>
          </div>
          <DeviceToggleComponent />
        </div>
      </header>

      {/* Quick Overview */}
      <section className="overview-section">
        <h2>🎯 Quick Overview</h2>
        <div className="overview-grid">
          <div className="overview-card">
            <div className="card-header">
              <h3>📤 Upload Quiz</h3>
            </div>
            <ul className="feature-list">
              <li>Drag & drop CSV files</li>
              <li>Auto student matching</li>
              <li>Real-time validation</li>
            </ul>
            <a href="http://localhost:5183" className="card-link" target="_blank" rel="noopener noreferrer">
              Open Upload App →
            </a>
          </div>

          <div className="overview-card">
            <div className="card-header">
              <h3>📈 Performance Trends</h3>
            </div>
            <ul className="feature-list">
              <li>Time-series analytics</li>
              <li>Visual trend charts</li>
              <li>Progress tracking</li>
            </ul>
            <a href="http://localhost:5184" className="card-link" target="_blank" rel="noopener noreferrer">
              Open Trends App →
            </a>
          </div>

          <div className="overview-card">
            <div className="card-header">
              <h3>🎯 Progress Levels</h3>
            </div>
            <ul className="feature-list">
              <li>Grade-level analysis</li>
              <li>Distribution charts</li>
              <li>Student groupings</li>
            </ul>
            <a href="http://localhost:5185" className="card-link" target="_blank" rel="noopener noreferrer">
              Open Progress App →
            </a>
          </div>

          <div className="overview-card">
            <div className="card-header">
              <h3>⚠️ At-Risk Students</h3>
            </div>
            <ul className="feature-list">
              <li>Early intervention</li>
              <li>Risk identification</li>
              <li>Action recommendations</li>
            </ul>
            <a href="http://localhost:5186" className="card-link" target="_blank" rel="noopener noreferrer">
              Open Risk App →
            </a>
          </div>
        </div>
      </section>

      {/* Assessment Analytics Workflow */}
      <section className="workflow-section">
        <h2>🚀 Assessment Analytics Workflow</h2>
        <div className="workflow-grid">
          <div className="workflow-step step-1">
            <div className="step-header">
              <span className="step-number">1</span>
              <h3>Upload Data</h3>
              <span className="step-icon">📤</span>
            </div>
            <p>Start by uploading your quiz CSV files. The system will automatically:</p>
            <ul>
              <li>Parse different CSV formats</li>
              <li>Match students to your roster</li>
              <li>Validate score data</li>
              <li>Store results securely</li>
            </ul>
          </div>

          <div className="workflow-step step-2">
            <div className="step-header">
              <span className="step-number">2</span>
              <h3>Analyze Trends</h3>
              <span className="step-icon">📈</span>
            </div>
            <p>Track performance patterns:</p>
            <ul>
              <li>Individual student trends</li>
              <li>Class-wide improvements</li>
              <li>Subject comparisons</li>
              <li>Time-based analysis</li>
            </ul>
          </div>

          <div className="workflow-step step-3">
            <div className="step-header">
              <span className="step-number">3</span>
              <h3>Check Progress</h3>
              <span className="step-icon">🎯</span>
            </div>
            <p>Understand achievement levels:</p>
            <ul>
              <li>Grade-level expectations</li>
              <li>Progress distribution</li>
              <li>Achievement categories</li>
              <li>Group planning</li>
            </ul>
          </div>

          <div className="workflow-step step-4">
            <div className="step-header">
              <span className="step-number">4</span>
              <h3>Support Students</h3>
              <span className="step-icon">⚠️</span>
            </div>
            <p>Identify intervention needs:</p>
            <ul>
              <li>Performance declines</li>
              <li>Low achievement alerts</li>
              <li>Action recommendations</li>
              <li>Tracking improvements</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Current Statistics */}
      <section className="stats-section">
        <h2>📊 Current Statistics</h2>
        {loading ? (
          <div className="loading">Loading statistics...</div>
        ) : overviewData ? (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{overviewData.total_quizzes || 0}</div>
              <div className="stat-label">Total Quizzes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overviewData.total_attempts || 0}</div>
              <div className="stat-label">Quiz Attempts</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overviewData.average_score || 0}%</div>
              <div className="stat-label">Average Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{overviewData.highest_score || 0}%</div>
              <div className="stat-label">Highest Score</div>
            </div>
          </div>
        ) : (
          <div className="no-data">Upload some quiz data to see statistics here!</div>
        )}
      </section>

      {/* Notes */}
      <section className="notes-section">
        <h2>📝 Notes</h2>
        <ul className="notes-list">
          <li>Each app runs independently with device mode toggles for responsive testing</li>
          <li>Data is shared between all Assessment Analytics apps</li>
          <li>Apps include cross-navigation for seamless workflow</li>
          <li>All student data remains local and secure</li>
        </ul>
      </section>
    </div>
  )
}

export default App
