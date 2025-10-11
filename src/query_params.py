from urllib.parse import urlencode
from typing import Dict, Optional

from config.settings import (
    SELECT, ORDER, LIMIT, BASE, CURSOR_FIELD
)
from src.filer_names import FILER_NAMES
from src.soql import in_list_clause
from config.credentials import SOCRATA_APP_TOKEN

def build_static_where() -> str:
    if not FILER_NAMES:
        raise ValueError("Please populate FILER_NAMES with your target committees.")
    return in_list_clause("filer_name", FILER_NAMES)

def build_cursor_where(last_seen: Optional[int]) -> str:
    """
    Combine static filer filter with the 'newer than last_seen' condition.
    We match your existing behavior: cast to int, then compare as a quoted string.
    """
    base = build_static_where()
    if last_seen:
        return f"{base} AND {CURSOR_FIELD} > '{int(last_seen)}'"
    return base

def build_params(last_seen: Optional[int] = None) -> Dict[str, str]:
    """Build the SoQL params dict. Optionally append a cursor (> last_seen)."""
    where = build_cursor_where(last_seen)

    params = {
        "$select": SELECT,
        "$where": where,
        "$order": ORDER,
        "$limit": str(LIMIT),
    }
    return params

def build_preview_url(last_seen: Optional[int] = None) -> str:
    q = build_params(last_seen)
    return f"{BASE}?{urlencode(q)}"

def socrata_headers() -> Dict[str, str]:
    return {"X-App-Token": SOCRATA_APP_TOKEN} if SOCRATA_APP_TOKEN else {}
