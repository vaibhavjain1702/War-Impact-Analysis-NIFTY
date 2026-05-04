"""
01_data_download.py — Download All Market Data via yfinance
============================================================
Downloads: NIFTY 50, SENSEX, Brent Crude, Gold, USD/INR, India VIX,
           and sectoral indices. Saves to Raw_Data/ as CSV files.

Usage:
    python Python_Code/01_data_download.py
"""

import sys
import yfinance as yf
import pandas as pd
from pathlib import Path

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    TICKERS, SECTOR_TICKERS, DATA_START_DATE, DATA_END_DATE, RAW_DATA_DIR
)


def download_ticker(name: str, ticker: str, start: str, end: str, save_dir: Path) -> pd.DataFrame:
    """
    Download historical daily OHLCV data for a single ticker.
    
    Parameters
    ----------
    name : str
        Descriptive name for the dataset (used in filename and logging).
    ticker : str
        Yahoo Finance ticker symbol.
    start, end : str
        Date range in 'YYYY-MM-DD' format.
    save_dir : Path
        Directory to save the CSV file.
    
    Returns
    -------
    pd.DataFrame or None
        Downloaded data, or None if download failed.
    """
    print(f"  Downloading {name} ({ticker})...", end=" ")
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        
        if df.empty:
            print("⚠️  EMPTY — no data returned. Check ticker symbol.")
            return None
        
        # Flatten multi-level columns if present (yfinance sometimes returns multi-index)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Save to CSV
        filepath = save_dir / f"{name}.csv"
        df.to_csv(filepath)
        print(f"✅  {len(df)} rows saved → {filepath.name}")
        return df
    
    except Exception as e:
        print(f"❌  FAILED — {e}")
        return None


def main():
    """Download all datasets and save to Raw_Data/."""
    
    print("=" * 60)
    print("DATA DOWNLOAD — War Impact on NIFTY 50 Study")
    print("=" * 60)
    print(f"Date range: {DATA_START_DATE} to {DATA_END_DATE}")
    print(f"Save directory: {RAW_DATA_DIR}")
    print()
    
    results = {}
    
    # --- Primary market data ---
    print("─── Primary Market Data ───")
    for name, ticker in TICKERS.items():
        # India VIX starts from 2008
        start = "2008-01-01" if name == "India_VIX" else DATA_START_DATE
        df = download_ticker(name, ticker, start, DATA_END_DATE, RAW_DATA_DIR)
        results[name] = df
    
    print()
    
    # --- Sectoral indices ---
    print("─── Sectoral Indices ───")
    for name, ticker in SECTOR_TICKERS.items():
        df = download_ticker(name, ticker, DATA_START_DATE, DATA_END_DATE, RAW_DATA_DIR)
        results[name] = df
    
    print()
    
    # --- Summary ---
    print("=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for name, df in results.items():
        if df is not None and not df.empty:
            date_range = f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}"
            print(f"  ✅ {name:20s} — {len(df):>6,} rows  |  {date_range}")
            success_count += 1
        else:
            print(f"  ❌ {name:20s} — FAILED / EMPTY")
            fail_count += 1
    
    print(f"\n  Total: {success_count} succeeded, {fail_count} failed")
    
    if fail_count > 0:
        print("\n  ⚠️  Some downloads failed. Common fixes:")
        print("     1. Check internet connection")
        print("     2. Some sectoral tickers may need manual download from NSE India")
        print("     3. India VIX data may be limited — try nseindia.com directly")
        print("     4. Pre-2000 data for Brent/Gold may need Macrotrends.net")
    
    print(f"\n  Raw data saved to: {RAW_DATA_DIR}")
    print("  Next step: python Python_Code/02_data_cleaning.py")


if __name__ == "__main__":
    main()
