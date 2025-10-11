import base64
import logging
import re
from pathlib import Path
from typing import Optional, Set, List, Dict

from email.message import EmailMessage as StdEmailMessage
from email.utils import make_msgid, formatdate

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mail.models import EmailMessage
from config.credentials import (
    GMAIL_CREDENTIALS_JSON,
    GMAIL_TOKEN_JSON,
)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

log = logging.getLogger(__name__)

def _get_service():
    if not GMAIL_CREDENTIALS_JSON:
        raise RuntimeError("GMAIL_CREDENTIALS_JSON not set (.env)")

    token_path = Path(GMAIL_TOKEN_JSON)
    creds: Optional[Credentials] = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_JSON, SCOPES)
            # First run opens a browser for consent, then writes the token file
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _html_to_text(html: str) -> str:
    """
    Minimal, safe HTML -> text fallback:
    - <br> -> newline
    - </p> -> double newline
    - <a href="URL">text</a> -> text (URL)
    - strip remaining tags
    """
    text = re.sub(r"(?i)<br\s*/?>", "\n", html)
    text = re.sub(r"(?i)</p>", "\n\n", text)
    text = re.sub(r'(?i)<a\s+href="([^"]+)">([^<]+)</a>', r"\2 (\1)", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _build_mime_from_model(msg: EmailMessage) -> StdEmailMessage:
    """
    Build a RFC-compliant MIME email.
    Prefers HTML when msg.html_body is present, with a text fallback.
    Falls back to plain text when only msg.text_body is present.
    """
    m = StdEmailMessage()
    m["Subject"] = msg.subject
    if getattr(msg, "sender", None):
        m["From"] = msg.sender
    # To / Cc / Bcc
    to_list: List[str] = list(getattr(msg, "to", []) or [])
    cc_list: List[str] = list(getattr(msg, "cc", []) or [])
    bcc_list: List[str] = list(getattr(msg, "bcc", []) or [])

    if to_list:
        m["To"] = ", ".join(to_list)
    if cc_list:
        m["Cc"] = ", ".join(cc_list)
    if bcc_list:
        # It's okay to include Bcc in the MIME; Gmail will strip it for recipients
        m["Bcc"] = ", ".join(bcc_list)

    # Extra headers (Reply-To, etc.)
    headers: Optional[Dict[str, str]] = getattr(msg, "headers", None)
    if headers:
        for k, v in headers.items():
            # Avoid overriding the core headers we already set
            if k.lower() not in {"subject", "from", "to", "cc", "bcc"}:
                m[k] = v

    # Helpful metadata
    m["Message-ID"] = make_msgid()
    m["Date"] = formatdate(localtime=True)

    # ----- Body selection -----
    html_body = getattr(msg, "html_body", None) or getattr(msg, "html", None)
    text_body = (
        getattr(msg, "text_body", None)
        or getattr(msg, "text", None)
        or None
    )

    if html_body:
        # multipart/alternative with plain-text fallback
        fallback_text = text_body or _html_to_text(html_body)
        m.set_content(fallback_text)
        m.add_alternative(html_body, subtype="html")
    else:
        # Plain text only (no HTML provided)
        m.set_content(text_body or "")
    # --------------------------

    # Validate recipients before returning
    all_rcpts: Set[str] = set(to_list) | set(cc_list) | set(bcc_list)
    if not all_rcpts:
        raise RuntimeError("No recipients provided (To/Cc/Bcc empty)")

    return m


class GmailAPITransport:
    def __init__(self):
        self.service = _get_service()

    def send(self, msg: EmailMessage) -> str:
        """
        Sends the given EmailMessage via Gmail API.
        Returns the Gmail message id on success.
        Raises a RuntimeError with details on failure.
        """
        mime = _build_mime_from_model(msg)
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode("utf-8")

        try:
            resp = self.service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()
            msg_id = resp.get("id")
            if not msg_id:
                raise RuntimeError("Gmail send returned no message id")
            return msg_id
        except HttpError as e:
            # Try to expose the structured JSON error if present
            try:
                content = e.content.decode("utf-8") if hasattr(e, "content") else str(e)
            except Exception:
                content = str(e)
            log.error("Gmail send failed: %s", content)
            raise RuntimeError(f"Gmail send failed: {content}") from e
        except Exception as e:
            log.exception("Unexpected error during Gmail send")
            raise