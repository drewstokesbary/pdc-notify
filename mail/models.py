from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class EmailMessage:
    subject: str
    to: List[str]
    text_body: Optional[str] = None      # plain-text body (optional)
    html_body: Optional[str] = None      # HTML body (optional)
    sender: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None