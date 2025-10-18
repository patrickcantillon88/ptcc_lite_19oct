import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    classCode: 'All Classes',
    limit: 20,
    behaviorType: 'All Behavior'
  })
  const [classes, setClasses] = useState([])
  const [error, setError] = useState(null)
  const [deviceMode, setDeviceMode] = useState('desktop') // Device layout mode

  // Load available classes and device mode on component mount
  useEffect(() => {
    fetchClasses()
    
    // Load saved device mode preference
    const savedDeviceMode = localStorage.getItem('device-mode-intervention')
    if (savedDeviceMode && ['mobile', 'tablet', 'desktop'].includes(savedDeviceMode)) {
      setDeviceMode(savedDeviceMode)
    }
  }, [])

  const fetchClasses = async () => {
    try {
      const response = await fetch('/api/classroom-tools/classes')
      if (response.ok) {
        const data = await response.json()
        setClasses(['All Classes', ...data.classes])
      }
    } catch (err) {
      console.error('Error fetching classes:', err)
    }
  }

  const fetchInterventionData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        limit: filters.limit,
        behavior_type: filters.behaviorType === 'All Behavior' ? 'all' : 
                       filters.behaviorType === 'Classroom Only' ? 'classroom' : 'cca'
      })
      
      if (filters.classCode !== 'All Classes') {
        params.append('class_code', filters.classCode)
      }

      const response = await fetch(`/api/classroom-tools/intervention-priority?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setStudents(data.students || [])
      } else {
        setError('Failed to load intervention data')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error fetching intervention data:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleDeviceMode = (mode) => {
    setDeviceMode(mode)
    localStorage.setItem('device-mode-intervention', mode)
  }

  const getPriorityLevel = (score) => {
    if (score >= 50) return { label: 'URGENT', color: '#dc3545', emoji: '🔴' }
    if (score >= 30) return { label: 'HIGH', color: '#fd7e14', emoji: '🟠' }
    if (score >= 15) return { label: 'MEDIUM', color: '#ffc107', emoji: '🟡' }
    return { label: 'LOW', color: '#28a745', emoji: '🟢' }
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>🚨 Students Needing Intervention</h1>
            <p>Prioritized list based on behavior patterns, assessment trends, and support needs</p>
          </div>
          <div className="device-mode-toggles">
            <button 
              className={`mode-btn ${deviceMode === 'mobile' ? 'active' : ''}`}
              onClick={() => toggleDeviceMode('mobile')}
              title="Mobile View (375px)"
            >
              📱
            </button>
            <button 
              className={`mode-btn ${deviceMode === 'tablet' ? 'active' : ''}`}
              onClick={() => toggleDeviceMode('tablet')}
              title="Tablet View (1024px)"
            >
              📊
            </button>
            <button 
              className={`mode-btn ${deviceMode === 'desktop' ? 'active' : ''}`}
              onClick={() => toggleDeviceMode('desktop')}
              title="Desktop View (Full Width)"
            >
              💻
            </button>
          </div>
        </div>
      </header>

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="class-filter">Filter by Class</label>
            <select 
              id="class-filter"
              value={filters.classCode} 
              onChange={(e) => setFilters({...filters, classCode: e.target.value})}
            >
              {classes.map(cls => (
                <option key={cls} value={cls}>{cls}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="limit-filter">Max Results</label>
            <input
              id="limit-filter"
              type="number"
              min="5"
              max="50"
              value={filters.limit}
              onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
            />
          </div>

          <div className="filter-group">
            <label htmlFor="behavior-filter">Behavior Type</label>
            <select 
              id="behavior-filter"
              value={filters.behaviorType} 
              onChange={(e) => setFilters({...filters, behaviorType: e.target.value})}
            >
              <option value="All Behavior">All Behavior</option>
              <option value="Classroom Only">Classroom Only</option>
              <option value="CCA Only">CCA Only</option>
            </select>
          </div>

          <div className="filter-group">
            <button 
              className="refresh-btn"
              onClick={fetchInterventionData}
              disabled={loading}
            >
              {loading ? '🔄 Loading...' : '🔄 Analyze Students'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      <div className="results-section">
        {students.length > 0 && (
          <div className="results-header">
            <h2>📊 Analysis Results</h2>
            <p><strong>Students Flagged:</strong> {students.length}</p>
          </div>
        )}

        <div className="students-grid">
          {students.map((student, index) => {
            const priority = getPriorityLevel(student.priority_score)
            
            return (
              <div 
                key={student.student_id} 
                className={`student-card priority-${priority.label.toLowerCase()}`}
                style={{ borderLeftColor: priority.color }}
              >
                <div className="student-header">
                  <div className="student-info">
                    <h3>{priority.emoji} #{index + 1} - {student.student_name}</h3>
                    <span className="class-code">({student.class_code})</span>
                    <span 
                      className="priority-badge"
                      style={{ backgroundColor: priority.color }}
                    >
                      {priority.label} Priority
                    </span>
                  </div>
                </div>

                <div className="student-metrics">
                  <div className="metric">
                    <label>Priority Score</label>
                    <span className="metric-value">{student.priority_score.toFixed(1)}</span>
                  </div>
                  <div className="metric">
                    <label>Recent Incidents</label>
                    <span className="metric-value">{student.recent_incidents}</span>
                  </div>
                  <div className="metric">
                    <label>Days Since Positive</label>
                    <span className="metric-value">
                      {student.days_since_positive !== null ? student.days_since_positive : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="risk-factors">
                  <h4>🎯 Risk Factors</h4>
                  <ul>
                    {student.risk_factors.map((factor, idx) => (
                      <li key={idx}>{factor}</li>
                    ))}
                  </ul>
                </div>

                <div className="recommended-actions">
                  <h4>💡 Recommended Actions</h4>
                  <ul>
                    {student.recommended_actions.map((action, idx) => (
                      <li 
                        key={idx}
                        className={action.includes('URGENT') ? 'urgent-action' : ''}
                      >
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="action-buttons">
                  <button className="action-btn primary">View Student Details</button>
                  <button className="action-btn secondary">Log Intervention</button>
                  <button className="action-btn secondary">Contact Parent</button>
                </div>
              </div>
            )
          })}
        </div>

        {!loading && students.length === 0 && !error && (
          <div className="no-results">
            <h3>✅ No students currently flagged for intervention!</h3>
            <p>Click "Analyze Students" to check for students needing support.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
