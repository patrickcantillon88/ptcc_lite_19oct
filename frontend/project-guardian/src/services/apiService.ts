import { Assessment } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const getAssessment = async (
  description: string,
  yearGroup: string,
  incidentHistory: string
): Promise<Assessment> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/guardian/assess`, {
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
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling assessment API:', error);
    if (error instanceof Error) {
      throw new Error(`Assessment API Error: ${error.message}`);
    }
    throw new Error('An unknown error occurred while fetching the assessment.');
  }
};
