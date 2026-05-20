# PRD: Second Brain — Personal AI Life Logger

## Problem Statement

Knowledge workers and learners face two compounding problems:

1. **Context switching overhead** — juggling work, personal projects, and home tasks creates mental load, anxiety, and lost momentum
2. **Knowledge fragmentation** — notes are scattered, retrieval is broken, and manual capture adds friction that kills consistency

Existing tools (Notion, Obsidian, Apple Notes) all require deliberate manual input. People don't use them consistently because capturing feels like a second job.

## Core Insight

The best capture is no capture. An AI-native life logger should passively observe what you do and build your second brain automatically. Manual input is a fallback, not the default.

---

## Target User

Solo individual (initially: the builder themselves) who:
- Juggles multiple projects simultaneously
- Wants to learn and retain knowledge better
- Feels anxious about open loops and unfinished tasks
- Dislikes manual note-taking

---

## Passive Capture Sources

| Source | What it captures | Effort |
|---|---|---|
| Browser history | Sites visited, time spent (LeetCode, GitHub, YouTube) | Low |
| Calendar | Meetings, blocked time, events | Low |
| Gmail | Emails sent/received, recruiters, decisions | Low |
| Git commits | Code written, repos worked on | Low |
| LeetCode API | Problems solved, submissions, difficulty | Medium |
| App/screen time | Time per app on desktop/mobile | Medium |
| Screen summarization | Periodic screenshot → AI summary | High |
| Voice | Ambient transcription + summarization | High |

**MVP focuses on:** Browser history + Calendar + Gmail + LeetCode

---

## Core Features

### 1. Passive Activity Logging
- Runs silently in the background (browser extension + desktop agent)
- Every N minutes, summarizes what you've been doing
- Stores structured activity log: `{timestamp, activity, category, duration, notes}`
- Example: *"3:00–5:30pm — LeetCode: solved 2 medium problems (Binary Search, Sliding Window)"*

### 2. Brain Dump
- Frictionless quick capture: voice memo, text, photo
- AI instantly categorizes, tags, and links it to existing knowledge
- No folders, no manual organization

### 3. Daily Summary
- Every evening: AI generates a digest of what you did, learned, and left unfinished
- Flags open loops so your brain can let go of them
- Suggests what to prioritize tomorrow

### 4. Semantic Search & Q&A
- Ask in natural language: *"What did I work on last Tuesday?"* or *"What do I know about sliding window?"*
- Returns relevant notes, activities, and context — not just keyword matches

### 5. Context Resume
- When switching back to a task, AI shows: last action, where you left off, relevant notes
- Reduces the "where was I?" tax

---

## Out of Scope (V1)
- Multi-user / team features
- Mobile app (desktop + browser extension first)
- Integrations beyond the MVP capture sources

---

## Technical Architecture (High Level)
- **Capture layer**: Browser extension + lightweight desktop agent
- **Storage**: Local SQLite (privacy-first, no cloud required)
- **AI layer**: Claude API for summarization, categorization, Q&A
- **Interface**: Simple web UI (FastAPI + HTMX) or CLI

---

## Success Metrics (Personal)
- Zero manual logging required for >80% of daily activities
- Can answer "what did I do/learn this week?" without thinking
- Noticeable reduction in end-of-day anxiety about open loops
