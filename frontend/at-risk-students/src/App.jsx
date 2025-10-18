import { useState } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('at-risk-students')
  const [atRiskData, setAtRiskData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState({
    threshold: 60.0,
    min_quizzes: 2
  })
  const [error, setError] = useState(null)

  const fetchAtRiskStudents = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        threshold: config.threshold,
        min_quizzes: config.min_quizzes
      })

      const response = await fetch(`/api/quiz-analytics/analytics/at-risk?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setAtRiskData(data)
      } else {
        setError('Failed to load at-risk students')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error fetching at-risk students:', err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevelColor = (reason) => {
    return reason === 'declining_performance' ? '#fd7e14' : '#dc3545'
  }

  const getRiskIcon = (reason) => {
    return reason === 'declining_performance' ? '📉' : '⚠️'
  }

  const formatReason = (reason) => {
    return reason.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>⚠️ At-Risk Students</h1>
            <p>Identify students with declining or low performance who may need intervention</p>
          </div>
          <DeviceToggleComponent />
        </div>
      </header>

      <div className="config-section">
        <div className="config-grid">
          <div className="config-group">
            <label htmlFor="threshold-input">Performance Threshold (%)</label>
            <input
              id="threshold-input"
              type="number"
              min="0"
              max="100"
              step="5"
              value={config.threshold}
              onChange={(e) => setConfig({...config, threshold: parseFloat(e.target.value)})}
            />
            <small>Students below this average will be flagged</small>
          </div>
          
          <div className="config-group">
            <label htmlFor="min-quizzes-input">Minimum Quizzes</label>
            <input
              id="min-quizzes-input"
              type="number"
              min="1"
              max="10"
              value={config.min_quizzes}
              onChange={(e) => setConfig({...config, min_quizzes: parseInt(e.target.value)})}
            />
            <small>Minimum quiz attempts required for analysis</small>
          </div>
          
          <div className="config-group">
            <button 
              className="analyze-btn"
              onClick={fetchAtRiskStudents}
              disabled={loading}
            >
              {loading ? '🔄 Loading...' : '🔍 Identify At-Risk Students'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {atRiskData && (
        <div className="results-section">
          <div className="results-header">
            <h2>🚨 At-Risk Student Analysis</h2>
            <div className="analysis-info">
              <span><strong>Students Identified:</strong> {atRiskData.at_risk_count}</span>
              <span><strong>Threshold Used:</strong> {atRiskData.threshold_used}%</span>
            </div>
          </div>

          {atRiskData.at_risk_count === 0 ? (
            <div className="no-risk-students">
              <div className="success-icon">✅</div>
              <h3>Great News!</h3>
              <p>No students are currently at risk based on your criteria.</p>
              <div className="criteria-info">
                <p>Criteria used:</p>
                <ul>
                  <li>Performance threshold: {config.threshold}%</li>
                  <li>Minimum quizzes: {config.min_quizzes}</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="students-grid">
              {atRiskData.students.map((student) => (
                <div 
                  key={student.student_id} 
                  className={`student-card risk-${student.reason.replace('_', '-')}`}
                  style={{ borderLeftColor: getRiskLevelColor(student.reason) }}
                >
                  <div className="student-header">
                    <div className="student-info">
                      <h3>{student.student_name}</h3>
                      <span className="class-code">({student.class_code})</span>
                      <span 
                        className="risk-badge"
                        style={{ backgroundColor: getRiskLevelColor(student.reason) }}
                      >
                        {getRiskIcon(student.reason)} {formatReason(student.reason)}
                      </span>
                    </div>
                  </div>

                  <div className="student-metrics">
                    <div className="metric">
                      <label>Average Score</label>
                      <span 
                        className="metric-value"
                        style={{ color: student.average_score < config.threshold ? '#dc3545' : '#ffc107' }}
                      >
                        {student.average_score}%
                      </span>
                    </div>
                    <div className="metric">
                      <label>Quiz Count</label>
                      <span className="metric-value">{student.quiz_count}</span>
                    </div>
                  </div>

                  {student.recent_scores && student.recent_scores.length > 0 && (
                    <div className="recent-scores">
                      <h4>📉 Recent Performance</h4>
                      <div className="scores-chart">
                        {student.recent_scores.map((score, index) => (
                          <div 
                            key={index} 
                            className="score-bar"
                            style={{
                              height: `${Math.max(score, 5)}px`,
                              backgroundColor: score >= config.threshold ? '#28a745' : 
                                             score >= config.threshold * 0.8 ? '#ffc107' : '#dc3545'
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

                  <div className="intervention-suggestions">
                    <h4>📝 Suggested Interventions</h4>
                    <ul>
                      {student.reason === 'declining_performance' ? [
                        'Schedule one-on-one tutoring session',
                        'Review recent quiz topics for understanding gaps', 
                        'Check for external factors affecting performance',
                        'Consider peer mentoring program'
                      ] : [
                        'Provide additional practice materials',
                        'Arrange parent-teacher conference',
                        'Assess learning style compatibility',
                        'Consider modified assessment format'
                      ].map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="action-buttons">
                    <button className="action-btn primary">Contact Parent</button>
                    <button className="action-btn secondary">Schedule Meeting</button>
                    <button className="action-btn secondary">View Full History</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quick Actions */}
          <div className="quick-actions">
            <h3>🚀 Quick Actions</h3>
            <div className="action-buttons">
              <button 
                className="action-btn primary"
                onClick={() => window.open('http://localhost:5183', '_blank')}
              >
                📤 Upload New Quiz Data
              </button>
              <button 
                className="action-btn secondary"
                onClick={() => window.open('http://localhost:5185', '_blank')}
              >
                🎯 View Progress Levels
              </button>
              <button 
                className="action-btn secondary"
                onClick={() => window.open('http://localhost:5184', '_blank')}
              >
                📈 Performance Trends
              </button>
            </div>
          </div>
        </div>
      )}

      {!loading && !atRiskData && !error && (
        <div className="no-results">
          <h3>🔍 Ready to Identify At-Risk Students</h3>
          <p>Configure your criteria and click "Identify At-Risk Students" to find students who may need intervention.</p>
        </div>
      )}
    </div>
  )
}

export default App
