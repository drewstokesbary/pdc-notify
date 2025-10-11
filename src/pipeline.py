# src/pipeline.py
from typing import List, Dict, Any, Optional

from config.settings import LIMIT
from src.client import fetch_page   # uses build_params under the hood
from src.query_params import build_preview_url
from state.cursor import read_last_seen, write_last_seen, safe_max_report
from src.matching import filter_records
from src.render import render_preview

def fetch_new_records(last_seen: Optional[int] = None, limit: int = LIMIT) -> List[Dict[str, Any]]:
    """
    Return rows newer than last_seen using the shared query builder.
    """
    # fetch_page uses build_params(last_seen=...) which uses our cursor WHERE
    return fetch_page(limit=limit, offset=0, last_seen=last_seen)

def process_new_records(limit: int = 200) -> None:
    """Full cycle: load cursor, fetch, filter, preview, update cursor."""
    last_seen = read_last_seen()
    print("Preview URL:", build_preview_url(last_seen))
    print(f"Last seen report_number: {last_seen}")

    rows = fetch_new_records(last_seen=last_seen, limit=limit)
    matches = filter_records(rows)

    if not matches:
        print("No new matching records.")
        return

    # Show preview
    print(render_preview(matches))

    # Advance cursor based on ALL fetched rows (not just matches)
    max_report = safe_max_report(rows)
    if max_report is not None:
        write_last_seen(max_report)
        print("Updated cursor to:", max_report)
    else:
        print("No valid report_number found; cursor unchanged.")