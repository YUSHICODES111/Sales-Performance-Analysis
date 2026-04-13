# 📊 Sales Performance Analysis

## 🗂️ Project Overview

An end-to-end sales data analysis pipeline that ingests raw transactional data, performs systematic data cleaning and outlier detection, executes SQL-based KPI queries, and generates a suite of visualisations plus an interactive browser dashboard.

This project demonstrates skills directly relevant to **AI/ML data engineering** workflows: data validation, quality assurance, structured querying, and insight reporting — the same pipeline steps used in LLM training-data curation.

---

## 📁 Repository Structure

```
sales-performance-analysis/
│
├── data/
│   └── sales_data.csv          # 75-row transactional dataset (H1 2024)
│
├── NOTEBOOK/
│   └── sales_analysis.py       # Main analysis script (Python · Pandas · SQL · Matplotlib)
│
├── SQL/
│   └── queries.sql             # 13 structured SQL queries across 7 analysis sections
│
├── Dashboard/
│   └── dashboard.html          # Interactive KPI dashboard (Chart.js · no framework)
│
├── reports/                    # Auto-generated on running the notebook
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_revenue_by_region.png
│   ├── 03_revenue_profit_by_category.png
│   ├── 04_top_sales_reps.png
│   ├── 05_discount_vs_profit.png
│   ├── 06_revenue_heatmap.png
│   └── summary_report.txt
│
├── .gitignore
└── README.md
```

---

## 🔑 Key Performance Indicators (H1 2024)

| KPI | Value |
|---|---|
| Total Revenue | ₹5,63,804 |
| Total Profit | ₹2,84,335 |
| Profit Margin | 50.4% |
| Avg Order Value | ₹7,517 |
| Total Units Sold | 654 |
| Avg Discount Applied | 5.5% |
| Outliers Flagged | 4 orders |

---

## 📌 Analysis Sections

### 1. Data Cleaning & Validation
- Parsed date columns and extracted month/quarter features
- Applied **IQR-based outlier detection** on revenue
- Validated column dtypes and missing value counts
- Flagged anomalous orders without dropping them

### 2. SQL Queries (13 queries across 7 categories)
- Overview KPIs & monthly trends
- Quarter-over-quarter growth
- Regional breakdown (revenue, profit, margin)
- Sales rep performance matrix
- Product category & top-10 product rankings
- Discount impact analysis by band
- Customer segment comparison

### 3. Python Analysis (Pandas + Matplotlib + Seaborn)
- Monthly revenue & profit trend (line chart with fill)
- Revenue by region (horizontal bar)
- Revenue vs Profit by category (grouped bar)
- Top reps by profit (bar)
- Discount % vs Profit scatter (coloured by revenue)
- Category × Month revenue heatmap (Seaborn)

### 4. Interactive Dashboard (HTML + Chart.js)
Open `Dashboard/dashboard.html` in any browser — no server needed.
- KPI cards row
- Monthly revenue & profit dual-line chart
- Doughnut chart for regional share
- Grouped bars for category performance
- Sales rep ranking table with margin badges

---

## 🚀 How to Run

**Prerequisites**
```bash
pip install pandas numpy matplotlib seaborn
```

**Run the analysis**
```bash
cd NOTEBOOK
python sales_analysis.py
```

Charts will be saved to `/reports/`. Open `Dashboard/dashboard.html` in a browser for the interactive view.

**SQL**  
Import `data/sales_data.csv` into MySQL or SQLite and run `SQL/queries.sql`.

---

## 💡 Key Insights

1. **North region** leads all regions in revenue, driven by Corporate-segment Electronics and Furniture orders.
2. **Electronics & Furniture** generate the highest absolute profit despite similar margin percentages to other categories.
3. **Discounts above 10%** show a measurable negative correlation with per-order profit margin.
4. **Sneha Patel** records the highest total profit (₹75,521) by consistently closing high-value Corporate deals.
5. **Revenue grew 54%** from January to June — a steady upward trend with no seasonal dip.

---

## 🛠️ Skills Demonstrated

| Skill | Where Applied |
|---|---|
| Python (Pandas, NumPy) | Data cleaning, aggregation, outlier detection |
| SQL (SQLite via `sqlite3`) | 13 structured queries run in-memory |
| Matplotlib + Seaborn | 6 publication-quality charts auto-saved to `/reports/` |
| IQR Outlier Detection | Statistical data quality flagging |
| HTML + Chart.js | Interactive no-dependency dashboard |
| Data Storytelling | Key insights written in `summary_report.txt` |

---


*This project is part of my data analytics portfolio. Feedback and suggestions welcome via Issues.*
