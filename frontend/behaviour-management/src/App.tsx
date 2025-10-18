import { useState, useEffect } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

// Types
interface Student {
  id: number;
  name: string;
  class_code: string;
  current_strikes: number;
  positive_count: number;
  total_house_points: number;
  recent_logs: LessonLog[];
}

interface LessonLog {
  id: number;
  student_id: number;
  student_name: string;
  log_type: 'strike' | 'positive' | 'admin_flag';
  description: string;
  timestamp: string;
  points_awarded?: number;
}

interface LessonSession {
  session_id: string;
  class_code: string;
  student_count: number;
  start_time: string;
  students: Student[];
  total_strikes: number;
  total_positive: number;
  total_house_points: number;
}

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('behaviour-management')
  const [lessonActive, setLessonActive] = useState(false);
  const [selectedClass, setSelectedClass] = useState('3A');
  const [lessonSession, setLessonSession] = useState<LessonSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  
  const availableClasses = ['3A', '4B', '5C', '6A'];
  
  // Auto-refresh lesson data when active
  useEffect(() => {
    if (lessonActive && lessonSession) {
      const interval = setInterval(() => {
        fetchLessonData(lessonSession.session_id, lessonSession.class_code);
      }, 5000); // Refresh every 5 seconds
      setRefreshInterval(interval);
      return () => clearInterval(interval);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }
  }, [lessonActive, lessonSession]);
  
  const startLesson = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/behavior-management/lesson/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_code: selectedClass })
      });
      
      if (response.ok) {
        const data = await response.json();
        setLessonActive(true);
        fetchLessonData(data.session_id, data.class_code);
      }
    } catch (error) {
      console.error('Failed to start lesson:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const endLesson = async () => {
    if (!lessonSession) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/behavior-management/lesson/end', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: lessonSession.session_id })
      });
      
      if (response.ok) {
        setLessonActive(false);
        setLessonSession(null);
        if (refreshInterval) {
          clearInterval(refreshInterval);
          setRefreshInterval(null);
        }
      }
    } catch (error) {
      console.error('Failed to end lesson:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchLessonData = async (sessionId: string, classCode: string) => {
    try {
      const response = await fetch(`/api/behavior-management/lesson/current?session_id=${sessionId}&class_code=${classCode}`);
      if (response.ok) {
        const data: LessonSession = await response.json();
        setLessonSession(data);
      }
    } catch (error) {
      console.error('Failed to fetch lesson data:', error);
    }
  };
  
  const logBehavior = async (studentId: number, logType: 'strike' | 'positive' | 'admin_flag', description: string, points?: number) => {
    if (!lessonSession) return;
    
    try {
      const response = await fetch('/api/behavior-management/lesson/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: lessonSession.session_id,
          student_id: studentId,
          log_type: logType,
          description,
          points_awarded: points || 0
        })
      });
      
      if (response.ok) {
        // Refresh lesson data
        fetchLessonData(lessonSession.session_id, lessonSession.class_code);
      }
    } catch (error) {
      console.error('Failed to log behavior:', error);
    }
  };
  
  const getStrikeColor = (strikes: number) => {
    if (strikes >= 3) return 'text-red-600 bg-red-50';
    if (strikes >= 2) return 'text-yellow-600 bg-yellow-50';
    if (strikes >= 1) return 'text-orange-600 bg-orange-50';
    return 'text-green-600 bg-green-50';
  };
  
  const getStrikeIcon = (strikes: number) => {
    if (strikes >= 3) return '🚫';
    if (strikes >= 2) return '⚠️⚠️';
    if (strikes >= 1) return '⚠️';
    return '🟢';
  };
  
  return (
    <div className={`app ${deviceMode}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="app-header mb-8">
          <div className="header-content">
            <div className="title-section">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">💻 Behaviour Management</h1>
              <p className="text-gray-600">Real-time behavior tracking with automatic consequences for ICT lessons</p>
            </div>
            <DeviceToggleComponent />
          </div>
        </header>
        
        {!lessonActive ? (
          /* Lesson Start Interface */
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-semibold mb-6">🎬 Start a New Lesson</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Class</label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="w-full"
                >
                  {availableClasses.map(cls => (
                    <option key={cls} value={cls}>{cls}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={startLesson}
                  disabled={isLoading}
                  className="btn-primary w-full"
                >
                  {isLoading ? '⏳ Starting...' : '▶️ Start Lesson'}
                </button>
              </div>
            </div>
            
            {/* Information Panel */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">ℹ️ How it Works</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-red-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-red-800 mb-2">Strike System</h4>
                  <ul className="text-sm text-red-700 space-y-1">
                    <li>⚠️ <strong>Strike 1:</strong> Verbal Warning</li>
                    <li>⚠️⚠️ <strong>Strike 2:</strong> Final Warning</li>
                    <li>🚫 <strong>Strike 3:</strong> Device Time-out</li>
                  </ul>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">Positive Behavior</h4>
                  <ul className="text-sm text-green-700 space-y-1">
                    <li>• Award house points</li>
                    <li>• Track excellence</li>
                    <li>• Build positive culture</li>
                  </ul>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">Admin Actions</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Flag admin notification</li>
                    <li>• Mark HOD consultation</li>
                    <li>• Schedule parent meetings</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Active Lesson Interface */
          <div>
            {/* Lesson Header */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-semibold text-green-600 mb-2">
                    🟢 ACTIVE LESSON - Class {lessonSession?.class_code}
                  </h2>
                  <p className="text-gray-600">Session: {lessonSession?.session_id}</p>
                </div>
                
                <div className="flex gap-3">
                  <button
                    onClick={() => lessonSession && fetchLessonData(lessonSession.session_id, lessonSession.class_code)}
                    className="btn-secondary btn-sm"
                  >
                    🔄 Refresh
                  </button>
                  <button
                    onClick={endLesson}
                    disabled={isLoading}
                    className="btn-danger btn-sm"
                  >
                    {isLoading ? '⏳ Ending...' : '⏹️ End Lesson'}
                  </button>
                </div>
              </div>
              
              {/* Summary Metrics */}
              {lessonSession && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Total Students</div>
                    <div className="font-semibold text-lg">{lessonSession.student_count}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Total Strikes</div>
                    <div className="font-semibold text-lg text-red-600">{lessonSession.total_strikes || 0}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-500">Positive Logs</div>
                    <div className="font-semibold text-lg text-green-600">{lessonSession.total_positive || 0}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-500">House Points</div>
                    <div className="font-semibold text-lg text-blue-600">{lessonSession.total_house_points || 0}</div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Student List */}
            {lessonSession && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4">Students ({lessonSession.students.length})</h3>
                
                <div className="space-y-3">
                  {lessonSession.students.map((student) => (
                    <div key={student.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          <h4 className="font-semibold text-lg">{student.name}</h4>
                          <span className={`px-2 py-1 rounded text-sm ${getStrikeColor(student.current_strikes)}`}>
                            {getStrikeIcon(student.current_strikes)} {student.current_strikes} strikes
                          </span>
                          {student.positive_count > 0 && (
                            <span className="px-2 py-1 rounded text-sm bg-green-100 text-green-800">
                              🎆 {student.positive_count} positive
                            </span>
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-500">
                          🏠 {student.total_house_points} points
                        </div>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex gap-2 mb-3">
                        <button
                          onClick={() => logBehavior(student.id, 'strike', 'Disruptive behavior')}
                          disabled={student.current_strikes >= 3}
                          className="btn-danger btn-sm"
                        >
                          ⚠️ Strike
                        </button>
                        <button
                          onClick={() => logBehavior(student.id, 'positive', 'Excellent work', 5)}
                          className="btn-success btn-sm"
                        >
                          ⭐ Positive (+5)
                        </button>
                        <button
                          onClick={() => logBehavior(student.id, 'admin_flag', 'Requires admin attention')}
                          className="btn-secondary btn-sm"
                        >
                          🚩 Flag Admin
                        </button>
                      </div>
                      
                      {/* Recent Logs */}
                      {student.recent_logs && student.recent_logs.length > 0 && (
                        <div className="border-t pt-2">
                          <div className="text-sm text-gray-600">
                            <strong>Recent activity:</strong>
                            <div className="mt-1 space-y-1">
                              {student.recent_logs.slice(0, 3).map((log, index) => (
                                <div key={index} className="flex justify-between text-xs">
                                  <span>
                                    {log.log_type === 'strike' ? '⚠️' : log.log_type === 'positive' ? '⭐' : '🚩'} 
                                    {log.description}
                                  </span>
                                  <span className="text-gray-500">
                                    {new Date(log.timestamp).toLocaleTimeString()}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
