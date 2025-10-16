# Project Guardian - Digital Citizenship Breach Triage

AI-powered tool for school staff to assess digital citizenship incidents and get actionable guidance.

## Overview

Project Guardian helps teachers and school staff quickly triage digital citizenship breaches by analyzing incident descriptions and providing:
- **Classification**: LOW (Teacher-level), MEDIUM (Head of Year), or HIGH (DSL-level)
- **Reasoning**: Why the incident received that classification
- **Next Steps**: Specific actionable steps to take
- **Contact Information**: Who needs to be notified

## Architecture

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI (Python) with Google Gemini AI integration
- **Database**: None (no data is stored)

## Setup

### 1. Install Dependencies

```bash
cd /Users/cantillonpatrick/Desktop/RAG_2/ptcc/frontend/project-guardian
npm install
```

### 2. Configure API Key

You need a Google Gemini API key. Get one free from [Google AI Studio](https://aistudio.google.com/app/apikey).

Add your API key to the `.env` file:
```bash
VITE_API_KEY=your_gemini_api_key_here
```

And add it to the backend environment (in the main PTCC `.env` file or export it):
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
```

Or add to `/Users/cantillonpatrick/Desktop/RAG_2/ptcc/.env`:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install Python Dependencies

```bash
pip install google-generativeai
```

## Running the Application

### Option 1: Integrated with PTCC (Streamlit)

1. Start the PTCC backend:
   ```bash
   cd /Users/cantillonpatrick/Desktop/RAG_2/ptcc
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. Start the Streamlit frontend:
   ```bash
   streamlit run frontend/desktop-web/app.py --server.port 8501
   ```

3. Navigate to **Project Guardian** in the sidebar

### Option 2: Standalone React App

1. Start the PTCC backend (needed for API calls):
   ```bash
   cd /Users/cantillonpatrick/Desktop/RAG_2/ptcc
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. Start the React dev server:
   ```bash
   cd frontend/project-guardian
   npm run dev
   ```

3. Open [http://localhost:5174](http://localhost:5174)

## Usage

1. Select the student's **Year Group** (3-6)
2. Indicate if this is a **First incident** or **Repeated offense**
3. Describe the incident (without using student names)
4. Click **Get Assessment**
5. Review the AI-generated classification, reasoning, and next steps

## Security & Privacy

- **No data is stored**: All assessments are processed in real-time and not saved
- **No PII**: Users are instructed not to include student names or identifiable information
- **Confidential**: Tool is for school staff use only
- **AI Advisory**: Always emphasizes that this is a decision support tool, not a replacement for professional judgment

## Assessment Criteria

### LOW (🟢 Teacher Level)
- Minor, unintentional, first-time offenses
- Limited impact, no malicious intent
- Examples: Using non-compliant apps, silly comments, accidental sharing

### MEDIUM (🟡 Head of Year)
- Deliberate but not severe breaches
- Repeated minor offenses
- Wider impact on others
- Examples: Minor cyberbullying, inappropriate searches, persistent rule-breaking

### HIGH (🔴 DSL/Safeguarding)
- Serious, malicious, or illegal behavior
- Significant risk to student or others
- Clear safeguarding concern
- Examples: Serious cyberbullying, explicit content, threats, discrimination

## Troubleshooting

**"AI service not configured"**: Ensure `GEMINI_API_KEY` is set in your environment or `.env` file

**"Failed to get assessment"**: Check that the backend is running on port 8000 and accessible

**CORS errors**: Verify that `http://localhost:5174` is in the CORS allowed origins in `backend/main.py`

## Development

Build for production:
```bash
npm run build
```

The built files will be in the `dist/` directory.

## License

Part of the PTCC (Personal Teaching Command Center) system.
