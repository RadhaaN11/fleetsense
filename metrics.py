
from pathlib import Path
import pandas as pd
import gc

# ==========================================
# FLEETSENSE - WEEK 3 METRICS
# ==========================================

DATA_FOLDER = Path("raw")
OUTPUT_FOLDER = Path("reports")

REQUIRED_COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "fare_amount",
    "total_amount"
]


def calculate_month_metrics(file_path):

    print(f"\nProcessing: {file_path.name}")

    df = pd.read_parquet(
        file_path,
        columns=REQUIRED_COLUMNS
    )

    df["tpep_pickup_datetime"] = pd.to_datetime(
        df["tpep_pickup_datetime"], errors="coerce"
    )

    df["tpep_dropoff_datetime"] = pd.to_datetime(
        df["tpep_dropoff_datetime"], errors="coerce"
    )

    df["fare_amount"] = pd.to_numeric(
        df["fare_amount"], errors="coerce"
    )

    df["total_amount"] = pd.to_numeric(
        df["total_amount"], errors="coerce"
    )

    df["duration_minutes"] = (
        df["tpep_dropoff_datetime"]
        - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    # Validation rules: only valid 2025 trips
    valid = (
        df["tpep_pickup_datetime"].notna()
        & df["tpep_dropoff_datetime"].notna()
        & df["fare_amount"].notna()
        & df["total_amount"].notna()
        & (df["tpep_pickup_datetime"].dt.year == 2025)
        & (df["duration_minutes"] > 0)
        & (df["duration_minutes"] <= 1440)
        & (df["fare_amount"] >= 0)
        & (df["total_amount"] >= 0)
    )

    valid_df = df.loc[valid]

    total_trips = len(valid_df)

    total_revenue = valid_df["total_amount"].sum()

    fare_sum = valid_df["fare_amount"].sum()

    duration_sum = valid_df["duration_minutes"].sum()

    average_fare = (
        fare_sum / total_trips if total_trips else 0
    )

    average_duration = (
        duration_sum / total_trips if total_trips else 0
    )

    # Monthly aggregate trip activity proxy
    month_text = file_path.stem.replace(
        "yellow_tripdata_", ""
    )

    month = pd.Period(month_text, freq="M")

    calendar_minutes = month.days_in_month * 24 * 60

    activity_proxy = (
        duration_sum / calendar_minutes
    ) * 100

    result = {
        "Month": month_text,
        "Trips": total_trips,
        "Revenue": total_revenue,
        "Average Fare": average_fare,
        "Average Duration (Minutes)": average_duration,
        "Aggregate Trip Activity Proxy (%)": activity_proxy
    }

    del valid_df
    del df
    gc.collect()

    return result, fare_sum, duration_sum


def main():

    files = sorted(
        DATA_FOLDER.glob("yellow_tripdata_2025-*.parquet")
    )

    if not files:
        print("No Parquet datasets found!")
        return

    print(f"Found {len(files)} monthly datasets.")

    monthly_results = []

    yearly_trips = 0
    yearly_revenue = 0
    yearly_fare_sum = 0
    yearly_duration_sum = 0

    for file_path in files:

        result, fare_sum, duration_sum = (
            calculate_month_metrics(file_path)
        )

        monthly_results.append(result)

        yearly_trips += result["Trips"]
        yearly_revenue += result["Revenue"]
        yearly_fare_sum += fare_sum
        yearly_duration_sum += duration_sum

    yearly_average_fare = (
        yearly_fare_sum / yearly_trips
        if yearly_trips else 0
    )

    yearly_average_duration = (
        yearly_duration_sum / yearly_trips
        if yearly_trips else 0
    )

    # 2025 has exactly 365 calendar days
    yearly_calendar_minutes = 365 * 24 * 60

    yearly_activity_proxy = (
        yearly_duration_sum / yearly_calendar_minutes
    ) * 100

    yearly_summary = {
        "Month": "YEAR TOTAL",
        "Trips": yearly_trips,
        "Revenue": yearly_revenue,
        "Average Fare": yearly_average_fare,
        "Average Duration (Minutes)": yearly_average_duration,
        "Aggregate Trip Activity Proxy (%)": yearly_activity_proxy
    }

    results_df = pd.DataFrame(monthly_results)

    results_df = pd.concat(
        [results_df, pd.DataFrame([yearly_summary])],
        ignore_index=True
    )

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_FOLDER / "metrics_2025.csv"

    results_df.to_csv(output_file, index=False)

    print("\n===================================")
    print("       WEEK 3 METRICS REPORT")
    print("===================================\n")

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}"
        )
    )

    print("\nAll monthly datasets processed successfully!")
    print("\nReport saved at:")
    print(output_file)


if __name__ == "__main__":
    main()
