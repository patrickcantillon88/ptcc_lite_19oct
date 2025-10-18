import { useState, useEffect } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('seating-chart')
  const [seatingData, setSeatingData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState({
    classCode: '',
    rows: 5,
    cols: 6,
    strategy: 'behavior_optimized'
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

  const generateSeatingChart = async () => {
    if (!config.classCode) {
      setError('Please select a class')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        class_code: config.classCode,
        rows: config.rows,
        cols: config.cols,
        strategy: config.strategy
      })

      const response = await fetch(`/api/classroom-tools/seating-chart?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setSeatingData(data)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to generate seating chart')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error generating seating chart:', err)
    } finally {
      setLoading(false)
    }
  }

  const strategyDescriptions = {
    behavior_optimized: "⚠️ Minimize behavioral conflicts - high-incident students at front/corners for monitoring",
    support_distributed: "🫂 Distribute support needs evenly across the room for balanced teacher attention",
    mixed_ability: "🎯 Mix high and low performers in snake pattern for peer learning",
    random: "🎲 Random assignment for baseline comparison"
  }

  const getSeatColor = (student) => {
    if (!student) return '#f9f9f9'
    const colors = {
      0: '#d4edda', // Green - no support
      1: '#fff3cd', // Yellow - low support  
      2: '#ffe5cc', // Orange - medium support
      3: '#f8d7da'  // Red - high support
    }
    return colors[student.support_level] || '#ffffff'
  }

  const getSeatBorder = (student) => {
    if (!student) return '1px dashed #ccc'
    return student.has_incidents ? '3px solid #dc3545' : '1px solid #6c757d'
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>🪩 Seating Chart Optimizer</h1>
            <p>Generate optimal seating arrangements based on behavior data, support needs, and learning patterns</p>
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
            <label htmlFor="rows-input">Rows</label>
            <input
              id="rows-input"
              type="number"
              min="3"
              max="10"
              value={config.rows}
              onChange={(e) => setConfig({...config, rows: parseInt(e.target.value)})}
            />
          </div>

          <div className="config-group">
            <label htmlFor="cols-input">Columns</label>
            <input
              id="cols-input"
              type="number"
              min="3"
              max="10"
              value={config.cols}
              onChange={(e) => setConfig({...config, cols: parseInt(e.target.value)})}
            />
          </div>

          <div className="config-group">
            <label htmlFor="strategy-select">Strategy</label>
            <select 
              id="strategy-select"
              value={config.strategy} 
              onChange={(e) => setConfig({...config, strategy: e.target.value})}
            >
              <option value="behavior_optimized">Behavior Optimized</option>
              <option value="support_distributed">Support Distributed</option>
              <option value="mixed_ability">Mixed Ability</option>
              <option value="random">Random</option>
            </select>
          </div>
        </div>

        <div className="strategy-description">
          <div className="strategy-info">
            {strategyDescriptions[config.strategy]}
          </div>
        </div>

        <button 
          className="generate-btn"
          onClick={generateSeatingChart}
          disabled={loading || !config.classCode}
        >
          {loading ? '🔄 Generating...' : '✨ Generate Seating Chart'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {seatingData && (
        <div className="results-section">
          <div className="results-header">
            <h2>📍 Seating Chart for {seatingData.class_code}</h2>
            <div className="chart-info">
              <span><strong>Strategy:</strong> {config.strategy.replace('_', ' ')}</span>
              <span><strong>Dimensions:</strong> {seatingData.dimensions.rows} × {seatingData.dimensions.cols} = {seatingData.dimensions.total_seats} seats</span>
              <span><strong>Students:</strong> {seatingData.student_count} | <strong>Empty:</strong> {seatingData.empty_seats}</span>
            </div>
            {seatingData.rationale && (
              <div className="rationale">
                ✅ {seatingData.rationale}
              </div>
            )}
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{seatingData.stats.total_support_needs}</div>
              <div className="stat-label">Total Support Needs</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{seatingData.stats.high_incident_count}</div>
              <div className="stat-label">High Incident Students</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {(seatingData.stats.support_per_row.reduce((a, b) => a + b, 0) / seatingData.stats.support_per_row.length).toFixed(1)}
              </div>
              <div className="stat-label">Avg Support per Row</div>
            </div>
          </div>

          <div className="classroom-layout">
            <div className="classroom-label">📚 <strong>Front of Classroom</strong> 📚</div>
            
            <div className="seating-grid" style={{
              gridTemplateColumns: `repeat(${seatingData.dimensions.cols}, 1fr)`,
              gridTemplateRows: `repeat(${seatingData.dimensions.rows}, 1fr)`
            }}>
              {seatingData.seating_grid.flat().map((student, index) => {
                const row = Math.floor(index / seatingData.dimensions.cols)
                const col = index % seatingData.dimensions.cols
                
                return (
                  <div
                    key={`${row}-${col}`}
                    className={`seat ${student ? 'occupied' : 'empty'}`}
                    style={{
                      backgroundColor: getSeatColor(student),
                      border: getSeatBorder(student)
                    }}
                  >
                    {student ? (
                      <div className="student-info">
                        <div className="student-name">
                          {student.name.split(' ').map(n => n[0]).join('.')} {student.name.split(' ').pop()}
                        </div>
                        <div className="student-metrics">
                          <span className={`behavior-indicator ${student.behavior_score >= 0 ? 'positive' : 'negative'}`}>
                            {student.behavior_score >= 0 ? '🟢' : '🔴'} {student.behavior_score > 0 ? '+' : ''}{student.behavior_score}
                          </span>
                          <span className="support-level">Supp: {student.support_level}</span>
                          <span className="avg-score">Avg: {student.avg_score}%</span>
                        </div>
                      </div>
                    ) : (
                      <div className="empty-seat">— Empty —</div>
                    )}
                  </div>
                )
              })}
            </div>

            <div className="classroom-label">🚪 <strong>Back of Classroom</strong> 🚪</div>
          </div>

          <div className="legend-section">
            <h3>🏷️ Legend</h3>
            <div className="legend-grid">
              <div className="legend-column">
                <h4>Background Colors (Support Level)</h4>
                <div className="legend-items">
                  <div className="legend-item"><span className="color-box" style={{backgroundColor: '#d4edda'}}></span> Green = No support (0)</div>
                  <div className="legend-item"><span className="color-box" style={{backgroundColor: '#fff3cd'}}></span> Yellow = Low support (1)</div>
                  <div className="legend-item"><span className="color-box" style={{backgroundColor: '#ffe5cc'}}></span> Orange = Medium support (2)</div>
                  <div className="legend-item"><span className="color-box" style={{backgroundColor: '#f8d7da'}}></span> Red = High support (3)</div>
                </div>
              </div>
              <div className="legend-column">
                <h4>Indicators</h4>
                <div className="legend-items">
                  <div className="legend-item">🔴 Red border = High behavioral incidents (>5)</div>
                  <div className="legend-item">🟢 Green circle = Positive behavior score</div>
                  <div className="legend-item">🔴 Red circle = Negative behavior score</div>
                  <div className="legend-item">Supp = Support level | Avg = Assessment average</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !seatingData && !error && (
        <div className="no-results">
          <h3>🪑 Ready to Generate Seating Chart</h3>
          <p>Configure your classroom layout and click "Generate Seating Chart" to create an optimal arrangement.</p>
        </div>
      )}
    </div>
  )
}

export default App
