"""
02_data_cleaning.py — Clean and Preprocess All Data
=====================================================
- Removes NaN/missing values
- Computes daily returns
- Saves each dataset with its FULL date range (no truncation)
- Outputs data quality summary

Usage:
    python Python_Code/02_data_cleaning.py
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RAW_DATA_DIR, CLEANED_DATA_DIR, TICKERS, SECTOR_TICKERS


def load_raw_data(name: str) -> pd.DataFrame:
    """Load a raw CSV file, parse dates as index."""
    filepath = RAW_DATA_DIR / f"{name}.csv"
    if not filepath.exists():
        print(f"  ⚠️  {filepath.name} not found — skipping")
        return None
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def clean_single_dataset(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Clean a single dataset:
    1. Sort by date
    2. Remove duplicate dates
    3. Remove rows where Close is NaN
    4. Compute daily returns
    """
    if df is None or df.empty:
        return None

    df = df.sort_index()
    duplicates_before = df.index.duplicated().sum()
    df = df[~df.index.duplicated(keep='first')]

    if 'Close' not in df.columns:
        print(f"  ⚠️  {name}: No 'Close' column found. Columns: {list(df.columns)}")
        return None

    nulls_before = df['Close'].isna().sum()
    df = df.dropna(subset=['Close'])

    # Compute daily returns — use fill_method=None to avoid FutureWarning
    df['Daily_Return'] = df['Close'].pct_change(fill_method=None) * 100

    print(f"  {name:20s} | {len(df):>6,} rows | "
          f"Nulls: {nulls_before:>3} | Dupes: {duplicates_before:>3} | "
          f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    return df


def main():
    print("=" * 60)
    print("DATA CLEANING & PREPROCESSING")
    print("=" * 60)

    all_tickers = {**TICKERS, **SECTOR_TICKERS}

    # Load raw data
    print("\n─── Loading & Cleaning ───")
    datasets = {}
    for name in all_tickers:
        df = load_raw_data(name)
        if df is not None:
            cleaned = clean_single_dataset(df, name)
            if cleaned is not None:
                datasets[name] = cleaned

    if not datasets:
        print("\n  ❌ No raw data files found. Run 01_data_download.py first.")
        return

    # Save each dataset with its FULL date range (no alignment/truncation)
    print("\n─── Saving Cleaned Data (full date range each) ───")
    for name, df in datasets.items():
        filepath = CLEANED_DATA_DIR / f"{name}_clean.csv"
        df.to_csv(filepath)

    print(f"  ✅ All {len(datasets)} datasets saved to: {CLEANED_DATA_DIR}")

    # Quality report
    rows = []
    for name, df in datasets.items():
        rows.append({
            "Dataset": name,
            "Rows": len(df),
            "Start": df.index.min().strftime('%Y-%m-%d'),
            "End": df.index.max().strftime('%Y-%m-%d'),
            "Close_Nulls": df['Close'].isna().sum(),
            "Mean_Ret_%": round(df['Daily_Return'].mean(), 4),
            "Std_Ret_%": round(df['Daily_Return'].std(), 4),
        })

    quality_df = pd.DataFrame(rows)
    quality_path = CLEANED_DATA_DIR / "data_quality_summary.csv"
    quality_df.to_csv(quality_path, index=False)

    print(f"\n{'=' * 80}")
    print("DATA QUALITY SUMMARY")
    print(f"{'=' * 80}")
    print(quality_df.to_string(index=False))
    print(f"\nSaved to: {quality_path}")
    print(f"\n  Next step: python Python_Code/03_pct_impact.py")


if __name__ == "__main__":
    main()
