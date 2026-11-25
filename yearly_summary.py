
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "monthly_summary_2025.csv"
)

df = pd.read_csv(INPUT_FILE)

yearly_summary = {
    "Year": 2025,
    "Total Trips": df["total_trips"].sum(),
    "Total Revenue": df["total_revenue"].sum(),
    "Average Fare": df["average_fare"].mean(),
    "Average Distance": df["average_distance"].mean(),
    "Total Distance": df["total_distance"].sum()
}

print("\n===== YEARLY SUMMARY 2025 =====")

for key, value in yearly_summary.items():
    if isinstance(value, float):
        print(f"{key}: {value:,.2f}")
    else:
        print(f"{key}: {value:,}")

print("\nYearly Analysis Completed!")
