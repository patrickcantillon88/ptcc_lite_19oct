import React, { useState, useEffect } from 'react';

interface LogEntry {
  id: number;
  student_id: number;
  student_name: string;
  log_type: string;
  category: string;
  note: string;
  timestamp: string;
  synced: boolean;
}

const LogsList: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    setError(null);

    try {
      // Try to load from API first
      const response = await fetch('/api/logs/recent');
      if (response.ok) {
        const apiLogs = await response.json();
        setLogs(apiLogs);
      } else {
        // If API fails, load from localStorage
        loadOfflineLogs();
      }
    } catch (err) {
      // Load offline logs if no connection
      loadOfflineLogs();
    } finally {
      setLoading(false);
    }
  };

  const loadOfflineLogs = () => {
    const offlineLogs = JSON.parse(localStorage.getItem('offlineLogs') || '[]');
    setLogs(offlineLogs.map((log: any, index: number) => ({
      id: Date.now() + index,
      student_id: log.student_id,
      student_name: 'Unknown Student',
      log_type: log.log_type,
      category: log.category,
      note: log.note,
      timestamp: log.timestamp,
      synced: false,
    })));
  };

  const syncOfflineLogs = async () => {
    const offlineLogs = JSON.parse(localStorage.getItem('offlineLogs') || '[]');

    if (offlineLogs.length === 0) return;

    try {
      for (const log of offlineLogs) {
        await fetch('/api/logs/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(log),
        });
      }

      // Clear offline logs after successful sync
      localStorage.removeItem('offlineLogs');
      loadLogs(); // Reload to show synced logs
    } catch (error) {
      setError('Failed to sync offline logs');
    }
  };

  const getLogIcon = (logType: string) => {
    switch (logType) {
      case 'behavior': return '📋';
      case 'performance': return '⭐';
      case 'attendance': return '✅';
      case 'note': return '📝';
      default: return '📝';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="logs-list">
        <div className="loading">
          <p>Loading recent logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="logs-list">
      <div className="logs-header">
        <h2>📋 Recent Logs</h2>
        <button onClick={loadLogs} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {error && (
        <div className="error">
          <p>{error}</p>
        </div>
      )}

      {logs.length === 0 ? (
        <div className="empty-state">
          <p>No recent logs</p>
        </div>
      ) : (
        <div className="logs-container">
          {logs.map((log) => (
            <div key={log.id} className={`log-entry ${log.synced ? 'synced' : 'offline'}`}>
              <div className="log-header">
                <div className="log-meta">
                  <span className="log-icon">{getLogIcon(log.log_type)}</span>
                  <span className="log-type">{log.log_type}</span>
                  <span className="log-category">{log.category}</span>
                  {!log.synced && <span className="offline-badge">Offline</span>}
                </div>
                <div className="log-time">
                  {formatTimestamp(log.timestamp)}
                </div>
              </div>

              <div className="log-student">
                <strong>{log.student_name}</strong>
              </div>

              <div className="log-note">
                {log.note}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Offline sync section */}
      {JSON.parse(localStorage.getItem('offlineLogs') || '[]').length > 0 && (
        <div className="offline-sync">
          <p>You have {JSON.parse(localStorage.getItem('offlineLogs') || '[]').length} offline logs</p>
          <button onClick={syncOfflineLogs} className="sync-button">
            🔄 Sync Now
          </button>
        </div>
      )}
    </div>
  );
};

export default LogsList;