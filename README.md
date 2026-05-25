# Second Brain

A personal AI-native life logger that passively captures what you do and builds your second brain automatically.

## Features

- **Passive Activity Logging** — Automatically track time spent on configured websites via ActivityWatch, emails from Gmail, and calendar events
- **Daily Dashboard** — View all your activities, emails, and sessions in one place with intelligent pagination
- **AI Q&A** — Ask natural language questions about what you did, learned, or worked on
- **Focus Sessions** — Create and track focused work sessions on projects or goals with notes and completion tracking
- **AI Chat Agent** — Conversational interface to analyze your activities and get insights
- **Session Merging** — Intelligently merge and summarize related work sessions
- **Hourly Sync** — Automatically syncs data from ActivityWatch, Gmail, and Calendar every hour

## Getting Started

### Prerequisites
- Python 3.8+
- ActivityWatch running locally (for activity tracking)
- Google credentials (for Gmail and Calendar access)

### Setup

1. Clone and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure your sources in `config.yaml`:
```yaml
sources:
  - name: LeetCode
    type: browser
    url: leetcode.com
    category: coding_practice
  - name: Gmail
    type: api
    connector: gmail
    category: communication
```

3. Set up environment variables in `.env`:
```
GOOGLE_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_anthropic_key
```

4. Run the app:
```bash
python -m uvicorn app.main:app --reload
```

Visit `http://localhost:8000` to access the dashboard.

## How It Works

### Data Sources
- **ActivityWatch** — Browser activity tracking for configured websites
- **Gmail** — Email monitoring and analysis
- **Google Calendar** — Event tracking
- **Focus Sessions** — Manual project/goal tracking

### Core Components
- **Sync** (`app/sync.py`) — Pulls data from connectors and stores in SQLite
- **Database** (`app/database.py`) — SQLite storage for activities, emails, sessions
- **AI** (`app/ai.py`) — Claude API integration for Q&A and chat
- **Connectors** (`app/connectors/`) — Data source integrations (ActivityWatch, Gmail, Calendar, etc.)

## Dashboard Features

- **Activities** — Paginated view of today's activities with timestamps
- **Emails** — Recent emails from Gmail with pagination
- **Calendar** — Today's events
- **Focus Sessions** — Manage your projects and goals with notes and completion status
- **Ask** — Query your activities with natural language questions
- **Chat** — Interactive AI agent for deeper analysis

## Development

See [PRD](docs/PRD.md) for the full product specification and roadmap.

## Architecture

- **Backend**: FastAPI + SQLite
- **Frontend**: HTMX (server-rendered, minimal JavaScript)
- **AI**: Claude API for Q&A and summarization
- **Data**: Local-first, privacy-preserving architecture
