# src/render.py
from datetime import datetime, timezone
from typing import Dict, List, Any

def render_message(record: Dict[str, Any]) -> str:
    origin = record.get("origin") or "campaign finance"
    filer = record.get("filer_name") or "(unknown filer)"

    url_field = record.get("url")
    if isinstance(url_field, dict):
        url = url_field.get("url", "(no URL provided)")
    else:
        url = url_field or "(no URL provided)"

    return f"There has been a new {origin} report filed by {filer}. View the report here: {url}"

def render_preview(matches: List[Dict[str, Any]]) -> str:
    lines = [f"Found {len(matches)} matching record(s) at {datetime.now(timezone.utc).isoformat()}Z", ""]
    for r in matches[:10]:  # keep preview short
        lines.append("• " + render_message(r))
    if len(matches) > 10:
        lines.append(f"(+{len(matches)-10} more)")
    return "\n".join(lines)