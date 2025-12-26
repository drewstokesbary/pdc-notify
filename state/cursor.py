# state/cusory.py

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable, Dict, Any

STATE_PATH = Path("state/cursor.json")

@dataclass(frozen=True)
class Cursor:
    ts: str   # ISO-8601 string
    tie: str  # string tie-breaker (report_number, report_id, etc.)

def read_last_seen(path: Path = STATE_PATH) -> Optional[Cursor]:
    """
    Reads the composite cursor:
      {"last_seen": {"ts": "...", "tie": "..."}}

    Backward compatible with your old format:
      {"last_seen_report_number": 123456789}
    In that case, returns None so you effectively re-baseline using timestamp logic.
    (You could alternatively treat it as tie-only, but without a timestamp it's not safe.)
    """
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())

        # New format
        last = data.get("last_seen")
        if isinstance(last, dict):
            ts = last.get("ts")
            tie = last.get("tie")
            if ts and tie is not None:
                return Cursor(ts=str(ts), tie=str(tie))

        # Old format present -> return None (forces one-time re-baseline)
        if data.get("last_seen_report_number") is not None:
            return None

        return None
    except Exception:
        return None

def write_last_seen(cursor: Cursor, path: Path = STATE_PATH) -> None:
    path.write_text(json.dumps({"last_seen": {"ts": cursor.ts, "tie": cursor.tie}}))

def max_cursor(rows: Iterable[Dict[str, Any]]) -> Optional[Cursor]:
    """
    Rows must include cursor_ts and cursor_tie fields (from SELECT aliases).
    Assumes cursor_ts is ISO-8601 so lexicographic ordering is chronological.
    """
    best: Optional[Cursor] = None
    for r in rows:
        ts = r.get("cursor_ts")
        tie = r.get("cursor_tie")
        if not ts or tie is None:
            continue
        c = Cursor(ts=str(ts), tie=str(tie))
        if best is None or (c.ts, c.tie) > (best.ts, best.tie):
            best = c
    return best