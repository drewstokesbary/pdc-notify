# src/client.py
from typing import Any, Dict, List, Optional
import requests

from config.settings import BASE, LIMIT
from src.query_params import build_params, socrata_headers
from src.retry import get_with_retries
from state.cursor import Cursor

Headers = Dict[str, str]

def _normalize_rows(obj: Any) -> List[Dict[str, Any]]:
    """
    Socrata JSON is normally a list; guard if a dict sneaks in.
    """
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        return obj.get("data", [])
    return []

def fetch_page(
    limit: int = LIMIT,
    offset: int = 0,
    *,
    last_seen: Optional[Cursor] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, str] = build_params(last_seen=last_seen)
    params["$limit"] = str(int(limit))
    params["$offset"] = str(int(offset))
    headers: Headers = socrata_headers()

    r = requests.get(BASE, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return _normalize_rows(r.json())

def fetch_page_resilient(
    limit: int = LIMIT,
    offset: int = 0,
    *,
    last_seen: Optional[Cursor] = None,
    timeout: int = 30,
    max_attempts: int = 5,
) -> List[Dict[str, Any]]:
    params: Dict[str, str] = build_params(last_seen=last_seen)
    params["$limit"] = str(int(limit))
    params["$offset"] = str(int(offset))
    headers: Headers = socrata_headers()

    r = get_with_retries(
        BASE,
        params=params,
        headers=headers,
        timeout=timeout,
        max_attempts=max_attempts,
    )
    return _normalize_rows(r.json())

def fetch_all_until_short_page(
    limit: int = LIMIT,
    max_pages: int = 3,
    *,
    last_seen: Optional[Cursor] = None,
    resilient: bool = False,
) -> List[Dict[str, Any]]:
    """
    Pull consecutive pages until a page returns < limit rows or we hit max_pages.
    """
    all_rows: List[Dict[str, Any]] = []
    offset = 0
    pages = 0

    fetch_fn = fetch_page_resilient if resilient else fetch_page

    while pages < max_pages:
        page = fetch_fn(limit=limit, offset=offset, last_seen=last_seen)
        print(f"Page {pages+1}: {len(page)} rows")
        if not page:
            break
        all_rows.extend(page)
        if len(page) < limit:
            break
        offset += limit
        pages += 1

    return all_rows