from datetime import datetime
from collections import defaultdict
import hashlib
import json
from app.database import get_connection, format_timestamp, LOCAL_TZ, get_cached_session, cache_session, get_todays_merges
from app.ai import summarize_session, summarize_claude_session
from app.connectors.claude_code import get_todays_sessions as get_claude_sessions


def get_sessions_today() -> list[dict]:
    today = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM activities
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """, (today,)).fetchall()

    events = [dict(r) for r in rows]
    if not events:
        return []

    sessions = _group_by_category(events)
    for session in sessions:
        session_id = _session_id(session["events"])
        cached = get_cached_session(session_id)
        if cached:
            session["label"], session["summary"] = cached
        else:
            label, summary = summarize_session(session["events"])
            session["label"], session["summary"] = label, summary
            cache_session(session_id, label, summary)

    # Add Claude Code sessions
    for cs in get_claude_sessions():
        cached = get_cached_session(cs["session_id"])
        if cached:
            label, summary = cached
        else:
            label, summary = summarize_claude_session(cs["messages"], cs["duration_mins"])
            cache_session(cs["session_id"], label, summary)
        # Normalize messages to match browser event structure for the template
        normalized_events = [
            {
                "source": "Claude Code",
                "title": m["content"][:80] + ("…" if len(m["content"]) > 80 else ""),
                "duration_seconds": 0,
                "timestamp": m["timestamp"].isoformat(),
                "category": "ai_coding",
                "url": "",
            }
            for m in cs["messages"]
        ]
        start_local = cs["start"].astimezone(LOCAL_TZ)
        end_local = cs["end"].astimezone(LOCAL_TZ)
        sessions.append({
            "category": "ai_coding",
            "events": normalized_events,
            "total_mins": cs["duration_mins"],
            "visit_count": len(cs["messages"]),
            "time_range": f"{start_local.strftime('%-I:%M %p')} – {end_local.strftime('%-I:%M %p')}",
            "label": label,
            "summary": summary,
        })

    sessions = _apply_merges(sessions)
    return sorted(sessions, key=lambda s: s["total_mins"], reverse=True)


def _apply_merges(sessions: list[dict]) -> list[dict]:
    merges = get_todays_merges()
    if not merges:
        return sessions

    import json as _json
    session_map = {s["category"] + str(i): s for i, s in enumerate(sessions)}

    # Build id map by position (matching how frontend assigns data-id)
    id_map = {str(i + 1): s for i, s in enumerate(sessions)}
    merged_away = set()

    for merge in merges:
        target_id = merge["target_id"]
        merged_ids = _json.loads(merge["merged_ids"])
        target = id_map.get(target_id)
        if not target:
            continue
        target["label"] = merge["label"]
        target["summary"] = merge["summary"]
        # Add time from merged sessions
        for mid in merged_ids:
            src = id_map.get(mid)
            if src:
                target["total_mins"] += src.get("total_mins", 0)
                merged_away.add(mid)

    return [s for i, s in enumerate(sessions) if str(i + 1) not in merged_away]


def _group_by_category(events: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for event in events:
        category = _infer_category(event)
        groups[category].append(event)

    sessions = []
    for category, evts in groups.items():
        timestamps = [_parse_ts(e["timestamp"]) for e in evts if _parse_ts(e["timestamp"])]
        total_secs = sum(e.get("duration_seconds", 0) for e in evts)
        sessions.append({
            "category": category,
            "events": evts,
            "total_mins": max(1, total_secs // 60),
            "visit_count": len(evts),
            "time_range": _format_range(timestamps),
            "label": "",
            "summary": "",
        })

    return sessions


def _infer_category(event: dict) -> str:
    source = (event.get("source") or "").lower()
    url = (event.get("url") or "").lower()
    title = (event.get("title") or "").lower()

    if any(x in url for x in ["leetcode", "hackerrank", "codewars", "neetcode"]):
        return "coding_practice"
    if any(x in url for x in ["github", "stackoverflow", "docs.", "developer."]):
        return "coding_research"
    if any(x in url for x in ["linkedin", "greenhouse", "lever", "ashby", "glassdoor", "wellfound"]):
        return "job_search"
    if any(x in url for x in ["youtube", "netflix", "twitch", "spotify"]):
        return "entertainment"
    if any(x in url for x in ["notion", "docs.google", "confluence", "figma"]):
        return "productivity"
    if any(x in url for x in ["twitter", "reddit", "hackernews", "news"]):
        return "reading"
    if event.get("category") not in ("other", "browsing", None):
        return event["category"]
    return "other"


def _session_id(events: list[dict]) -> str:
    key = json.dumps([e.get("id") for e in events], sort_keys=True)
    return hashlib.md5(key.encode()).hexdigest()


def _format_range(timestamps: list) -> str:
    if not timestamps:
        return ""
    start = min(timestamps)
    end = max(timestamps)
    return f"{start.strftime('%-I:%M %p')} – {end.strftime('%-I:%M %p')}"


def _parse_ts(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(LOCAL_TZ)
    except Exception:
        return None
