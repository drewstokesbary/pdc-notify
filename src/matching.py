# src/matching.py
from typing import Dict, List, Iterable
from src.filer_names import FILER_NAMES  # <- your standalone list

STRICT_NAME_MATCH = False  # flip to True to re-check filer_name in code
FILER_NAME_SET = set(FILER_NAMES)

def normalize_name(s: str) -> str:
    return (s or "").strip().lower()

def matches_criteria(record: Dict) -> bool:
    """
    Return True if this record should be considered a match.
    Currently: optional in-code filer_name validation (off by default).
    Add more business rules here later.
    """
    if STRICT_NAME_MATCH:
        fn = record.get("filer_name")
        if normalize_name(fn) not in {normalize_name(x) for x in FILER_NAME_SET}:
            return False
    return True

def filter_records(rows: Iterable[Dict]) -> List[Dict]:
    """Apply matches_criteria() to a list of rows and return only the matches."""
    out: List[Dict] = []
    for r in rows:
        try:
            if matches_criteria(r):
                out.append(r)
        except Exception:
            # Be permissive: skip malformed rows rather than failing the whole batch
            pass
    return out