import React, { useState } from 'react';
import Camera from './Camera';

interface Student {
  id: number;
  name: string;
  class_code: string;
  year_group: string;
  campus: string;
}

interface QuickLogProps {
  selectedStudent: Student | null;
}

interface LogEntry {
  student_id: number;
  log_type: 'behavior' | 'performance' | 'attendance' | 'note';
  category: string;
  note: string;
  timestamp: string;
}

const QuickLog: React.FC<QuickLogProps> = ({ selectedStudent }) => {
  const [logType, setLogType] = useState<'behavior' | 'performance' | 'attendance' | 'note'>('behavior');
  const [category, setCategory] = useState('');
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState<string | null>(null);
  const [photoBlob, setPhotoBlob] = useState<Blob | null>(null);

  const logTypeOptions = [
    { value: 'behavior', label: '📋 Behavior', icon: '📋' },
    { value: 'performance', label: '⭐ Performance', icon: '⭐' },
    { value: 'attendance', label: '✅ Attendance', icon: '✅' },
    { value: 'note', label: '📝 Note', icon: '📝' },
  ];

  const categoryOptions = {
    behavior: ['Positive', 'Needs Improvement', 'Incident', 'Praise', 'Concern'],
    performance: ['Excellent', 'Good', 'Satisfactory', 'Needs Support', 'Outstanding'],
    attendance: ['Present', 'Late', 'Absent', 'Left Early', 'Medical'],
    note: ['General', 'Parent Contact', 'Meeting', 'Assessment', 'Other'],
  };

  const handlePhotoCapture = (photoData: string, photoBlob: Blob) => {
    setCapturedPhoto(photoData);
    setPhotoBlob(photoBlob);
    setShowCamera(false);
  };

  const removePhoto = () => {
    setCapturedPhoto(null);
    setPhotoBlob(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedStudent || !category || !note.trim()) {
      return;
    }

    setSaving(true);

    const logEntry: LogEntry = {
      student_id: selectedStudent.id,
      log_type: logType,
      category,
      note: note.trim(),
      timestamp: new Date().toISOString(),
    };

    try {
      // Try to save to API first
      const response = await fetch('/api/logs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logEntry),
      });

      if (response.ok) {
        setSaved(true);
        setNote('');
        setCategory('');
        setTimeout(() => setSaved(false), 2000);
      } else {
        // If API fails, save to localStorage for later sync
        saveOffline(logEntry);
      }
    } catch (error) {
      // Save offline if no connection
      saveOffline(logEntry);
    } finally {
      setSaving(false);
    }
  };

  const saveOffline = (logEntry: LogEntry) => {
    const offlineLogs = JSON.parse(localStorage.getItem('offlineLogs') || '[]');
    offlineLogs.push(logEntry);
    localStorage.setItem('offlineLogs', JSON.stringify(offlineLogs));

    setSaved(true);
    setNote('');
    setCategory('');
    setTimeout(() => setSaved(false), 2000);
  };

  if (!selectedStudent) {
    return (
      <div className="quick-log">
        <div className="empty-state">
          <p>👆 Please select a student first</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="quick-log">
        <div className="student-summary">
          <h3>📝 Log for: {selectedStudent.name}</h3>
          <p>{selectedStudent.class_code} • Year {selectedStudent.year_group} • {selectedStudent.campus}</p>
        </div>

      <form onSubmit={handleSubmit} className="log-form">
        <div className="form-group">
          <label>Log Type</label>
          <div className="log-type-buttons">
            {logTypeOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`log-type-button ${logType === option.value ? 'active' : ''}`}
                onClick={() => {
                  setLogType(option.value as any);
                  setCategory('');
                }}
              >
                <span className="type-icon">{option.icon}</span>
                <span className="type-label">{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Category</label>
          <div className="category-buttons">
            {categoryOptions[logType].map((cat) => (
              <button
                key={cat}
                type="button"
                className={`category-button ${category === cat ? 'active' : ''}`}
                onClick={() => setCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Note</label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Enter your note..."
            className="log-note-input"
            rows={3}
            required
          />
        </div>

        <div className="form-group">
          <label>Photo (Optional)</label>
          <div className="photo-section">
            {!capturedPhoto ? (
              <button
                type="button"
                onClick={() => setShowCamera(true)}
                className="camera-button"
              >
                📷 Take Photo
              </button>
            ) : (
              <div className="photo-preview">
                <img src={capturedPhoto} alt="Log photo" className="preview-image" />
                <button
                  type="button"
                  onClick={removePhoto}
                  className="remove-photo"
                >
                  🗑️ Remove
                </button>
              </div>
            )}
          </div>
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={!category || !note.trim() || saving}
        >
          {saving ? '💾 Saving...' : '📝 Save Log'}
        </button>

        {saved && (
          <div className="success-message">
            ✅ Log saved successfully!
          </div>
        )}
      </form>

      {/* Camera Modal */}
      {showCamera && (
        <Camera
          onPhotoCapture={handlePhotoCapture}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
    </>
  );
};

export default QuickLog;