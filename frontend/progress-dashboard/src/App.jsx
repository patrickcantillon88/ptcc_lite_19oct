import { useState, useEffect } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('progress-dashboard')
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    classCode: 'All Classes',
    days: 30,
    behaviorType: 'All Behavior'
  })
  const [classes, setClasses] = useState([])
  const [error, setError] = useState(null)

  // Load available classes on component mount
  useEffect(() => {
    fetchClasses()
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

  const fetchDashboardData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        days: filters.days,
        behavior_type: filters.behaviorType === 'All Behavior' ? 'all' : 
                       filters.behaviorType === 'Classroom Only' ? 'classroom' : 'cca'
      })
      
      if (filters.classCode !== 'All Classes') {
        params.append('class_code', filters.classCode)
      }

      const response = await fetch(`/api/classroom-tools/progress-dashboard?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      } else {
        setError('Failed to load dashboard data')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error fetching dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatTrendData = (trendData) => {
    if (!trendData || trendData.length === 0) return []
    
    return trendData.map(item => ({
      date: new Date(item.date).toLocaleDateString(),
      positive: item.positive || 0,
      negative: item.negative || 0,
      neutral: item.neutral || 0,
      net: (item.positive || 0) - (item.negative || 0)
    }))
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>📈 Progress Tracking Dashboard</h1>
            <p>Visual analytics showing class and student progress over time</p>
          </div>
          <DeviceToggleComponent />
        </div>
      </header>

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="class-filter">Select Class</label>
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
            <label htmlFor="days-filter">Time Period</label>
            <select 
              id="days-filter"
              value={filters.days} 
              onChange={(e) => setFilters({...filters, days: parseInt(e.target.value)})}
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
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
              onClick={fetchDashboardData}
              disabled={loading}
            >
              {loading ? '🔄 Loading...' : '🔄 Generate Dashboard'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {dashboardData && (
        <div className="dashboard-content">
          {/* Summary Metrics */}
          <div className="metrics-section">
            <h2>📊 Summary Metrics</h2>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value positive">
                  +{dashboardData.summary?.total_positive_logs || 0}
                </div>
                <div className="metric-label">Positive Logs</div>
              </div>
              
              <div className="metric-card">
                <div className="metric-value negative">
                  -{dashboardData.summary?.total_negative_logs || 0}
                </div>
                <div className="metric-label">Negative Logs</div>
              </div>
              
              <div className="metric-card">
                <div className={`metric-value ${dashboardData.summary?.net_behavior_score >= 0 ? 'positive' : 'negative'}`}>
                  {dashboardData.summary?.net_behavior_score >= 0 ? '+' : ''}{dashboardData.summary?.net_behavior_score || 0}
                </div>
                <div className="metric-label">Net Behavior Score</div>
              </div>
              
              <div className="metric-card">
                <div className="metric-value neutral">
                  {dashboardData.summary?.average_class_score || 'N/A'}%
                </div>
                <div className="metric-label">Avg Assessment Score</div>
              </div>
            </div>
            <div className="period-info">
              <strong>{dashboardData.class_code}</strong> | {dashboardData.student_count} students | Last {filters.days} days
            </div>
          </div>

          {/* Behavior Trends */}
          <div className="section">
            <h3>📈 Behavior Trends Over Time</h3>
            {dashboardData.behavior_trend && dashboardData.behavior_trend.length > 0 ? (
              <div className="trend-chart">
                {formatTrendData(dashboardData.behavior_trend).map((item, index) => (
                  <div key={index} className="trend-item">
                    <div className="trend-date">{item.date}</div>
                    <div className="trend-bars">
                      <div className="bar positive" style={{height: `${Math.max(item.positive * 20, 5)}px`}} title={`+${item.positive} positive`}></div>
                      <div className="bar negative" style={{height: `${Math.max(item.negative * 20, 5)}px`}} title={`-${item.negative} negative`}></div>
                    </div>
                    <div className="net-score">
                      Net: {item.net >= 0 ? '+' : ''}{item.net}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">No behavior data available for this period</div>
            )}
          </div>

          {/* Support Distribution */}
          <div className="section">
            <h3>🎯 Support Level Distribution</h3>
            <div className="support-grid">
              {Object.entries(dashboardData.support_distribution || {}).map(([level, count]) => {
                const labels = {0: 'None (0)', 1: 'Low (1)', 2: 'Medium (2)', 3: 'High (3)'}
                const colors = {0: '#28a745', 1: '#ffc107', 2: '#fd7e14', 3: '#dc3545'}
                return (
                  <div key={level} className="support-card">
                    <div className="support-count" style={{color: colors[level]}}>{count}</div>
                    <div className="support-label">{labels[level] || `Level ${level}`}</div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Top Performers and Attention */}
          <div className="students-section">
            <div className="students-grid">
              <div className="students-column">
                <h3>⭐ Top Performers (Behavior)</h3>
                {dashboardData.top_performers && dashboardData.top_performers.length > 0 ? (
                  <div className="student-list">
                    {dashboardData.top_performers.slice(0, 5).map((student, index) => (
                      <div key={student.student_id} className="student-item positive">
                        <span className="student-rank">#{index + 1}</span>
                        <span className="student-name">{student.student_name}</span>
                        <span className="student-class">({student.class_code})</span>
                        <span className="student-score">Net: +{student.net_behavior}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-data">No data available</div>
                )}
              </div>

              <div className="students-column">
                <h3>⚠️ Needs Attention (Behavior)</h3>
                {dashboardData.needs_attention && dashboardData.needs_attention.length > 0 ? (
                  <div className="student-list">
                    {dashboardData.needs_attention.slice(0, 5).map((student, index) => (
                      <div key={student.student_id} className="student-item negative">
                        <span className="student-rank">#{index + 1}</span>
                        <span className="student-name">{student.student_name}</span>
                        <span className="student-class">({student.class_code})</span>
                        <span className="student-score">Net: {student.net_behavior}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-data success">✅ No students currently need attention!</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !dashboardData && !error && (
        <div className="no-results">
          <h3>📈 Ready to Generate Dashboard</h3>
          <p>Select your filters and click "Generate Dashboard" to view progress analytics.</p>
        </div>
      )}
    </div>
  )
}

export default App
