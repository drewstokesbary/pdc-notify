# src/pipeline.py

from typing import List, Dict, Any, Optional

from config.settings import LIMIT
from src.client import fetch_page
from state.cursor import read_last_seen, write_last_seen, max_cursor, Cursor
from src.matching import filter_records
from src.render import render_preview
from mail.compose import make_digest_message
from mail.send import send_message

def fetch_new_records(last_seen: Optional[Cursor] = None, limit: int = LIMIT) -> List[Dict[str, Any]]:
    return fetch_page(limit=limit, offset=0, last_seen=last_seen)

def process_new_records(limit: int = 200) -> None:
    last_seen = read_last_seen()
    print(f"Last seen cursor: {last_seen}")

    rows = fetch_new_records(last_seen=last_seen, limit=limit)
    matches = filter_records(rows)

    if not matches:
        print("No new matching records.")
        return

    print(render_preview(matches))

    email_msg = make_digest_message(matches)
    if not email_msg.to:
        print("⚠️  DEFAULT_RECIPIENTS not set; skipping send.")
        return

    try:
        send_message(email_msg)
        print(f"Sent digest: {email_msg.subject}")

        # Advance cursor only after successful send — use ALL fetched rows
        new_cursor = max_cursor(rows)
        if new_cursor is not None:
            write_last_seen(new_cursor)
            print("Updated cursor to:", new_cursor)
        else:
            print("No valid cursor fields found; cursor unchanged.")
    except Exception as e:
        print("Email send failed; cursor not advanced:", e)