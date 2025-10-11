# socrata_mailer/socrata/http.py
import time
import requests
from typing import Dict, Any, Optional

TRANSIENT_STATUSES = {429, 500, 502, 503, 504}

def get_with_retries(
    url: str,
    *,
    params: Dict[str, Any],
    headers: Optional[Dict[str, str]],
    timeout: int = 30,
    max_attempts: int = 5,
    backoff_base: float = 0.8,
) -> requests.Response:
    """
    Simple retry for transient errors (429/5xx) with exponential backoff + tiny jitter.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code in TRANSIENT_STATUSES:
                raise requests.HTTPError(f"Transient {r.status_code}", response=r)
            r.raise_for_status()
            return r
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if attempt >= max_attempts or status not in TRANSIENT_STATUSES:
                raise
            sleep_s = (backoff_base ** attempt) * (1.0 + 0.2 * (attempt % 3))
            print(f"[Retry {attempt}/{max_attempts}] {status} — sleeping {sleep_s:.2f}s")
            time.sleep(sleep_s)
        except requests.RequestException as e:
            if attempt >= max_attempts:
                raise
            sleep_s = (backoff_base ** attempt) * (1.0 + 0.2 * (attempt % 3))
            print(f"[Retry {attempt}/{max_attempts}] Network error ({e.__class__.__name__}) — sleeping {sleep_s:.2f}s")
            time.sleep(sleep_s)