import { useState, useEffect } from 'react';
import './App.css';
import AgentAnalysis from './components/AgentAnalysis';

// Types
interface Student {
  id: number;
  name: string;
  class_code: string;
  year_group: string;
}

interface LogEntry {
  id?: string;
  student_id: number;
  student_name: string;
  log_type: 'positive' | 'negative' | 'neutral';
  category: string;
  note?: string;
  timestamp: string;
  synced: boolean;
}

// Behavior categories with quick-tap options
const BEHAVIORS = {
  negative: [
    { category: 'off_task', label: '📱 Off Task', color: '#ff6b6b' },
    { category: 'disruption', label: '🗣️ Disruption', color: '#ff8787' },
    { category: 'warning_given', label: '⚠️ Warning', color: '#ffa8a8' },
    { category: 'incomplete_work', label: '📝 Incomplete', color: '#ffb3b3' },
  ],
  positive: [
    { category: 'excellent_contribution', label: '⭐ Excellent', color: '#51cf66' },
    { category: 'helping_others', label: '🤝 Helpful', color: '#69db7c' },
    { category: 'good_effort', label: '💪 Good Effort', color: '#8ce99a' },
    { category: 'participation', label: '🙋 Participation', color: '#b2f2bb' },
  ],
  neutral: [
    { category: 'note', label: '📋 Note', color: '#74c0fc' },
    { category: 'absence', label: '❌ Absent', color: '#a5b4fc' },
  ]
};

function App() {
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showLogs, setShowLogs] = useState(false);
  const [viewMode, setViewMode] = useState<'logger' | 'agents'>('logger'); // New: view mode switcher
  const [deviceMode, setDeviceMode] = useState<'mobile' | 'tablet' | 'desktop'>('mobile'); // Device layout mode

  // Load students on component mount
  useEffect(() => {
    fetchStudents();
    
    // Load saved logs from localStorage
    const savedLogs = localStorage.getItem('quick-logs');
    if (savedLogs) {
      setLogs(JSON.parse(savedLogs));
    }
    
    // Load saved device mode preference
    const savedDeviceMode = localStorage.getItem('device-mode');
    if (savedDeviceMode && ['mobile', 'tablet', 'desktop'].includes(savedDeviceMode)) {
      setDeviceMode(savedDeviceMode as 'mobile' | 'tablet' | 'desktop');
    }

    // Listen for online/offline
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Sync logs when coming online
  useEffect(() => {
    if (isOnline) {
      syncPendingLogs();
    }
  }, [isOnline]);

  const fetchStudents = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/students/');
      if (response.ok) {
        const data = await response.json();
        setStudents(data);
      }
    } catch (error) {
      console.error('Failed to fetch students:', error);
    }
  };

  const addLog = async (logType: 'positive' | 'negative' | 'neutral', category: string) => {
    if (!selectedStudent) return;

    const logEntry: LogEntry = {
      id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      student_id: selectedStudent.id,
      student_name: selectedStudent.name,
      log_type: logType,
      category,
      timestamp: new Date().toISOString(),
      synced: false
    };

    // Add to local state
    const newLogs = [logEntry, ...logs];
    setLogs(newLogs);
    
    // Save to localStorage
    localStorage.setItem('quick-logs', JSON.stringify(newLogs));

    // Try to sync immediately if online
    if (isOnline) {
      try {
        const response = await fetch(`http://localhost:8001/api/students/${selectedStudent.id}/logs`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            class_code: selectedStudent.class_code,
            log_type: logType,
            category,
            note: '',
            points: 0
          }),
        });

        if (response.ok) {
          // Mark as synced
          logEntry.synced = true;
          const updatedLogs = newLogs.map(log => 
            log.id === logEntry.id ? { ...log, synced: true } : log
          );
          setLogs(updatedLogs);
          localStorage.setItem('quick-logs', JSON.stringify(updatedLogs));
        }
      } catch (error) {
        console.error('Failed to sync log:', error);
      }
    }

    // Show brief feedback
    const behavior = [...BEHAVIORS.negative, ...BEHAVIORS.positive, ...BEHAVIORS.neutral]
      .find(b => b.category === category);
    
    if (behavior) {
      // Create temporary feedback
      const feedback = document.createElement('div');
      feedback.textContent = `✓ Logged: ${behavior.label}`;
      feedback.style.cssText = `
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: ${behavior.color}; color: white; padding: 12px 24px;
        border-radius: 8px; font-weight: bold; z-index: 1000;
        animation: fadeOut 1.5s ease-in-out forwards;
      `;
      document.body.appendChild(feedback);
      setTimeout(() => feedback.remove(), 1500);
    }
  };

  const syncPendingLogs = async () => {
    const unsyncedLogs = logs.filter(log => !log.synced);
    
    for (const log of unsyncedLogs) {
      try {
        const response = await fetch(`http://localhost:8001/api/students/${log.student_id}/logs`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            class_code: students.find(s => s.id === log.student_id)?.class_code || '',
            log_type: log.log_type,
            category: log.category,
            note: log.note || '',
            points: 0
          }),
        });

        if (response.ok) {
          // Mark as synced
          const updatedLogs = logs.map(l => 
            l.id === log.id ? { ...l, synced: true } : l
          );
          setLogs(updatedLogs);
          localStorage.setItem('quick-logs', JSON.stringify(updatedLogs));
        }
      } catch (error) {
        console.error('Failed to sync log:', error);
        break; // Stop syncing if there's an error
      }
    }
  };

  const filteredStudents = students.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.class_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderBehaviorButtons = (type: 'positive' | 'negative' | 'neutral') => (
    <div className="behavior-section">
      <h3 className={`behavior-title ${type}`}>
        {type === 'positive' ? '✅ Positive' : type === 'negative' ? '⚠️ Needs Attention' : '📝 Notes'}
      </h3>
      <div className="behavior-grid">
        {BEHAVIORS[type].map(behavior => (
          <button
            key={behavior.category}
            className="behavior-btn"
            style={{ backgroundColor: behavior.color }}
            onClick={() => addLog(type, behavior.category)}
          >
            {behavior.label}
          </button>
        ))}
      </div>
    </div>
  );

  // Save device mode preference when changed
  const handleDeviceModeChange = (mode: 'mobile' | 'tablet' | 'desktop') => {
    setDeviceMode(mode);
    localStorage.setItem('device-mode', mode);
  };

  return (
    <div className={`quick-logger ${deviceMode}`}>
      {/* Header */}
      <header className="logger-header">
        <h1>🏫 PTCC</h1>
        
        {/* Device Mode Toggle - Full Width */}
        <div className="device-switcher">
          <button
            className={`device-btn ${deviceMode === 'mobile' ? 'active' : ''}`}
            onClick={() => handleDeviceModeChange('mobile')}
            title="Mobile view (375px)"
          >
            📱 Mobile
          </button>
          <button
            className={`device-btn ${deviceMode === 'tablet' ? 'active' : ''}`}
            onClick={() => handleDeviceModeChange('tablet')}
            title="Tablet view (1024px)"
          >
            📱 Tablet
          </button>
          <button
            className={`device-btn ${deviceMode === 'desktop' ? 'active' : ''}`}
            onClick={() => handleDeviceModeChange('desktop')}
            title="Desktop view (responsive)"
          >
            🖥️ Desktop
          </button>
        </div>
        
        {/* Width Indicator */}
        <div className="width-indicator">
          {deviceMode === 'mobile' && 'Mobile view (375px)'}
          {deviceMode === 'tablet' && 'Tablet view (1024px)'}
          {deviceMode === 'desktop' && 'Desktop view (responsive)'}
        </div>
        
        <div className="status-bar">
          {/* View Mode Switcher */}
          <div className="view-switcher">
            <button
              className={`view-btn ${viewMode === 'logger' ? 'active' : ''}`}
              onClick={() => setViewMode('logger')}
              title="Quick logging mode"
            >
              📝 Logger
            </button>
            <button
              className={`view-btn ${viewMode === 'agents' ? 'active' : ''}`}
              onClick={() => setViewMode('agents')}
              title="AI agents analysis"
            >
              🤖 Agents
            </button>
          </div>
          <span className={`connection-status ${isOnline ? 'online' : 'offline'}`}>
            {isOnline ? '🟢' : '🔴'}
          </span>
          {viewMode === 'logger' && (
            <button 
              className="logs-btn"
              onClick={() => setShowLogs(!showLogs)}
            >
              📋 ({logs.length})
            </button>
          )}
        </div>
      </header>

      {viewMode === 'agents' ? (
        // Agents Analysis View
        <main className="logger-content">
          {!selectedStudent ? (
            // Class/Student selection for Agents
            <div className="student-selection">
              <h2>📊 Select Student for Analysis</h2>
              <div className="search-box">
                <input
                  type="text"
                  placeholder="🔍 Search by name or class..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="students-grid">
                {filteredStudents.slice(0, 20).map(student => (
                  <button
                    key={student.id}
                    className="student-btn agents-student-btn"
                    onClick={() => setSelectedStudent(student)}
                  >
                    <div className="student-name">{student.name}</div>
                    <div className="student-class">{student.class_code}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // Agent Analysis Display
            <div>
              <button 
                className="change-student"
                onClick={() => setSelectedStudent(null)}
              >
                ← Back to Student Selection
              </button>
              <AgentAnalysis studentId={selectedStudent.id} classCode={selectedStudent.class_code} />
            </div>
          )}
        </main>
      ) : showLogs ? (
        // Logs view
        <div className="logs-view">
          <div className="logs-header">
            <h2>Recent Logs</h2>
            <button onClick={() => setShowLogs(false)}>✕ Close</button>
          </div>
          <div className="logs-list">
            {logs.map(log => (
              <div key={log.id} className={`log-entry ${log.log_type}`}>
                <div className="log-main">
                  <span className="log-student">{log.student_name}</span>
                  <span className="log-category">{log.category.replace('_', ' ')}</span>
                  <span className={`sync-status ${log.synced ? 'synced' : 'pending'}`}>
                    {log.synced ? '✓' : '⏳'}
                  </span>
                </div>
                <div className="log-time">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        // Main logging interface
        <main className="logger-content">
          {!selectedStudent ? (
            // Student selection
            <div className="student-selection">
              <h2>Select Student</h2>
              <div className="search-box">
                <input
                  type="text"
                  placeholder="🔍 Search students..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="students-grid">
                {filteredStudents.slice(0, 20).map(student => (
                  <button
                    key={student.id}
                    className="student-btn"
                    onClick={() => setSelectedStudent(student)}
                  >
                    <div className="student-name">{student.name}</div>
                    <div className="student-class">{student.class_code}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // Behavior logging
            <div className="behavior-logging">
              <div className="selected-student">
                <h2>{selectedStudent.name}</h2>
                <span className="student-details">{selectedStudent.class_code} • Year {selectedStudent.year_group}</span>
                <button 
                  className="change-student"
                  onClick={() => setSelectedStudent(null)}
                >
                  🔄 Change Student
                </button>
              </div>

              <div className="behaviors-container">
                {renderBehaviorButtons('negative')}
                {renderBehaviorButtons('positive')}
                {renderBehaviorButtons('neutral')}
              </div>
            </div>
          )}
        </main>
      )}
    </div>
  );
}

// Add CSS animation for feedback
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeOut {
    0% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    70% { opacity: 1; transform: translate(-50%, -50%) scale(1.05); }
    100% { opacity: 0; transform: translate(-50%, -50%) scale(0.95); }
  }
`;
document.head.appendChild(style);

export default App;
