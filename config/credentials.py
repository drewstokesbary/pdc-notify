import os
from typing import Optional

# Optional: load .env automatically in local dev (not required in CI)
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except Exception:
    pass

# Socrata
SOCRATA_APP_TOKEN: Optional[str] = os.getenv("SOCRATA_APP_TOKEN")

# Gmail (fill in whatever you ultimately use)
# Examples:
# - GMAIL_API_CREDENTIALS_JSON (path) or raw JSON text
# - GMAIL_SENDER
GMAIL_SENDER: Optional[str] = os.getenv("GMAIL_SENDER")
GMAIL_CREDENTIALS_JSON: Optional[str] = os.getenv("GMAIL_CREDENTIALS_JSON")  # path or inline JSON
