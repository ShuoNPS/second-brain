import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def get_todays_sessions() -> list[dict]:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    sessions = {}

    for jsonl_file in CLAUDE_PROJECTS_DIR.rglob("*.jsonl"):
        try:
            _parse_file(jsonl_file, sessions, today)
        except Exception:
            continue

    result = []
    for session_id, data in sessions.items():
        if not data["messages"]:
            continue
        timestamps = [m["timestamp"] for m in data["messages"]]
        start = min(timestamps)
        end = max(timestamps)
        duration_mins = max(1, int((end - start).total_seconds() / 60))

        result.append({
            "session_id": session_id,
            "start": start,
            "end": end,
            "duration_mins": duration_mins,
            "duration_seconds": duration_mins * 60,
            "messages": data["messages"],
            "cwd": data.get("cwd", ""),
            "source": "Claude Code",
            "category": "ai_coding",
            "title": f"Claude Code session ({duration_mins} mins)",
            "url": "",
            "timestamp": start.isoformat(),
        })

    return sorted(result, key=lambda s: s["start"])


def _parse_file(path: Path, sessions: dict, since: datetime):
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except Exception:
                continue

            if entry.get("type") not in ("user", "assistant"):
                continue

            ts_str = entry.get("timestamp")
            if not ts_str:
                continue

            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if ts < since:
                continue

            session_id = entry.get("sessionId", path.stem)
            if session_id not in sessions:
                sessions[session_id] = {
                    "messages": [],
                    "cwd": entry.get("cwd", ""),
                }

            content = entry.get("message", {}).get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"
                )

            if content and entry["type"] == "user":
                sessions[session_id]["messages"].append({
                    "role": "user",
                    "content": str(content)[:300],
                    "timestamp": ts,
                })
