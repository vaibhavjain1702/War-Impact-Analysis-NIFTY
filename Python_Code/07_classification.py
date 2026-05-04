"""
07_classification.py — War Impact Classification (A/B/C)
=========================================================
Classify each war into impact categories based on computed CAR
and volatility ratio.

Usage:
    python Python_Code/07_classification.py
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    EXCEL_OUTPUT_DIR, EVENTS,
    CAR_THRESHOLD_A, CAR_THRESHOLD_B,
    VOL_RATIO_THRESHOLD_A, VOL_RATIO_THRESHOLD_B
)


def classify_war(car_30d, vol_ratio):
    """Classify: A (strong), B (moderate), C (minimal)."""
    if pd.isna(car_30d) and pd.isna(vol_ratio):
        return "N/A"
    is_a = (not pd.isna(car_30d) and car_30d < CAR_THRESHOLD_A) or \
           (not pd.isna(vol_ratio) and vol_ratio > VOL_RATIO_THRESHOLD_A)
    if is_a:
        return "A"
    is_b = (not pd.isna(car_30d) and CAR_THRESHOLD_A <= car_30d < CAR_THRESHOLD_B) or \
           (not pd.isna(vol_ratio) and VOL_RATIO_THRESHOLD_B <= vol_ratio <= VOL_RATIO_THRESHOLD_A)
    if is_b:
        return "B"
    return "C"


def main():
    print("=" * 60)
    print("WAR IMPACT CLASSIFICATION — A / B / C")
    print("=" * 60)

    car_path = EXCEL_OUTPUT_DIR / "event_study_CAR_summary.csv"
    vol_path = EXCEL_OUTPUT_DIR / "volatility_analysis.csv"

    if not car_path.exists():
        print(f"\n  ❌ Run 04_event_study.py first.")
        return
    if not vol_path.exists():
        print(f"\n  ❌ Run 05_volatility.py first.")
        return

    car_df = pd.read_csv(car_path)
    vol_df = pd.read_csv(vol_path)
    merged = car_df.merge(vol_df[['Event', 'Volatility_Ratio']], on='Event', how='left')

    print(f"\n─── Classifying {len(merged)} Events ───\n")
    rows = []
    for _, row in merged.iterrows():
        car_30 = row.get('CAR_30d', np.nan)
        vol_ratio = row.get('Volatility_Ratio', np.nan)
        category = classify_war(car_30, vol_ratio)
        rows.append({
            "Event": row['Event'], "Date": row['Date'],
            "Expected_Category": row.get('Expected_Category', 'N/A'),
            "CAR_30d_%": car_30, "Volatility_Ratio": vol_ratio,
            "ACTUAL_Category": category,
        })
        color = "🔴" if category == "A" else "🟡" if category == "B" else "🟢"
        car_s = f"{car_30:+.2f}%" if not pd.isna(car_30) else "N/A"
        vol_s = f"{vol_ratio:.2f}" if not pd.isna(vol_ratio) else "N/A"
        print(f"  {color} [{category}] {row['Event']:35s} | CAR: {car_s:>8s} | Vol: {vol_s}")

    class_df = pd.DataFrame(rows)

    # Save
    excel_path = EXCEL_OUTPUT_DIR / "war_classification.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        class_df.to_excel(writer, sheet_name="Classification", index=False)
        ranked = class_df.sort_values('CAR_30d_%', ascending=True, na_position='last')
        ranked.to_excel(writer, sheet_name="Ranked_by_Impact", index=False)

    print(f"\n  ✅ Saved to: {excel_path}")
    csv_path = EXCEL_OUTPUT_DIR / "war_classification.csv"
    class_df.to_csv(csv_path, index=False)
    print(f"  Next step: python Python_Code/08_hypothesis_testing.py")


if __name__ == "__main__":
    main()
