# src/query_params.py

from urllib.parse import urlencode
from typing import Dict, Optional

from config.settings import (
    SELECT, ORDER, LIMIT, BASE,
    CURSOR_TS_FIELD, CURSOR_TIE_FIELD
)
from src.filer_names import FILER_NAMES
from src.soql import in_list_clause
from config.credentials import SOCRATA_APP_TOKEN
from state.cursor import Cursor

def _escape_soql_string(s: str) -> str:
    # SoQL string escaping: single quote doubled
    return s.replace("'", "''")

def build_static_where() -> str:
    if not FILER_NAMES:
        raise ValueError("Please populate FILER_NAMES with your target committees.")
    return in_list_clause("filer_name", FILER_NAMES)

def build_cursor_where(last_seen: Optional[Cursor]) -> str:
    """
    (static filer filter) AND (
        cursor_ts > '...'
        OR (cursor_ts = '...' AND cursor_tie > '...')
    )
    """
    base = build_static_where()
    if last_seen:
        ts = _escape_soql_string(last_seen.ts)
        tie = _escape_soql_string(last_seen.tie)

        # Use the *aliases* you selected (cursor_ts/cursor_tie),
        # not the raw Socrata fields, for consistency.
        cursor_clause = (
            f"(cursor_ts > '{ts}' OR (cursor_ts = '{ts}' AND cursor_tie > '{tie}'))"
        )
        return f"{base} AND {cursor_clause}"

    return base

def build_params(last_seen: Optional[Cursor] = None) -> Dict[str, str]:
    where = build_cursor_where(last_seen)
    params = {
        "$select": SELECT,
        "$where": where,
        "$order": ORDER,
        "$limit": str(LIMIT),
    }
    return params

def build_preview_url(last_seen: Optional[Cursor] = None) -> str:
    q = build_params(last_seen)
    return f"{BASE}?{urlencode(q)}"

def socrata_headers() -> Dict[str, str]:
    return {"X-App-Token": SOCRATA_APP_TOKEN} if SOCRATA_APP_TOKEN else {}