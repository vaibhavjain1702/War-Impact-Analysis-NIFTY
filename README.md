# Impact of Global Wars and Geopolitical Crises on Indian Stock Market (NIFTY 50)

> **A 20+ Year Empirical Analysis** — Financial Markets Final Project

## 📋 Research Objective

**How do global wars and geopolitical crises systematically affect the Indian stock market?**

Following Professor Hirdesh's guidelines, this study moves beyond single-event qualitative analysis to build a **generalized, quantitative framework**. It examines 15 critical geopolitical events across a 24-year period (2000–2024) to validate hypotheses across diverse contexts and improve robustness.

## 🔬 Generalized Hypothesis Testing Framework

To ensure all arguments are quantitative, the study tests five generalized hypotheses across the entire dataset of 15 events:

1. **H1: Oil Transmission Channel** — Wars in oil-producing regions cause significantly larger negative market returns than wars in non-oil regions. *(Tested via Two-sample Welch's t-test)*
2. **H2: Safe Haven Effect** — Gold prices increase significantly during war periods, confirming gold as a safe haven asset. *(Tested via One-sample t-test)*
3. **H3: Volatility Amplification** — Market volatility (standard deviation of daily returns) increases significantly during war periods compared to pre-war normal periods. *(Tested via Paired t-test)*
4. **H4: Sector Asymmetry** — Defensive sectors (Pharma, FMCG) outperform cyclical sectors (Bank, Energy) during geopolitical crises. *(Tested via Paired t-test)*
5. **H5: Indirect Transmission** — The magnitude of market decline during wars is explained by indirect channels: oil price spikes, currency depreciation, and gold movement. *(Tested via OLS Regression: Market_pct = α + β₁·Oil + β₂·Gold + β₃·USD/INR)*

## 📊 Methodology & Data Pipeline

- **Data Range:** 1990–2024 (Primary analysis focuses on 2000–2024 based on data availability).
- **Market Proxies:** NIFTY 50 (primary) with an **automated fallback to BSE SENSEX** for pre-2007 events (e.g., Iraq War 2003, Afghanistan War 2001) to ensure robust sample sizes and solve data sparsity issues.
- **Event Study Methodology:** 
  - Estimation Window: t = -120 to t = -31 (90 trading days) to calculate expected returns.
  - Event Windows: Day +1, +7, +15, +30, +90, +180 to capture short and medium-term impacts.
  - Metrics: Abnormal Returns (AR), Cumulative Abnormal Returns (CAR), and statistical significance (t-stats, p-values).

## 🗂️ Project Structure

```
Project/
├── Raw_Data/              ← Downloaded CSVs (NIFTY, SENSEX, oil, gold, FX, sectors)
├── Cleaned_Data/          ← Preprocessed data (full date ranges preserved)
├── Python_Code/
│   ├── config.py          ← Central config (events, hypotheses, thresholds)
│   ├── 01_data_download.py
│   ├── 02_data_cleaning.py
│   ├── 03_pct_impact.py
│   ├── 04_event_study.py
│   ├── 05_volatility.py
│   ├── 06_sectoral.py
│   ├── 07_classification.py
│   ├── 08_hypothesis_testing.py  ← Core statistical testing (t-tests, OLS)
│   └── 09_graphs.py
├── Graphs/                ← All matplotlib output PNGs (300 DPI)
├── Excel_Output/          ← Summary tables, findings, regression results
├── PPT/                   ← Presentation file
├── Final_Report/          ← Word/PDF report
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download all market data (Starts from 1990 to cover older events)
python Python_Code/01_data_download.py

# 3. Clean and preprocess (Saves SENSEX with full range for fallback)
python Python_Code/02_data_cleaning.py

# 4. Run percentage impact analysis (Utilizes SENSEX fallback)
python Python_Code/03_pct_impact.py

# 5. Run event study (CAR analysis & t-stats)
python Python_Code/04_event_study.py

# 6. Volatility analysis (War vs Normal periods)
python Python_Code/05_volatility.py

# 7. Sectoral analysis (Defensive vs Cyclical)
python Python_Code/06_sectoral.py

# 8. War classification (A/B/C impact ranking)
python Python_Code/07_classification.py

# 9. Generalized Hypothesis Testing (Cross-event statistics - Core Requirement)
python Python_Code/08_hypothesis_testing.py

# 10. Generate all required graphs
python Python_Code/09_graphs.py
```

## 📈 15 War Events Studied

| # | Event | Date | Proximity / Oil Region |
|---|-------|------|------------------------|
| 1 | Russia-Ukraine War | Feb 24, 2022 | Distant / Yes |
| 2 | Israel-Hamas / Middle East | Oct 7, 2023 | Regional / Yes |
| 3 | Iraq War | Mar 20, 2003 | Regional / Yes |
| 4 | Afghanistan War (post-9/11) | Oct 7, 2001 | Direct / Yes |
| 5 | Gulf War | Aug 2, 1990 | Regional / Yes |
| 6 | Georgia War | Aug 8, 2008 | Distant / No |
| 7 | Kosovo War | Mar 24, 1999 | Distant / No |
| 8 | Bosnia War | Apr 6, 1992 | Distant / No |
| 9 | Nagorno-Karabakh | Sep 27, 2020 | Distant / No |
| 10 | Ethiopia-Tigray | Nov 4, 2020 | Distant / No |
| 11 | Sri Lanka Civil War (end) | May 19, 2009 | Direct / No |
| 12 | Lebanon Civil War | Apr 13, 1975 | Regional / Yes |
| 13 | DRC Conflict | Aug 2, 1998 | Distant / No |
| 14 | Iran-Iraq War | Sep 22, 1980 | Regional / Yes |
| 15 | Falklands War | Apr 2, 1982 | Distant / No |

## 📦 Key Variables

- **Market**: NIFTY 50, BSE SENSEX (Pre-2007 Fallback)
- **Commodities**: Brent Crude Oil, Gold (spot)
- **Macro**: USD/INR exchange rate, India VIX
- **Sectors**: NIFTY Pharma, Bank, Energy, FMCG

## 📄 Deliverables

1. **Final Report** — 6 sections (Intro → Lit Review → Methodology → Findings → Discussion → Conclusion)
2. **Presentation PPT** — 15 slides
3. **GitHub Repository** — All code, data, graphs, and documentation

## 👤 Author

Vaibhav Jain (Roll No: 230697)  
Financial Markets — Semester 6
