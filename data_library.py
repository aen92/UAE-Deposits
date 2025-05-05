
"""
data_library.py
Dynamic data layer for UAE deposit products.
"""

from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import requests
from bs4 import BeautifulSoup

try:
    _BASE_DIR = Path(__file__).resolve().parent
except NameError:
    _BASE_DIR = Path.cwd()

DATA_PATH = _BASE_DIR / "deposit_products.csv"

INITIAL_DATA = [
    {
        "provider": "StashAway",
        "product_name": "StashAway Simple",
        "interest_rate_pct": 3.1,
        "rate_type": "projected",
        "compounding": "daily",
        "min_deposit": 0,
        "max_deposit": None,
        "tenure": "fully liquid",
        "early_access": "no penalty",
        "currency": "SGD",
        "url": "https://www.stashaway.ae/simple"
    },
    {
        "provider": "StashAway",
        "product_name": "StashAway Simple Guaranteed",
        "interest_rate_pct": 2.45,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 0,
        "max_deposit": None,
        "tenure": "1/3/6/12 months",
        "early_access": "not permitted",
        "currency": "SGD",
        "url": "https://www.stashaway.ae/simple-guaranteed"
    },
    {
        "provider": "StashAway",
        "product_name": "StashAway Simple Plus",
        "interest_rate_pct": 3.6,
        "rate_type": "projected",
        "compounding": "daily",
        "min_deposit": 0,
        "max_deposit": None,
        "tenure": "fully liquid",
        "early_access": "no penalty",
        "currency": "SGD",
        "url": "https://www.stashaway.ae/simple-plus"
    },
    {
        "provider": "Wio",
        "product_name": "Wio Fixed Deposit",
        "interest_rate_pct": 4.75,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 10000,
        "max_deposit": None,
        "tenure": "1 month (also 3/6/12)",
        "early_access": "no penalty ≤3m",
        "currency": "AED",
        "url": "https://wio.io/save"
    },
    {
        "provider": "Wio",
        "product_name": "Wio On‑Demand Savings",
        "interest_rate_pct": 3.5,
        "rate_type": "variable",
        "compounding": "real‑time",
        "min_deposit": 0,
        "max_deposit": None,
        "tenure": "fully liquid",
        "early_access": "no penalty",
        "currency": "USD & AED",
        "url": "https://wio.io/save"
    },
    {
        "provider": "Sarwa",
        "product_name": "Sarwa Save",
        "interest_rate_pct": None,
        "rate_type": "partner yield",
        "compounding": "annualised",
        "min_deposit": 500,
        "max_deposit": None,
        "tenure": "fully liquid",
        "early_access": "no penalty",
        "currency": "USD",
        "url": "https://www.sarwa.co"
    },
    {
        "provider": "Mashreq",
        "product_name": "Mashreq NEO Fixed Deposit",
        "interest_rate_pct": 2.45,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 10000,
        "max_deposit": None,
        "tenure": "1m – 1y",
        "early_access": "2% penalty",
        "currency": "AED USD GBP",
        "url": "https://www.mashreq.com/en/uae/neo/accounts/term-deposits/fixed-deposit/"
    },
    {
        "provider": "Mashreq",
        "product_name": "Mashreq NEO Unfixed Deposit",
        "interest_rate_pct": 1.88,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 10000,
        "max_deposit": None,
        "tenure": "6m – 5y",
        "early_access": "partial withdrawals allowed",
        "currency": "AED USD",
        "url": "https://www.mashreq.com/en/uae/neo/accounts/term-deposits/unfixed-deposit/"
    },
    {
        "provider": "Mashreq",
        "product_name": "Mashreq NEO Wakala Deposit",
        "interest_rate_pct": 1.98,
        "rate_type": "profit",
        "compounding": "not applicable",
        "min_deposit": 10000,
        "max_deposit": None,
        "tenure": "1 – 24m",
        "early_access": "profit based on last tenor",
        "currency": "AED USD EUR GBP",
        "url": "https://www.mashreq.com/en/uae/neo/accounts/term-deposits/wakala-deposit/"
    },
    {
        "provider": "Emirates NBD",
        "product_name": "ENBD FlexiDeposit",
        "interest_rate_pct": 3.5,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 50000,
        "max_deposit": None,
        "tenure": "≥3m",
        "early_access": "unlimited no penalty",
        "currency": "AED USD GBP etc.",
        "url": "https://www.emiratesnbd.com/en/flexi-deposit"
    },
    {
        "provider": "Emirates NBD",
        "product_name": "ENBD RegulaReturns Deposit",
        "interest_rate_pct": 3.5,
        "rate_type": "fixed",
        "compounding": "payout",
        "min_deposit": 50000,
        "max_deposit": None,
        "tenure": "3m – 5y",
        "early_access": "reduced interest",
        "currency": "AED",
        "url": "https://www.emiratesnbd.com/en/regular-returns-fixed-deposit"
    },
    {
        "provider": "Emirates NBD",
        "product_name": "ENBD Fixed Deposit",
        "interest_rate_pct": 2.1,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 10000,
        "max_deposit": None,
        "tenure": "1m – 5y",
        "early_access": "1% rate reduction",
        "currency": "AED USD GBP SAR AUD CAD",
        "url": "https://www.emiratesnbd.com/en/fixed-deposit"
    },
    {
        "provider": "Emirates NBD",
        "product_name": "ENBD FlexiSweep Deposit",
        "interest_rate_pct": 2.2,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 1000,
        "max_deposit": None,
        "tenure": "≥3m",
        "early_access": "reduced rate if <6m",
        "currency": "AED",
        "url": "https://www.emiratesnbd.com/en/flexisweep-deposit"
    },
    {
        "provider": "ADCB",
        "product_name": "ADCB Century Deposit (USD)",
        "interest_rate_pct": 4.15,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 5000,
        "max_deposit": None,
        "tenure": "500d",
        "early_access": "1% penalty / no interest <6m",
        "currency": "USD",
        "url": "https://www.adcb.com/en/personal/bank/deposits/century-deposit"
    },
    {
        "provider": "ADCB",
        "product_name": "ADCB Advantage FD (AED)",
        "interest_rate_pct": 3.65,
        "rate_type": "fixed",
        "compounding": "None",
        "min_deposit": 50000,
        "max_deposit": None,
        "tenure": "1m – 500d",
        "early_access": "penalties apply",
        "currency": "AED",
        "url": "https://www.adcb.com/en/personal/bank/deposits/advantage-fd"
    },
    {
        "provider": "Wahed",
        "product_name": "Wahed Save",
        "interest_rate_pct": None,
        "rate_type": "variable",
        "compounding": "annualised",
        "min_deposit": None,
        "max_deposit": None,
        "tenure": "fully liquid",
        "early_access": "no penalty",
        "currency": "USD",
        "url": "https://www.wahed.com/uae"
    }
]

def _bootstrap():
    if not DATA_PATH.exists():
        df = pd.DataFrame(INITIAL_DATA)
        df['last_scraped'] = pd.NaT
        df.to_csv(DATA_PATH, index=False)
    return load_data()

def load_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    return _bootstrap()

def _scrape_row(row: pd.Series) -> pd.Series:
    """Skeleton scraper – extend with product‑specific logic."""
    try:
        resp = requests.get(row['url'], timeout=15, headers={{'User-Agent': 'Mozilla/5.0'}})
        soup = BeautifulSoup(resp.text, 'html.parser')
        pct = soup.find(text=lambda t: t and '%' in t)
        if pct:
            value = float(''.join(c for c in pct if (c.isdigit() or c == '.')))
            if value:
                row['interest_rate_pct'] = value
    except Exception as exc:
        print(f'[WARN] {row["product_name"]}: {{exc}}')
    return row

def refresh_data():
    df = load_data()
    df = df.apply(_scrape_row, axis=1)
    df['last_scraped'] = datetime.now(timezone.utc).isoformat()
    df.to_csv(DATA_PATH, index=False)
    return df
