import { useState } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('progress-levels')
  const [progressData, setProgressData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    subject: '',
    class_code: ''
  })
  const [error, setError] = useState(null)

  const fetchProgressLevels = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams()
      if (filters.subject) params.append('subject', filters.subject)
      if (filters.class_code) params.append('class_code', filters.class_code)

      const response = await fetch(`/api/quiz-analytics/analytics/progress-levels?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setProgressData(data)
      } else {
        setError('Failed to load progress levels')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error fetching progress levels:', err)
    } finally {
      setLoading(false)
    }
  }

  const getLevelColor = (level) => {
    const colors = {
      exceeding: '#28a745',
      meeting: '#ffc107',
      working_towards: '#dc3545'
    }
    return colors[level] || '#6c757d'
  }

  const getLevelIcon = (level) => {
    const icons = {
      exceeding: '🏆',
      meeting: '🎯',
      working_towards: '💪'
    }
    return icons[level] || '❓'
  }

  const getLevelDescription = (level) => {
    const descriptions = {
      exceeding: 'Students performing above grade level expectations (85%+ average)',
      meeting: 'Students meeting grade level expectations (70-84% average)', 
      working_towards: 'Students working towards grade level expectations (<70% average)'
    }
    return descriptions[level] || ''
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>🎯 Progress Levels</h1>
            <p>Analyze student progress distribution across grade-level expectations</p>
          </div>
          <DeviceToggleComponent />
        </div>
      </header>

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="subject-filter">Subject (optional)</label>
            <input
              id="subject-filter"
              type="text"
              placeholder="e.g., Mathematics"
              value={filters.subject}
              onChange={(e) => setFilters({...filters, subject: e.target.value})}
            />
          </div>
          
          <div className="filter-group">
            <label htmlFor="class-filter">Class Code (optional)</label>
            <input
              id="class-filter"
              type="text"
              placeholder="e.g., 7A"
              value={filters.class_code}
              onChange={(e) => setFilters({...filters, class_code: e.target.value})}
            />
          </div>
          
          <div className="filter-group">
            <button 
              className="analyze-btn"
              onClick={fetchProgressLevels}
              disabled={loading}
            >
              {loading ? '🔄 Loading...' : '📊 Analyze Progress Levels'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {progressData && (
        <div className="results-section">
          <div className="results-header">
            <h2>📊 Progress Level Distribution</h2>
            <p><strong>Total Students:</strong> {progressData.total_students}</p>
          </div>
          
          {progressData.total_students === 0 ? (
            <div className="no-data-banner">
              <div className="no-data-icon">📊</div>
              <div className="no-data-content">
                <h3>No Student Data Available</h3>
                <p>Upload some quiz results first to see student progress levels and analytics.</p>
                <button 
                  className="upload-data-btn"
                  onClick={() => window.open('http://localhost:5183', '_blank')}
                >
                  📤 Upload Quiz Data
                </button>
              </div>
            </div>
          ) : (

          {/* Summary Cards */}
          <div className="summary-grid">
            <div className="summary-card exceeding" style={{borderLeftColor: getLevelColor('exceeding')}}>
              <div className="card-header">
                <div className="card-icon">{getLevelIcon('exceeding')}</div>
                <div className="card-title">Exceeding Expectations</div>
              </div>
              <div className="card-stats">
                <div className="stat-large">{progressData.exceeding.count}</div>
                <div className="stat-percentage">{progressData.exceeding.percentage}%</div>
              </div>
              <div className="card-description">
                {getLevelDescription('exceeding')}
              </div>
            </div>

            <div className="summary-card meeting" style={{borderLeftColor: getLevelColor('meeting')}}>
              <div className="card-header">
                <div className="card-icon">{getLevelIcon('meeting')}</div>
                <div className="card-title">Meeting Expectations</div>
              </div>
              <div className="card-stats">
                <div className="stat-large">{progressData.meeting.count}</div>
                <div className="stat-percentage">{progressData.meeting.percentage}%</div>
              </div>
              <div className="card-description">
                {getLevelDescription('meeting')}
              </div>
            </div>

            <div className="summary-card working-towards" style={{borderLeftColor: getLevelColor('working_towards')}}>
              <div className="card-header">
                <div className="card-icon">{getLevelIcon('working_towards')}</div>
                <div className="card-title">Working Towards</div>
              </div>
              <div className="card-stats">
                <div className="stat-large">{progressData.working_towards.count}</div>
                <div className="stat-percentage">{progressData.working_towards.percentage}%</div>
              </div>
              <div className="card-description">
                {getLevelDescription('working_towards')}
              </div>
            </div>
          </div>

          {/* Student Lists */}
          <div className="student-lists">
            <div className="student-list-section">
              <h3 style={{color: getLevelColor('exceeding')}}>
                {getLevelIcon('exceeding')} Exceeding Expectations ({progressData.exceeding.count} students)
              </h3>
              <div className="student-grid">
                {progressData.exceeding.students.map((student, index) => (
                  <div key={index} className="student-chip exceeding">
                    {student}
                  </div>
                ))}
              </div>
            </div>

            <div className="student-list-section">
              <h3 style={{color: getLevelColor('meeting')}}>
                {getLevelIcon('meeting')} Meeting Expectations ({progressData.meeting.count} students)
              </h3>
              <div className="student-grid">
                {progressData.meeting.students.map((student, index) => (
                  <div key={index} className="student-chip meeting">
                    {student}
                  </div>
                ))}
              </div>
            </div>

            <div className="student-list-section">
              <h3 style={{color: getLevelColor('working_towards')}}>
                {getLevelIcon('working_towards')} Working Towards Expectations ({progressData.working_towards.count} students)
              </h3>
              <div className="student-grid">
                {progressData.working_towards.students.map((student, index) => (
                  <div key={index} className="student-chip working-towards">
                    {student}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-section">
            <div className="action-buttons">
              <button 
                className="action-btn primary"
                onClick={() => window.open('http://localhost:5186', '_blank')}
              >
                ⚠️ View At-Risk Students
              </button>
              <button 
                className="action-btn secondary"
                onClick={() => window.open('http://localhost:5184', '_blank')}
              >
                📈 Performance Trends
              </button>
              <button 
                className="action-btn secondary"
                onClick={() => window.open('http://localhost:5183', '_blank')}
              >
                📤 Upload Quiz
              </button>
            </div>
          </div>
          )}
        </div>
      )}

      {!loading && !progressData && !error && (
        <div className="no-results">
          <h3>🎯 Ready to Analyze Progress</h3>
          <p>Click "Analyze Progress Levels" to see how students are performing relative to grade-level expectations.</p>
        </div>
      )}
    </div>
  )
}

export default App
