# state/cursor.py
import json
from pathlib import Path
from typing import Optional, Iterable, Dict, Any

STATE_PATH = Path("state/state.json")

def read_last_seen(path: Path = STATE_PATH) -> Optional[int]:
    """Return last_seen_report_number if saved; otherwise None."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        val = data.get("last_seen_report_number")
        return int(val) if val is not None else None
    except Exception:
        return None

def write_last_seen(last_seen: int, path: Path = STATE_PATH) -> None:
    """Save the most recent report_number we've processed."""
    path.write_text(json.dumps({"last_seen_report_number": int(last_seen)}))

def safe_max_report(rows: Iterable[Dict[str, Any]]) -> Optional[int]:
    """Return the largest numeric report_number from the given rows."""
    max_val: Optional[int] = None
    for r in rows:
        rn = r.get("report_number")
        try:
            v = int(rn)
            if max_val is None or v > max_val:
                max_val = v
        except (TypeError, ValueError):
            pass
    return max_val