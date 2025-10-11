# mail/compose.py
from typing import Dict, Any, List
from mail.format import title_case_outside_parens, extract_url
from mail.models import EmailMessage
from config.credentials import DEFAULT_SENDER, DEFAULT_RECIPIENTS_CSV

def _default_recipients() -> List[str]:
    if not DEFAULT_RECIPIENTS_CSV:
        return []
    return [x.strip() for x in DEFAULT_RECIPIENTS_CSV.split(",") if x.strip()]

def _line_from_record(record: Dict[str, Any]) -> str:
    origin = (record.get("origin") or "campaign finance").strip()
    filer_raw = record.get("filer_name")
    filer = title_case_outside_parens(filer_raw)
    url = extract_url(record.get("url"))
    html_text = (
        f"<p>There has been a new {origin} report filed by {filer}. <br> View the report here: {url}</p>"
    )
    return html_text

def make_message_from_record(record: Dict[str, Any]) -> EmailMessage:
    # (kept for flexibility, but not used by the digest flow)
    line = _line_from_record(record)
    origin = (record.get("origin") or "campaign finance").strip()
    subject = f"New {origin} report: {title_case_outside_parens(record.get('filer_name'))}"
    return EmailMessage(
        subject=subject,
        sender=DEFAULT_SENDER,
        to=_default_recipients(),
        html_body=line,
    )

def make_digest_message(records: List[Dict[str, Any]]) -> EmailMessage:
    lines = [_line_from_record(r) for r in records]
    body = "".join(lines)
    subject = f"New PDC Reports Filed ({len(records)} new filing{'s' if len(records) != 1 else ''})"
    return EmailMessage(
        subject=subject,
        sender=DEFAULT_SENDER,
        to=_default_recipients(),
        html_body=body,
    )