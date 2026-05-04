"""
06_sectoral.py — Sectoral Performance Analysis
================================================
Analyze how different sectors respond to each war event.
Build a sector × war matrix showing % change during each crisis.

Expected patterns:
    Pharma / Defense → positive (supply/demand spike)
    Banking → negative (risk aversion)
    Energy → mixed (oil price dependent)
    FMCG → stable (inelastic demand)

Usage:
    python Python_Code/06_sectoral.py
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    CLEANED_DATA_DIR, EXCEL_OUTPUT_DIR, EVENTS,
    SECTOR_TICKERS, POST_EVENT_WINDOWS
)


def load_sector_data() -> dict:
    """Load all available sectoral index data."""
    sectors = {}
    
    for name in SECTOR_TICKERS:
        filepath = CLEANED_DATA_DIR / f"{name}_clean.csv"
        if filepath.exists():
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            sectors[name] = df
            print(f"  ✅ {name:20s} — {len(df):,} rows")
        else:
            print(f"  ⚠️  {name:20s} — not found (may need manual download)")
    
    return sectors


def compute_sector_impact(df: pd.DataFrame, event_date: str, window: int = 30) -> float:
    """
    Compute % change for a sector around an event.
    
    Returns % change from t-1 to t+window, or NaN if data not available.
    """
    event_ts = pd.Timestamp(event_date)
    dates = df.index
    
    if event_ts not in dates:
        future = dates[dates >= event_ts]
        if len(future) == 0:
            return np.nan
        event_ts = future[0]
    
    idx = dates.get_loc(event_ts)
    
    if idx < 1:
        return np.nan
    
    initial_price = df.iloc[idx - 1]['Close']
    
    target_idx = idx + window
    if target_idx >= len(df):
        return np.nan
    
    final_price = df.iloc[target_idx]['Close']
    
    return round(((final_price - initial_price) / initial_price) * 100, 4)


def build_sector_war_matrix(sectors: dict, events: dict, window: int = 30) -> pd.DataFrame:
    """
    Build the sector × war heatmap matrix.
    
    Rows = wars, Columns = sectors
    Values = % change from t-1 to t+window
    """
    matrix_data = []
    
    for event_name, event_info in events.items():
        row = {"Event": event_name, "Date": event_info["date"]}
        
        for sector_name, sector_df in sectors.items():
            pct = compute_sector_impact(sector_df, event_info["date"], window)
            # Clean name for column header
            clean_name = sector_name.replace("NIFTY_", "")
            row[clean_name] = pct
        
        matrix_data.append(row)
    
    return pd.DataFrame(matrix_data)


def main():
    print("=" * 60)
    print("SECTORAL PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Load sectoral data
    print("\n─── Loading Sectoral Index Data ───")
    sectors = load_sector_data()
    
    if not sectors:
        print("\n  ❌ No sectoral data found. Download from NSE India manually")
        print("     or check if yfinance tickers worked in 01_data_download.py")
        return
    
    # Build matrix for 30-day window
    print(f"\n─── Building Sector × War Matrix (30-day window) ───")
    matrix_30 = build_sector_war_matrix(sectors, EVENTS, window=30)
    
    # Display
    print(f"\n{'=' * 80}")
    print("SECTOR × WAR MATRIX — % Change (30-day)")
    print(f"{'=' * 80}")
    print(matrix_30.to_string(index=False))
    
    # Build matrices for other windows too
    print(f"\n─── Building Multi-Window Matrices ───")
    
    excel_path = EXCEL_OUTPUT_DIR / "sectoral_analysis.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 30-day primary matrix
        matrix_30.to_excel(writer, sheet_name="30_Day", index=False)
        
        # Other windows
        for window in [7, 15, 90]:
            matrix_w = build_sector_war_matrix(sectors, EVENTS, window=window)
            matrix_w.to_excel(writer, sheet_name=f"{window}_Day", index=False)
            print(f"  ✅ {window}-day matrix computed")
    
    print(f"\n  ✅ Saved to: {excel_path}")
    
    # Identify patterns
    print(f"\n─── Pattern Analysis ───")
    
    sector_cols = [c for c in matrix_30.columns if c not in ["Event", "Date"]]
    
    for sector in sector_cols:
        values = matrix_30[sector].dropna()
        if len(values) > 0:
            positive = (values > 0).sum()
            negative = (values < 0).sum()
            avg = values.mean()
            print(f"  {sector:15s} | Avg: {avg:+.2f}% | Positive: {positive}/{len(values)} | Negative: {negative}/{len(values)}")
    
    # CSV backup
    csv_path = EXCEL_OUTPUT_DIR / "sectoral_matrix_30d.csv"
    matrix_30.to_csv(csv_path, index=False)
    print(f"\n  ✅ CSV backup: {csv_path}")
    
    print(f"\n  Next step: python Python_Code/07_classification.py")


if __name__ == "__main__":
    main()
