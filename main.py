from src.query_params import (
    build_params, build_preview_url, socrata_headers
)
from config.settings import BASE
from state.cursor import read_last_seen

print("Hello, World!")

def main() -> None:
    last_seen = read_last_seen()  # None on first run
    params = build_params(last_seen=last_seen)
    headers = socrata_headers()

    print("Base URL:", BASE)
    print("Query params:", params)
    print("Headers:", headers if headers else "(none)")
    print("Preview URL:", build_preview_url(last_seen))

if __name__ == "__main__":
    main()
