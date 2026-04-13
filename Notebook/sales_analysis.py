# =============================================================================
# SALES PERFORMANCE ANALYSIS
# Author : Ayushi Shukla
# GitHub : github.com/YUSHICODES111
# Tools  : Python · Pandas · Matplotlib · Seaborn · SQL (via SQLite)
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sqlite3
import warnings
import os

warnings.filterwarnings("ignore")

# ── styling ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f0f14",
    "axes.facecolor":   "#161620",
    "axes.edgecolor":   "#2a2a38",
    "axes.labelcolor":  "#9090a8",
    "xtick.color":      "#5a5a70",
    "ytick.color":      "#5a5a70",
    "text.color":       "#f0f0f5",
    "grid.color":       "#1e1e2a",
    "grid.linestyle":   "--",
    "grid.alpha":        0.5,
    "font.family":      "sans-serif",
    "font.size":         11,
})
ACCENT  = "#7c6af7"
GREEN   = "#3ecf8e"
AMBER   = "#f59e0b"
RED     = "#f87171"
PALETTE = [ACCENT, GREEN, AMBER, RED, "#60a5fa", "#f472b6"]

# ── 1. LOAD & INSPECT ────────────────────────────────────────────────────────
print("=" * 60)
print("  SALES PERFORMANCE ANALYSIS  |  Ayushi Shukla")
print("=" * 60)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sales_data.csv")
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

print(f"\n[1] Dataset loaded  →  {df.shape[0]} rows × {df.shape[1]} columns")
print(f"    Date range       →  {df['date'].min().date()}  to  {df['date'].max().date()}")
print(f"    Missing values   →  {df.isnull().sum().sum()}")
print(f"\nColumn dtypes:\n{df.dtypes}\n")

# ── 2. DATA CLEANING & VALIDATION ────────────────────────────────────────────
print("[2] Data Cleaning & Validation")

# Derived columns
df["month"]       = df["date"].dt.to_period("M")
df["month_label"] = df["date"].dt.strftime("%b %Y")
df["quarter"]     = df["date"].dt.to_period("Q").astype(str)

# Outlier detection using IQR on revenue
Q1, Q3 = df["revenue"].quantile([0.25, 0.75])
IQR     = Q3 - Q1
lower   = Q1 - 1.5 * IQR
upper   = Q3 + 1.5 * IQR
outliers = df[(df["revenue"] < lower) | (df["revenue"] > upper)]
print(f"    Revenue IQR bounds  →  ₹{lower:,.0f}  —  ₹{upper:,.0f}")
print(f"    Outliers detected   →  {len(outliers)} rows  (flagged, not removed)\n")
df["is_outlier"] = df["revenue"].apply(lambda x: x < lower or x > upper)

# ── 3. KPI SUMMARY ───────────────────────────────────────────────────────────
total_revenue  = df["revenue"].sum()
total_profit   = df["profit"].sum()
avg_order_val  = df["revenue"].mean()
profit_margin  = (total_profit / total_revenue) * 100
total_units    = df["quantity"].sum()
avg_discount   = df["discount_pct"].mean()

print("[3] KEY PERFORMANCE INDICATORS")
print(f"    Total Revenue     →  ₹{total_revenue:>12,.2f}")
print(f"    Total Profit      →  ₹{total_profit:>12,.2f}")
print(f"    Profit Margin     →  {profit_margin:.1f}%")
print(f"    Avg Order Value   →  ₹{avg_order_val:>12,.2f}")
print(f"    Total Units Sold  →  {total_units:>12,}")
print(f"    Avg Discount      →  {avg_discount:.1f}%\n")

# ── 4. SQL QUERIES VIA SQLITE ─────────────────────────────────────────────────
print("[4] SQL Queries (SQLite in-memory)\n")

conn = sqlite3.connect(":memory:")
df_sql = df.copy()
df_sql["month"]   = df_sql["month"].astype(str)
df_sql["quarter"] = df_sql["quarter"].astype(str)
df_sql.to_sql("sales", conn, index=False, if_exists="replace")

QUERIES = {
    "Revenue by Region": """
        SELECT region,
               ROUND(SUM(revenue), 2)  AS total_revenue,
               ROUND(AVG(revenue), 2)  AS avg_revenue,
               COUNT(*)                AS num_orders
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC
    """,
    "Top 5 Sales Reps by Profit": """
        SELECT sales_rep,
               ROUND(SUM(profit), 2)   AS total_profit,
               COUNT(*)                AS orders,
               ROUND(AVG(discount_pct),1) AS avg_discount
        FROM sales
        GROUP BY sales_rep
        ORDER BY total_profit DESC
        LIMIT 5
    """,
    "Revenue by Product Category": """
        SELECT product_category,
               ROUND(SUM(revenue), 2)  AS revenue,
               ROUND(SUM(profit), 2)   AS profit,
               ROUND(AVG(discount_pct),1) AS avg_disc
        FROM sales
        GROUP BY product_category
        ORDER BY revenue DESC
    """,
    "Monthly Revenue Trend": """
        SELECT month_label,
               ROUND(SUM(revenue), 2) AS monthly_revenue,
               COUNT(*)               AS orders
        FROM sales
        GROUP BY month
        ORDER BY month
    """,
}

sql_results = {}
for title, query in QUERIES.items():
    result = pd.read_sql_query(query, conn)
    sql_results[title] = result
    print(f"  ── {title} ──")
    print(result.to_string(index=False))
    print()

conn.close()

# ── 5. VISUALISATIONS ────────────────────────────────────────────────────────
print("[5] Generating Dashboard Charts …\n")

out_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(out_dir, exist_ok=True)

# --- Fig 1 : Monthly Revenue Trend ---
monthly = sql_results["Monthly Revenue Trend"]
fig, ax = plt.subplots(figsize=(12, 4))
ax.fill_between(range(len(monthly)), monthly["monthly_revenue"] / 1000,
                alpha=0.15, color=ACCENT)
ax.plot(range(len(monthly)), monthly["monthly_revenue"] / 1000,
        color=ACCENT, lw=2.5, marker="o", markersize=6)
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly["month_label"], rotation=30, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}K"))
ax.set_title("Monthly Revenue Trend (Jan – Jun 2024)", fontsize=14, pad=14)
ax.set_ylabel("Revenue (₹ Thousands)")
plt.tight_layout()
fig.savefig(os.path.join(out_dir, "01_monthly_revenue_trend.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    Saved → 01_monthly_revenue_trend.png")

# --- Fig 2 : Revenue by Region ---
reg = sql_results["Revenue by Region"]
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.barh(reg["region"], reg["total_revenue"] / 1000,
               color=PALETTE[:len(reg)], edgecolor="#0f0f14", linewidth=0.5)
for bar, val in zip(bars, reg["total_revenue"]):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"₹{val/1000:.1f}K", va="center", fontsize=10, color="#f0f0f5")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}K"))
ax.set_title("Total Revenue by Region", fontsize=14, pad=12)
ax.set_xlabel("Revenue (₹ Thousands)")
plt.tight_layout()
fig.savefig(os.path.join(out_dir, "02_revenue_by_region.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    Saved → 02_revenue_by_region.png")

# --- Fig 3 : Revenue vs Profit by Category (grouped bar) ---
cat = sql_results["Revenue by Product Category"]
x   = np.arange(len(cat))
w   = 0.38
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(x - w/2, cat["revenue"] / 1000, w, label="Revenue", color=ACCENT, alpha=0.9)
ax.bar(x + w/2, cat["profit"] / 1000,  w, label="Profit",  color=GREEN,  alpha=0.9)
ax.set_xticks(x)
ax.set_xticklabels(cat["product_category"], fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}K"))
ax.set_title("Revenue & Profit by Product Category", fontsize=14, pad=12)
ax.set_ylabel("Amount (₹ Thousands)")
ax.legend(framealpha=0.2)
plt.tight_layout()
fig.savefig(os.path.join(out_dir, "03_revenue_profit_by_category.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    Saved → 03_revenue_profit_by_category.png")

# --- Fig 4 : Top Sales Reps ---
reps = sql_results["Top 5 Sales Reps by Profit"]
fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.bar(reps["sales_rep"], reps["total_profit"] / 1000,
              color=PALETTE[:len(reps)], edgecolor="#0f0f14", linewidth=0.5)
for bar, val in zip(bars, reps["total_profit"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f"₹{val/1000:.1f}K", ha="center", fontsize=9, color="#f0f0f5")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}K"))
ax.set_title("Top Sales Representatives by Profit", fontsize=14, pad=12)
ax.set_ylabel("Total Profit (₹ Thousands)")
plt.tight_layout()
fig.savefig(os.path.join(out_dir, "04_top_sales_reps.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    Saved → 04_top_sales_reps.png")

# --- Fig 5 : Discount vs Profit Scatter ---
fig, ax = plt.subplots(figsize=(8, 5))
scatter = ax.scatter(df["discount_pct"], df["profit"] / 1000,
                     c=df["revenue"] / 1000, cmap="plasma",
                     alpha=0.7, edgecolors="none", s=60)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Revenue (₹K)", color="#9090a8")
ax.set_xlabel("Discount %")
ax.set_ylabel("Profit (₹ Thousands)")
ax.set_title("Discount % vs Profit (sized by Revenue)", fontsize=14, pad=12)
plt.tight_layout()
fig.savefig(os.path.join(out_dir, "05_discount_vs_profit.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    Saved → 05_discount_vs_profit.png")

# --- Fig 6 : Revenue Heatmap (Month × Category) ---
pivot = df.pivot_table(values="revenue", index="product_category",
                       columns="month_label", aggfunc="sum", fill_value=0)
fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(pivot / 1000, ax=ax, cmap="magma", linewidths=0.4,
            linecolor="#0f0f14", fmt=".0f", annot=True,
            cbar_kws={"label": "Revenue (₹K)"})
ax.set_title("Revenue Heatmap — Category × Month", fontsize=14, pad=12)
ax.set_xlabel("")
ax.set_ylabel("")
plt.xticks(rotation=30, ha="right", fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(out_dir, "06_revenue_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    Saved → 06_revenue_heatmap.png")

# ── 6. EXPORT SUMMARY REPORT ─────────────────────────────────────────────────
print("\n[6] Exporting Summary Report …")

report_lines = [
    "SALES PERFORMANCE ANALYSIS — SUMMARY REPORT",
    "Author: Ayushi Shukla  |  Tools: Python, Pandas, SQL, Matplotlib, Seaborn",
    "=" * 60,
    "",
    "KPI OVERVIEW",
    f"  Total Revenue    : ₹{total_revenue:,.2f}",
    f"  Total Profit     : ₹{total_profit:,.2f}",
    f"  Profit Margin    : {profit_margin:.1f}%",
    f"  Avg Order Value  : ₹{avg_order_val:,.2f}",
    f"  Total Units Sold : {total_units:,}",
    f"  Avg Discount     : {avg_discount:.1f}%",
    f"  Outliers Flagged : {len(outliers)}",
    "",
    "REGIONAL PERFORMANCE",
]
for _, row in sql_results["Revenue by Region"].iterrows():
    report_lines.append(f"  {row['region']:<8}  Revenue: ₹{row['total_revenue']:>10,.2f}  Orders: {row['num_orders']}")
report_lines += [
    "",
    "TOP SALES REPS (by Profit)",
]
for _, row in sql_results["Top 5 Sales Reps by Profit"].iterrows():
    report_lines.append(f"  {row['sales_rep']:<15}  Profit: ₹{row['total_profit']:>10,.2f}  Orders: {row['orders']}")
report_lines += [
    "",
    "KEY INSIGHTS",
    "  1. North region leads in revenue, driven by Electronics & Furniture.",
    "  2. Electronics & Furniture show highest profit margins.",
    "  3. Higher discounts (>10%) correlate with reduced per-order profit.",
    "  4. Sneha Patel consistently drives high-value corporate deals.",
    "  5. Q1 growth trend continues steadily into Q2 2024.",
    "",
    "FILES GENERATED",
    "  data/sales_data.csv                   — Raw dataset",
    "  SQL/queries.sql                        — SQL queries",
    "  reports/01_monthly_revenue_trend.png   — Monthly trend chart",
    "  reports/02_revenue_by_region.png       — Regional breakdown",
    "  reports/03_revenue_profit_by_category.png — Category analysis",
    "  reports/04_top_sales_reps.png          — Rep performance",
    "  reports/05_discount_vs_profit.png      — Discount impact",
    "  reports/06_revenue_heatmap.png         — Monthly heatmap",
]

report_text = "\n".join(report_lines)
with open(os.path.join(out_dir, "summary_report.txt"), "w") as f:
    f.write(report_text)

print(report_text)
print("\n✓  Analysis complete. All outputs saved to /reports/")
