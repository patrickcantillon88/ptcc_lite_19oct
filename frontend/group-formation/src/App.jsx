import { useState, useEffect } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('group-formation')
  const [groupsData, setGroupsData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState({
    classCode: '',
    groupSize: 4,
    strategy: 'mixed_ability'
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

  const generateGroups = async () => {
    if (!config.classCode) {
      setError('Please select a class')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        class_code: config.classCode,
        group_size: config.groupSize,
        strategy: config.strategy
      })

      const response = await fetch(`/api/classroom-tools/group-formation?${params}`)
      
      if (response.ok) {
        const data = await response.json()
        setGroupsData(data)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to generate groups')
      }
    } catch (err) {
      setError('Error connecting to backend')
      console.error('Error generating groups:', err)
    } finally {
      setLoading(false)
    }
  }

  const strategyDescriptions = {
    mixed_ability: "🎯 Mix high and low performers to promote peer learning",
    similar_ability: "📚 Group similar performers for targeted instruction",
    behavioral_balance: "⚖️ Distribute behavioral dynamics evenly across groups",
    support_aware: "🫂 Distribute support needs evenly for teacher management"
  }

  const getSupportIcon = (level) => {
    const icons = { 0: '🟢', 1: '🟡', 2: '🟠', 3: '🔴' }
    return icons[level] || '⚪'
  }

  const getBehaviorIcon = (score) => {
    return score >= 0 ? '🟢' : '🔴'
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>👥 Student Group Formation</h1>
            <p>Generate optimal student groups based on assessment data, behavior patterns, and support needs</p>
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
            <label htmlFor="size-input">Group Size</label>
            <input
              id="size-input"
              type="number"
              min="2"
              max="10"
              value={config.groupSize}
              onChange={(e) => setConfig({...config, groupSize: parseInt(e.target.value)})}
            />
          </div>

          <div className="config-group">
            <label htmlFor="strategy-select">Grouping Strategy</label>
            <select 
              id="strategy-select"
              value={config.strategy} 
              onChange={(e) => setConfig({...config, strategy: e.target.value})}
            >
              <option value="mixed_ability">Mixed Ability</option>
              <option value="similar_ability">Similar Ability</option>
              <option value="behavioral_balance">Behavioral Balance</option>
              <option value="support_aware">Support Aware</option>
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
          onClick={generateGroups}
          disabled={loading || !config.classCode}
        >
          {loading ? '🔄 Generating...' : '✨ Generate Groups'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {groupsData && (
        <div className="results-section">
          <div className="results-header">
            <h2>🎯 Generated Groups for {groupsData.class_code}</h2>
            <div className="groups-info">
              <span><strong>Strategy:</strong> {config.strategy.replace('_', ' ')}</span>
              <span><strong>Total Students:</strong> {groupsData.total_students}</span>
              <span><strong>Groups Created:</strong> {groupsData.num_groups}</span>
            </div>
            {groupsData.rationale && (
              <div className="rationale">
                ✅ {groupsData.rationale}
              </div>
            )}
          </div>

          <div className="groups-grid">
            {groupsData.groups && groupsData.groups.map((group) => (
              <div key={group.group_number} className="group-card">
                <div className="group-header">
                  <h3>👥 Group {group.group_number}</h3>
                  <div className="group-stats">
                    <span className="stat">Size: {group.group_stats.size}</span>
                    <span className="stat">Avg: {group.group_stats.avg_assessment_score}%</span>
                  </div>
                </div>

                <div className="group-metrics">
                  <div className="metric">
                    <div className="metric-label">Avg Assessment Score</div>
                    <div className="metric-value">{group.group_stats.avg_assessment_score}%</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Total Support Level</div>
                    <div className="metric-value">{group.group_stats.total_support_level}</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Avg Behavior Score</div>
                    <div className="metric-value">
                      {group.group_stats.avg_behavior_score >= 0 ? '+' : ''}{group.group_stats.avg_behavior_score.toFixed(1)}
                    </div>
                  </div>
                </div>

                <div className="group-members">
                  <h4>Members</h4>
                  <div className="members-list">
                    {group.members.map((member, index) => (
                      <div key={index} className="member-card">
                        <div className="member-info">
                          <div className="member-name">
                            {getSupportIcon(member.support_level)} <strong>{member.name}</strong>
                          </div>
                          <div className="member-details">
                            <span className="detail">Avg: {member.avg_score}%</span>
                            <span className="detail">
                              Behavior: {getBehaviorIcon(member.behavior_score)} {member.behavior_score >= 0 ? '+' : ''}{member.behavior_score}
                            </span>
                            <span className="detail">Support: Level {member.support_level}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="legend-section">
            <h3>🏷️ Legend</h3>
            <div className="legend-grid">
              <div className="legend-column">
                <h4>Support Level Indicators</h4>
                <div className="legend-items">
                  <div className="legend-item">🟢 Green = No support (0)</div>
                  <div className="legend-item">🟡 Yellow = Low support (1)</div>
                  <div className="legend-item">🟠 Orange = Medium support (2)</div>
                  <div className="legend-item">🔴 Red = High support (3)</div>
                </div>
              </div>
              <div className="legend-column">
                <h4>Behavior Indicators</h4>
                <div className="legend-items">
                  <div className="legend-item">🟢 Green circle = Positive behavior score</div>
                  <div className="legend-item">🔴 Red circle = Negative behavior score</div>
                  <div className="legend-item">Higher scores = better recent behavior</div>
                </div>
              </div>
            </div>
          </div>

          <div className="action-section">
            <button className="action-btn" onClick={() => console.log('Copy functionality')}>
              📋 Copy to Clipboard
            </button>
            <button className="action-btn" onClick={() => console.log('Export functionality')}>
              📊 Export to CSV
            </button>
          </div>
        </div>
      )}

      {!loading && !groupsData && !error && (
        <div className="no-results">
          <h3>👥 Ready to Generate Groups</h3>
          <p>Select your class, configure group settings, and click "Generate Groups" to create optimal student groupings.</p>
        </div>
      )}
    </div>
  )
}

export default App
