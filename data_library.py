"""
data_library.py
Dynamic data layer for UAE deposit products.
"""

from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import requests, re
from bs4 import BeautifulSoup

# ───────────────────── directories
BASE_DIR   = Path(__file__).resolve().parent
DATA_PATH  = BASE_DIR / "deposit_products.csv"

# ───────────────────── initial seed (unchanged)  ← shortened here for clarity
INITIAL_DATA = [
    # … keep your full INITIAL_DATA list exactly as provided …
]

# ───────────────────── bootstrap / load
def _bootstrap():
    if not DATA_PATH.exists():
        df = pd.DataFrame(INITIAL_DATA)
        df["last_scraped"] = pd.NaT
        df.to_csv(DATA_PATH, index=False)
    return load_data()

def load_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    return _bootstrap()

# ───────────────────── generic fetch helper
HEADERS = {"User-Agent": "Mozilla/5.0"}

def _get(url):
    return BeautifulSoup(requests.get(url, headers=HEADERS, timeout=15).text,
                         "html.parser")

# ───────────────────── provider‑specific scraper
def scrape_stashaway_simple_plus(row):
    """
    Scrape projected rate from https://www.stashaway.sg/simple-plus
    Looks for the first 'Projected x.xx%' token.
    """
    soup = _get(row["url"])
    m = re.search(r"Projected\\s+(\\d+\\.\\d+)%", soup.text)
    if m:
        row["interest_rate_pct"] = float(m.group(1))
        row["rate_type"]         = "projected"
        row["compounding"]       = "daily"
        row["tenure"]            = "fully liquid"
    return row

# ───────────────────── scraper router
SCRAPER_MAP = {
    "StashAway Simple Plus": scrape_stashaway_simple_plus,
    # add additional provider mappings here
}

# ───────────────────── row wrapper
def _scrape_row(row: pd.Series) -> pd.Series:
    fn = SCRAPER_MAP.get(row["product_name"])
    if fn:
        try:
            row = fn(row)
        except Exception as exc:
            print(f"[WARN] {row['product_name']}: {exc}")
    return row

# ───────────────────── orchestrator
def refresh_data():
    df = load_data().apply(_scrape_row, axis=1)
    df["last_scraped"] = datetime.now(timezone.utc).isoformat()
    df.to_csv(DATA_PATH, index=False)
    return df
