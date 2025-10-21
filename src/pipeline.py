# src/pipeline.py
from typing import List, Dict, Any, Optional

from config.settings import LIMIT
from src.client import fetch_page   # uses build_params under the hood
#from src.query_params import build_preview_url
from state.cursor import read_last_seen, write_last_seen, safe_max_report
from src.matching import filter_records
from src.render import render_preview
from mail.compose import make_digest_message
from mail.send import send_message

def fetch_new_records(last_seen: Optional[int] = None, limit: int = LIMIT) -> List[Dict[str, Any]]:
    """
    Return rows newer than last_seen using the shared query builder.
    """
    # fetch_page uses build_params(last_seen=...) which uses our cursor WHERE
    return fetch_page(limit=limit, offset=0, last_seen=last_seen)

def process_new_records(limit: int = 200) -> None:
    last_seen = read_last_seen()
    #print("Preview URL:", build_preview_url(last_seen))
    print(f"Last seen report_number: {last_seen}")

    rows = fetch_new_records(last_seen=last_seen, limit=limit)
    matches = filter_records(rows)

    if not matches:
        print("No new matching records.")
        return

    # Optional: console preview
    print(render_preview(matches))

    # Build one email that lists all matches, one per line
    email_msg = make_digest_message(matches)
    if not email_msg.to:
        print("⚠️  DEFAULT_RECIPIENTS not set; skipping send.")
        return

    try:
        send_message(email_msg)
        print(f"Sent digest: {email_msg.subject}")

        # Advance cursor only after successful send — use ALL fetched rows
        max_report = safe_max_report(rows)
        if max_report is not None:
            write_last_seen(max_report)
            print("Updated cursor to:", max_report)
        else:
            print("No valid report_number found; cursor unchanged.")
    except Exception as e:
        print("Email send failed; cursor not advanced:", e)