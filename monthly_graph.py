

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# FLEETSENSE - MONTHLY REVENUE GRAPH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "monthly_summary_2025.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "monthly_revenue_graph.png"
)

print("Loading Monthly Summary...")

if not INPUT_FILE.exists():
    print("Monthly summary CSV not found!")
    raise SystemExit(1)

df = pd.read_csv(INPUT_FILE)

if not {"month", "total_revenue"}.issubset(df.columns):
    print("Required columns are missing!")
    raise SystemExit(1)

df["total_revenue"] = pd.to_numeric(
    df["total_revenue"], errors="coerce"
)

df = df.dropna(subset=["month", "total_revenue"])

if df.empty:
    print("No valid monthly revenue data found!")
    raise SystemExit(1)

plt.figure(figsize=(12, 6))

bars = plt.bar(
    df["month"].astype(str),
    df["total_revenue"]
)

plt.xlabel("Month")
plt.ylabel("Total Revenue ($)")
plt.title("Monthly Revenue Analysis - 2025")

plt.xticks(rotation=45)

plt.bar_label(
    bars,
    labels=[
        f"${value:,.0f}"
        for value in df["total_revenue"]
    ],
    padding=3,
    fontsize=8
)

plt.tight_layout()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(OUTPUT_FILE, dpi=300)

plt.show()

print("\nMonthly Revenue Graph Created!")
print("Saved at:", OUTPUT_FILE)
