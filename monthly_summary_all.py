
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

files = sorted(
    DATA_DIR.glob("service_day_trips_2025-??.parquet")
)

print("Monthly files found:", len(files))

if len(files) != 12:
    print("Warning: Expected 12 monthly files!")

monthly_results = []

for file in files:

    month = file.stem.replace("service_day_trips_", "")

    print("Analyzing:", month)

    df = pd.read_parquet(
        file,
        columns=[
            "total_amount",
            "fare_amount",
            "trip_distance"
        ]
    )

    summary = {
        "month": month,
        "total_trips": len(df),
        "total_revenue": df["total_amount"].sum(),
        "average_fare": df["fare_amount"].mean(),
        "average_distance": df["trip_distance"].mean(),
        "total_distance": df["trip_distance"].sum()
    }

    monthly_results.append(summary)

    del df

result = pd.DataFrame(monthly_results)

output_file = DATA_DIR / "monthly_summary_2025.csv"

result.to_csv(output_file, index=False)

print("\n--- 2025 MONTHLY SUMMARY ---")
print(result.to_string(index=False))

print("\nMonthly Summary Completed!")
print("CSV Saved at:", output_file)
