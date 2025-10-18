import { useState, useEffect } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('performance-trends')
  const [trendsData, setTrendsData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    subject: '',
    class_code: '',
    limit: 50
  })
  const [overviewData, setOverviewData] = useState(null)
  const [error, setError] = useState(null)

  // Load overview data on component mount
  useEffect(() => {
    fetchOverview()
  }, [])

  const fetchOverview = async () => {
    try {
      const params = new URLSearchParams({ days: 90 })
      if (filters.subject) params.append('subject', filters.subject)
      if (filters.class_code) params.append('class_code', filters.class_code)
      
      const response = await fetch(`/api/quiz-analytics/analytics/overview?${params}`)
      if (response.ok) {
        const data = await response.json()
        setOverviewData(data)
      }
    } catch (err) {
      console.error('Error fetching overview:', err)
    }
  }

  const fetchTrends = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({ limit: filters.limit })
      if (filters.subject) params.append('subject', filters.subject)
      if (filters.class_code) params.append('class_code', filters.class_code)

      const response = await fetch(`/api/quiz-analytics/analytics/student-trends?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setTrendsData(data)
      } else {
        setError('Failed to load performance trends')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error fetching trends:', err)
    } finally {
      setLoading(false)
    }
  }

  const getTrendIcon = (trend) => {
    const icons = {
      improving: '📈',
      declining: '📉', 
      stable: '➡️',
      insufficient_data: '❓'
    }
    return icons[trend] || '➡️'
  }

  const getTrendColor = (trend) => {
    const colors = {
      improving: '#28a745',
      declining: '#dc3545',
      stable: '#ffc107',
      insufficient_data: '#6c757d'
    }
    return colors[trend] || '#6c757d'
  }

  const getProgressLevelColor = (level) => {
    const colors = {
      'Exceeding': '#28a745',
      'Meeting': '#ffc107',
      'Working Towards': '#dc3545'
    }
    return colors[level] || '#6c757d'
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>📈 Performance Trends</h1>
            <p>Track student quiz performance over time with detailed analytics and trend analysis</p>
          </div>
          <DeviceToggleComponent />
        </div>
      </header>

      {/* Overview Cards */}
      {overviewData && (
        <div className="overview-section">
          {overviewData.total_quizzes === 0 ? (
            <div className="no-data-banner">
              <div className="no-data-icon">📊</div>
              <div className="no-data-content">
                <h3>No Quiz Data Available</h3>
                <p>Upload some quiz results first to see performance trends and analytics.</p>
                <button 
                  className="upload-data-btn"
                  onClick={() => window.open('http://localhost:5183', '_blank')}
                >
                  📤 Upload Quiz Data
                </button>
              </div>
            </div>
          ) : (
            <div className="overview-grid">
              <div className="overview-card">
                <div className="overview-value">{overviewData.total_quizzes}</div>
                <div className="overview-label">Total Quizzes</div>
              </div>
              <div className="overview-card">
                <div className="overview-value">{overviewData.total_attempts}</div>
                <div className="overview-label">Quiz Attempts</div>
              </div>
              <div className="overview-card">
                <div className="overview-value">{overviewData.average_score}%</div>
                <div className="overview-label">Average Score</div>
              </div>
              <div className="overview-card">
                <div className="overview-value">{overviewData.highest_score}%</div>
                <div className="overview-label">Highest Score</div>
              </div>
            </div>
          )}
        </div>
      )}

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
            <label htmlFor="limit-filter">Max Students</label>
            <input
              id="limit-filter"
              type="number"
              min="10"
              max="100"
              value={filters.limit}
              onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
            />
          </div>
          
          <div className="filter-group">
            <button 
              className="analyze-btn"
              onClick={fetchTrends}
              disabled={loading}
            >
              {loading ? '🔄 Loading...' : '📊 Analyze Trends'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {trendsData && (
        <div className="results-section">
          <div className="results-header">
            <h2>📊 Student Performance Trends</h2>
            <p><strong>Students Analyzed:</strong> {trendsData.total}</p>
          </div>
          
          {trendsData.total === 0 ? (
            <div className="no-students-found">
              <div className="no-data-icon">👥</div>
              <h3>No Student Trends Found</h3>
              <p>No students match your current filters, or there isn't enough quiz data to analyze trends.</p>
              <div className="suggestions">
                <p><strong>Try:</strong></p>
                <ul>
                  <li>Removing subject or class filters</li>
                  <li>Increasing the maximum students limit</li>
                  <li>Uploading more quiz data</li>
                </ul>
              </div>
            </div>
          ) : (
            <>
            {/* Trend Statistics */}
            <div className="trend-stats">
            <div className="trend-stat-card improving">
              <div className="stat-icon">📈</div>
              <div className="stat-info">
                <div className="stat-value">
                  {trendsData.students.filter(s => s.trend === 'improving').length}
                </div>
                <div className="stat-label">Improving</div>
              </div>
            </div>
            
            <div className="trend-stat-card stable">
              <div className="stat-icon">➡️</div>
              <div className="stat-info">
                <div className="stat-value">
                  {trendsData.students.filter(s => s.trend === 'stable').length}
                </div>
                <div className="stat-label">Stable</div>
              </div>
            </div>
            
            <div className="trend-stat-card declining">
              <div className="stat-icon">📉</div>
              <div className="stat-info">
                <div className="stat-value">
                  {trendsData.students.filter(s => s.trend === 'declining').length}
                </div>
                <div className="stat-label">Declining</div>
              </div>
            </div>
          </div>

          <div className="students-grid">
            {trendsData.students.map((student) => (
              <div 
                key={student.student_id} 
                className={`student-card trend-${student.trend}`}
                style={{ borderLeftColor: getTrendColor(student.trend) }}
              >
                <div className="student-header">
                  <div className="student-info">
                    <h3>{student.student_name}</h3>
                    <span className="class-code">({student.class_code})</span>
                    <span 
                      className="progress-badge"
                      style={{ backgroundColor: getProgressLevelColor(student.progress_level) }}
                    >
                      {student.progress_level}
                    </span>
                  </div>
                  <div className="trend-indicator">
                    <span 
                      className="trend-icon"
                      style={{ color: getTrendColor(student.trend) }}
                    >
                      {getTrendIcon(student.trend)}
                    </span>
                    <span className="trend-label">{student.trend.replace('_', ' ')}</span>
                  </div>
                </div>

                <div className="student-metrics">
                  <div className="metric">
                    <label>Quiz Count</label>
                    <span className="metric-value">{student.quiz_count}</span>
                  </div>
                  <div className="metric">
                    <label>Average Score</label>
                    <span className="metric-value">{student.average_percentage}%</span>
                  </div>
                  <div className="metric">
                    <label>Score Range</label>
                    <span className="metric-value">
                      {student.score_range.min}% - {student.score_range.max}%
                    </span>
                  </div>
                </div>

                {student.recent_scores && student.recent_scores.length > 0 && (
                  <div className="recent-scores">
                    <h4>📊 Recent Scores</h4>
                    <div className="scores-chart">
                      {student.recent_scores.map((score, index) => (
                        <div 
                          key={index} 
                          className="score-bar"
                          style={{
                            height: `${Math.max(score, 5)}px`,
                            backgroundColor: score >= 85 ? '#28a745' : 
                                           score >= 70 ? '#ffc107' : '#dc3545'
                          }}
                          title={`Score: ${score}%`}
                        ></div>
                      ))}
                    </div>
                    <div className="scores-labels">
                      <span>Oldest</span>
                      <span>Recent</span>
                    </div>
                  </div>
                )}

                <div className="action-buttons">
                  <button className="action-btn primary">View Details</button>
                  <button 
                    className="action-btn secondary"
                    onClick={() => window.open('http://localhost:5185', '_blank')}
                  >
                    Progress Levels
                  </button>
                </div>
              </div>
            ))}
          </div>
            </>
          )}
        </div>
      )}

      {!loading && !trendsData && !error && (
        <div className="no-results">
          <h3>📈 Ready to Analyze Trends</h3>
          <p>Click "Analyze Trends" to view student performance patterns over time.</p>
        </div>
      )}
    </div>
  )
}

export default App
