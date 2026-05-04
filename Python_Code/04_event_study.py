"""
04_event_study.py — Event Study Methodology (CAR Analysis)
============================================================
The most important technical section of the project.
Proves whether market movements were ABNORMAL — not just normal fluctuation.

Uses NIFTY 50 as primary index, falls back to SENSEX for events
before NIFTY data availability.

Methodology:
    Step 1: Actual return         Rt = (Pt - Pt-1) / Pt-1
    Step 2: Expected return       E(Rt) = mean(returns in estimation window)
    Step 3: Abnormal return       ARt = Rt - E(Rt)
    Step 4: Cumulative AR         CAR = Σ ARt over event window
    Step 5: t-statistic           t = CAR / (σ_AR × √N)

Usage:
    python Python_Code/04_event_study.py
"""

import sys
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    CLEANED_DATA_DIR, EXCEL_OUTPUT_DIR, GRAPHS_DIR, EVENTS,
    ESTIMATION_WINDOW_START, ESTIMATION_WINDOW_END,
    POST_EVENT_WINDOWS
)


def load_market_data() -> dict:
    """Load both NIFTY and SENSEX cleaned data."""
    data = {}
    for name in ["NIFTY_50", "SENSEX"]:
        filepath = CLEANED_DATA_DIR / f"{name}_clean.csv"
        if filepath.exists():
            data[name] = pd.read_csv(filepath, index_col=0, parse_dates=True)
    return data


def is_event_in_range(df: pd.DataFrame, event_date: str, min_pre_days: int = 130) -> bool:
    """Check if event has enough pre-event data for estimation window (120 days + buffer)."""
    event_ts = pd.Timestamp(event_date)
    data_start = df.index.min()
    data_end = df.index.max()
    earliest_viable = data_start + pd.Timedelta(days=min_pre_days * 1.5)
    return earliest_viable <= event_ts <= data_end


def choose_market_index(market_data: dict, event_date: str) -> tuple:
    """
    Choose NIFTY or SENSEX for a given event date.
    Returns (dataframe, source_name) or (None, "NO DATA").
    """
    if "NIFTY_50" in market_data and is_event_in_range(market_data["NIFTY_50"], event_date):
        return market_data["NIFTY_50"], "NIFTY_50"
    elif "SENSEX" in market_data and is_event_in_range(market_data["SENSEX"], event_date):
        return market_data["SENSEX"], "SENSEX (proxy)"
    else:
        return None, "NO DATA"


def event_study(df: pd.DataFrame, event_date: str, 
                est_start: int = -120, est_end: int = -31,
                window: int = 30) -> dict:
    """
    Perform a complete event study for a single event.
    
    Parameters
    ----------
    df : DataFrame
        Must contain 'Daily_Return' column with DatetimeIndex.
    event_date : str
        Event start date in 'YYYY-MM-DD' format.
    est_start : int
        Start of estimation window relative to event (default: -120).
    est_end : int
        End of estimation window relative to event (default: -31).
    window : int
        Length of event window in trading days (default: 30).
    
    Returns
    -------
    dict with keys: event_date, expected_return, AR, CAR, CAR_final,
                    t_stat, p_value, significant, estimation_std, N_days
    """
    # Find the closest trading day to the event date
    event_ts = pd.Timestamp(event_date)
    dates = df.index
    
    if event_ts not in dates:
        future = dates[dates >= event_ts]
        if len(future) == 0:
            return None
        event_ts = future[0]
    
    idx = dates.get_loc(event_ts)
    
    # --- Step 1: Estimation window returns ---
    est_start_idx = idx + est_start
    est_end_idx = idx + est_end
    
    if est_start_idx < 0:
        print(f"    ⚠️  Insufficient pre-event data for estimation window")
        return None
    
    estimation_returns = df['Daily_Return'].iloc[est_start_idx:est_end_idx + 1].dropna()
    
    if len(estimation_returns) < 30:
        print(f"    ⚠️  Estimation window too small ({len(estimation_returns)} days)")
        return None
    
    # --- Step 2: Expected return (mean of estimation window) ---
    expected_return = estimation_returns.mean()
    estimation_std = estimation_returns.std()
    
    # --- Step 3: Event window ---
    event_end_idx = min(idx + window, len(df) - 1)
    event_window = df['Daily_Return'].iloc[idx:event_end_idx + 1].copy()
    
    # --- Step 4: Abnormal returns ---
    AR = event_window - expected_return
    
    # --- Step 5: Cumulative Abnormal Return ---
    CAR = AR.cumsum()
    
    # --- Step 6: t-statistic ---
    N = len(AR)
    car_final = CAR.iloc[-1] if len(CAR) > 0 else np.nan
    
    if estimation_std > 0 and N > 0:
        t_stat = car_final / (estimation_std * np.sqrt(N))
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=N - 1))
    else:
        t_stat = np.nan
        p_value = np.nan
    
    return {
        'event_date': event_ts,
        'expected_return': round(expected_return, 6),
        'estimation_std': round(estimation_std, 6),
        'AR': AR,
        'CAR': CAR,
        'CAR_final': round(car_final, 4),
        't_stat': round(t_stat, 4) if not np.isnan(t_stat) else np.nan,
        'p_value': round(p_value, 4) if not np.isnan(p_value) else np.nan,
        'significant': p_value < 0.05 if not np.isnan(p_value) else False,
        'N_days': N,
    }


def run_event_study_all_windows(df: pd.DataFrame, event_date: str, 
                                 windows: list) -> dict:
    """Run event study for multiple window sizes."""
    results = {}
    for w in windows:
        result = event_study(df, event_date, window=w)
        if result is not None:
            results[w] = result
    return results


def main():
    print("=" * 60)
    print("EVENT STUDY METHODOLOGY — CAR Analysis")
    print("=" * 60)
    
    # Load market data (NIFTY + SENSEX)
    print("\n─── Loading Market Data ───")
    market_data = load_market_data()
    
    for name, df in market_data.items():
        print(f"  ✅ {name:15s} — {len(df):,} rows | "
              f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    
    if not market_data:
        print("\n  ❌ No market data found. Run 02_data_cleaning.py first.")
        return
    
    # Run event study for all events
    print(f"\n─── Running Event Study for {len(EVENTS)} Events ───")
    print(f"  Estimation window: t = {ESTIMATION_WINDOW_START} to {ESTIMATION_WINDOW_END}")
    print(f"  Event windows: {POST_EVENT_WINDOWS} days")
    print(f"  Auto-fallback: NIFTY → SENSEX for older events\n")
    
    all_results = []
    car_series = {}
    
    for event_name, event_info in EVENTS.items():
        event_date = event_info["date"]
        
        # Choose the right market index
        df, source = choose_market_index(market_data, event_date)
        
        print(f"  📌 {event_name} ({event_date}) — using {source}")
        
        if df is None:
            print(f"    ❌ NO DATA — event predates all available market data")
            all_results.append({
                "Event": event_name,
                "Date": event_date,
                "Expected_Category": event_info["expected_category"],
                "Data_Source": "NO DATA",
                "CAR_30d": np.nan,
                "t_stat": np.nan,
                "p_value": np.nan,
                "Significant": False,
            })
            continue
        
        # Run for the primary window (30 days)
        result_30 = event_study(df, event_date, window=30)
        
        if result_30 is None:
            print(f"    ⚠️  Skipped (insufficient estimation window data)")
            all_results.append({
                "Event": event_name,
                "Date": event_date,
                "Expected_Category": event_info["expected_category"],
                "Data_Source": source,
                "CAR_30d": np.nan,
                "t_stat": np.nan,
                "p_value": np.nan,
                "Significant": False,
            })
            continue
        
        # Store CAR series
        car_series[event_name] = result_30['CAR']
        
        # Run for all windows
        multi_window_results = run_event_study_all_windows(df, event_date, POST_EVENT_WINDOWS)
        
        row = {
            "Event": event_name,
            "Date": event_date,
            "Expected_Category": event_info["expected_category"],
            "Data_Source": source,
            "Expected_Return_%": result_30['expected_return'],
            "Estimation_Std_%": result_30['estimation_std'],
        }
        
        # Add CAR for each window
        for w, res in multi_window_results.items():
            row[f"CAR_{w}d"] = res['CAR_final']
            row[f"t_stat_{w}d"] = res['t_stat']
            row[f"p_value_{w}d"] = res['p_value']
            row[f"Significant_{w}d"] = res['significant']
        
        all_results.append(row)
        
        # Print summary
        car_30 = result_30['CAR_final']
        sig = "✓ SIGNIFICANT" if result_30['significant'] else "✗ not significant"
        print(f"    CAR (30-day): {car_30:+.2f}%  |  t = {result_30['t_stat']}  |  p = {result_30['p_value']}  |  {sig}")
    
    # Build summary table
    summary_df = pd.DataFrame(all_results)
    
    # Display summary
    print(f"\n{'=' * 80}")
    print("EVENT STUDY SUMMARY — CAR (30-day)")
    print(f"{'=' * 80}")
    
    display_cols = ["Event", "Date", "Data_Source", "Expected_Category"]
    for c in ["CAR_30d", "t_stat_30d", "Significant_30d"]:
        if c in summary_df.columns:
            display_cols.append(c)
    
    available = [c for c in display_cols if c in summary_df.columns]
    print(summary_df[available].to_string(index=False))
    
    # Coverage stats
    total = len(summary_df)
    analyzed = summary_df['CAR_30d'].notna().sum()
    no_data = (summary_df.get('Data_Source', '') == 'NO DATA').sum()
    print(f"\n  📊 {analyzed}/{total} events analyzed | {no_data} events have no available data")
    
    # Save to Excel
    excel_path = EXCEL_OUTPUT_DIR / "event_study_results.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name="CAR_Summary", index=False)
        
        for event_name, car in car_series.items():
            safe_name = event_name[:31].replace("/", "-").replace("(", "").replace(")", "")
            car_df = pd.DataFrame({
                "Date": car.index,
                "CAR_%": car.values
            })
            car_df.to_excel(writer, sheet_name=safe_name, index=False)
    
    print(f"\n  ✅ Event study results saved to: {excel_path}")
    
    csv_path = EXCEL_OUTPUT_DIR / "event_study_CAR_summary.csv"
    summary_df.to_csv(csv_path, index=False)
    print(f"  ✅ CSV backup saved to: {csv_path}")
    
    print(f"\n  Next step: python Python_Code/05_volatility.py")


if __name__ == "__main__":
    main()
