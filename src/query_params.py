from urllib.parse import urlencode
from typing import Dict, Optional

from config.settings import (
    SELECT, ORDER, LIMIT, BASE, CURSOR_FIELD
)
from filters.filer_names import FILER_NAMES
from src.soql import in_list_clause
from config.credentials import SOCRATA_APP_TOKEN

def build_static_where() -> str:
    if not FILER_NAMES:
        raise ValueError("Please populate FILER_NAMES with your target committees.")
    return in_list_clause("filer_name", FILER_NAMES)

def build_params(last_seen: Optional[str] = None) -> Dict[str, str]:
    """Build the SoQL params dict. Optionally append a cursor (> last_seen)."""
    where_clauses = [build_static_where()]
    if last_seen is not None:
        where_clauses.append(f"{CURSOR_FIELD} > {last_seen}")

    params = {
        "$select": SELECT,
        "$where": " AND ".join(where_clauses),
        "$order": ORDER,
        "$limit": str(LIMIT),
    }
    return params

def build_preview_url(last_seen: Optional[str] = None) -> str:
    q = build_params(last_seen)
    return f"{BASE}?{urlencode(q)}"

def socrata_headers() -> Dict[str, str]:
    return {"X-App-Token": SOCRATA_APP_TOKEN} if SOCRATA_APP_TOKEN else {}
