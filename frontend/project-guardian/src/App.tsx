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
  const [showCriteria, setShowCriteria] = useState<boolean>(false);

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

          {/* Assessment Criteria Panel */}
          {!assessment && !isLoading && (
            <div className="mt-6 border-t border-gray-200 pt-6">
              <button
                onClick={() => setShowCriteria(!showCriteria)}
                className="flex items-center gap-2 w-full text-left px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
              >
                <div className="flex-shrink-0">
                  {showCriteria ? (
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-semibold text-blue-800">View Assessment Criteria</span>
                  </div>
                  <p className="text-sm text-blue-600 mt-1">See how incidents are classified (currently using rule-based assessment)</p>
                </div>
              </button>
              
              {showCriteria && (
                <div className="mt-4 p-6 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="mb-4 p-3 bg-blue-100 rounded-lg border-l-4 border-blue-500">
                    <p className="text-sm text-blue-800">
                      <strong>Demo Note:</strong> This prototype uses transparent rule-based assessment. 
                      Production version will integrate AI (Gemini) while maintaining these criteria as fallback.
                    </p>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="border-l-4 border-green-500 pl-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🟢</span>
                        <h3 className="text-lg font-bold text-green-800">LOW (Teacher Level Resolution)</h3>
                      </div>
                      <p className="text-sm text-gray-700 mb-2"><strong>Characteristics:</strong> Minor, unintentional, first-time offenses with limited impact. No clear malicious intent.</p>
                      <p className="text-sm text-gray-700 mb-2"><strong>Keywords/Examples:</strong></p>
                      <ul className="text-sm text-gray-600 list-disc list-inside space-y-1 ml-4">
                        <li>Accidental sharing of non-sensitive information</li>
                        <li>Using non-compliant apps (games, social media) during class for the first time</li>
                        <li>Cleared browser history for non-sensitive searches</li>
                        <li>Mildly off-topic or silly comments in a school chat</li>
                        <li>Using a VPN for the first time without accessing harmful content</li>
                        <li>Forgetting iPad or using it outside of learning time without malice</li>
                        <li>Inappropriate but not offensive profile content (e.g., a silly meme)</li>
                      </ul>
                    </div>

                    <div className="border-l-4 border-amber-500 pl-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🟡</span>
                        <h3 className="text-lg font-bold text-amber-800">MEDIUM (Head of Year Resolution)</h3>
                      </div>
                      <p className="text-sm text-gray-700 mb-2"><strong>Characteristics:</strong> Deliberate but not severe breaches, repeated minor offenses, or actions with wider impact on others.</p>
                      <p className="text-sm text-gray-700 mb-2"><strong>Keywords/Examples:</strong></p>
                      <ul className="text-sm text-gray-600 list-disc list-inside space-y-1 ml-4">
                        <li>Minor cyberbullying (unkind messages, name-calling, creating a joke meme about someone)</li>
                        <li>Sharing photos/videos of others without consent where no harm was intended</li>
                        <li>Persistent use of non-compliant apps or VPNs after a warning</li>
                        <li>Inappropriate searches (for swear words, non-explicit but mature topics)</li>
                        <li>Using swear words in chats</li>
                        <li>Creating fake (but not malicious) accounts</li>
                        <li>Minor hacking attempts (trying to guess a friend's password as a joke)</li>
                      </ul>
                    </div>

                    <div className="border-l-4 border-red-500 pl-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🔴</span>
                        <h3 className="text-lg font-bold text-red-800">HIGH (DSL Level Resolution)</h3>
                      </div>
                      <p className="text-sm text-gray-700 mb-2"><strong>Characteristics:</strong> Serious, malicious, or illegal behavior. Poses significant risk to student or others. Clear safeguarding concern.</p>
                      <p className="text-sm text-gray-700 mb-2"><strong>Keywords/Examples:</strong></p>
                      <ul className="text-sm text-gray-600 list-disc list-inside space-y-1 ml-4">
                        <li>Serious, persistent, or targeted cyberbullying; harassment; threats</li>
                        <li>Sharing or searching for explicit, pornographic, violent, or illegal content</li>
                        <li>Sexting: creating, sending, or receiving indecent images of minors</li>
                        <li>Impersonating others online to cause harm or distress</li>
                        <li>Hacking into accounts with malicious intent</li>
                        <li>Discriminatory behavior (racism, homophobia, etc.)</li>
                        <li>Anything indicating potential for self-harm, radicalization, or criminal activity</li>
                        <li>Taking and sharing photos/videos to humiliate or embarrass someone</li>
                      </ul>
                    </div>

                    <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      <div className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                        <div>
                          <p className="text-sm font-semibold text-yellow-800">Additional Rules:</p>
                          <ul className="text-sm text-yellow-700 mt-1 space-y-1">
                            <li>• <strong>Repeated offenses</strong> escalate classification by one level</li>
                            <li>• <strong>Years 3-4</strong> receive additional leniency (still learning digital citizenship)</li>
                            <li>• <strong>Unknown cases</strong> default to "seek Head of Year advice"</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
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
