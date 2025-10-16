# PTCC Dashboard

React-based dashboard for managing PTCC agents, workflows, and tasks.

## Features

- **Agent Management** - View all registered agents with stats
- **Workflow Monitoring** - Track available workflows
- **Task History** - Monitor recent task executions
- **System Statistics** - Real-time system metrics
- **Quick Actions** - Generate lesson plans, assessments, and feedback

## Setup

### 1. Install Dependencies

```bash
cd frontend/dashboard
npm install
```

### 2. Start Backend

Make sure the PTCC backend is running:

```bash
cd ../../
./scripts/start_ptcc.sh
```

Backend should be running on `http://localhost:8001`

### 3. Start Dashboard

```bash
npm run dev
```

Dashboard will open at `http://localhost:3000`

## Usage

### Agents View
- See all registered agents
- View agent capabilities and status
- Monitor execution statistics

### Workflows View
- Browse available workflow templates
- Execute workflows
- Track workflow performance

### Task History
- View recent task executions
- See execution times and costs
- Monitor success/failure rates

### Statistics
- Total tasks executed
- Success rate
- Average execution time
- Total API costs
- Active agents count

### Quick Actions
- **Lesson Plan Generator**: Create lesson plans instantly
- **Assessment Generator**: Generate quizzes and tests
- **Feedback Composer**: Create student feedback

## API Endpoints Used

- `GET /api/orchestration/agents` - List agents
- `GET /api/workflows/` - List workflows
- `GET /api/orchestration/tasks/history` - Task history
- `GET /api/orchestration/stats/overview` - System stats
- `POST /api/orchestration/quick/lesson-plan` - Generate lesson
- `POST /api/orchestration/quick/assessment` - Generate assessment
- `POST /api/orchestration/quick/feedback` - Compose feedback

## Development

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **CSS3** - Styling with animations
- **Fetch API** - HTTP requests

## Troubleshooting

### "Failed to fetch agents"

Make sure the backend is running:
```bash
curl http://localhost:8001/health
```

### CORS Errors

Ensure backend allows `http://localhost:3000` in CORS settings (already configured in `backend/main.py`).

### Port Already in Use

Change port in `vite.config.js`:
```js
server: {
  port: 3001  // Change to different port
}
```

## Screenshots

Dashboard includes:
- Modern gradient header
- Responsive grid layouts
- Real-time data updates
- Smooth animations
- Mobile-friendly design

## Future Enhancements

- [ ] Workflow execution interface
- [ ] Real-time task monitoring
- [ ] Agent configuration editor
- [ ] Task detail modals
- [ ] Export/import functionality
- [ ] Dark mode
- [ ] User authentication
