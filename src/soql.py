from typing import Iterable

def soql_quote(s: str) -> str:
    """Quote a string for SoQL: wrap in single quotes, doubling inner quotes."""
    return "'" + s.replace("'", "''") + "'"

def in_list_clause(field: str, items: Iterable[str]) -> str:
    quoted = ", ".join(soql_quote(x) for x in items)
    return f"{field} IN ({quoted})"
