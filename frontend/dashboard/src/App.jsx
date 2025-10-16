import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8001';

function App() {
  const [view, setView] = useState('agents'); // agents, workflows, tasks, stats
  const [agents, setAgents] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch data on mount
  useEffect(() => {
    fetchAgents();
    fetchWorkflows();
    fetchStats();
    fetchTasks();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/orchestration/agents`);
      const data = await response.json();
      setAgents(data);
    } catch (err) {
      setError('Failed to fetch agents');
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows/`);
      const data = await response.json();
      setWorkflows(data);
    } catch (err) {
      console.error('Failed to fetch workflows', err);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/orchestration/tasks/history?limit=10`);
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      console.error('Failed to fetch tasks', err);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/orchestration/stats/overview`);
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats', err);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🎓 PTCC Agent Dashboard</h1>
        <p>Personal Teaching Command Center - Agent Management</p>
      </header>

      <nav className="nav">
        <button 
          className={view === 'agents' ? 'active' : ''}
          onClick={() => setView('agents')}
        >
          Agents
        </button>
        <button 
          className={view === 'workflows' ? 'active' : ''}
          onClick={() => setView('workflows')}
        >
          Workflows
        </button>
        <button 
          className={view === 'tasks' ? 'active' : ''}
          onClick={() => setView('tasks')}
        >
          Task History
        </button>
        <button 
          className={view === 'stats' ? 'active' : ''}
          onClick={() => setView('stats')}
        >
          Statistics
        </button>
        <button 
          className={view === 'quickActions' ? 'active' : ''}
          onClick={() => setView('quickActions')}
        >
          Quick Actions
        </button>
      </nav>

      <main className="main">
        {error && <div className="error">{error}</div>}
        
        {view === 'agents' && <AgentsView agents={agents} />}
        {view === 'workflows' && <WorkflowsView workflows={workflows} />}
        {view === 'tasks' && <TasksView tasks={tasks} refresh={fetchTasks} />}
        {view === 'stats' && <StatsView stats={stats} />}
        {view === 'quickActions' && <QuickActionsView onTaskCreated={fetchTasks} />}
      </main>
    </div>
  );
}

// Agents View
function AgentsView({ agents }) {
  return (
    <div className="view">
      <h2>Registered Agents</h2>
      <div className="grid">
        {agents.map(agent => (
          <div key={agent.agent_id} className="card">
            <h3>{agent.name}</h3>
            <p className="agent-type">{agent.agent_type}</p>
            <div className="agent-meta">
              <span className={`status ${agent.is_active ? 'active' : 'inactive'}`}>
                {agent.is_active ? '● Active' : '○ Inactive'}
              </span>
              <span className="executions">{agent.total_executions || 0} executions</span>
            </div>
            <p className="agent-desc">{agent.description}</p>
            <div className="capabilities">
              {agent.capabilities?.slice(0, 3).map(cap => (
                <span key={cap} className="capability">{cap}</span>
              ))}
            </div>
            <div className="agent-stats">
              <div>Success: {agent.success_rate?.toFixed(1) || 0}%</div>
              <div>Avg: {agent.avg_execution_time_ms || 0}ms</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Workflows View
function WorkflowsView({ workflows }) {
  return (
    <div className="view">
      <h2>Available Workflows</h2>
      <div className="grid">
        {workflows.map(workflow => (
          <div key={workflow.workflow_id} className="card">
            <h3>{workflow.name}</h3>
            <p>{workflow.description}</p>
            <div className="workflow-meta">
              <span>{workflow.node_count} nodes</span>
              <span>v{workflow.version}</span>
            </div>
            <button className="btn-primary">Execute</button>
          </div>
        ))}
      </div>
    </div>
  );
}

// Tasks View
function TasksView({ tasks, refresh }) {
  return (
    <div className="view">
      <div className="view-header">
        <h2>Recent Tasks</h2>
        <button onClick={refresh} className="btn-secondary">↻ Refresh</button>
      </div>
      <div className="tasks-list">
        {tasks.map(task => (
          <div key={task.task_id} className="task-card">
            <div className="task-header">
              <h4>{task.task_type}</h4>
              <span className={`task-status ${task.status}`}>{task.status}</span>
            </div>
            <div className="task-meta">
              <span>Agent: {task.agent_id}</span>
              <span>Time: {task.execution_time_ms}ms</span>
              <span>Cost: ${task.cost_estimate?.toFixed(4) || 0}</span>
            </div>
            <div className="task-time">{new Date(task.created_at).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Stats View
function StatsView({ stats }) {
  if (!stats) return <div className="loading">Loading stats...</div>;

  return (
    <div className="view">
      <h2>System Statistics</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_tasks}</div>
          <div className="stat-label">Total Tasks</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.success_rate?.toFixed(1)}%</div>
          <div className="stat-label">Success Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.avg_execution_time_ms}ms</div>
          <div className="stat-label">Avg Execution Time</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">${stats.total_cost?.toFixed(2)}</div>
          <div className="stat-label">Total Cost</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.total_agents}</div>
          <div className="stat-label">Active Agents</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.failed_tasks || 0}</div>
          <div className="stat-label">Failed Tasks</div>
        </div>
      </div>
    </div>
  );
}

// Quick Actions View
function QuickActionsView({ onTaskCreated }) {
  const [formData, setFormData] = useState({
    action: 'lesson-plan',
    grade: '5th Grade',
    subject: 'Science',
    topic: '',
    duration: '45 minutes',
    studentName: 'Student',
    studentScores: JSON.stringify({ math: 85, reading: 88, science: 82 })
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      let endpoint, payload;
      
      if (formData.action === 'lesson-plan') {
        endpoint = '/api/orchestration/quick/lesson-plan';
        payload = {
          grade: formData.grade,
          subject: formData.subject,
          topic: formData.topic,
          duration: formData.duration,
          user_id: 'dashboard_user'
        };
      } else if (formData.action === 'assessment') {
        endpoint = '/api/orchestration/quick/assessment';
        payload = {
          grade: formData.grade,
          subject: formData.subject,
          topic: formData.topic,
          question_count: 5,
          user_id: 'dashboard_user'
        };
      } else if (formData.action === 'feedback') {
        endpoint = '/api/orchestration/quick/feedback';
        payload = {
          student_name: formData.studentName,
          grade: formData.grade,
          subject: formData.subject,
          scores: JSON.parse(formData.studentScores || '{}'),
          user_id: 'dashboard_user'
        };
      } else if (formData.action === 'differentiate') {
        endpoint = '/api/orchestration/quick/differentiate';
        payload = {
          grade: formData.grade,
          subject: formData.subject,
          topic: formData.topic,
          user_id: 'dashboard_user'
        };
      }

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      setResult(data);
      onTaskCreated();
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view">
      <h2>Quick Actions</h2>
      <div className="quick-actions">
        <form onSubmit={handleSubmit} className="action-form">
          <div className="form-group">
            <label>Action Type</label>
            <select 
              value={formData.action}
              onChange={(e) => setFormData({...formData, action: e.target.value})}
            >
              <option value="lesson-plan">📚 Generate Lesson Plan</option>
              <option value="assessment">📝 Generate Assessment</option>
              <option value="feedback">💬 Compose Feedback (NEW!)</option>
              <option value="differentiate">🎯 Differentiate Content (NEW!)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Grade Level</label>
            <input 
              type="text"
              value={formData.grade}
              onChange={(e) => setFormData({...formData, grade: e.target.value})}
              placeholder="e.g., 5th Grade"
            />
          </div>

          <div className="form-group">
            <label>Subject</label>
            <input 
              type="text"
              value={formData.subject}
              onChange={(e) => setFormData({...formData, subject: e.target.value})}
              placeholder="e.g., Science"
            />
          </div>

          <div className="form-group">
            <label>Topic</label>
            <input 
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({...formData, topic: e.target.value})}
              placeholder="e.g., Photosynthesis"
              required
            />
          </div>

          {formData.action === 'lesson-plan' && (
            <div className="form-group">
              <label>Duration</label>
              <input 
                type="text"
                value={formData.duration}
                onChange={(e) => setFormData({...formData, duration: e.target.value})}
                placeholder="e.g., 45 minutes"
              />
            </div>
          )}

          {formData.action === 'feedback' && (
            <>
              <div className="form-group">
                <label>Student Name</label>
                <input 
                  type="text"
                  value={formData.studentName}
                  onChange={(e) => setFormData({...formData, studentName: e.target.value})}
                  placeholder="e.g., Alex Chen"
                />
              </div>
              <div className="form-group">
                <label>Student Scores (JSON)</label>
                <textarea 
                  value={formData.studentScores}
                  onChange={(e) => setFormData({...formData, studentScores: e.target.value})}
                  placeholder='{ "math": 85, "reading": 88, "science": 82 }'
                  rows="3"
                />
              </div>
            </>
          )}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Generating...' : 'Generate'}
          </button>
        </form>

        {result && (
          <div className="result-panel">
            <h3>Result</h3>
            {result.error ? (
              <div className="error">{result.error}</div>
            ) : (
              <pre className="result-content">
                {JSON.stringify(result, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
