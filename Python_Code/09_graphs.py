"""
09_graphs.py — Generate All 7 Required Graphs
===============================================
All graphs saved as 300 DPI PNGs to Graphs/ folder.

Graph 1: NIFTY timeline with war event markers
Graph 2: Brent crude % change by war (bar chart)
Graph 3: Gold price movement chart
Graph 4: Market index % change ranked bar chart
Graph 5: Sector × war heatmap
Graph 6: War impact ranking (A/B/C color coded)
Graph 7: Normal vs war volatility comparison

Usage:
    python Python_Code/09_graphs.py
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    CLEANED_DATA_DIR, EXCEL_OUTPUT_DIR, GRAPHS_DIR, EVENTS,
    GRAPH_DPI, GRAPH_FIGSIZE, CATEGORY_COLORS, HEATMAP_CMAP
)

# Set global style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
    'axes.grid': True,
    'grid.alpha': 0.3,
})


def load_csv(path):
    if path.exists():
        return pd.read_csv(path, index_col=0, parse_dates=True) if '_clean' in path.name \
            else pd.read_csv(path)
    print(f"  ⚠️ {path.name} not found")
    return None


def graph_1_nifty_timeline():
    """Graph 1: NIFTY 50 timeline with vertical war markers."""
    print("  📊 Graph 1: NIFTY timeline with war markers...", end=" ")
    df = load_csv(CLEANED_DATA_DIR / "NIFTY_50_clean.csv")
    if df is None:
        return

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(df.index, df['Close'], color='#2c3e50', linewidth=0.8, alpha=0.9)

    colors = {'A': '#e74c3c', 'B': '#f39c12', 'C': '#95a5a6'}
    for name, info in EVENTS.items():
        dt = pd.Timestamp(info['date'])
        if dt >= df.index.min() and dt <= df.index.max():
            cat = info['expected_category']
            ax.axvline(x=dt, color=colors.get(cat, 'gray'), alpha=0.7,
                       linestyle='--', linewidth=1.2)
            y_pos = df['Close'].max() * 0.95
            ax.text(dt, y_pos, name.split('(')[0].strip()[:20],
                    rotation=45, fontsize=7, ha='right', color=colors.get(cat, 'gray'))

    ax.set_title("NIFTY 50 Index — Historical Timeline with War Event Markers")
    ax.set_xlabel("Year")
    ax.set_ylabel("NIFTY 50 Close Price (₹)")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Legend
    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0], [0], color='#e74c3c', linestyle='--', label='Cat A (Strong)'),
        Line2D([0], [0], color='#f39c12', linestyle='--', label='Cat B (Moderate)'),
        Line2D([0], [0], color='#95a5a6', linestyle='--', label='Cat C (Minimal)'),
    ]
    ax.legend(handles=legend_items, loc='upper left')
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "01_nifty_timeline_wars.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def graph_2_oil_bar():
    """Graph 2: Brent crude % change by war."""
    print("  📊 Graph 2: Oil price % change by war...", end=" ")
    impact = load_csv(EXCEL_OUTPUT_DIR / "pct_impact_all_events.csv")
    if impact is None:
        return

    col = [c for c in impact.columns if 'Brent_Crude' in c and 'Day +30' in c]
    if not col:
        print("⚠️ No Brent Crude 30-day column found")
        return

    data = impact[['Event', col[0]]].dropna().copy()
    data.columns = ['Event', 'Pct_Change']
    data = data.sort_values('Pct_Change')

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = ['#e74c3c' if v > 0 else '#27ae60' for v in data['Pct_Change']]
    bars = ax.barh(data['Event'], data['Pct_Change'], color=colors, edgecolor='white')

    ax.set_title("Brent Crude Oil — % Change (30-day) by War Event")
    ax.set_xlabel("% Change")
    ax.axvline(x=0, color='black', linewidth=0.8)

    for bar, val in zip(bars, data['Pct_Change']):
        ax.text(val + (0.5 if val >= 0 else -0.5), bar.get_y() + bar.get_height()/2,
                f'{val:+.1f}%', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "02_oil_pct_change_by_war.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def graph_3_gold():
    """Graph 3: Gold price movement chart."""
    print("  📊 Graph 3: Gold price movement...", end=" ")
    impact = load_csv(EXCEL_OUTPUT_DIR / "pct_impact_all_events.csv")
    if impact is None:
        return

    col = [c for c in impact.columns if 'Gold' in c and 'Day +30' in c]
    if not col:
        print("⚠️ No Gold 30-day column found")
        return

    data = impact[['Event', col[0]]].dropna().copy()
    data.columns = ['Event', 'Pct_Change']
    data = data.sort_values('Pct_Change', ascending=False)

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = ['#f1c40f' if v > 0 else '#7f8c8d' for v in data['Pct_Change']]
    bars = ax.barh(data['Event'], data['Pct_Change'], color=colors, edgecolor='white')

    ax.set_title("Gold Price — % Change (30-day) by War Event")
    ax.set_xlabel("% Change")
    ax.axvline(x=0, color='black', linewidth=0.8)
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "03_gold_pct_change_by_war.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def graph_4_nifty_ranked():
    """Graph 4: Market index % change ranked bar chart."""
    print("  📊 Graph 4: Market index % change ranked...", end=" ")
    impact = load_csv(EXCEL_OUTPUT_DIR / "pct_impact_all_events.csv")
    if impact is None:
        return

    # Try Market_Index column first (from updated pct_impact), fallback to NIFTY_50
    col = [c for c in impact.columns if 'Market_Index' in c and 'Day +30' in c]
    if not col:
        col = [c for c in impact.columns if 'NIFTY_50' in c and 'Day +30' in c]
    if not col:
        print("⚠️ No market index 30-day column found")
        return

    data = impact[['Event', col[0]]].dropna().copy()
    data.columns = ['Event', 'Pct_Change']
    data = data.sort_values('Pct_Change')

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = ['#e74c3c' if v < 0 else '#27ae60' for v in data['Pct_Change']]
    bars = ax.barh(data['Event'], data['Pct_Change'], color=colors, edgecolor='white')

    ax.set_title("Indian Market Index — % Change (30-day) Ranked by War Impact")
    ax.set_xlabel("% Change")
    ax.axvline(x=0, color='black', linewidth=0.8)

    for bar, val in zip(bars, data['Pct_Change']):
        ax.text(val + (0.3 if val >= 0 else -0.3), bar.get_y() + bar.get_height()/2,
                f'{val:+.1f}%', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "04_market_ranked_war_impact.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def graph_5_sector_heatmap():
    """Graph 5: Sector × war heatmap."""
    print("  📊 Graph 5: Sector heatmap...", end=" ")
    matrix = load_csv(EXCEL_OUTPUT_DIR / "sectoral_matrix_30d.csv")
    if matrix is None:
        return

    # Set Event as index, keep only numeric columns
    num_cols = matrix.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        print("⚠️ No numeric columns in sectoral matrix")
        return

    plot_data = matrix.set_index('Event')[num_cols]

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(plot_data, annot=True, fmt=".1f", cmap=HEATMAP_CMAP,
                center=0, linewidths=0.5, ax=ax,
                cbar_kws={'label': '% Change (30-day)'})

    ax.set_title("Sectoral Performance During Wars — % Change Heatmap")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "05_sector_war_heatmap.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def graph_6_war_ranking():
    """Graph 6: War impact ranking with A/B/C color coding."""
    print("  📊 Graph 6: War impact ranking A/B/C...", end=" ")
    classif = load_csv(EXCEL_OUTPUT_DIR / "war_classification.csv")
    if classif is None:
        return

    data = classif.dropna(subset=['CAR_30d_%']).sort_values('CAR_30d_%')

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = [CATEGORY_COLORS.get(c, '#95a5a6') for c in data['ACTUAL_Category']]
    bars = ax.barh(data['Event'], data['CAR_30d_%'], color=colors, edgecolor='white')

    ax.set_title("War Impact Ranking — CAR (30-day) with A/B/C Classification")
    ax.set_xlabel("Cumulative Abnormal Return (%)")
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.axvline(x=-5, color='#e74c3c', linestyle=':', alpha=0.5, label='Cat A threshold (-5%)')
    ax.axvline(x=-2, color='#f39c12', linestyle=':', alpha=0.5, label='Cat B threshold (-2%)')

    ax.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "06_war_ranking_ABC.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def graph_7_volatility():
    """Graph 7: Normal vs war volatility comparison."""
    print("  📊 Graph 7: Volatility comparison...", end=" ")
    vol = load_csv(EXCEL_OUTPUT_DIR / "volatility_analysis.csv")
    if vol is None:
        return

    data = vol.dropna(subset=['σ_normal (%)', 'σ_war (%)']).copy()

    fig, ax = plt.subplots(figsize=(14, 8))
    x = np.arange(len(data))
    width = 0.35

    bars1 = ax.bar(x - width/2, data['σ_normal (%)'], width, label='Normal Period (σ)',
                   color='#3498db', alpha=0.8, edgecolor='white')
    bars2 = ax.bar(x + width/2, data['σ_war (%)'], width, label='War Period (σ)',
                   color='#e74c3c', alpha=0.8, edgecolor='white')

    ax.set_title("Volatility Comparison — Normal vs. War Period (Std Dev of Daily Returns)")
    ax.set_ylabel("Standard Deviation (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(data['Event'], rotation=45, ha='right', fontsize=8)
    ax.legend()

    # Add ratio labels
    for i, (_, row) in enumerate(data.iterrows()):
        ratio = row['Volatility_Ratio']
        ax.text(i, max(row['σ_normal (%)'], row['σ_war (%)']) + 0.05,
                f'{ratio:.1f}x', ha='center', fontsize=8, fontweight='bold',
                color='#e74c3c' if ratio > 1.5 else '#2c3e50')

    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "07_volatility_comparison.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def graph_8_duration_vs_shock():
    """Graph 8: Conflict Duration vs Market Impact (H1 Visualization)."""
    print("  📊 Graph 8: Duration vs Shock scatter...", end=" ")
    impact = load_csv(EXCEL_OUTPUT_DIR / "pct_impact_all_events.csv")
    if impact is None:
        return

    # Extract CAR 30d
    car_df = load_csv(EXCEL_OUTPUT_DIR / "event_study_CAR_summary.csv")
    if car_df is None:
        return

    data = []
    for name, info in EVENTS.items():
        if name in car_df['Event'].values:
            car = car_df.loc[car_df['Event'] == name, 'CAR_30d'].values[0]
            dur_cat = info['duration_category']
            # Map duration category to numeric for plotting
            dur_map = {'short': 1, 'medium': 2, 'long': 3}
            data.append({
                'Event': name,
                'CAR_30d': car,
                'Duration': info['duration_str'],
                'Duration_Num': dur_map.get(dur_cat, 0),
                'Group': info['group']
            })
    
    plot_df = pd.DataFrame(data).dropna()
    if plot_df.empty:
        print("⚠️ No data for duration plot")
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.scatterplot(data=plot_df, x='Duration_Num', y='CAR_30d', hue='Group', 
                    style='Group', s=200, palette='viridis', ax=ax)
    
    # Annotate points
    for i, row in plot_df.iterrows():
        ax.text(row['Duration_Num'] + 0.05, row['CAR_30d'], row['Event'], 
                fontsize=8, alpha=0.7)

    ax.set_title("Conflict Duration vs. Market Impact (30-day CAR)")
    ax.set_xlabel("Duration Category (1=Short, 2=Medium, 3=Long)")
    ax.set_ylabel("Cumulative Abnormal Return (%)")
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(['Short (<6mo)', 'Medium (6mo-2yr)', 'Long (>2yr)'])
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')

    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "08_duration_vs_shock.png", dpi=GRAPH_DPI)
    plt.close()
    print("✅")


def main():
    print("=" * 60)
    print("GRAPH GENERATION — 8 Required Graphs")
    print("=" * 60)
    print(f"  Output: {GRAPHS_DIR}")
    print(f"  DPI: {GRAPH_DPI}\n")

    graph_1_nifty_timeline()
    graph_2_oil_bar()
    graph_3_gold()
    graph_4_nifty_ranked()
    graph_5_sector_heatmap()
    graph_6_war_ranking()
    graph_7_volatility()
    graph_8_duration_vs_shock()

    # List generated files
    pngs = list(GRAPHS_DIR.glob("*.png"))
    print(f"\n{'=' * 60}")
    print(f"  ✅ {len(pngs)} graphs generated:")
    for p in sorted(pngs):
        print(f"    📊 {p.name}")
    print(f"\n  All graphs saved to: {GRAPHS_DIR}")


if __name__ == "__main__":
    main()
