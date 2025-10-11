# socrata_mailer/main.py
from src.client import (
    fetch_page, fetch_page_resilient, fetch_all_until_short_page
)
from src.query_params import build_preview_url
from state.cursor import read_last_seen

def main() -> None:
    last_seen = read_last_seen()  # None on first run
    print("Preview URL:", build_preview_url(last_seen))

    rows = fetch_page(limit=5, offset=0, last_seen=last_seen)
    print("Fetched rows:", len(rows))
    for i, row in enumerate(rows[:2], start=1):
        print(f"\nRow {i} preview:")
        for k, v in row.items():
            print(f"  {k}: {v}")

    test_rows = fetch_page_resilient(limit=3, offset=0, last_seen=last_seen)
    print("\nResilient fetch returned:", len(test_rows), "rows")

    paged_rows = fetch_all_until_short_page(limit=200, max_pages=2, last_seen=last_seen, resilient=True)
    print(f"\nTotal accumulated rows (test): {len(paged_rows)}")
    for i, row in enumerate(paged_rows[:2], start=1):
        print(f"  {i}. report_number={row.get('report_number')} filer_name={row.get('filer_name')}")

if __name__ == "__main__":
    main()