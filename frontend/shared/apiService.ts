/**
 * Unified API Service
 * Provides compatibility layer for both old and new backend APIs
 * Supports seamless switching between API versions
 */

// Configuration
const API_CONFIG = {
  // Use new safeguarding API by default
  USE_NEW_API: import.meta.env.VITE_USE_NEW_API !== 'false',
  
  // Base URLs
  OLD_API_BASE: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  NEW_API_BASE: import.meta.env.VITE_NEW_API_BASE_URL || 'http://localhost:8001/api',
  
  // Endpoints
  OLD_ENDPOINTS: {
    students: '/api/students',
    search: '/api/search',
    guardian_assess: '/api/guardian/assess',
    safeguarding: '/api/safeguarding',
  },
  
  NEW_ENDPOINTS: {
    analyze: '/analyze',
    compliance: '/compliance',
    health: '/health',
    summary: '/summary',
  },
};

// ============================================================================
// OLD API COMPATIBILITY (Legacy endpoints)
// ============================================================================

export interface Student {
  id: number;
  name: string;
  class_code: string;
  year_group: string;
  campus: string;
}

export interface Assessment {
  risk_level: string;
  confidence: number;
  patterns: string[];
  pattern_combinations: string[];
  evidence_summary: string;
  recommendations: string[];
}

/**
 * Fetch students list (OLD API)
 */
export const fetchStudents = async (): Promise<Student[]> => {
  const endpoint = `${API_CONFIG.OLD_API_BASE}${API_CONFIG.OLD_ENDPOINTS.students}/`;
  try {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch students:', error);
    throw error;
  }
};

/**
 * Search students (OLD API)
 */
export const searchStudents = async (query: string): Promise<Student[]> => {
  const endpoint = `${API_CONFIG.OLD_API_BASE}${API_CONFIG.OLD_ENDPOINTS.search}/?q=${encodeURIComponent(query)}`;
  try {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to search students:', error);
    throw error;
  }
};

/**
 * Get guardian assessment (OLD API)
 */
export const getGuardianAssessment = async (
  description: string,
  yearGroup: string,
  incidentHistory: string
): Promise<Assessment> => {
  const endpoint = `${API_CONFIG.OLD_API_BASE}${API_CONFIG.OLD_ENDPOINTS.guardian_assess}`;
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        description,
        year_group: yearGroup,
        incident_history: incidentHistory,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Guardian assessment failed:', error);
    throw error;
  }
};

// ============================================================================
// NEW API INTEGRATION (Safeguarding endpoints)
// ============================================================================

export interface StudentData {
  student_id: string;
  behavioral_incidents?: Array<{ type: string; timestamp: string; severity?: string }>;
  assessments?: Array<{ subject: string; performance_level: string; timestamp: string }>;
  attendance?: Array<{ status: string; timestamp: string }>;
  communications?: Array<{ source: string; urgency: string; timestamp: string }>;
}

export interface AnalysisResult {
  status: string;
  data: {
    student_token: string;
    risk_level: string;
    patterns: string[];
    recommendations?: string[];
    timestamp: string;
  };
}

export interface ComplianceResult {
  status: string;
  data: {
    ferpa: string;
    gdpr: string;
    data_encryption: string;
    overall_status: string;
  };
}

export interface HealthResult {
  status: string;
  timestamp: string;
  services: {
    database?: string;
    llm_client?: string;
    tokenization?: string;
  };
}

/**
 * Analyze student data with new safeguarding API
 */
export const analyzeStudentData = async (
  studentData: StudentData
): Promise<AnalysisResult> => {
  if (!API_CONFIG.USE_NEW_API) {
    throw new Error('New API is not enabled. Set VITE_USE_NEW_API=true');
  }

  const endpoint = `${API_CONFIG.NEW_API_BASE}${API_CONFIG.NEW_ENDPOINTS.analyze}`;
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify(studentData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Student analysis failed:', error);
    throw error;
  }
};

/**
 * Check system compliance status
 */
export const checkCompliance = async (): Promise<ComplianceResult> => {
  if (!API_CONFIG.USE_NEW_API) {
    throw new Error('New API is not enabled. Set VITE_USE_NEW_API=true');
  }

  const endpoint = `${API_CONFIG.NEW_API_BASE}${API_CONFIG.NEW_ENDPOINTS.compliance}`;
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Compliance check failed:', error);
    throw error;
  }
};

/**
 * Check system health status
 */
export const checkHealth = async (): Promise<HealthResult> => {
  if (!API_CONFIG.USE_NEW_API) {
    throw new Error('New API is not enabled. Set VITE_USE_NEW_API=true');
  }

  const endpoint = `${API_CONFIG.NEW_API_BASE}${API_CONFIG.NEW_ENDPOINTS.health}`;
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Get student summary from safeguarding system
 */
export const getSafeguardingSummary = async (studentId: string): Promise<AnalysisResult> => {
  if (!API_CONFIG.USE_NEW_API) {
    throw new Error('New API is not enabled. Set VITE_USE_NEW_API=true');
  }

  const endpoint = `${API_CONFIG.NEW_API_BASE}${API_CONFIG.NEW_ENDPOINTS.summary}/${studentId}`;
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch summary:', error);
    throw error;
  }
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get authentication token from localStorage
 */
const getAuthToken = (): string => {
  return localStorage.getItem('auth_token') || '';
};

/**
 * Set authentication token
 */
export const setAuthToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

/**
 * Clear authentication token
 */
export const clearAuthToken = (): void => {
  localStorage.removeItem('auth_token');
};

/**
 * Check if new API is available
 */
export const isNewAPIAvailable = async (): Promise<boolean> => {
  if (!API_CONFIG.USE_NEW_API) {
    return false;
  }

  try {
    const result = await checkHealth();
    return result.status === 'healthy';
  } catch {
    return false;
  }
};

/**
 * Get current API configuration
 */
export const getAPIConfig = () => API_CONFIG;

/**
 * Switch API version at runtime
 */
export const switchAPIVersion = (useNewAPI: boolean): void => {
  API_CONFIG.USE_NEW_API = useNewAPI;
};

// ============================================================================
// BRIDGE FUNCTIONS (Convert between old and new API formats)
// ============================================================================

/**
 * Convert assessment to student data format for analysis
 */
export const convertAssessmentToStudentData = (
  assessment: Assessment,
  studentId: string
): StudentData => {
  return {
    student_id: studentId,
    behavioral_incidents: [],
    assessments: [{
      subject: 'General Assessment',
      performance_level: assessment.risk_level.toLowerCase(),
      timestamp: new Date().toISOString(),
    }],
    attendance: [],
    communications: [],
  };
};

/**
 * Convert student data to guardian assessment format
 */
export const convertStudentDataToAssessment = (
  result: AnalysisResult
): Assessment => {
  return {
    risk_level: result.data.risk_level,
    confidence: 0.85,
    patterns: result.data.patterns,
    pattern_combinations: result.data.patterns,
    evidence_summary: `Risk Level: ${result.data.risk_level}`,
    recommendations: result.data.recommendations || [],
  };
};

export default {
  // Old API
  fetchStudents,
  searchStudents,
  getGuardianAssessment,
  
  // New API
  analyzeStudentData,
  checkCompliance,
  checkHealth,
  getSafeguardingSummary,
  
  // Utilities
  setAuthToken,
  clearAuthToken,
  isNewAPIAvailable,
  getAPIConfig,
  switchAPIVersion,
  
  // Converters
  convertAssessmentToStudentData,
  convertStudentDataToAssessment,
};
