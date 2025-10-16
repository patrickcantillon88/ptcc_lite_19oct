import React, { useState, useEffect } from 'react';

interface Student {
  id: number;
  name: string;
  class_code: string;
  year_group: string;
  campus: string;
}

interface StudentSearchProps {
  onStudentSelect: (student: Student | null) => void;
}

const StudentSearch: React.FC<StudentSearchProps> = ({ onStudentSelect }) => {
  const [query, setQuery] = useState('');
  const [students, setStudents] = useState<Student[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch students from API
  useEffect(() => {
    const fetchStudents = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/students/');
        if (response.ok) {
          const data = await response.json();
          setStudents(data);
          setFilteredStudents(data);
        } else {
          setError('Failed to load students');
        }
      } catch (err) {
        setError('Cannot connect to server');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

  // Filter students based on search query
  useEffect(() => {
    if (query.trim() === '') {
      setFilteredStudents(students);
    } else {
      const filtered = students.filter(student =>
        student.name.toLowerCase().includes(query.toLowerCase()) ||
        student.class_code.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredStudents(filtered);
    }
  }, [query, students]);

  const handleStudentSelect = (student: Student) => {
    onStudentSelect(student);
    setQuery('');
  };

  return (
    <div className="student-search">
      <div className="search-header">
        <h2>👥 Select Student</h2>
        <div className="search-input-container">
          <input
            type="text"
            placeholder="Search by name or class..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="search-input"
            autoFocus
          />
        </div>
      </div>

      <div className="students-list">
        {loading && (
          <div className="loading">
            <p>Loading students...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        )}

        {!loading && !error && filteredStudents.length === 0 && query === '' && (
          <div className="empty-state">
            <p>No students loaded</p>
          </div>
        )}

        {!loading && !error && filteredStudents.length === 0 && query !== '' && (
          <div className="no-results">
            <p>No students found for "{query}"</p>
          </div>
        )}

        {!loading && !error && filteredStudents.length > 0 && (
          <div className="students-grid">
            {filteredStudents.slice(0, 20).map((student) => (
              <button
                key={student.id}
                className="student-card"
                onClick={() => handleStudentSelect(student)}
              >
                <div className="student-info">
                  <div className="student-name">{student.name}</div>
                  <div className="student-details">
                    {student.class_code} • Year {student.year_group} • {student.campus}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentSearch;