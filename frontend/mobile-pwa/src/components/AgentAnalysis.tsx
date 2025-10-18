import React, { useState } from 'react';
import type { AgentAnalysis as AgentAnalysisType } from '../services/agentsApi';
import { useStudentAnalysis } from '../services/agentsApi';
import './AgentAnalysis.css';

interface AgentAnalysisProps {
  studentId: number | null;
  classCode?: string;
}

const AgentAnalysis: React.FC<AgentAnalysisProps> = ({ studentId, classCode }) => {
  const { data, loading, error } = useStudentAnalysis(studentId, classCode);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  if (!studentId) {
    return (
      <div className="agent-analysis-container empty">
        <div className="empty-state">
          <div className="empty-icon">🤖</div>
          <p>Select a student to view agent analysis</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="agent-analysis-container loading">
        <div className="loading-state">
          <div className="spinner" />
          <p>Analyzing student context...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="agent-analysis-container error">
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <p className="error-message">{error}</p>
          <p className="error-hint">Make sure the backend API is running on http://localhost:8001</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="agent-analysis-container">
      {/* Header Section */}
      <div className="analysis-header">
        <div className="header-info">
          <h2>🎓 Student Analysis</h2>
          <div className="student-info">
            <span className="student-name">{data.student_name}</span>
            <span className="class-badge">{data.class_code}</span>
            <span className="timestamp">{new Date(data.timestamp).toLocaleTimeString()}</span>
          </div>
        </div>
        {data.high_priority_count > 0 && (
          <div className="alert-badge">
            <span className="alert-count">{data.high_priority_count}</span>
            <span className="alert-label">High Priority</span>
          </div>
        )}
      </div>

      {/* Agents Grid - Desktop optimized */}
      <div className="agents-grid">
        {/* Period Briefing Agent */}
        {data.agents.period_briefing && (
          <AgentCard
            agent={data.agents.period_briefing}
            isExpanded={expandedAgent === 'period_briefing'}
            onToggle={() =>
              setExpandedAgent(
                expandedAgent === 'period_briefing' ? null : 'period_briefing'
              )
            }
          />
        )}

        {/* CCA Engagement Agent */}
        {data.agents.cca_engagement && (
          <AgentCard
            agent={data.agents.cca_engagement}
            isExpanded={expandedAgent === 'cca_engagement'}
            onToggle={() =>
              setExpandedAgent(
                expandedAgent === 'cca_engagement' ? null : 'cca_engagement'
              )
            }
          />
        )}

        {/* Accommodation Compliance Agent */}
        {data.agents.accommodation_compliance && (
          <AgentCard
            agent={data.agents.accommodation_compliance}
            isExpanded={expandedAgent === 'accommodation_compliance'}
            onToggle={() =>
              setExpandedAgent(
                expandedAgent === 'accommodation_compliance' ? null : 'accommodation_compliance'
              )
            }
          />
        )}
      </div>
    </div>
  );
};

interface AgentCardProps {
  agent: AgentAnalysisType;
  isExpanded: boolean;
  onToggle: () => void;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, isExpanded, onToggle }) => {
  const priorityConfig = {
    critical: { color: '#ff4444', label: '🔴 Critical', bg: '#fff5f5' },
    high: { color: '#ff8800', label: '🟠 High', bg: '#fff8f0' },
    medium: { color: '#ffcc00', label: '🟡 Medium', bg: '#fffbf0' },
    low: { color: '#44aa44', label: '🟢 Low', bg: '#f5fff5' },
  };

  // Teacher-friendly titles and descriptions
  const getTitleAndDescription = (originalTitle: string) => {
    switch (originalTitle) {
      case 'Period Briefing':
        return { title: 'Class Summary', description: 'Recent updates and notes' };
      case 'Accommodation Compliance':
        return { title: 'Learning Support', description: 'Accommodations and requirements' };
      default:
        return { title: originalTitle, description: null };
    }
  };

  const { title, description } = getTitleAndDescription(agent.title);
  const config = priorityConfig[agent.priority];

  return (
    <div
      className={`agent-card priority-${agent.priority} ${isExpanded ? 'expanded' : ''}`}
      style={{ borderLeftColor: config.color, backgroundColor: isExpanded ? config.bg : 'white' }}
    >
      {/* Card Header - Always Visible */}
      <div className="card-header" onClick={onToggle}>
        <div className="header-content">
          <h3 className="agent-title">{title}</h3>
          {description && <p className="agent-description">{description}</p>}
          <div className="agent-badges">
            <span className="priority-badge" style={{ backgroundColor: config.color }}>
              {config.label}
            </span>
            <span className="type-badge">{agent.intervention_type}</span>
            {agent.action_required && <span className="action-badge">⚡ Action</span>}
          </div>
        </div>
        <button className="toggle-btn" aria-expanded={isExpanded}>
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {/* Card Body - Expandable */}
      {isExpanded && (
        <div className="card-body">
          {/* Recommended Actions */}
          <section className="actions-section">
            <h4>📋 Recommended Actions</h4>
            <ul className="actions-list">
              {agent.recommended_actions.map((action, idx) => (
                <li key={idx}>
                  <span className="checkmark">✓</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Reasoning */}
          <section className="reasoning-section">
            <h4>💭 Analysis Reasoning</h4>
            <p className="reasoning-text">{agent.reasoning}</p>
          </section>
        </div>
      )}
    </div>
  );
};

export default AgentAnalysis;
