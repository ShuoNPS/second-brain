import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def answer_question(question: str, activities: list[dict], emails: list[dict]) -> str:
    context = _build_context(activities, emails)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "You are a personal AI assistant with access to the user's activity log. "
            "Answer questions about what they did, learned, or worked on based on the data provided. "
            "Be concise and helpful. If the data doesn't contain enough information, say so."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Here is my activity data:\n\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    return response.content[0].text


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
