from datetime import datetime, timedelta, timezone
from app.config import load_config, get_browser_sources, get_api_sources
from app.connectors.activitywatch import get_browser_activity
from app.connectors.gmail import get_recent_emails
from app.database import insert_activity, insert_email
import json


def sync_activitywatch():
    config = load_config()
    browser_sources = get_browser_sources(config)
    tracked_urls = [s["url"] for s in browser_sources]
    source_map = {s["url"]: s for s in browser_sources}

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)

    events = get_browser_activity(start, end, tracked_urls)

    for event in events:
        matched = event["matched_source"]
        source = source_map[matched]
        insert_activity(
            source=source["name"],
            category=source["category"],
            timestamp=event["timestamp"],
            url=event["url"],
            title=event["title"],
            duration_seconds=event["duration_seconds"],
            raw_data=json.dumps(event),
        )

    print(f"[sync] ActivityWatch: {len(events)} events synced")


def sync_gmail():
    emails = get_recent_emails(hours=1)
    for email in emails:
        insert_email(
            message_id=email["message_id"],
            timestamp=email["timestamp"],
            sender=email["sender"],
            subject=email["subject"],
            snippet=email["snippet"],
            category="communication",
        )
    print(f"[sync] Gmail: {len(emails)} emails synced")


def sync_all():
    print(f"[sync] Starting sync at {datetime.now()}")
    sync_activitywatch()
    sync_gmail()
    print(f"[sync] Done")
