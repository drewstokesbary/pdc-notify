# filters/filer_names.py
from pathlib import Path

# Path to the plain text file relative to this script
FILENAMES_PATH = Path("filters/filer_names.txt")

def load_filer_names() -> list[str]:
    """
    Reads filer names from a text file, one per line.
    Returns a list of non-empty, stripped names.
    """
    if not FILENAMES_PATH.exists():
        raise FileNotFoundError(f"Missing filer_names file at: {FILENAMES_PATH}")
    
    with FILENAMES_PATH.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    
    # Filter out blank lines and comments
    return [line for line in lines if line and not line.startswith("#")]

# Load immediately when imported
FILER_NAMES = load_filer_names()