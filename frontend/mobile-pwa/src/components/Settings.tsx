import React, { useState, useEffect } from 'react';
import useNotifications from '../hooks/useNotifications';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost:8000',
    autoSync: true,
    syncInterval: 30,
    maxOfflineLogs: 100,
    notifications: true,
  });

  const [connectionStatus, setConnectionStatus] = useState<'online' | 'offline' | 'checking'>('checking');

  const {
    isSupported: notificationsSupported,
    permission: notificationPermission,
    settings: notificationSettings,
    requestPermission,
    sendNotification,
    updateSettings: updateNotificationSettings,
  } = useNotifications();

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('ptccSettings');
    if (savedSettings) {
      setSettings({ ...settings, ...JSON.parse(savedSettings) });
    }

    // Check connection status
    checkConnection();
  }, []);

  const checkConnection = async () => {
    setConnectionStatus('checking');
    try {
      const response = await fetch(`${settings.apiUrl}/health`, { method: 'GET' });
      setConnectionStatus(response.ok ? 'online' : 'offline');
    } catch (error) {
      setConnectionStatus('offline');
    }
  };

  const saveSettings = () => {
    localStorage.setItem('ptccSettings', JSON.stringify(settings));
    alert('Settings saved!');
  };

  const clearOfflineData = () => {
    if (confirm('Are you sure you want to clear all offline logs? This cannot be undone.')) {
      localStorage.removeItem('offlineLogs');
      alert('Offline data cleared!');
    }
  };

  const exportData = () => {
    const offlineLogs = localStorage.getItem('offlineLogs');
    const settings = localStorage.getItem('ptccSettings');

    const exportData = {
      settings,
      offlineLogs,
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ptcc-mobile-backup-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="settings">
      <h2>⚙️ Settings</h2>

      {/* Connection Status */}
      <div className="settings-section">
        <h3>Connection Status</h3>
        <div className={`status-indicator ${connectionStatus}`}>
          <span className="status-dot"></span>
          <span className="status-text">
            {connectionStatus === 'online' && '🟢 Connected to PTCC Backend'}
            {connectionStatus === 'offline' && '🔴 Cannot connect to backend'}
            {connectionStatus === 'checking' && '🟡 Checking connection...'}
          </span>
        </div>
        <button onClick={checkConnection} className="check-button">
          🔄 Check Connection
        </button>
      </div>

      {/* API Configuration */}
      <div className="settings-section">
        <h3>API Configuration</h3>
        <div className="form-group">
          <label>Backend URL</label>
          <input
            type="url"
            value={settings.apiUrl}
            onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
            placeholder="http://localhost:8001"
          />
        </div>
      </div>

      {/* Sync Settings */}
      <div className="settings-section">
        <h3>Sync Settings</h3>
        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={settings.autoSync}
              onChange={(e) => setSettings({ ...settings, autoSync: e.target.checked })}
            />
            Auto-sync when online
          </label>
        </div>
        <div className="form-group">
          <label>Sync Interval (seconds)</label>
          <input
            type="number"
            min="10"
            max="300"
            value={settings.syncInterval}
            onChange={(e) => setSettings({ ...settings, syncInterval: parseInt(e.target.value) })}
          />
        </div>
        <div className="form-group">
          <label>Max Offline Logs</label>
          <input
            type="number"
            min="50"
            max="1000"
            value={settings.maxOfflineLogs}
            onChange={(e) => setSettings({ ...settings, maxOfflineLogs: parseInt(e.target.value) })}
          />
        </div>
      </div>

      {/* Notifications */}
      <div className="settings-section">
        <h3>🔔 Notifications</h3>

        {!notificationsSupported ? (
          <div className="notification-status">
            <p>❌ Notifications not supported in this browser</p>
          </div>
        ) : (
          <>
            <div className="notification-status">
              <p>
                Status: <strong>
                  {notificationPermission === 'granted' && '✅ Granted'}
                  {notificationPermission === 'denied' && '❌ Denied'}
                  {notificationPermission === 'default' && '⏳ Not requested'}
                </strong>
              </p>
            </div>

            {notificationPermission !== 'granted' && (
              <button onClick={requestPermission} className="notification-button">
                🔕 Request Permission
              </button>
            )}

            {notificationPermission === 'granted' && (
              <>
                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={notificationSettings.enabled}
                      onChange={(e) => updateNotificationSettings({ enabled: e.target.checked })}
                    />
                    Enable notifications
                  </label>
                </div>

                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={notificationSettings.reminders}
                      onChange={(e) => updateNotificationSettings({ reminders: e.target.checked })}
                    />
                    Reminder notifications
                  </label>
                </div>

                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={notificationSettings.logs}
                      onChange={(e) => updateNotificationSettings({ logs: e.target.checked })}
                    />
                    Log confirmation notifications
                  </label>
                </div>

                <button
                  onClick={() => sendNotification('PTCC Test', { body: 'Notifications working!' })}
                  className="notification-button"
                >
                  🧪 Test Notification
                </button>
              </>
            )}
          </>
        )}
      </div>

      {/* Data Management */}
      <div className="settings-section">
        <h3>Data Management</h3>
        <button onClick={exportData} className="export-button">
          📤 Export Data
        </button>
        <button onClick={clearOfflineData} className="clear-button">
          🗑️ Clear Offline Data
        </button>
      </div>

      {/* Action Buttons */}
      <div className="settings-actions">
        <button onClick={saveSettings} className="save-button">
          💾 Save Settings
        </button>
      </div>

      {/* App Info */}
      <div className="settings-section">
        <h3>About</h3>
        <p><strong>PTCC Mobile</strong></p>
        <p>Version 1.0.0</p>
        <p>Personal Teaching Command Center</p>
      </div>
    </div>
  );
};

export default Settings;