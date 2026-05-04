"""
config.py — Central Configuration for the War Impact Study
===========================================================
Research Question: "Do stock market reaction curves depend on war duration,
or are they primarily driven by economic disruption and investor psychology?"

21 Events: 14 Global Conflicts + 7 India-Specific Incidents
All events, tickers, paths, parameters, and HYPOTHESES defined here.
"""

import os
from pathlib import Path
from collections import OrderedDict

# ─────────────────────────────────────────────────────────
# PROJECT PATHS
# ─────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "Raw_Data"
CLEANED_DATA_DIR = PROJECT_ROOT / "Cleaned_Data"
GRAPHS_DIR = PROJECT_ROOT / "Graphs"
EXCEL_OUTPUT_DIR = PROJECT_ROOT / "Excel_Output"
PPT_DIR = PROJECT_ROOT / "PPT"
REPORT_DIR = PROJECT_ROOT / "Final_Report"

# Create all directories
for d in [RAW_DATA_DIR, CLEANED_DATA_DIR, GRAPHS_DIR, EXCEL_OUTPUT_DIR, PPT_DIR, REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────
# DATA DOWNLOAD CONFIGURATION
# ─────────────────────────────────────────────────────────
DATA_START_DATE = "1990-01-01"
DATA_END_DATE   = "2024-12-31"

# Tickers for yfinance download
TICKERS = {
    "NIFTY_50":    "^NSEI",
    "SENSEX":      "^BSESN",
    "Brent_Crude": "BZ=F",
    "Gold":        "GC=F",
    "USD_INR":     "INR=X",
    "India_VIX":   "^INDIAVIX",
}

# Sectoral index tickers
SECTOR_TICKERS = {
    "NIFTY_Pharma":  "^CNXPHARMA",
    "NIFTY_Bank":    "^NSEBANK",
    "NIFTY_Energy":  "^CNXENERGY",
    "NIFTY_FMCG":    "^CNXFMCG",
}


# ─────────────────────────────────────────────────────────
# 21 WAR / CRISIS EVENTS
# ─────────────────────────────────────────────────────────
# Each event is tagged with:
#   group:            "global" or "india_specific"
#   duration_category:"short" (<6mo) / "medium" (6mo–2yr) / "long" (>2yr)
#   duration_str:     human-readable duration
#   oil_disruption:   True / False — does it disrupt oil supply?
#   disruption_level: "high" / "medium" / "low"
#   india_exposure:   brief text on India's exposure channel
#
# These tags power the HYPOTHESIS TESTING (group comparisons).

EVENTS = OrderedDict({
    # ───── GROUP A: GLOBAL CONFLICTS (14) ─────
    "Iran-Iraq War": {
        "date": "1980-09-22",
        "group": "global",
        "expected_category": "A",
        "duration_category": "long",
        "duration_str": "8 years",
        "oil_disruption": True,
        "disruption_level": "high",
        "india_exposure": "Oil shock, Indian workers in Gulf",
    },
    "Gulf War": {
        "date": "1990-08-02",
        "group": "global",
        "expected_category": "A",
        "duration_category": "short",
        "duration_str": "6 weeks",
        "oil_disruption": True,
        "disruption_level": "high",
        "india_exposure": "Oil price shock, Indian expats",
    },
    "Bosnia War": {
        "date": "1992-04-06",
        "group": "global",
        "expected_category": "C",
        "duration_category": "medium",
        "duration_str": "3 years",
        "oil_disruption": False,
        "disruption_level": "low",
        "india_exposure": "Minimal trade links",
    },
    "Kosovo War": {
        "date": "1999-03-24",
        "group": "global",
        "expected_category": "C",
        "duration_category": "short",
        "duration_str": "1 year",
        "oil_disruption": False,
        "disruption_level": "low",
        "india_exposure": "Limited direct exposure",
    },
    "Afghanistan War (post-9/11)": {
        "date": "2001-10-07",
        "group": "global",
        "expected_category": "A",
        "duration_category": "long",
        "duration_str": "20 years",
        "oil_disruption": True,
        "disruption_level": "high",
        "india_exposure": "Post-9/11 global panic, supply chain",
    },
    "Iraq War": {
        "date": "2003-03-20",
        "group": "global",
        "expected_category": "A",
        "duration_category": "long",
        "duration_str": "8 years",
        "oil_disruption": True,
        "disruption_level": "high",
        "india_exposure": "Oil supply fear, global risk-off",
    },
    "Sri Lanka Civil War (end)": {
        "date": "2009-05-19",
        "group": "global",
        "expected_category": "B",
        "duration_category": "long",
        "duration_str": "26 years",
        "oil_disruption": False,
        "disruption_level": "medium",
        "india_exposure": "Regional stability, trade",
    },
    "DRC Conflict": {
        "date": "1998-08-02",
        "group": "global",
        "expected_category": "C",
        "duration_category": "medium",
        "duration_str": "5 years",
        "oil_disruption": False,
        "disruption_level": "low",
        "india_exposure": "No significant India link",
    },
    "Syria Civil War": {
        "date": "2011-03-15",
        "group": "global",
        "expected_category": "B",
        "duration_category": "long",
        "duration_str": "13+ years (ongoing)",
        "oil_disruption": True,
        "disruption_level": "medium",
        "india_exposure": "Oil route concern, refugee crisis",
    },
    "Yemen Civil War": {
        "date": "2015-03-26",
        "group": "global",
        "expected_category": "B",
        "duration_category": "long",
        "duration_str": "10+ years (ongoing)",
        "oil_disruption": True,
        "disruption_level": "medium",
        "india_exposure": "Red Sea shipping, Indian diaspora",
    },
    "Libya Civil War": {
        "date": "2014-05-16",
        "group": "global",
        "expected_category": "B",
        "duration_category": "medium",
        "duration_str": "6 years",
        "oil_disruption": True,
        "disruption_level": "medium",
        "india_exposure": "Oil supply, Indian workers evacuated",
    },
    "Ethiopia-Tigray": {
        "date": "2020-11-04",
        "group": "global",
        "expected_category": "C",
        "duration_category": "medium",
        "duration_str": "2 years",
        "oil_disruption": False,
        "disruption_level": "low",
        "india_exposure": "No direct India channel",
    },
    "Myanmar Civil War": {
        "date": "2021-02-01",
        "group": "global",
        "expected_category": "C",
        "duration_category": "long",
        "duration_str": "4+ years (ongoing)",
        "oil_disruption": False,
        "disruption_level": "low",
        "india_exposure": "Border instability, NE India",
    },
    "Russia-Ukraine War": {
        "date": "2022-02-24",
        "group": "global",
        "expected_category": "A",
        "duration_category": "long",
        "duration_str": "3+ years (ongoing)",
        "oil_disruption": True,
        "disruption_level": "high",
        "india_exposure": "Oil, wheat, fertilizer disruption",
    },

    # ───── GROUP B: INDIA-SPECIFIC INCIDENTS (7) ─────
    "Kargil War": {
        "date": "1999-05-03",
        "group": "india_specific",
        "expected_category": "A",
        "duration_category": "short",
        "duration_str": "~3 months",
        "oil_disruption": False,
        "disruption_level": "high",
        "india_exposure": "Direct military conflict on border",
    },
    "Uri Attack & Surgical Strikes": {
        "date": "2016-09-18",
        "group": "india_specific",
        "expected_category": "B",
        "duration_category": "short",
        "duration_str": "Days",
        "oil_disruption": False,
        "disruption_level": "medium",
        "india_exposure": "Military escalation fear, nuclear risk",
    },
    "Pulwama Attack": {
        "date": "2019-02-14",
        "group": "india_specific",
        "expected_category": "B",
        "duration_category": "short",
        "duration_str": "Days",
        "oil_disruption": False,
        "disruption_level": "medium",
        "india_exposure": "Terror attack, India-Pak escalation",
    },
    "Balakot Airstrike": {
        "date": "2019-02-26",
        "group": "india_specific",
        "expected_category": "B",
        "duration_category": "short",
        "duration_str": "Days",
        "oil_disruption": False,
        "disruption_level": "medium",
        "india_exposure": "Cross-border airstrike, retaliation fear",
    },
    "Galwan Valley Clash": {
        "date": "2020-06-15",
        "group": "india_specific",
        "expected_category": "B",
        "duration_category": "short",
        "duration_str": "Days",
        "oil_disruption": False,
        "disruption_level": "medium",
        "india_exposure": "India-China border, 20 soldiers killed",
    },
    "India-Pakistan Border Tensions": {
        "date": "2021-02-25",
        "group": "india_specific",
        "expected_category": "C",
        "duration_category": "short",
        "duration_str": "Weeks",
        "oil_disruption": False,
        "disruption_level": "low",
        "india_exposure": "Ceasefire agreement, de-escalation",
    },
    "Soleimani Assassination Impact": {
        "date": "2020-01-03",
        "group": "india_specific",
        "expected_category": "B",
        "duration_category": "short",
        "duration_str": "Days",
        "oil_disruption": True,
        "disruption_level": "high",
        "india_exposure": "Oil price spike, Middle East escalation",
    },
})


# ─────────────────────────────────────────────────────────
# EVENT STUDY PARAMETERS
# ─────────────────────────────────────────────────────────
ESTIMATION_WINDOW_START = -120
ESTIMATION_WINDOW_END   = -31
PRE_WAR_WINDOW = 30
POST_EVENT_WINDOWS = [1, 5, 7, 15, 30, 90, 180]   # Day +5 added for behavioral shock

# ─────────────────────────────────────────────────────────
# CLASSIFICATION THRESHOLDS
# ─────────────────────────────────────────────────────────
CAR_THRESHOLD_A = -5.0
CAR_THRESHOLD_B = -2.0
VOL_RATIO_THRESHOLD_A = 2.0
VOL_RATIO_THRESHOLD_B = 1.3


# ─────────────────────────────────────────────────────────
# GENERALIZED HYPOTHESES
# ─────────────────────────────────────────────────────────
# Primary Research Question:
#   "Do stock market reaction curves depend on war duration,
#    or are they primarily driven by economic disruption and
#    investor psychology?"
#
# H0: Reaction curves are INDEPENDENT of duration.
# H1: Longer conflicts → prolonged recovery.

HYPOTHESES = {
    "H1": {
        "name": "Duration Independence",
        "statement": "Short conflicts (<6 months) and long conflicts (>2 years) "
                     "produce statistically similar market reactions (CAR at Day+30).",
        "test": "Two-sample t-test: CAR(short) vs CAR(long)",
        "metric": "CAR_30d",
    },
    "H2": {
        "name": "Disruption Dominance",
        "statement": "Oil-disrupting conflicts cause significantly larger market "
                     "declines than non-oil conflicts, regardless of duration.",
        "test": "Two-sample t-test: CAR(oil=True) vs CAR(oil=False)",
        "metric": "CAR_30d",
    },
    "H3": {
        "name": "India-Specific vs Global",
        "statement": "India-specific military incidents produce different market "
                     "reactions than distant global conflicts.",
        "test": "Two-sample t-test: CAR(india) vs CAR(global)",
        "metric": "CAR_30d",
    },
    "H4": {
        "name": "Behavioral Overreaction (Prospect Theory)",
        "statement": "The initial shock (Day 0-5) is disproportionately large "
                     "compared to sustained impact, indicating investor overreaction.",
        "test": "Paired t-test: |CAR_5d| vs |CAR_30d|/6 (normalized)",
        "metric": "CAR_5d vs CAR_30d",
    },
    "H5": {
        "name": "Market Adaptation (Adaptive Market Hypothesis)",
        "statement": "Markets stabilize within 90 days regardless of conflict "
                     "continuation, supporting the Adaptive Market Hypothesis.",
        "test": "Paired t-test: CAR_30d vs CAR_90d (H0: no further change)",
        "metric": "CAR_30d vs CAR_90d",
    },
}


# ─────────────────────────────────────────────────────────
# GRAPH SETTINGS
# ─────────────────────────────────────────────────────────
GRAPH_DPI = 300
GRAPH_FIGSIZE = (14, 8)
CATEGORY_COLORS = {
    "A": "#e74c3c",
    "B": "#f39c12",
    "C": "#27ae60",
}
HEATMAP_CMAP = "RdYlGn_r"


# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────
def get_events_by_group(group):
    """Return events filtered by group ('global' or 'india_specific')."""
    return {n: i for n, i in EVENTS.items() if i["group"] == group}

def get_events_by_duration(category):
    """Return events filtered by duration_category ('short'/'medium'/'long')."""
    return {n: i for n, i in EVENTS.items() if i["duration_category"] == category}

def get_oil_disruption_events():
    """Return events that disrupt oil supply."""
    return {n: i for n, i in EVENTS.items() if i["oil_disruption"]}

def get_non_oil_events():
    """Return events that do NOT disrupt oil supply."""
    return {n: i for n, i in EVENTS.items() if not i["oil_disruption"]}


if __name__ == "__main__":
    print("=" * 60)
    print("PROJECT CONFIGURATION")
    print("=" * 60)
    print(f"\nProject root:  {PROJECT_ROOT}")
    print(f"Data range:    {DATA_START_DATE} to {DATA_END_DATE}")
    print(f"Total events:  {len(EVENTS)}")
    print(f"  Global:      {len(get_events_by_group('global'))}")
    print(f"  India:       {len(get_events_by_group('india_specific'))}")
    print(f"  Short:       {len(get_events_by_duration('short'))}")
    print(f"  Medium:      {len(get_events_by_duration('medium'))}")
    print(f"  Long:        {len(get_events_by_duration('long'))}")
    print(f"  Oil-disrupt: {len(get_oil_disruption_events())}")
    print(f"\n--- Hypotheses ---")
    for hid, h in HYPOTHESES.items():
        print(f"  {hid}: {h['name']} — {h['statement'][:80]}...")
    print(f"\n--- Events ---")
    for name, info in EVENTS.items():
        oil = "🛢️" if info["oil_disruption"] else "  "
        grp = "🇮🇳" if info["group"] == "india_specific" else "🌍"
        dur = f"[{info['duration_category']:6s}]"
        print(f"  {info['date']}  [{info['expected_category']}] {dur} {oil} {grp} {name}")
