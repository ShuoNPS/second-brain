from datetime import datetime, timezone
from app.connectors.gmail import get_gmail_service
from googleapiclient.discovery import build
import pickle
from pathlib import Path

TOKEN_PATH = Path("token.pickle")


def get_calendar_service():
    with open(TOKEN_PATH, "rb") as f:
        creds = pickle.load(f)
    return build("calendar", "v3", credentials=creds)


def get_todays_events() -> list[dict]:
    service = get_calendar_service()

    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)

    result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for item in result.get("items", []):
        start = item["start"].get("dateTime", item["start"].get("date", ""))
        end = item["end"].get("dateTime", item["end"].get("date", ""))
        events.append({
            "title": item.get("summary", "No title"),
            "start": start,
            "end": end,
            "location": item.get("location", ""),
            "description": item.get("description", ""),
            "attendees": [a.get("email") for a in item.get("attendees", [])],
            "meet_link": item.get("hangoutLink", ""),
        })

    return events
