"""
05_volatility.py — Volatility Analysis
========================================
Compare standard deviation of daily returns between normal and war periods.
Higher std deviation during war = confirmed panic / elevated risk.

Metrics:
    σ_normal  = std(daily returns, t = -120 to t = -31)
    σ_war     = std(daily returns, t = 0 to t = +30)
    Volatility Ratio = σ_war / σ_normal

Interpretation:
    Ratio > 1.5 → significant volatility spike
    Ratio > 2.0 → severe spike (Category A indicator)

Usage:
    python Python_Code/05_volatility.py
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    CLEANED_DATA_DIR, EXCEL_OUTPUT_DIR, EVENTS,
    ESTIMATION_WINDOW_START, ESTIMATION_WINDOW_END,
    VOL_RATIO_THRESHOLD_A, VOL_RATIO_THRESHOLD_B
)


def load_market_data() -> dict:
    """Load both NIFTY and SENSEX cleaned data."""
    data = {}
    for name in ["NIFTY_50", "SENSEX"]:
        filepath = CLEANED_DATA_DIR / f"{name}_clean.csv"
        if filepath.exists():
            data[name] = pd.read_csv(filepath, index_col=0, parse_dates=True)
    return data


def is_event_in_range(df, event_date, min_pre_days=130):
    """Check if event has enough pre-event data."""
    event_ts = pd.Timestamp(event_date)
    earliest = df.index.min() + pd.Timedelta(days=min_pre_days * 1.5)
    return earliest <= event_ts <= df.index.max()


def choose_market_index(market_data, event_date):
    """Choose NIFTY or SENSEX fallback."""
    if "NIFTY_50" in market_data and is_event_in_range(market_data["NIFTY_50"], event_date):
        return market_data["NIFTY_50"], "NIFTY_50"
    elif "SENSEX" in market_data and is_event_in_range(market_data["SENSEX"], event_date):
        return market_data["SENSEX"], "SENSEX (proxy)"
    return None, "NO DATA"


def compute_volatility(df: pd.DataFrame, event_date: str,
                        est_start: int = -120, est_end: int = -31,
                        war_window: int = 30) -> dict:
    """
    Compute normal vs war period volatility for a single event.
    
    Parameters
    ----------
    df : DataFrame with 'Daily_Return' and DatetimeIndex
    event_date : str
    est_start, est_end : estimation window bounds
    war_window : post-event window size
    
    Returns
    -------
    dict with σ_normal, σ_war, ratio, and interpretation
    """
    event_ts = pd.Timestamp(event_date)
    dates = df.index
    
    if event_ts not in dates:
        future = dates[dates >= event_ts]
        if len(future) == 0:
            return None
        event_ts = future[0]
    
    idx = dates.get_loc(event_ts)
    
    # Normal period volatility (estimation window)
    est_start_idx = idx + est_start
    est_end_idx = idx + est_end
    
    if est_start_idx < 0:
        return None
    
    normal_returns = df['Daily_Return'].iloc[est_start_idx:est_end_idx + 1].dropna()
    
    if len(normal_returns) < 30:
        return None
    
    sigma_normal = normal_returns.std()
    
    # War period volatility
    war_end_idx = min(idx + war_window, len(df) - 1)
    war_returns = df['Daily_Return'].iloc[idx:war_end_idx + 1].dropna()
    
    if len(war_returns) < 5:
        return None
    
    sigma_war = war_returns.std()
    
    # Volatility ratio
    ratio = sigma_war / sigma_normal if sigma_normal > 0 else np.nan
    
    # Interpretation
    if ratio >= VOL_RATIO_THRESHOLD_A:
        interpretation = "SEVERE SPIKE"
    elif ratio >= VOL_RATIO_THRESHOLD_B:
        interpretation = "MODERATE SPIKE"
    else:
        interpretation = "NORMAL"
    
    return {
        'sigma_normal_%': round(sigma_normal, 4),
        'sigma_war_%': round(sigma_war, 4),
        'volatility_ratio': round(ratio, 4),
        'interpretation': interpretation,
        'normal_days': len(normal_returns),
        'war_days': len(war_returns),
        'normal_mean_%': round(normal_returns.mean(), 4),
        'war_mean_%': round(war_returns.mean(), 4),
    }


def main():
    print("=" * 60)
    print("VOLATILITY ANALYSIS — Normal vs. War Periods")
    print("=" * 60)
    
    # Load data (NIFTY + SENSEX)
    market_data = load_market_data()
    for name, df in market_data.items():
        print(f"\n  ✅ {name:15s} — {len(df):,} rows | "
              f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    
    if not market_data:
        print("\n  ❌ No market data found. Run 02_data_cleaning.py first.")
        return
    
    # Compute volatility for all events
    print(f"\n─── Volatility Analysis for {len(EVENTS)} Events ───\n")
    
    results = []
    
    for event_name, event_info in EVENTS.items():
        event_date = event_info["date"]
        df, source = choose_market_index(market_data, event_date)
        
        if df is None:
            print(f"  ❌ {event_name} — NO DATA (predates all available data)")
            results.append({
                "Event": event_name, "Date": event_date,
                "Data_Source": "NO DATA",
                "σ_normal (%)": np.nan, "σ_war (%)": np.nan,
                "Volatility_Ratio": np.nan, "Interpretation": "N/A",
            })
            continue
        
        vol = compute_volatility(df, event_date)
        
        if vol is None:
            print(f"  ⚠️  {event_name} ({source}) — insufficient data, skipped")
            results.append({
                "Event": event_name,
                "Date": event_date,
                "Data_Source": source,
                "σ_normal (%)": np.nan,
                "σ_war (%)": np.nan,
                "Volatility_Ratio": np.nan,
                "Interpretation": "N/A",
            })
            continue
        
        row = {
            "Event": event_name,
            "Date": event_date,
            "Data_Source": source,
            "σ_normal (%)": vol['sigma_normal_%'],
            "σ_war (%)": vol['sigma_war_%'],
            "Volatility_Ratio": vol['volatility_ratio'],
            "Interpretation": vol['interpretation'],
            "Normal_Days": vol['normal_days'],
            "War_Days": vol['war_days'],
            "Normal_Mean_Return_%": vol['normal_mean_%'],
            "War_Mean_Return_%": vol['war_mean_%'],
        }
        results.append(row)
        
        # Print summary
        marker = "🔴" if vol['interpretation'] == "SEVERE SPIKE" else \
                 "🟡" if vol['interpretation'] == "MODERATE SPIKE" else "🟢"
        print(f"  {marker} {event_name:35s} [{source}] | σ_normal: {vol['sigma_normal_%']:.4f}% | "
              f"σ_war: {vol['sigma_war_%']:.4f}% | Ratio: {vol['volatility_ratio']:.2f} | "
              f"{vol['interpretation']}")
    
    # Summary table
    vol_df = pd.DataFrame(results)
    
    print(f"\n{'=' * 80}")
    print("VOLATILITY SUMMARY")
    print(f"{'=' * 80}")
    
    # Count by interpretation
    counts = vol_df['Interpretation'].value_counts()
    for interp, count in counts.items():
        print(f"  {interp}: {count} events")
    
    # Save to Excel
    excel_path = EXCEL_OUTPUT_DIR / "volatility_analysis.xlsx"
    vol_df.to_excel(excel_path, index=False, sheet_name="Volatility")
    print(f"\n  ✅ Saved to: {excel_path}")
    
    # CSV backup
    csv_path = EXCEL_OUTPUT_DIR / "volatility_analysis.csv"
    vol_df.to_csv(csv_path, index=False)
    print(f"  ✅ CSV backup: {csv_path}")
    
    print(f"\n  Next step: python Python_Code/06_sectoral.py")


if __name__ == "__main__":
    main()
