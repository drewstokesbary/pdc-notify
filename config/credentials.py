import os
from typing import Optional

try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()  # reads .env file automatically if present
except Exception:
    pass

SOCRATA_APP_TOKEN: Optional[str] = os.getenv("SOCRATA_APP_TOKEN")

# --- Gmail API (OAuth2) ---
DEFAULT_SENDER: Optional[str] = os.getenv("GMAIL_SENDER")
DEFAULT_RECIPIENTS_CSV: Optional[str] = os.getenv("DEFAULT_RECIPIENTS")

GMAIL_CREDENTIALS_JSON: Optional[str] = os.getenv("GMAIL_CREDENTIALS_JSON")  # path to client secrets
GMAIL_TOKEN_JSON: str = os.getenv("GMAIL_TOKEN_JSON", "state/token.json")    # where to persist the token