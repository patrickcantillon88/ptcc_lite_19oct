import React, { useState, useEffect } from 'react';
import '../styles/staff-board.css';

interface StaffMember {
  id: number;
  name: string;
  role: string;
  class_code: string;
  term: string;
  active: boolean;
}

interface StaffBoardProps {
  classCode: string;
}

export const StaffBoard: React.FC<StaffBoardProps> = ({ classCode }) => {
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStaffByClass();
  }, [classCode]);

  const fetchStaffByClass = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8001/api/staff/by-class/${classCode}`
      );
      if (response.ok) {
        const data = await response.json();
        setStaff(data);
        setError(null);
      } else {
        setError('Failed to load staff');
      }
    } catch (err) {
      console.error('Error fetching staff:', err);
      setError('Error loading staff data');
    } finally {
      setLoading(false);
    }
  };

  const roleEmoji = (role: string): string => {
    switch (role) {
      case 'Class Teacher':
        return '👨‍🏫';
      case 'Learning Support Teacher':
        return '🤝';
      case 'TA':
        return '👩‍💼';
      case 'Specialist':
        return '🎨';
      default:
        return '👤';
    }
  };

  if (loading) {
    return <div className="staff-board loading">Loading staff...</div>;
  }

  if (error) {
    return <div className="staff-board error">{error}</div>;
  }

  return (
    <div className="staff-board">
      <h3>👥 Class Staff - {classCode}</h3>
      <div className="staff-list">
        {staff.map((member) => (
          <div key={member.id} className="staff-card">
            <div className="staff-emoji">{roleEmoji(member.role)}</div>
            <div className="staff-info">
              <div className="staff-name">{member.name}</div>
              <div className="staff-role">{member.role}</div>
              {member.term && <div className="staff-term">{member.term}</div>}
            </div>
            <div className="staff-status">
              {member.active ? (
                <span className="active">✓ Active</span>
              ) : (
                <span className="inactive">○ Inactive</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StaffBoard;
