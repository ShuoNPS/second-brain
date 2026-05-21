import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def _generate(prompt: str) -> str:
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text.strip()


def answer_question(question: str, activities: list[dict], emails: list[dict]) -> str:
    context = _build_context(activities, emails)
    prompt = (
        "You are a personal AI assistant with access to the user's activity log.\n"
        "Answer the question based on the data provided.\n\n"
        "Format your response as structured sections using this style:\n"
        "📌 Section Title\n"
        "  • bullet point\n"
        "  • bullet point\n\n"
        "Use relevant emojis for section titles (e.g. 🧠 Deep Work, 💼 Job Search, 📅 Upcoming, 📧 Emails).\n"
        "Be concise. Only include sections that have relevant data.\n"
        "If the data doesn't contain enough information, say so briefly.\n\n"
        f"Activity data:\n{context}\n\nQuestion: {question}"
    )
    return _generate(prompt)


def summarize_session(events: list[dict]) -> tuple[str, str]:
    total_mins = sum(e.get("duration_seconds", 0) for e in events) // 60

    seen = set()
    unique_titles = []
    for e in events:
        t = (e.get("title") or "").strip()
        if t and t not in seen:
            seen.add(t)
            unique_titles.append(f"- {t} ({e.get('duration_seconds', 0) // 60} mins)")

    prompt = (
        f"A user spent {total_mins} minutes on these pages:\n"
        f"{chr(10).join(unique_titles[:15])}\n\n"
        f"1. Give a short label (3-5 words) with a relevant emoji for what they were working on.\n"
        f"2. Write one sentence describing what they did, including specific page/problem names where relevant.\n\n"
        f"Respond in exactly this format:\n"
        f"LABEL: <emoji> <label>\n"
        f"SUMMARY: <one sentence>"
    )
    try:
        text = _generate(prompt)
        label, summary = "", ""
        for line in text.splitlines():
            if line.startswith("LABEL:"):
                label = line.replace("LABEL:", "").strip()
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
        return label or "🌐 Browsing", summary or ""
    except Exception:
        return "🌐 Browsing", ""


def summarize_merged_sessions(labels: list[str], summaries: list[str]) -> tuple[str, str]:
    prompt = (
        f"The following work sessions are being merged into one:\n\n"
        + "\n".join(f"- {l}: {s}" for l, s in zip(labels, summaries))
        + "\n\n"
        f"Generate a single combined label and summary.\n"
        f"1. Give a short label (3-5 words) with a relevant emoji.\n"
        f"2. Write one sentence summarizing all the work done.\n\n"
        f"Respond in exactly this format:\n"
        f"LABEL: <emoji> <label>\n"
        f"SUMMARY: <one sentence>"
    )
    try:
        text = _generate(prompt)
        label, summary = "", ""
        for line in text.splitlines():
            if line.startswith("LABEL:"):
                label = line.replace("LABEL:", "").strip()
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
        return label or labels[0], summary or summaries[0]
    except Exception:
        return labels[0], summaries[0]


def summarize_claude_session(messages: list[dict], duration_mins: int) -> tuple[str, str]:
    user_messages = [m["content"] for m in messages if m.get("role") == "user"][:15]
    prompt = (
        f"A user spent {duration_mins} minutes in a Claude Code AI coding session.\n"
        f"Here are their messages:\n"
        + "\n".join(f"- {m}" for m in user_messages)
        + "\n\n"
        f"1. Give a short label (3-5 words) with a relevant emoji for what they were working on.\n"
        f"2. Write one sentence describing what they built or discussed in detail.\n\n"
        f"Respond in exactly this format:\n"
        f"LABEL: <emoji> <label>\n"
        f"SUMMARY: <one sentence>"
    )
    try:
        text = _generate(prompt)
        label, summary = "", ""
        for line in text.splitlines():
            if line.startswith("LABEL:"):
                label = line.replace("LABEL:", "").strip()
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
        return label or "🤖 AI Coding Session", summary or ""
    except Exception:
        return "🤖 AI Coding Session", ""


def summarize_email(sender: str, subject: str, snippet: str) -> str:
    prompt = (
        f"Summarize this email in one short sentence (max 20 words).\n\n"
        f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}"
    )
    try:
        return _generate(prompt)
    except Exception:
        return snippet[:100]


def _build_context(activities: list[dict], emails: list[dict]) -> str:
    parts = []

    if activities:
        parts.append("=== Browser Activity ===")
        for a in activities:
            mins = a["duration_seconds"] // 60
            parts.append(f"- {a['source']} | {a['title']} | {mins} mins | {a['timestamp']}")

    if emails:
        parts.append("\n=== Emails ===")
        for e in emails:
            parts.append(f"- From: {e['sender']} | Subject: {e['subject']} | {e['timestamp']}")

    return "\n".join(parts) if parts else "No activity data available."
