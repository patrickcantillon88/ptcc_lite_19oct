import { useState, useCallback } from 'react'
import { useDeviceMode } from '../../shared/DeviceToggle.jsx'
import '../../shared/DeviceToggle.css'
import './App.css'

function App() {
  const { deviceMode, DeviceToggleComponent } = useDeviceMode('quiz-upload')
  const [uploadState, setUploadState] = useState('idle') // idle, uploading, success, error
  const [uploadResult, setUploadResult] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [formData, setFormData] = useState({
    subject: '',
    topic: '',
    quiz_date: ''
  })
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setSelectedFile(file)
      } else {
        alert('Please upload a CSV file')
      }
    }
  }, [])

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
      setSelectedFile(file)
    } else {
      alert('Please select a CSV file')
    }
  }

  const uploadQuiz = async () => {
    if (!selectedFile) {
      alert('Please select a CSV file')
      return
    }

    setUploadState('uploading')
    setUploadResult(null)

    const formDataToSend = new FormData()
    formDataToSend.append('file', selectedFile)
    if (formData.subject) formDataToSend.append('subject', formData.subject)
    if (formData.topic) formDataToSend.append('topic', formData.topic)
    if (formData.quiz_date) formDataToSend.append('quiz_date', formData.quiz_date)

    try {
      const response = await fetch('/api/quiz-analytics/upload', {
        method: 'POST',
        body: formDataToSend
      })

      const result = await response.json()

      if (response.ok) {
        setUploadState('success')
        setUploadResult(result)
      } else {
        setUploadState('error')
        setUploadResult(result)
      }
    } catch (error) {
      setUploadState('error')
      setUploadResult({ detail: `Network error: ${error.message}` })
    }
  }

  const resetUpload = () => {
    setUploadState('idle')
    setSelectedFile(null)
    setUploadResult(null)
    setFormData({ subject: '', topic: '', quiz_date: '' })
  }

  return (
    <div className={`app ${deviceMode}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="title-section">
            <h1>📤 Upload Quiz Results</h1>
            <p>Upload CSV files with quiz results for automatic processing and analysis</p>
          </div>
          <DeviceToggleComponent />
        </div>
      </header>

      <div className="upload-section">
        {uploadState === 'idle' && (
          <div className="upload-interface">
            <div className="form-section">
              <h2>📝 Quiz Information</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="subject">Subject (optional)</label>
                  <input
                    id="subject"
                    type="text"
                    placeholder="e.g., Mathematics, English"
                    value={formData.subject}
                    onChange={(e) => setFormData({...formData, subject: e.target.value})}
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="topic">Topic (optional)</label>
                  <input
                    id="topic"
                    type="text"
                    placeholder="e.g., Fractions, Grammar"
                    value={formData.topic}
                    onChange={(e) => setFormData({...formData, topic: e.target.value})}
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="quiz_date">Quiz Date (optional)</label>
                  <input
                    id="quiz_date"
                    type="date"
                    value={formData.quiz_date}
                    onChange={(e) => setFormData({...formData, quiz_date: e.target.value})}
                  />
                </div>
              </div>
            </div>

            <div 
              className={`file-drop-zone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'file-selected' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              {selectedFile ? (
                <div className="selected-file">
                  <div className="file-icon">📄</div>
                  <div className="file-info">
                    <div className="file-name">{selectedFile.name}</div>
                    <div className="file-size">
                      {(selectedFile.size / 1024).toFixed(2)} KB
                    </div>
                  </div>
                  <button 
                    className="remove-file-btn"
                    onClick={() => setSelectedFile(null)}
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <div className="drop-zone-content">
                  <div className="drop-zone-icon">📁</div>
                  <h3>Drop CSV file here</h3>
                  <p>or click to browse files</p>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    className="file-input"
                  />
                </div>
              )}
            </div>

            <div className="format-guide">
              <h3>📋 Expected CSV Format</h3>
              <div className="format-examples">
                <div className="format-example">
                  <h4>Supported Columns:</h4>
                  <ul>
                    <li><strong>Student Name:</strong> "Student Name", "Name", "Student", "Participant"</li>
                    <li><strong>Score:</strong> "Score", "Points", "Percentage", "%", "Accuracy"</li>
                    <li><strong>Max Score:</strong> "Max Score", "Out of", "Maximum" (optional)</li>
                  </ul>
                </div>
                <div className="format-example">
                  <h4>Example CSV:</h4>
                  <div className="csv-preview">
                    Student Name,Score,Max Score<br/>
                    John Smith,18,20<br/>
                    Emma Johnson,85%<br/>
                    Mike Davis,92
                  </div>
                </div>
              </div>
            </div>

            <button 
              className="upload-btn"
              onClick={uploadQuiz}
              disabled={!selectedFile}
            >
              🚀 Upload Quiz Results
            </button>
          </div>
        )}

        {uploadState === 'uploading' && (
          <div className="upload-status uploading">
            <div className="status-icon">⏳</div>
            <h2>Processing Quiz Results...</h2>
            <div className="loading-bar">
              <div className="loading-progress"></div>
            </div>
            <p>Parsing CSV, matching students, and storing results</p>
          </div>
        )}

        {uploadState === 'success' && uploadResult && (
          <div className="upload-status success">
            <div className="status-icon">✅</div>
            <h2>Upload Successful!</h2>
            
            <div className="results-grid">
              <div className="result-card">
                <div className="result-value">{uploadResult.records_processed}</div>
                <div className="result-label">Records Processed</div>
              </div>
              <div className="result-card">
                <div className="result-value">{uploadResult.records_inserted}</div>
                <div className="result-label">Records Inserted</div>
              </div>
              <div className="result-card">
                <div className="result-value">{uploadResult.errors?.length || 0}</div>
                <div className="result-label">Errors</div>
              </div>
              <div className="result-card">
                <div className="result-value">{uploadResult.warnings?.length || 0}</div>
                <div className="result-label">Warnings</div>
              </div>
            </div>

            <div className="upload-details">
              <h3>📊 Upload Details</h3>
              <div className="detail-item">
                <strong>Quiz Name:</strong> {uploadResult.quiz_name}
              </div>
              <div className="detail-item">
                <strong>Upload Date:</strong> {new Date(uploadResult.upload_date).toLocaleString()}
              </div>
            </div>

            {uploadResult.warnings && uploadResult.warnings.length > 0 && (
              <div className="warnings-section">
                <h3>⚠️ Warnings</h3>
                <ul className="warnings-list">
                  {uploadResult.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}

            {uploadResult.errors && uploadResult.errors.length > 0 && (
              <div className="errors-section">
                <h3>❌ Errors</h3>
                <ul className="errors-list">
                  {uploadResult.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="action-buttons">
              <button className="upload-another-btn" onClick={resetUpload}>
                📤 Upload Another Quiz
              </button>
              <button 
                className="view-analytics-btn"
                onClick={() => window.open('http://localhost:5184', '_blank')}
              >
                📈 View Performance Trends
              </button>
            </div>
          </div>
        )}

        {uploadState === 'error' && uploadResult && (
          <div className="upload-status error">
            <div className="status-icon">❌</div>
            <h2>Upload Failed</h2>
            <div className="error-message">
              {uploadResult.detail || 'An unknown error occurred'}
            </div>
            <button className="retry-btn" onClick={resetUpload}>
              🔄 Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
