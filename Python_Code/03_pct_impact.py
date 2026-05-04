"""
03_pct_impact.py — Percentage Impact Analysis
===============================================
Core quantitative analysis: calculate % change in NIFTY, Brent Crude,
Gold, and USD/INR across all event windows for all 15 wars.

Formula: % Change = (Final_Value - Initial_Value) / Initial_Value × 100

SENSEX fallback: For events before NIFTY data range, uses SENSEX as proxy
for the market index column.

Usage:
    python Python_Code/03_pct_impact.py
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    CLEANED_DATA_DIR, EXCEL_OUTPUT_DIR, EVENTS,
    PRE_WAR_WINDOW, POST_EVENT_WINDOWS
)


# Datasets to analyze for % impact
DATASETS_TO_ANALYZE = ["NIFTY_50", "SENSEX", "Brent_Crude", "Gold", "USD_INR"]


def load_cleaned_data(name: str) -> pd.DataFrame:
    """Load a cleaned dataset."""
    filepath = CLEANED_DATA_DIR / f"{name}_clean.csv"
    if not filepath.exists():
        print(f"  ⚠️  {filepath.name} not found — skipping")
        return None
    return pd.read_csv(filepath, index_col=0, parse_dates=True)


def is_event_in_range(df: pd.DataFrame, event_date: str, min_pre_days: int = 31) -> bool:
    """
    Check if an event date falls within the dataset's range,
    with enough pre-event data for meaningful analysis.
    
    Returns False if event is before (data_start + min_pre_days) or after data_end.
    """
    event_ts = pd.Timestamp(event_date)
    data_start = df.index.min()
    data_end = df.index.max()
    
    # Need at least min_pre_days of data before the event
    earliest_viable = data_start + pd.Timedelta(days=min_pre_days * 1.5)  # 1.5x for weekends
    
    return earliest_viable <= event_ts <= data_end


def get_closest_trading_day(df: pd.DataFrame, target_date: str, direction: str = "forward") -> pd.Timestamp:
    """
    Find the closest trading day to the target date.
    Returns None if the target is outside the data range.
    """
    target = pd.Timestamp(target_date)
    dates = df.index
    
    if target in dates:
        return target
    
    if direction == "forward":
        future_dates = dates[dates >= target]
        return future_dates[0] if len(future_dates) > 0 else None
    else:
        past_dates = dates[dates <= target]
        return past_dates[-1] if len(past_dates) > 0 else None


def compute_pct_change(df: pd.DataFrame, event_date: str, windows: list) -> dict:
    """
    Compute % change for each event window.
    Returns NaN for all windows if event is out of data range.
    """
    nan_result = {"Pre-war (t-30 to t-1)": np.nan}
    nan_result.update({f"Day +{w}": np.nan for w in windows})
    
    # Guard: check event is in data range
    if not is_event_in_range(df, event_date):
        return nan_result
    
    # Find event day index
    event_ts = get_closest_trading_day(df, event_date, direction="forward")
    if event_ts is None:
        return nan_result
    
    event_idx = df.index.get_loc(event_ts)
    
    # Need at least 1 day before event for initial price
    if event_idx < 1:
        return nan_result
    
    initial_price = df.iloc[event_idx - 1]['Close']  # t-1 (day before event)
    
    if pd.isna(initial_price) or initial_price == 0:
        return nan_result
    
    results = {}
    
    # Pre-war window: t-30 to t-1
    pre_war_start_idx = max(0, event_idx - PRE_WAR_WINDOW)
    pre_war_price = df.iloc[pre_war_start_idx]['Close']
    if pd.notna(pre_war_price) and pre_war_price != 0:
        results["Pre-war (t-30 to t-1)"] = ((initial_price - pre_war_price) / pre_war_price) * 100
    else:
        results["Pre-war (t-30 to t-1)"] = np.nan
    
    # Post-event windows
    for window in windows:
        target_idx = event_idx + window
        if target_idx < len(df):
            final_price = df.iloc[target_idx]['Close']
            if pd.notna(final_price):
                pct = ((final_price - initial_price) / initial_price) * 100
                results[f"Day +{window}"] = round(pct, 4)
            else:
                results[f"Day +{window}"] = np.nan
        else:
            results[f"Day +{window}"] = np.nan
    
    return results


def choose_market_index(nifty_df, sensex_df, event_date: str) -> tuple:
    """
    Choose NIFTY or SENSEX for a given event date.
    Returns (dataframe, source_name).
    Falls back to SENSEX if NIFTY doesn't cover the event.
    """
    if nifty_df is not None and is_event_in_range(nifty_df, event_date):
        return nifty_df, "NIFTY_50"
    elif sensex_df is not None and is_event_in_range(sensex_df, event_date):
        return sensex_df, "SENSEX (proxy)"
    else:
        return None, "NO DATA"


def build_impact_table(datasets: dict, events: dict, windows: list) -> pd.DataFrame:
    """
    Build the master findings table with SENSEX fallback for market index.
    """
    nifty_df = datasets.get("NIFTY_50")
    sensex_df = datasets.get("SENSEX")
    
    all_rows = []
    
    for event_name, event_info in events.items():
        event_date = event_info["date"]
        
        # Choose market index (NIFTY or SENSEX fallback)
        market_df, market_source = choose_market_index(nifty_df, sensex_df, event_date)
        
        row = {
            "Event": event_name,
            "Date": event_date,
            "Expected_Category": event_info["expected_category"],
            "Market_Source": market_source,
        }
        
        # Market index % change
        if market_df is not None:
            market_results = compute_pct_change(market_df, event_date, windows)
            for window_name, pct_val in market_results.items():
                row[f"Market_Index | {window_name}"] = pct_val
        else:
            row["Market_Index | Pre-war (t-30 to t-1)"] = np.nan
            for w in windows:
                row[f"Market_Index | Day +{w}"] = np.nan
        
        # Other datasets (commodities, FX) — skip NIFTY/SENSEX since handled above
        for ds_name, df in datasets.items():
            if ds_name in ("NIFTY_50", "SENSEX") or df is None:
                continue
            
            pct_results = compute_pct_change(df, event_date, windows)
            
            for window_name, pct_val in pct_results.items():
                col_name = f"{ds_name} | {window_name}"
                row[col_name] = pct_val
        
        all_rows.append(row)
    
    return pd.DataFrame(all_rows)


def main():
    print("=" * 60)
    print("PERCENTAGE IMPACT ANALYSIS")
    print("=" * 60)
    
    # Load cleaned data
    print("\n─── Loading Cleaned Data ───")
    datasets = {}
    for name in DATASETS_TO_ANALYZE:
        df = load_cleaned_data(name)
        if df is not None:
            datasets[name] = df
            print(f"  ✅ {name:20s} — {len(df):,} rows | "
                  f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    
    if not datasets:
        print("\n  ❌ No cleaned data found. Run 02_data_cleaning.py first.")
        return
    
    # Show NIFTY vs SENSEX coverage
    nifty_df = datasets.get("NIFTY_50")
    sensex_df = datasets.get("SENSEX")
    if nifty_df is not None:
        print(f"\n  ℹ️  NIFTY covers events from ~{nifty_df.index.min().strftime('%Y')} onward")
    if sensex_df is not None:
        print(f"  ℹ️  SENSEX covers events from ~{sensex_df.index.min().strftime('%Y')} onward (fallback)")
    
    # Compute % impact for all events
    print(f"\n─── Computing % Change for {len(EVENTS)} Events ───")
    print(f"  Windows: Pre-war, {', '.join(f'Day +{w}' for w in POST_EVENT_WINDOWS)}")
    
    impact_table = build_impact_table(datasets, EVENTS, POST_EVENT_WINDOWS)
    
    # Display results
    print(f"\n{'=' * 80}")
    print("IMPACT TABLE — Market Index (NIFTY/SENSEX)")
    print(f"{'=' * 80}")
    
    market_cols = ["Event", "Date", "Market_Source"] + [
        c for c in impact_table.columns if "Market_Index" in c
    ]
    available_cols = [c for c in market_cols if c in impact_table.columns]
    
    if available_cols:
        preview = impact_table[available_cols].copy()
        print(preview.to_string(index=False))
    
    # Flag events with no data
    no_data = impact_table[impact_table["Market_Source"] == "NO DATA"]
    if len(no_data) > 0:
        print(f"\n  ⚠️  {len(no_data)} events have NO market data available:")
        for _, row in no_data.iterrows():
            print(f"     • {row['Event']} ({row['Date']}) — need manual SENSEX/BSE download")
    
    # Save to Excel
    excel_path = EXCEL_OUTPUT_DIR / "pct_impact_all_events.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Full table
        impact_table.to_excel(writer, sheet_name="All_Variables", index=False)
        
        # Market index sheet
        if available_cols:
            impact_table[available_cols].to_excel(writer, sheet_name="Market_Index", index=False)
        
        # Per-commodity sheets
        for ds_name in datasets:
            if ds_name in ("NIFTY_50", "SENSEX"):
                continue
            ds_cols = ["Event", "Date", "Expected_Category"] + [
                c for c in impact_table.columns if ds_name in c
            ]
            available = [c for c in ds_cols if c in impact_table.columns]
            if available:
                impact_table[available].to_excel(writer, sheet_name=ds_name[:31], index=False)
    
    print(f"\n  ✅ Full impact table saved to: {excel_path}")
    
    # Save CSV as well
    csv_path = EXCEL_OUTPUT_DIR / "pct_impact_all_events.csv"
    impact_table.to_csv(csv_path, index=False)
    
    print(f"  ✅ CSV backup saved to: {csv_path}")
    print(f"\n  Next step: python Python_Code/04_event_study.py")


if __name__ == "__main__":
    main()
