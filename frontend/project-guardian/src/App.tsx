import React, { useState, useCallback } from 'react';
import { getAssessment } from './services/apiService';
import { type Assessment } from './types';
import InputForm, { type FormState } from './components/InputForm';
import DecisionCard from './components/DecisionCard';
import { ShieldCheckIcon } from './components/icons';

const App: React.FC = () => {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>({
    description: '',
    yearGroup: 'Year 3',
    incidentHistory: 'First incident'
  });

  const handleSubmit = useCallback(async (data: FormState) => {
    if (!data.description.trim()) {
      setError("Please enter a description of the incident.");
      return;
    }
    setFormState(data);
    setIsLoading(true);
    setError(null);
    setAssessment(null);

    try {
      const result = await getAssessment(data.description, data.yearGroup, data.incidentHistory);
      setAssessment(result);
    } catch (err) {
      console.error(err);
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred.";
      if (errorMessage.includes('API_KEY') || errorMessage.includes('GEMINI')) {
        setError("AI service not configured. Please contact your system administrator.");
      } else {
        setError(`Failed to get assessment: ${errorMessage}`);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleReset = () => {
    setAssessment(null);
    setError(null);
  };

  return (
    <div className="min-h-screen font-sans text-gray-800 flex flex-col items-center p-4 sm:p-6 md:p-8">
      <div className="w-full max-w-3xl mx-auto">
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-4 mb-2">
            <ShieldCheckIcon className="w-12 h-12 text-guardian-blue-600" />
            <h1 className="text-4xl sm:text-5xl font-bold text-guardian-blue-900">
              Project Guardian
            </h1>
          </div>
          <p className="text-lg text-guardian-blue-800">
            Digital Citizenship Breach Triage Tool
          </p>
          <p className="text-sm text-guardian-blue-700 mt-2">
            Confidential Consultation for School Staff
          </p>
        </header>

        <main className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200">
          {!assessment && !isLoading && (
            <InputForm onSubmit={handleSubmit} isLoading={false} initialState={formState} />
          )}

          {isLoading && (
            <div className="flex flex-col items-center justify-center space-y-4 p-8">
              <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-guardian-blue-600"></div>
              <p className="text-guardian-blue-800 font-medium">Analyzing incident...</p>
            </div>
          )}

          {error && (
            <div className="text-center p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
              <p className="font-bold">Error</p>
              <p>{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  setIsLoading(false);
                  setAssessment(null);
                }}
                className="mt-4 px-4 py-2 bg-guardian-blue-600 text-white rounded-lg hover:bg-guardian-blue-700 focus:outline-none focus:ring-2 focus:ring-guardian-blue-500 focus:ring-opacity-50"
              >
                Try Again
              </button>
            </div>
          )}

          {assessment && (
            <div>
              <DecisionCard assessment={assessment} yearGroup={formState.yearGroup} />
              <div className="mt-6 text-center">
                <button
                  onClick={handleReset}
                  className="px-6 py-2 bg-guardian-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-guardian-blue-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-guardian-blue-500 focus:ring-offset-2">
                  Start New Consultation
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
