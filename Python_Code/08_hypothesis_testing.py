"""
08_hypothesis_testing.py — Generalized Hypothesis Testing
==========================================================
Tests 5 quantitative hypotheses ACROSS all 21 events.

H1: Duration Independence — short vs long conflicts → similar CAR
H2: Disruption Dominance — oil-disruption wars → larger market decline
H3: India-Specific vs Global — proximity matters?
H4: Behavioral Overreaction — Day 0-5 shock vs sustained impact
H5: Market Adaptation — stabilization within 90 days

Usage:
    python Python_Code/08_hypothesis_testing.py
"""

import sys
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    EXCEL_OUTPUT_DIR, EVENTS, HYPOTHESES,
    get_events_by_group, get_events_by_duration,
    get_oil_disruption_events, get_non_oil_events
)


def load_results():
    """Load all previous analysis outputs."""
    data = {}
    files = {
        "car": "event_study_CAR_summary.csv",
        "volatility": "volatility_analysis.csv",
        "pct_impact": "pct_impact_all_events.csv",
        "classification": "war_classification.csv",
        "sectoral": "sectoral_matrix_30d.csv",
    }
    for key, filename in files.items():
        path = EXCEL_OUTPUT_DIR / filename
        if path.exists():
            data[key] = pd.read_csv(path)
        else:
            print(f"  ⚠️  {filename} not found — some tests may be skipped")
            data[key] = None
    return data


def test_h1_duration(data):
    """
    H1: Duration Independence.
    Short conflicts (<6 months) and long conflicts (>2 years) produce
    statistically similar market reactions.
    Test: Two-sample t-test on CAR_30d.
    """
    print("\n" + "=" * 70)
    print("H1: DURATION INDEPENDENCE")
    print("=" * 70)
    print("  Statement:", HYPOTHESES["H1"]["statement"])

    car_df = data.get("car")
    if car_df is None or "CAR_30d" not in car_df.columns:
        print("  ❌ CAR data not available")
        return None

    short_events = set(get_events_by_duration("short").keys())
    long_events = set(get_events_by_duration("long").keys())

    short_cars = car_df[car_df["Event"].isin(short_events)]["CAR_30d"].dropna()
    long_cars = car_df[car_df["Event"].isin(long_events)]["CAR_30d"].dropna()

    print(f"\n  Short-duration events (n={len(short_cars)}):")
    for _, row in car_df[car_df["Event"].isin(short_events)].iterrows():
        val = row.get("CAR_30d", np.nan)
        if pd.notna(val):
            dur = EVENTS.get(row["Event"], {}).get("duration_str", "?")
            print(f"    • {row['Event']:35s} [{dur:>12s}] CAR: {val:+.2f}%")

    print(f"\n  Long-duration events (n={len(long_cars)}):")
    for _, row in car_df[car_df["Event"].isin(long_events)].iterrows():
        val = row.get("CAR_30d", np.nan)
        if pd.notna(val):
            dur = EVENTS.get(row["Event"], {}).get("duration_str", "?")
            print(f"    • {row['Event']:35s} [{dur:>12s}] CAR: {val:+.2f}%")

    if len(short_cars) < 2 or len(long_cars) < 2:
        print("\n  ⚠️  Insufficient data for two-sample test")
        return {"Hypothesis": "H1: Duration Independence", "p_value": np.nan,
                "Significant": False, "n_short": len(short_cars), "n_long": len(long_cars)}

    short_mean = short_cars.mean()
    long_mean = long_cars.mean()
    t_stat, p_value = stats.ttest_ind(short_cars, long_cars, equal_var=False)

    print(f"\n  ─── Results ───")
    print(f"  Short-duration mean CAR:  {short_mean:+.2f}%")
    print(f"  Long-duration mean CAR:   {long_mean:+.2f}%")
    print(f"  Difference:               {short_mean - long_mean:+.2f}%")
    print(f"  Welch's t-statistic:      {t_stat:.4f}")
    print(f"  p-value:                  {p_value:.4f}")

    if p_value >= 0.05:
        print(f"  Conclusion: ✅ H1 SUPPORTED — No significant difference (p≥0.05)")
        print(f"    → Duration does NOT determine market reaction curves.")
        supported = True
    else:
        print(f"  Conclusion: ❌ H1 NOT SUPPORTED — Significant difference found (p<0.05)")
        supported = False

    return {
        "Hypothesis": "H1: Duration Independence",
        "Short_Mean_CAR": round(short_mean, 4),
        "Long_Mean_CAR": round(long_mean, 4),
        "t_stat": round(t_stat, 4),
        "p_value": round(p_value, 4),
        "Significant": supported,
        "n_short": len(short_cars),
        "n_long": len(long_cars),
    }


def test_h2_disruption(data):
    """
    H2: Disruption Dominance.
    Oil-disrupting conflicts cause larger market declines.
    Test: Two-sample t-test on CAR_30d.
    """
    print("\n" + "=" * 70)
    print("H2: DISRUPTION DOMINANCE (OIL CHANNEL)")
    print("=" * 70)
    print("  Statement:", HYPOTHESES["H2"]["statement"])

    car_df = data.get("car")
    if car_df is None or "CAR_30d" not in car_df.columns:
        print("  ❌ CAR data not available")
        return None

    oil_events = set(get_oil_disruption_events().keys())
    non_oil_events = set(get_non_oil_events().keys())

    oil_cars = car_df[car_df["Event"].isin(oil_events)]["CAR_30d"].dropna()
    non_oil_cars = car_df[car_df["Event"].isin(non_oil_events)]["CAR_30d"].dropna()

    print(f"\n  Oil-disruption events (n={len(oil_cars)}):")
    for _, row in car_df[car_df["Event"].isin(oil_events)].iterrows():
        val = row.get("CAR_30d", np.nan)
        if pd.notna(val):
            print(f"    • {row['Event']:35s} CAR: {val:+.2f}%")

    print(f"\n  Non-oil events (n={len(non_oil_cars)}):")
    for _, row in car_df[car_df["Event"].isin(non_oil_events)].iterrows():
        val = row.get("CAR_30d", np.nan)
        if pd.notna(val):
            print(f"    • {row['Event']:35s} CAR: {val:+.2f}%")

    if len(oil_cars) < 2 or len(non_oil_cars) < 2:
        print("\n  ⚠️  Insufficient data")
        return {"Hypothesis": "H2: Disruption Dominance", "p_value": np.nan,
                "Significant": False}

    oil_mean = oil_cars.mean()
    non_oil_mean = non_oil_cars.mean()
    t_stat, p_value = stats.ttest_ind(oil_cars, non_oil_cars, equal_var=False)

    print(f"\n  ─── Results ───")
    print(f"  Oil-disruption mean CAR:  {oil_mean:+.2f}%")
    print(f"  Non-oil mean CAR:         {non_oil_mean:+.2f}%")
    print(f"  Difference:               {oil_mean - non_oil_mean:+.2f}%")
    print(f"  Welch's t-statistic:      {t_stat:.4f}")
    print(f"  p-value:                  {p_value:.4f}")

    supported = p_value < 0.05 and oil_mean < non_oil_mean
    sig = "✅ SUPPORTED" if supported else "❌ NOT SUPPORTED"
    print(f"  Conclusion:               {sig}")

    return {
        "Hypothesis": "H2: Disruption Dominance",
        "Oil_Mean_CAR": round(oil_mean, 4),
        "NonOil_Mean_CAR": round(non_oil_mean, 4),
        "t_stat": round(t_stat, 4),
        "p_value": round(p_value, 4),
        "Significant": supported,
        "n_oil": len(oil_cars),
        "n_non_oil": len(non_oil_cars),
    }


def test_h3_india_vs_global(data):
    """
    H3: India-Specific vs Global.
    India-specific incidents produce different reactions than global conflicts.
    Test: Two-sample t-test on CAR_30d.
    """
    print("\n" + "=" * 70)
    print("H3: INDIA-SPECIFIC vs GLOBAL CONFLICTS")
    print("=" * 70)
    print("  Statement:", HYPOTHESES["H3"]["statement"])

    car_df = data.get("car")
    if car_df is None or "CAR_30d" not in car_df.columns:
        print("  ❌ CAR data not available")
        return None

    india_events = set(get_events_by_group("india_specific").keys())
    global_events = set(get_events_by_group("global").keys())

    india_cars = car_df[car_df["Event"].isin(india_events)]["CAR_30d"].dropna()
    global_cars = car_df[car_df["Event"].isin(global_events)]["CAR_30d"].dropna()

    print(f"\n  India-specific events (n={len(india_cars)}):")
    for _, row in car_df[car_df["Event"].isin(india_events)].iterrows():
        val = row.get("CAR_30d", np.nan)
        if pd.notna(val):
            print(f"    • {row['Event']:35s} CAR: {val:+.2f}%")

    print(f"\n  Global events (n={len(global_cars)}):")
    for _, row in car_df[car_df["Event"].isin(global_events)].iterrows():
        val = row.get("CAR_30d", np.nan)
        if pd.notna(val):
            print(f"    • {row['Event']:35s} CAR: {val:+.2f}%")

    if len(india_cars) < 2 or len(global_cars) < 2:
        print("\n  ⚠️  Insufficient data")
        return {"Hypothesis": "H3: India vs Global", "p_value": np.nan,
                "Significant": False}

    india_mean = india_cars.mean()
    global_mean = global_cars.mean()
    t_stat, p_value = stats.ttest_ind(india_cars, global_cars, equal_var=False)

    print(f"\n  ─── Results ───")
    print(f"  India-specific mean CAR:  {india_mean:+.2f}%")
    print(f"  Global mean CAR:          {global_mean:+.2f}%")
    print(f"  Difference:               {india_mean - global_mean:+.2f}%")
    print(f"  Welch's t-statistic:      {t_stat:.4f}")
    print(f"  p-value:                  {p_value:.4f}")

    supported = p_value < 0.05
    sig = "✅ SIGNIFICANT DIFFERENCE" if supported else "❌ NO SIGNIFICANT DIFFERENCE"
    print(f"  Conclusion:               {sig}")

    return {
        "Hypothesis": "H3: India vs Global",
        "India_Mean_CAR": round(india_mean, 4),
        "Global_Mean_CAR": round(global_mean, 4),
        "t_stat": round(t_stat, 4),
        "p_value": round(p_value, 4),
        "Significant": supported,
        "n_india": len(india_cars),
        "n_global": len(global_cars),
    }


def test_h4_overreaction(data):
    """
    H4: Behavioral Overreaction (Prospect Theory).
    Initial shock (Day 0-5) is disproportionately large vs sustained impact.
    Test: Compare absolute CAR at Day+5 vs Day+30.
    """
    print("\n" + "=" * 70)
    print("H4: BEHAVIORAL OVERREACTION (PROSPECT THEORY)")
    print("=" * 70)
    print("  Statement:", HYPOTHESES["H4"]["statement"])

    car_df = data.get("car")
    if car_df is None:
        print("  ❌ CAR data not available")
        return None

    # Check for CAR_5d column
    car_5d_col = "CAR_5d" if "CAR_5d" in car_df.columns else None
    car_30d_col = "CAR_30d" if "CAR_30d" in car_df.columns else None

    if not car_5d_col:
        # Try CAR_7d as alternative
        car_5d_col = "CAR_7d" if "CAR_7d" in car_df.columns else None
        if car_5d_col:
            print("  ℹ️  Using CAR_7d as proxy for CAR_5d")

    if not car_5d_col or not car_30d_col:
        print(f"  ❌ Missing columns. Available: {list(car_df.columns)}")
        return None

    valid = car_df.dropna(subset=[car_5d_col, car_30d_col]).copy()

    # Compute shock intensity: |CAR_5d| per day vs |CAR_30d| per day
    days_short = 5 if "5d" in car_5d_col else 7
    valid["Shock_Intensity"] = valid[car_5d_col].abs() / days_short
    valid["Sustained_Intensity"] = valid[car_30d_col].abs() / 30

    print(f"\n  Shock vs sustained intensity across {len(valid)} events:")
    for _, row in valid.iterrows():
        print(f"    • {row['Event']:35s} "
              f"Shock: {row['Shock_Intensity']:.3f}%/day  "
              f"Sustained: {row['Sustained_Intensity']:.3f}%/day  "
              f"Ratio: {row['Shock_Intensity']/max(row['Sustained_Intensity'], 0.001):.1f}x")

    if len(valid) < 3:
        print("\n  ⚠️  Insufficient data")
        return {"Hypothesis": "H4: Behavioral Overreaction", "p_value": np.nan,
                "Significant": False}

    shock = valid["Shock_Intensity"].values
    sustained = valid["Sustained_Intensity"].values
    t_stat, p_value = stats.ttest_rel(shock, sustained)

    print(f"\n  ─── Results ───")
    print(f"  Mean shock intensity:     {shock.mean():.4f}%/day")
    print(f"  Mean sustained intensity: {sustained.mean():.4f}%/day")
    print(f"  Mean overreaction ratio:  {(shock / np.maximum(sustained, 0.001)).mean():.2f}x")
    print(f"  Paired t-statistic:       {t_stat:.4f}")
    print(f"  p-value:                  {p_value:.4f}")

    supported = p_value < 0.05 and shock.mean() > sustained.mean()
    sig = "✅ SUPPORTED — Initial shock is disproportionate" if supported \
          else "❌ NOT SUPPORTED"
    print(f"  Conclusion:               {sig}")

    return {
        "Hypothesis": "H4: Behavioral Overreaction",
        "Mean_Shock": round(shock.mean(), 4),
        "Mean_Sustained": round(sustained.mean(), 4),
        "Overreaction_Ratio": round((shock / np.maximum(sustained, 0.001)).mean(), 4),
        "t_stat": round(t_stat, 4),
        "p_value": round(p_value, 4),
        "Significant": supported,
        "n_events": len(valid),
    }


def test_h5_adaptation(data):
    """
    H5: Market Adaptation (Adaptive Market Hypothesis).
    Markets stabilize within 90 days regardless of conflict continuation.
    Test: Paired t-test on CAR_30d vs CAR_90d.
    """
    print("\n" + "=" * 70)
    print("H5: MARKET ADAPTATION (ADAPTIVE MARKET HYPOTHESIS)")
    print("=" * 70)
    print("  Statement:", HYPOTHESES["H5"]["statement"])

    car_df = data.get("car")
    if car_df is None:
        print("  ❌ CAR data not available")
        return None

    if "CAR_30d" not in car_df.columns or "CAR_90d" not in car_df.columns:
        print(f"  ❌ Missing columns. Available: {list(car_df.columns)}")
        return None

    valid = car_df.dropna(subset=["CAR_30d", "CAR_90d"]).copy()
    valid["CAR_Change_30_to_90"] = valid["CAR_90d"] - valid["CAR_30d"]

    print(f"\n  CAR evolution (Day+30 → Day+90) across {len(valid)} events:")
    for _, row in valid.iterrows():
        change = row["CAR_Change_30_to_90"]
        direction = "↗️" if change > 1 else "↘️" if change < -1 else "→"
        print(f"    • {row['Event']:35s} "
              f"CAR₃₀: {row['CAR_30d']:+.2f}%  "
              f"CAR₉₀: {row['CAR_90d']:+.2f}%  "
              f"Δ: {change:+.2f}% {direction}")

    if len(valid) < 3:
        print("\n  ⚠️  Insufficient data")
        return {"Hypothesis": "H5: Market Adaptation", "p_value": np.nan,
                "Significant": False}

    car_30 = valid["CAR_30d"].values
    car_90 = valid["CAR_90d"].values
    changes = valid["CAR_Change_30_to_90"].values

    # Test if the change from 30 to 90 is significantly different from zero
    t_stat, p_value = stats.ttest_1samp(changes, 0)

    print(f"\n  ─── Results ───")
    print(f"  Mean CAR at Day+30:       {car_30.mean():+.2f}%")
    print(f"  Mean CAR at Day+90:       {car_90.mean():+.2f}%")
    print(f"  Mean Δ (30→90):           {changes.mean():+.2f}%")
    print(f"  t-statistic:              {t_stat:.4f}")
    print(f"  p-value:                  {p_value:.4f}")

    # H5 is SUPPORTED if there's no significant further change (p >= 0.05)
    # → markets have stabilized
    if p_value >= 0.05:
        print(f"  Conclusion: ✅ SUPPORTED — No significant further change after Day+30")
        print(f"    → Markets adapt and stabilize, supporting AMH.")
        supported = True
    else:
        print(f"  Conclusion: ❌ NOT SUPPORTED — Significant change between Day+30 and Day+90")
        supported = False

    return {
        "Hypothesis": "H5: Market Adaptation",
        "Mean_CAR_30d": round(car_30.mean(), 4),
        "Mean_CAR_90d": round(car_90.mean(), 4),
        "Mean_Delta": round(changes.mean(), 4),
        "t_stat": round(t_stat, 4),
        "p_value": round(p_value, 4),
        "Significant": supported,
        "n_events": len(valid),
    }


def main():
    print("=" * 70)
    print("GENERALIZED HYPOTHESIS TESTING")
    print("Cross-event quantitative analysis — 21 events")
    print("Research Q: Do reaction curves depend on duration or disruption?")
    print("=" * 70)

    # Load all previous results
    print("\n─── Loading Analysis Results ───")
    data = load_results()

    # Run all 5 hypothesis tests
    results = []

    r1 = test_h1_duration(data)
    if r1: results.append(r1)

    r2 = test_h2_disruption(data)
    if r2: results.append(r2)

    r3 = test_h3_india_vs_global(data)
    if r3: results.append(r3)

    r4 = test_h4_overreaction(data)
    if r4: results.append(r4)

    r5 = test_h5_adaptation(data)
    if r5: results.append(r5)

    # Summary table
    print(f"\n{'=' * 70}")
    print("HYPOTHESIS TESTING SUMMARY")
    print(f"{'=' * 70}")

    summary_rows = []
    for r in results:
        if isinstance(r, dict) and "Hypothesis" in r:
            sig = r.get("Significant", "N/A")
            p = r.get("p_value", "N/A")
            if sig == True:
                status = "✅ SUPPORTED"
            elif sig == False:
                status = "❌ NOT SUPPORTED"
            else:
                status = "⚠️ INSUFFICIENT DATA"
            print(f"  {r['Hypothesis']:35s} | p={p} | {status}")
            summary_rows.append(r)

    # Save results
    if summary_rows:
        flat_rows = []
        for r in summary_rows:
            flat = {k: v for k, v in r.items() if not isinstance(v, dict)}
            flat_rows.append(flat)
        summary_df = pd.DataFrame(flat_rows)
        excel_path = EXCEL_OUTPUT_DIR / "hypothesis_testing_results.xlsx"
        summary_df.to_excel(excel_path, index=False, sheet_name="Summary")
        print(f"\n  ✅ Saved to: {excel_path}")

        csv_path = EXCEL_OUTPUT_DIR / "hypothesis_testing_results.csv"
        summary_df.to_csv(csv_path, index=False)

    print(f"\n  Next step: python Python_Code/09_graphs.py")


if __name__ == "__main__":
    main()
