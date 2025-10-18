import React, { useState, useEffect } from 'react';
import '../styles/timetable-view.css';

interface TimetableEntry {
  id: number;
  class_code: string;
  day_of_week: string;
  period: number;
  start_time: string;
  end_time: string;
  subject: string;
  lesson_type: string;
  specialist_name: string | null;
  room: string | null;
  notes: string | null;
}

interface TimetableViewProps {
  classCode: string;
  showToday?: boolean;
}

export const TimetableView: React.FC<TimetableViewProps> = ({
  classCode,
  showToday = false,
}) => {
  const [timetable, setTimetable] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDay, setSelectedDay] = useState<string>('Monday');

  useEffect(() => {
    if (showToday) {
      fetchTodayTimetable();
    } else {
      fetchWeeklyTimetable();
    }
  }, [classCode, showToday]);

  const fetchTodayTimetable = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8001/api/timetable/today/${classCode}`
      );
      if (response.ok) {
        const data = await response.json();
        setTimetable(data);
        setError(null);
      } else {
        setError('Failed to load today\'s timetable');
      }
    } catch (err) {
      console.error('Error fetching timetable:', err);
      setError('Error loading timetable');
    } finally {
      setLoading(false);
    }
  };

  const fetchWeeklyTimetable = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8001/api/timetable/class/${classCode}`
      );
      if (response.ok) {
        const data = await response.json();
        setTimetable(data);
        setError(null);
      } else {
        setError('Failed to load timetable');
      }
    } catch (err) {
      console.error('Error fetching timetable:', err);
      setError('Error loading timetable');
    } finally {
      setLoading(false);
    }
  };

  const lessonTypeEmoji = (type: string): string => {
    switch (type) {
      case 'Literacy':
        return '📚';
      case 'Numeracy':
        return '🔢';
      case 'Specialist':
        return '✨';
      case 'Foundation':
        return '🏫';
      case 'CCA':
        return '🎯';
      default:
        return '📖';
    }
  };

  const lessonTypeColor = (type: string): string => {
    switch (type) {
      case 'Literacy':
        return '#4f46e5';
      case 'Numeracy':
        return '#06b6d4';
      case 'Specialist':
        return '#f59e0b';
      case 'Foundation':
        return '#8b5cf6';
      case 'CCA':
        return '#ec4899';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return <div className="timetable-view loading">Loading timetable...</div>;
  }

  if (error) {
    return <div className="timetable-view error">{error}</div>;
  }

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const dayTimetable = showToday
    ? timetable
    : timetable.filter((entry) => entry.day_of_week === selectedDay);

  return (
    <div className="timetable-view">
      <h3>📅 Class Timetable - {classCode}</h3>

      {!showToday && (
        <div className="day-selector">
          {days.map((day) => (
            <button
              key={day}
              className={`day-btn ${selectedDay === day ? 'active' : ''}`}
              onClick={() => setSelectedDay(day)}
            >
              {day.slice(0, 3)}
            </button>
          ))}
        </div>
      )}

      <div className="periods-list">
        {dayTimetable.length > 0 ? (
          dayTimetable.map((entry) => (
            <div
              key={entry.id}
              className="period-card"
              style={{
                borderLeftColor: lessonTypeColor(entry.lesson_type),
              }}
            >
              <div className="period-time">
                <div className="time">{entry.start_time}</div>
                <div className="dash">→</div>
                <div className="time">{entry.end_time}</div>
              </div>

              <div className="period-content">
                <div className="period-subject">
                  <span className="emoji">
                    {lessonTypeEmoji(entry.lesson_type)}
                  </span>
                  <span className="name">{entry.subject}</span>
                </div>

                <div className="period-meta">
                  <span className="type">{entry.lesson_type}</span>
                  {entry.specialist_name && (
                    <span className="specialist">
                      👤 {entry.specialist_name}
                    </span>
                  )}
                  {entry.room && <span className="room">📍 {entry.room}</span>}
                </div>

                {entry.notes && <div className="period-notes">{entry.notes}</div>}
              </div>
            </div>
          ))
        ) : (
          <div className="no-periods">No periods scheduled</div>
        )}
      </div>
    </div>
  );
};

export default TimetableView;
