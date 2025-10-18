import { useState, useEffect } from 'react'
import './DeviceToggle.css'

/**
 * Reusable Device Mode Toggle Component
 * Manages device mode state (mobile/tablet/desktop) with localStorage persistence
 * 
 * @param {string} appName - Unique app identifier for localStorage key
 * @param {function} onDeviceModeChange - Callback when device mode changes
 * @returns {object} - { deviceMode, DeviceToggleComponent }
 */
export function useDeviceMode(appName) {
  const [deviceMode, setDeviceMode] = useState('desktop')

  // Load saved device mode on mount
  useEffect(() => {
    const savedMode = localStorage.getItem(`device-mode-${appName}`)
    if (savedMode && ['mobile', 'tablet', 'desktop'].includes(savedMode)) {
      setDeviceMode(savedMode)
    }
  }, [appName])

  const toggleDeviceMode = (mode) => {
    setDeviceMode(mode)
    localStorage.setItem(`device-mode-${appName}`, mode)
  }

  const DeviceToggleComponent = () => (
    <div className="device-mode-toggles">
      <button 
        className={`mode-btn ${deviceMode === 'mobile' ? 'active' : ''}`}
        onClick={() => toggleDeviceMode('mobile')}
        title="Mobile View (375px)"
      >
        📱
      </button>
      <button 
        className={`mode-btn ${deviceMode === 'tablet' ? 'active' : ''}`}
        onClick={() => toggleDeviceMode('tablet')}
        title="Tablet View (1024px)"
      >
        📊
      </button>
      <button 
        className={`mode-btn ${deviceMode === 'desktop' ? 'active' : ''}`}
        onClick={() => toggleDeviceMode('desktop')}
        title="Desktop View (Full Width)"
      >
        💻
      </button>
    </div>
  )

  return { deviceMode, DeviceToggleComponent }
}