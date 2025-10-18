import React, { useState, useEffect } from 'react';
import '../styles/student-context.css';

interface Accommodation {
  id: number;
  student_id: number;
  student_name: string;
  accommodation_type: string;
  description: string;
  implementation_details: string | null;
  active: boolean;
  effective_date: string;
  notes: string | null;
}

interface StudentContextViewProps {
  studentId: number;
  studentName: string;
}

export const StudentContextView: React.FC<StudentContextViewProps> = ({
  studentId,
  studentName,
}) => {
  const [accommodations, setAccommodations] = useState<Accommodation[]>([]);
  const [activeOnly, setActiveOnly] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAccommodations();
  }, [studentId]);

  const fetchAccommodations = async () => {
    try {
      setLoading(true);
      const endpoint = activeOnly
        ? `http://localhost:8001/api/accommodations/active/${studentId}`
        : `http://localhost:8001/api/accommodations/student/${studentId}`;

      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        setAccommodations(data);
        setError(null);
      } else {
        setError('No accommodations found');
      }
    } catch (err) {
      console.error('Error fetching accommodations:', err);
      setError('Error loading accommodations');
    } finally {
      setLoading(false);
    }
  };

  const accommodationTypeEmoji = (type: string): string => {
    switch (type) {
      case 'sensory':
        return '👁️';
      case 'behavioral':
        return '💭';
      case 'social':
        return '👥';
      case 'communication':
        return '🗣️';
      case 'equipment':
        return '🖥️';
      case 'schedule':
        return '⏰';
      default:
        return '✨';
    }
  };

  const accommodationTypeColor = (type: string): string => {
    switch (type) {
      case 'sensory':
        return '#ef4444';
      case 'behavioral':
        return '#f59e0b';
      case 'social':
        return '#3b82f6';
      case 'communication':
        return '#8b5cf6';
      case 'equipment':
        return '#10b981';
      case 'schedule':
        return '#06b6d4';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return <div className="context-view loading">Loading accommodations...</div>;
  }

  if (error) {
    return <div className="context-view error">{error}</div>;
  }

  return (
    <div className="context-view">
      <div className="context-header">
        <h3>🎯 Student Context - {studentName}</h3>
        <div className="filter-toggle">
          <button
            className={`toggle-btn ${activeOnly ? 'active' : ''}`}
            onClick={() => {
              setActiveOnly(!activeOnly);
            }}
          >
            {activeOnly ? '⚡ Active Only' : '📋 All'}
          </button>
        </div>
      </div>

      {accommodations.length > 0 ? (
        <div className="accommodations-grid">
          {accommodations.map((acc) => (
            <div
              key={acc.id}
              className="accommodation-card"
              style={{
                borderTopColor: accommodationTypeColor(acc.accommodation_type),
              }}
            >
              <div className="acc-header">
                <span className="emoji">
                  {accommodationTypeEmoji(acc.accommodation_type)}
                </span>
                <span className="type">{acc.accommodation_type}</span>
                {acc.active && <span className="active-badge">✓ Active</span>}
              </div>

              <div className="acc-description">{acc.description}</div>

              {acc.implementation_details && (
                <div className="acc-implementation">
                  <strong>How to implement:</strong>
                  <p>{acc.implementation_details}</p>
                </div>
              )}

              {acc.notes && (
                <div className="acc-notes">
                  <strong>Notes:</strong>
                  <p>{acc.notes}</p>
                </div>
              )}

              <div className="acc-meta">
                <small>Since: {new Date(acc.effective_date).toLocaleDateString()}</small>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-accommodations">
          {activeOnly
            ? 'No active accommodations'
            : 'No accommodations found'}
        </div>
      )}
    </div>
  );
};

export default StudentContextView;
