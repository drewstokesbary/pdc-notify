import os
from typing import Optional

try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()  # reads .env file automatically if present
except Exception:
    pass

SOCRATA_APP_TOKEN: Optional[str] = os.getenv("SOCRATA_APP_TOKEN")
GMAIL_API_KEY: Optional[str] = os.getenv("GMAIL_API_KEY")
GMAIL_SENDER: Optional[str] = os.getenv("GMAIL_SENDER")
