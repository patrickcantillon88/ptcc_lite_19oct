import React, { useState } from 'react';

export interface FormState {
  description: string;
  yearGroup: string;
  incidentHistory: 'First incident' | 'Repeated offense';
}

interface InputFormProps {
  onSubmit: (data: FormState) => void;
  isLoading: boolean;
  initialState: FormState;
}

const yearGroups = ["Year 3", "Year 4", "Year 5", "Year 6"];

const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading, initialState }) => {
  const [formState, setFormState] = useState<FormState>(initialState);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };

  const handleRadioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormState(prevState => ({ ...prevState, incidentHistory: e.target.value as FormState['incidentHistory'] }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formState);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="p-4 bg-guardian-blue-100 border border-guardian-blue-200 rounded-lg text-sm text-guardian-blue-900">
        <p className="font-bold">Disclaimer</p>
        <p>This is a tool to help you make better informed decisions. If you are still unsure of the outcome, please contact your Head of Year (HOY) or Designated Safeguarding Lead (DSL). No names should be used in this consultation form. Reminder: No data will be stored.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="yearGroup" className="block text-lg font-medium text-gray-700 mb-2">
            Year Group
          </label>
          <select
            id="yearGroup"
            name="yearGroup"
            value={formState.yearGroup}
            onChange={handleChange}
            className="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-guardian-blue-500 focus:border-guardian-blue-500 transition duration-150 ease-in-out text-base"
            disabled={isLoading}
          >
            {yearGroups.map(yg => <option key={yg} value={yg}>{yg}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-lg font-medium text-gray-700 mb-2">
            Incident History
          </label>
          <div className="flex items-center space-x-6 h-full">
            <label className="flex items-center">
              <input
                type="radio"
                name="incidentHistory"
                value="First incident"
                checked={formState.incidentHistory === 'First incident'}
                onChange={handleRadioChange}
                className="h-4 w-4 text-guardian-blue-600 border-gray-300 focus:ring-guardian-blue-500"
                disabled={isLoading}
              />
              <span className="ml-2 text-base text-gray-700">First incident</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="incidentHistory"
                value="Repeated offense"
                checked={formState.incidentHistory === 'Repeated offense'}
                onChange={handleRadioChange}
                className="h-4 w-4 text-guardian-blue-600 border-gray-300 focus:ring-guardian-blue-500"
                disabled={isLoading}
              />
              <span className="ml-2 text-base text-gray-700">Repeated offense</span>
            </label>
          </div>
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-lg font-medium text-gray-700 mb-2">
          Describe the Incident
        </label>
        <textarea
          id="description"
          name="description"
          value={formState.description}
          onChange={handleChange}
          placeholder="e.g., 'A student has been receiving unkind messages...' or 'I found a student accessing inappropriate content...'"
          className="w-full h-48 p-4 border border-gray-300 rounded-lg shadow-sm focus:ring-guardian-blue-500 focus:border-guardian-blue-500 transition duration-150 ease-in-out text-base"
          required
          disabled={isLoading}
        />
      </div>

      <div>
        <button
          type="submit"
          disabled={isLoading || !formState.description.trim()}
          className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-md text-lg font-semibold text-white bg-guardian-blue-600 hover:bg-guardian-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-guardian-blue-500 transition-colors duration-300"
        >
          {isLoading ? 'Analyzing...' : 'Get Assessment'}
        </button>
      </div>
    </form>
  );
};

export default InputForm;
