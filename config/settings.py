# config/settings.py

BASE = "https://data.wa.gov/resource/7qr9-q2c9.json"

# --- Cursor strategy (recommended) ---
# Use a Socrata system timestamp if available. Prefer :updated_at if you want amended/updated
# filings to re-trigger; use :created_at if you only care about first appearance.
CURSOR_TS_FIELD = ":updated_at"      # or ":created_at"
CURSOR_TIE_FIELD = "report_number"   # string tie-breaker; handles 9-digit and C6-####

# Always SELECT the cursor fields, aliased to normal names for Python + SoQL simplicity.
# Note: SoQL supports "as" aliases.
SELECT_FIELDS = [
    "report_number",
    "origin",
    "filer_name",
    "url",
    f"{CURSOR_TS_FIELD} as cursor_ts",
    f"{CURSOR_TIE_FIELD} as cursor_tie",
]
SELECT = ",".join(SELECT_FIELDS)

# Deterministic ordering for paging + cursor advancement.
# Use ASC so "max_cursor" is just the last/largest by (ts, tie).
ORDER = "cursor_ts ASC, cursor_tie ASC"

LIMIT = 10000