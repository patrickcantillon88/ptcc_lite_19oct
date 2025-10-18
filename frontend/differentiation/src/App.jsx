import { useState, useEffect } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('differentiation')
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState({
    classCode: '',
    subject: ''
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
        setClasses(data.classes)
        if (data.classes.length > 0) {
          setConfig(prev => ({...prev, classCode: data.classes[0]}))
        }
      }
    } catch (err) {
      console.error('Error fetching classes:', err)
    }
  }

  const analyzeDifferentiation = async () => {
    if (!config.classCode) {
      setError('Please select a class')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        class_code: config.classCode
      })
      
      if (config.subject) {
        params.append('subject', config.subject)
      }

      const response = await fetch(`/api/classroom-tools/differentiation-support?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setAnalysisData(data)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to analyze class')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error analyzing differentiation:', err)
    } finally {
      setLoading(false)
    }
  }

  const getLevelColor = (level) => {
    const colors = {
      extension: '#28a745',
      on_level: '#ffc107', 
      support_needed: '#dc3545',
      unknown: '#6c757d'
    }
    return colors[level] || '#6c757d'
  }

  const getLevelIcon = (level) => {
    const icons = {
      extension: '🟢',
      on_level: '🟡',
      support_needed: '🔴',
      unknown: '⚪'
    }
    return icons[level] || '⚪'
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>🎯 Differentiation Decision Support</h1>
            <p>Identify students' learning levels and plan differentiated instruction based on assessment data</p>
          </div>
          <DeviceToggleComponent />
        </div>
      </header>

      <div className="config-section">
        <div className="config-grid">
          <div className="config-group">
            <label htmlFor="class-select">Select Class</label>
            <select 
              id="class-select"
              value={config.classCode} 
              onChange={(e) => setConfig({...config, classCode: e.target.value})}
            >
              <option value="">Choose a class...</option>
              {classes.map(cls => (
                <option key={cls} value={cls}>{cls}</option>
              ))}
            </select>
          </div>

          <div className="config-group">
            <label htmlFor="subject-input">Subject (optional)</label>
            <input
              id="subject-input"
              type="text"
              placeholder="e.g., Math, English"
              value={config.subject}
              onChange={(e) => setConfig({...config, subject: e.target.value})}
            />
          </div>
        </div>

        <button 
          className="generate-btn"
          onClick={analyzeDifferentiation}
          disabled={loading || !config.classCode}
        >
          {loading ? '🔄 Analyzing...' : '✨ Analyze Class for Differentiation'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {analysisData && (
        <div className="results-section">
          <div className="results-header">
            <h2>📊 Analysis Results for {analysisData.class_code}</h2>
            <div className="analysis-info">
              <span><strong>Subject:</strong> {analysisData.subject}</span>
              <span><strong>Total Students:</strong> {analysisData.total_students}</span>
            </div>
          </div>

          {/* Summary Metrics */}
          <div className="summary-section">
            <h3>📊 Summary</h3>
            <div className="summary-grid">
              <div className="summary-card" style={{borderLeftColor: getLevelColor('extension')}}>
                <div className="summary-value">{analysisData.summary.extension_count}</div>
                <div className="summary-label">🟢 Extension</div>
                <div className="summary-desc">Ready for challenge</div>
              </div>
              <div className="summary-card" style={{borderLeftColor: getLevelColor('on_level')}}>
                <div className="summary-value">{analysisData.summary.on_level_count}</div>
                <div className="summary-label">🟡 On-Level</div>
                <div className="summary-desc">Meeting grade level</div>
              </div>
              <div className="summary-card" style={{borderLeftColor: getLevelColor('support_needed')}}>
                <div className="summary-value">{analysisData.summary.support_count}</div>
                <div className="summary-label">🔴 Need Support</div>
                <div className="summary-desc">Below grade level</div>
              </div>
              <div className="summary-card">
                <div className="summary-value">
                  {analysisData.summary.avg_class_score ? `${analysisData.summary.avg_class_score}%` : 'N/A'}
                </div>
                <div className="summary-label">Class Average</div>
                <div className="summary-desc">Overall performance</div>
              </div>
            </div>
          </div>

          {/* Suggested Groups */}
          {analysisData.suggested_groups && analysisData.suggested_groups.length > 0 && (
            <div className="groups-section">
              <h3>🎯 Suggested Instructional Groups</h3>
              <div className="groups-grid">
                {analysisData.suggested_groups.map((group, index) => (
                  <div key={index} className="group-card" style={{borderLeftColor: getLevelColor(group.level)}}>
                    <div className="group-header">
                      <h4>{getLevelIcon(group.level)} {group.group_name}</h4>
                      <span className="group-size">({group.student_count} students)</span>
                    </div>
                    
                    <div className="group-focus">
                      <strong>Focus:</strong> {group.focus}
                    </div>

                    <div className="group-students">
                      <strong>Students:</strong>
                      <div className="students-list">
                        {group.students.map((student, idx) => (
                          <span key={idx} className="student-tag">{student}</span>
                        ))}
                      </div>
                    </div>

                    <div className="group-strategies">
                      <strong>Recommended Strategies:</strong>
                      <ul>
                        {group.strategies.map((strategy, idx) => (
                          <li key={idx}>{strategy}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Student Analysis */}
          <div className="details-section">
            <h3>📏 Individual Student Details</h3>
            
            {/* Extension Students */}
            {analysisData.students_by_level.extension && analysisData.students_by_level.extension.length > 0 && (
              <div className="level-section">
                <h4 style={{color: getLevelColor('extension')}}>
                  {getLevelIcon('extension')} Extension Students ({analysisData.students_by_level.extension.length})
                </h4>
                <div className="students-grid">
                  {analysisData.students_by_level.extension.map((student, index) => (
                    <div key={index} className="student-detail-card" style={{borderLeftColor: getLevelColor('extension')}}>
                      <div className="student-header">
                        <h5>{student.student_name}</h5>
                        <span className="student-avg">Avg: {student.avg_score}%</span>
                      </div>
                      <div className="student-info">
                        <div><strong>Trend:</strong> {student.trend.replace('_', ' ')}</div>
                        <div><strong>Assessments:</strong> {student.assessment_count}</div>
                      </div>
                      <div className="student-needs">
                        <strong>Needs:</strong>
                        <ul>
                          {student.needs.map((need, idx) => (
                            <li key={idx}>{need}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="student-recommendations">
                        <strong>Recommendations:</strong>
                        <ul>
                          {student.recommendations.map((rec, idx) => (
                            <li key={idx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* On-Level Students */}
            {analysisData.students_by_level.on_level && analysisData.students_by_level.on_level.length > 0 && (
              <div className="level-section">
                <h4 style={{color: getLevelColor('on_level')}}>
                  {getLevelIcon('on_level')} On-Level Students ({analysisData.students_by_level.on_level.length})
                </h4>
                <div className="students-grid">
                  {analysisData.students_by_level.on_level.map((student, index) => (
                    <div key={index} className="student-detail-card" style={{borderLeftColor: getLevelColor('on_level')}}>
                      <div className="student-header">
                        <h5>{student.student_name}</h5>
                        <span className="student-avg">Avg: {student.avg_score}%</span>
                      </div>
                      <div className="student-info">
                        <div><strong>Trend:</strong> {student.trend.replace('_', ' ')}</div>
                        <div><strong>Assessments:</strong> {student.assessment_count}</div>
                      </div>
                      <div className="student-needs">
                        <strong>Needs:</strong>
                        <ul>
                          {student.needs.map((need, idx) => (
                            <li key={idx}>{need}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="student-recommendations">
                        <strong>Recommendations:</strong>
                        <ul>
                          {student.recommendations.map((rec, idx) => (
                            <li key={idx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Support Needed Students */}
            {analysisData.students_by_level.support_needed && analysisData.students_by_level.support_needed.length > 0 && (
              <div className="level-section">
                <h4 style={{color: getLevelColor('support_needed')}}>
                  {getLevelIcon('support_needed')} Students Needing Support ({analysisData.students_by_level.support_needed.length})
                </h4>
                <div className="students-grid">
                  {analysisData.students_by_level.support_needed.map((student, index) => {
                    const isUrgent = student.trend === 'declining' || student.support_level >= 2
                    return (
                      <div key={index} className={`student-detail-card ${isUrgent ? 'urgent' : ''}`} style={{borderLeftColor: getLevelColor('support_needed')}}>
                        <div className="student-header">
                          <h5>{isUrgent ? '⚠️ ' : ''}{student.student_name}</h5>
                          <span className="student-avg">Avg: {student.avg_score || 'N/A'}%</span>
                        </div>
                        <div className="student-info">
                          <div><strong>Trend:</strong> {student.trend.replace('_', ' ')}</div>
                          <div><strong>Support Level:</strong> {student.support_level}</div>
                          <div><strong>Assessments:</strong> {student.assessment_count}</div>
                        </div>
                        <div className="student-needs">
                          <strong>Needs:</strong>
                          <ul>
                            {student.needs.map((need, idx) => (
                              <li key={idx} className={need.includes('Declining') || need.includes('High support') ? 'urgent-need' : ''}>
                                {need}
                              </li>
                            ))}
                          </ul>
                        </div>
                        {student.gaps && (
                          <div className="student-gaps">
                            <strong>Specific Gaps:</strong>
                            <ul>
                              {student.gaps.map((gap, idx) => (
                                <li key={idx}>{gap}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        <div className="student-recommendations">
                          <strong>Recommendations:</strong>
                          <ul>
                            {student.recommendations.map((rec, idx) => (
                              <li key={idx} className={rec.includes('Urgent') || rec.includes('1-on-1') ? 'urgent-recommendation' : ''}>
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>

          <div className="action-section">
            <button className="action-btn" onClick={() => console.log('Copy functionality')}>
              📋 Copy Groups to Clipboard
            </button>
            <button className="action-btn" onClick={() => console.log('Export functionality')}>
              📊 Export to CSV
            </button>
          </div>
        </div>
      )}

      {!loading && !analysisData && !error && (
        <div className="no-results">
          <h3>🎯 Ready to Analyze Class</h3>
          <p>Select a class and optionally specify a subject to analyze student performance levels for differentiated instruction planning.</p>
        </div>
      )}
    </div>
  )
}

export default App
