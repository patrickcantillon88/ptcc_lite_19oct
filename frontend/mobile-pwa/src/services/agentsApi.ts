import { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:8001';

export interface AgentAnalysis {
  agent_name: string;
  title: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  action_required: boolean;
  intervention_type: string;
  recommended_actions: string[];
  reasoning: string;
}

export interface StudentAnalysisResponse {
  student_id: number;
  student_name: string;
  class_code: string;
  timestamp: string;
  summary: string;
  high_priority_count: number;
  agents: {
    period_briefing?: AgentAnalysis;
    cca_engagement?: AgentAnalysis;
    accommodation_compliance?: AgentAnalysis;
  };
}

export interface AgentListResponse {
  agents: Array<{
    name: string;
    display_name: string;
    description: string;
    intervention_type: string;
    focus_areas: string[];
  }>;
  total_agents: number;
}

export interface AgentHealthResponse {
  status: string;
  agents: string[];
  agent_count: number;
}

// API Functions
export const checkAgentsHealth = async (): Promise<AgentHealthResponse> => {
  const response = await fetch(`${API_BASE}/api/agents/health`);
  if (!response.ok) throw new Error('Failed to check agents health');
  return response.json();
};

export const getAgentsList = async (): Promise<AgentListResponse> => {
  const response = await fetch(`${API_BASE}/api/agents/list`);
  if (!response.ok) throw new Error('Failed to get agents list');
  return response.json();
};

export const analyzeStudent = async (
  studentId: number,
  classCode?: string,
  periodCode?: string
): Promise<StudentAnalysisResponse> => {
  const params = new URLSearchParams();
  if (classCode) params.append('class_code', classCode);
  if (periodCode) params.append('period_code', periodCode);

  const url = `${API_BASE}/api/agents/analyze/${studentId}${
    params.toString() ? '?' + params.toString() : ''
  }`;
  const response = await fetch(url, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to analyze student');
  return response.json();
};

// React Hooks
export const useStudentAnalysis = (
  studentId: number | null,
  classCode?: string
) => {
  const [data, setData] = useState<StudentAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!studentId) {
      setData(null);
      return;
    }

    const fetchAnalysis = async () => {
      setLoading(true);
      setError(null);
      try {
        const analysis = await analyzeStudent(studentId, classCode);
        setData(analysis);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [studentId, classCode]);

  return { data, loading, error };
};

export const useAgentsList = () => {
  const [data, setData] = useState<AgentListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchList = async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await getAgentsList();
        setData(list);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchList();
  }, []);

  return { data, loading, error };
};
