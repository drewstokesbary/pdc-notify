import re
from string import capwords
from typing import Any, Optional

_paren_re = re.compile(r"\(([^)]*)\)")

def title_case_outside_parens(s: Optional[str]) -> str:
    if not s:
        return ""
    parts, last = [], 0
    for m in _paren_re.finditer(s):
        parts.append(capwords(s[last:m.start()].lower()))
        parts.append(s[m.start():m.end()])
        last = m.end()
    parts.append(capwords(s[last:].lower()))
    out = "".join(parts)
    return re.sub(r"\s{2,}", " ", out).strip()

def extract_url(url_field: Any) -> str:
    if isinstance(url_field, dict):
        return url_field.get("url") or ""
    return url_field or ""