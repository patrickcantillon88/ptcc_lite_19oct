import { useState, useEffect } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

// Types
interface Student {
  id: number;
  name: string;
  form: string;
  comment_count: number;
}

interface StudentsData {
  total: number;
  students_by_form: Record<string, Student[]>;
}

interface Comment {
  id: number;
  subject: string;
  comment: string;
  type: 'positive' | 'neutral' | 'concern';
  timestamp: string;
}

interface StudentCommentsData {
  student_name: string;
  form: string;
  comments_by_subject: Record<string, Comment | null>;
}

interface CCASubjectsData {
  subjects: string[];
}

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('cca-comments')
  const [searchQuery, setSearchQuery] = useState('');
  const [studentsData, setStudentsData] = useState<StudentsData | null>(null);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [studentCommentsData, setStudentCommentsData] = useState<StudentCommentsData | null>(null);
  const [ccaSubjects, setCcaSubjects] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingComment, setEditingComment] = useState<{
    subject: string;
    comment: string;
    type: 'positive' | 'neutral' | 'concern';
    commentId?: number;
    mode: 'add' | 'edit';
  } | null>(null);
  
  // Load initial data
  useEffect(() => {
    fetchStudents();
    fetchCCASubjects();
  }, []);
  
  // Fetch students when search query changes
  useEffect(() => {
    fetchStudents();
  }, [searchQuery]);
  
  // Fetch student comments when student is selected
  useEffect(() => {
    if (selectedStudentId) {
      fetchStudentComments(selectedStudentId);
    } else {
      setStudentCommentsData(null);
    }
  }, [selectedStudentId]);
  
  const fetchStudents = async () => {
    try {
      const params = new URLSearchParams({ q: searchQuery });
      const response = await fetch(`/api/cca/students/search?${params}`);
      if (response.ok) {
        const data: StudentsData = await response.json();
        setStudentsData(data);
      }
    } catch (error) {
      console.error('Failed to fetch students:', error);
    }
  };
  
  const fetchStudentComments = async (studentId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/cca/students/${studentId}/comments`);
      if (response.ok) {
        const data: StudentCommentsData = await response.json();
        setStudentCommentsData(data);
      }
    } catch (error) {
      console.error('Failed to fetch student comments:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchCCASubjects = async () => {
    try {
      const response = await fetch('/api/cca/subjects');
      if (response.ok) {
        const data: CCASubjectsData = await response.json();
        setCcaSubjects(data.subjects || []);
      }
    } catch (error) {
      console.error('Failed to fetch CCA subjects:', error);
    }
  };
  
  const handleSaveComment = async () => {
    if (!editingComment || !selectedStudentId) return;
    
    setIsLoading(true);
    try {
      if (editingComment.mode === 'edit' && editingComment.commentId) {
        // Update existing comment
        const response = await fetch(`/api/cca/comments/${editingComment.commentId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            comment: editingComment.comment,
            comment_type: editingComment.type
          })
        });
        if (response.ok) {
          setEditingComment(null);
          fetchStudentComments(selectedStudentId);
        }
      } else {
        // Create new comment
        const response = await fetch('/api/cca/comments', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: selectedStudentId,
            cca_subject: editingComment.subject,
            comment: editingComment.comment,
            comment_type: editingComment.type
          })
        });
        if (response.ok) {
          setEditingComment(null);
          fetchStudentComments(selectedStudentId);
          fetchStudents(); // Refresh to update comment counts
        }
      }
    } catch (error) {
      console.error('Failed to save comment:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleDeleteComment = async (commentId: number) => {
    if (!selectedStudentId) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/cca/comments/${commentId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchStudentComments(selectedStudentId);
        fetchStudents(); // Refresh to update comment counts
      }
    } catch (error) {
      console.error('Failed to delete comment:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const exportToCSV = async () => {
    try {
      const response = await fetch('/api/cca/export/csv');
      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([data.csv_content], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to export CSV:', error);
    }
  };
  
  const getCommentTypeIcon = (type: 'positive' | 'neutral' | 'concern') => {
    switch (type) {
      case 'positive': return '🟢';
      case 'neutral': return '🟡';
      case 'concern': return '🔴';
      default: return '⚪';
    }
  };
  
  const getCommentTypeClass = (type: 'positive' | 'neutral' | 'concern') => {
    switch (type) {
      case 'positive': return 'comment-positive';
      case 'neutral': return 'comment-neutral';
      case 'concern': return 'comment-concern';
      default: return '';
    }
  };
  
  return (
    <div className={`app ${deviceMode}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="app-header mb-8">
          <div className="header-content">
            <div className="title-section">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">🎵 CCA Comments</h1>
              <p className="text-gray-600">Manage Co-Curricular Activities behavior comments for students</p>
            </div>
            <DeviceToggleComponent />
          </div>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column - Student Search */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">🔍 Student Search</h2>
            
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., Emma or 4B"
              className="w-full mb-4"
            />
            
            {studentsData && (
              <div>
                <p className="text-sm text-gray-600 mb-4">
                  <strong>Found {studentsData.total} students</strong>
                </p>
                
                <div className="student-list space-y-2">
                  {Object.entries(studentsData.students_by_form || {}).map(([form, students]) => (
                    <div key={form}>
                      <h3 className="font-medium text-gray-800 mb-2">🎫 {form} ({students.length} students)</h3>
                      <div className="space-y-1 mb-4">
                        {students.map((student) => (
                          <div
                            key={student.id}
                            onClick={() => setSelectedStudentId(student.id)}
                            className={`student-item ${selectedStudentId === student.id ? 'selected' : ''}`}
                          >
                            <div className="flex justify-between items-center">
                              <span className="font-medium">{student.name}</span>
                              {student.comment_count > 0 && (
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                  📝 {student.comment_count}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Data Management */}
            <div className="border-t pt-4 mt-6">
              <h3 className="font-medium text-gray-800 mb-3">📊 Data Management</h3>
              <div className="space-y-2">
                <button 
                  onClick={exportToCSV}
                  className="w-full btn-secondary"
                >
                  ⬇️ Export to CSV
                </button>
              </div>
            </div>
          </div>
          
          {/* Middle & Right Columns - Comment Manager */}
          <div className="md:col-span-2 bg-white rounded-lg shadow p-6">
            {selectedStudentId && studentCommentsData ? (
              <div>
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-900">🎯 {studentCommentsData.student_name}</h2>
                    <p className="text-gray-600"><strong>Form:</strong> {studentCommentsData.form}</p>
                  </div>
                  <button
                    onClick={() => setSelectedStudentId(null)}
                    className="btn-secondary btn-sm"
                  >
                    ← Back to List
                  </button>
                </div>
                
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="text-gray-500">Loading...</div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {ccaSubjects.map((subject) => {
                      const comment = studentCommentsData.comments_by_subject[subject];
                      return (
                        <div key={subject} className={`border rounded-lg p-4 ${comment ? `border-l-4 ${getCommentTypeClass(comment.type)}` : 'border-gray-200'}`}>
                          <div className="flex justify-between items-start mb-3">
                            <h3 className="font-semibold text-lg">📝 {subject}</h3>
                            {comment && (
                              <span className="text-sm text-gray-500">
                                {getCommentTypeIcon(comment.type)} {comment.type.charAt(0).toUpperCase() + comment.type.slice(1)}
                              </span>
                            )}
                          </div>
                          
                          {comment ? (
                            <div>
                              <p className="text-gray-700 mb-2">{comment.comment}</p>
                              <p className="text-xs text-gray-500 mb-3">
                                Last updated: {new Date(comment.timestamp).toLocaleDateString()}
                              </p>
                              <div className="flex gap-2">
                                <button
                                  onClick={() => setEditingComment({
                                    subject,
                                    comment: comment.comment,
                                    type: comment.type,
                                    commentId: comment.id,
                                    mode: 'edit'
                                  })}
                                  className="btn-primary btn-sm"
                                >
                                  ✏️ Edit
                                </button>
                                <button
                                  onClick={() => handleDeleteComment(comment.id)}
                                  className="btn-danger btn-sm"
                                >
                                  🗑️ Delete
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div>
                              <p className="text-gray-500 mb-3">No comment for this subject</p>
                              <button
                                onClick={() => setEditingComment({
                                  subject,
                                  comment: '',
                                  type: 'neutral',
                                  mode: 'add'
                                })}
                                className="btn-success btn-sm"
                              >
                                ➕ Add Comment
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">👈</div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">Select a Student</h3>
                <p className="text-gray-500">Choose a student from the list to manage their CCA comments</p>
                
                {ccaSubjects.length > 0 && (
                  <div className="mt-8">
                    <h4 className="font-semibold mb-3">📋 Available CCA Subjects</h4>
                    <div className="grid grid-cols-3 gap-2">
                      {ccaSubjects.map((subject) => (
                        <div key={subject} className="text-sm text-gray-600">
                          • {subject}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Edit/Add Comment Modal */}
        {editingComment && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" style={{ zIndex: 1000 }}>
            <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6">
              <h3 className="text-lg font-semibold mb-4">
                {editingComment.mode === 'edit' ? '✏️ Edit' : '➕ Add'} Comment - {editingComment.subject}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Comment</label>
                  <textarea
                    value={editingComment.comment}
                    onChange={(e) => setEditingComment({ ...editingComment, comment: e.target.value })}
                    placeholder="Enter CCA comment..."
                    rows={4}
                    className="w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Comment Type</label>
                  <select
                    value={editingComment.type}
                    onChange={(e) => setEditingComment({ ...editingComment, type: e.target.value as 'positive' | 'neutral' | 'concern' })}
                    className="w-full"
                  >
                    <option value="positive">🟢 Positive</option>
                    <option value="neutral">🟡 Neutral</option>
                    <option value="concern">🔴 Concern</option>
                  </select>
                </div>
              </div>
              
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveComment}
                  disabled={!editingComment.comment.trim() || isLoading}
                  className="flex-1 btn-primary"
                >
                  {isLoading ? '⏳ Saving...' : '✅ Save'}
                </button>
                <button
                  onClick={() => setEditingComment(null)}
                  className="flex-1 btn-secondary"
                  disabled={isLoading}
                >
                  ❌ Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
