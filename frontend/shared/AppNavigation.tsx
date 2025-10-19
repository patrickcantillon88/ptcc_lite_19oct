import React from 'react';
import './AppNavigation.css';

interface AppNavigationProps {
  appName: string;
  appIcon: string;
  appDescription?: string;
}

const AppNavigation: React.FC<AppNavigationProps> = ({ 
  appName, 
  appIcon, 
  appDescription 
}) => {
  const dashboardUrl = 'http://localhost:8501?skip_onboarding=true';
  
  const handleBackToDashboard = () => {
    // Check if user has completed onboarding before
    const onboardingComplete = localStorage.getItem('ptcc_onboarding_complete');
    const finalUrl = onboardingComplete === 'true' ? dashboardUrl : 'http://localhost:8501';
    window.location.href = finalUrl;
  };

  const appLinks = [
    { name: 'Dashboard', icon: '🏫', url: 'http://localhost:8501', active: false },
    { name: 'Mobile PWA', icon: '📱', url: 'http://localhost:5173', active: false },
    { name: 'Digital Citizenship', icon: '🛡️', url: 'http://localhost:5174', active: false },
    { name: 'Classroom Tools', icon: '🛠️', url: 'http://localhost:5175', active: false },
    { name: 'CCA Comments', icon: '🎵', url: 'http://localhost:5176', active: appName === 'CCA Comments' },
    { name: 'Behaviour Management', icon: '📊', url: 'http://localhost:5177', active: appName === 'Behaviour Management' },
    { name: 'Intervention Priority', icon: '🚨', url: 'http://localhost:5178', active: appName === 'Intervention Priority' },
    { name: 'Progress Dashboard', icon: '📈', url: 'http://localhost:5179', active: appName === 'Progress Dashboard' },
    { name: 'Seating Chart', icon: '🪑', url: 'http://localhost:5180', active: appName === 'Seating Chart' },
    { name: 'Group Formation', icon: '👥', url: 'http://localhost:5181', active: appName === 'Group Formation' },
    { name: 'Differentiation', icon: '🎯', url: 'http://localhost:5182', active: appName === 'Differentiation' },
    { name: 'Quiz Upload', icon: '📤', url: 'http://localhost:5183', active: appName === 'Quiz Upload' },
    { name: 'Performance Trends', icon: '📈', url: 'http://localhost:5184', active: appName === 'Performance Trends' },
    { name: 'Progress Levels', icon: '📊', url: 'http://localhost:5185', active: appName === 'Progress Levels' },
    { name: 'At-Risk Students', icon: '⚠️', url: 'http://localhost:5186', active: appName === 'At-Risk Students' },
    { name: 'Assessment Overview', icon: '📊', url: 'http://localhost:5187', active: appName === 'Assessment Overview' },
  ];

  return (
    <nav className="ptcc-app-nav">
      {/* Top bar with back button and current app */}
      <div className="nav-top-bar">
        <div className="nav-left">
          <button 
            onClick={handleBackToDashboard}
            className="back-button"
            title="Return to PTCC Dashboard"
          >
            ← Dashboard
          </button>
          <div className="current-app">
            <span className="app-icon">{appIcon}</span>
            <div className="app-info">
              <h1 className="app-name">{appName}</h1>
              {appDescription && (
                <p className="app-description">{appDescription}</p>
              )}
            </div>
          </div>
        </div>
        
        <div className="nav-right">
          <div className="ptcc-brand">
            <span className="brand-icon">🏫</span>
            <span className="brand-text">PTCC</span>
          </div>
        </div>
      </div>

      {/* Navigation links (collapsible) */}
      <details className="nav-links-section">
        <summary className="nav-toggle">
          📋 All Apps ({appLinks.length})
        </summary>
        <div className="nav-links-grid">
          {appLinks.map((link) => (
            <a
              key={link.name}
              href={link.url}
              className={`nav-link ${link.active ? 'active' : ''}`}
              title={`Open ${link.name}`}
            >
              <span className="link-icon">{link.icon}</span>
              <span className="link-text">{link.name}</span>
            </a>
          ))}
        </div>
      </details>
    </nav>
  );
};

export default AppNavigation;