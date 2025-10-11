BASE = "https://data.wa.gov/resource/7qr9-q2c9.json"

SELECT_FIELDS = [
    "report_number",
    "origin",
    "filer_name",
    "url",
]
SELECT = ",".join(SELECT_FIELDS)

ORDER = "report_number DESC"
LIMIT = 500

# Cursor strategy
CURSOR_FIELD = "report_number"   # or "receipt_date"
