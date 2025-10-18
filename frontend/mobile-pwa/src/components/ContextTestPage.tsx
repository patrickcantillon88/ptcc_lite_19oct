import React, { useState } from 'react';
import StaffBoard from './StaffBoard';
import TimetableView from './TimetableView';
import StudentContextView from './StudentContextView';
import '../styles/context-test.css';

// Test student data
const TEST_STUDENTS = [
  { id: 1, name: 'Marcus Thompson', class_code: '3A' },
  { id: 2, name: 'Sophie Chen', class_code: '3A' },
  { id: 3, name: 'Joshua Finch', class_code: '4B' },
  { id: 5, name: 'Freya Nielsen', class_code: '5C' },
];

export const ContextTestPage: React.FC = () => {
  const [selectedStudent, setSelectedStudent] = useState(TEST_STUDENTS[0]);

  return (
    <div className="context-test-page">
      <header className="test-header">
        <h1>🎯 Context-Aware System Test Page</h1>
        <p>Phase 2 Components + Phase 3 Agent Testing</p>
      </header>

      <div className="test-container">
        {/* Student Selector */}
        <aside className="student-selector">
          <h3>📚 Select Student</h3>
          <div className="student-buttons">
            {TEST_STUDENTS.map((student) => (
              <button
                key={student.id}
                className={`student-btn ${
                  selectedStudent.id === student.id ? 'active' : ''
                }`}
                onClick={() => setSelectedStudent(student)}
              >
                <div className="student-name">{student.name}</div>
                <div className="student-class">{student.class_code}</div>
              </button>
            ))}
          </div>
        </aside>

        {/* Main Content */}
        <main className="test-content">
          <section className="context-section">
            <h2>👤 {selectedStudent.name}</h2>
            <p className="class-info">Class: {selectedStudent.class_code}</p>
          </section>

          {/* Staff Board */}
          <section className="context-section">
            <StaffBoard classCode={selectedStudent.class_code} />
          </section>

          {/* Today's Timetable */}
          <section className="context-section">
            <h3>📅 Today's Schedule</h3>
            <TimetableView classCode={selectedStudent.class_code} showToday={true} />
          </section>

          {/* Weekly Timetable */}
          <section className="context-section">
            <h3>📋 Weekly Schedule</h3>
            <TimetableView classCode={selectedStudent.class_code} showToday={false} />
          </section>

          {/* Student Accommodations */}
          <section className="context-section">
            <StudentContextView
              studentId={selectedStudent.id}
              studentName={selectedStudent.name}
            />
          </section>
        </main>
      </div>

      {/* API Status */}
      <footer className="test-footer">
        <p>✅ Connected to Phase 1 APIs on localhost:8001</p>
        <p>📡 Endpoints: /api/staff, /api/timetable, /api/accommodations</p>
      </footer>
    </div>
  );
};

export default ContextTestPage;
