import json
from pathlib import Path
from typing import Optional

DEFAULT_PATH = Path(".cursor.json")

def read_last_seen(path: Path = DEFAULT_PATH) -> Optional[str]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return data.get("last_seen")
    except Exception:
        return None

def write_last_seen(value: str, path: Path = DEFAULT_PATH) -> None:
    path.write_text(json.dumps({"last_seen": value}))
