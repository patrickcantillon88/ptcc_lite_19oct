import React from 'react';
import { type Assessment, Classification } from '../types';
import { CheckCircleIcon, ExclamationTriangleIcon, ShieldExclamationIcon } from './icons';

interface DecisionCardProps {
  assessment: Assessment;
  yearGroup: string;
}

const classificationConfig = {
  [Classification.LOW]: {
    title: "LOW - Teacher Level Resolution",
    bgColor: "bg-green-50",
    borderColor: "border-green-500",
    textColor: "text-green-800",
    icon: <CheckCircleIcon className="w-8 h-8 text-green-500" />,
  },
  [Classification.MEDIUM]: {
    title: "MEDIUM - Head of Year Resolution",
    bgColor: "bg-amber-50",
    borderColor: "border-amber-500",
    textColor: "text-amber-800",
    icon: <ExclamationTriangleIcon className="w-8 h-8 text-amber-500" />,
  },
  [Classification.HIGH]: {
    title: "HIGH - DSL Level Resolution",
    bgColor: "bg-red-50",
    borderColor: "border-red-500",
    textColor: "text-red-800",
    icon: <ShieldExclamationIcon className="w-8 h-8 text-red-500" />,
  },
};

const contactConfig: { [key: string]: string } = {
  "Year 3": "hoy.year3@school.edu",
  "Year 4": "hoy.year4@school.edu",
  "Year 5": "hoy.year5@school.edu",
  "Year 6": "hoy.year6@school.edu",
  "DSL": "dsl@school.edu",
};

const DecisionCard: React.FC<DecisionCardProps> = ({ assessment, yearGroup }) => {
  const config = classificationConfig[assessment.classification];
  const hoyEmail = contactConfig[yearGroup] || 'your-head-of-year@school.edu';
  const dslEmail = contactConfig["DSL"];

  const renderContactSection = () => {
    switch (assessment.classification) {
      case Classification.MEDIUM:
        return (
          <div>
            <h3 className="font-bold text-lg">Who to Contact</h3>
            <p>Inform your Head of Year. <a href={`mailto:${hoyEmail}`} className="text-guardian-blue-700 font-semibold underline">{hoyEmail}</a></p>
          </div>
        );
      case Classification.HIGH:
        return (
          <div>
            <h3 className="font-bold text-lg">Who to Contact</h3>
            <p>
              <span className="font-bold">You must contact</span> your Designated Safeguarding Lead (DSL) immediately. <a href={`mailto:${dslEmail}`} className="text-guardian-blue-700 font-semibold underline">{dslEmail}</a>
            </p>
          </div>
        );
      case Classification.LOW:
      default:
        return null;
    }
  };

  return (
    <div className={`rounded-xl border-l-8 p-6 shadow-lg ${config.borderColor} ${config.bgColor} ${config.textColor}`}>
      <div className="flex items-center gap-4 mb-4">
        {config.icon}
        <h2 className="text-2xl font-bold">ASSESSMENT COMPLETE</h2>
      </div>
      
      <div className="space-y-6">
        <div>
          <h3 className="font-bold text-lg">Recommended Resolution Level</h3>
          <p className="text-xl font-semibold">{config.title}</p>
        </div>

        <div>
          <h3 className="font-bold text-lg">Why?</h3>
          <p>{assessment.reason}</p>
        </div>

        <div>
          <h3 className="font-bold text-lg">Next Steps</h3>
          <ul className="list-disc list-inside space-y-1 pl-2">
            {assessment.nextSteps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>
        
        {renderContactSection()}

        <div>
          <h3 className="font-bold text-lg">Key Resources</h3>
          <ul className="list-disc list-inside space-y-1 pl-2">
            <li><a href="#" className="text-guardian-blue-700 underline">Digital Citizenship Breach Policy</a></li>
            <li><a href="#" className="text-guardian-blue-700 underline">Log in CPOMS</a></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DecisionCard;
