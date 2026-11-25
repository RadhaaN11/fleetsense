
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# FLEETSENSE - ZONE ANALYSIS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "processed" / "service_day_trips.parquet"
ZONE_FILE = BASE_DIR / "raw" / "taxi_zone_lookup.csv"
OUTPUT_FOLDER = BASE_DIR / "data" / "processed"

print("Loading Dataset...")

df = pd.read_parquet(DATA_FILE)

print("Dataset Loaded:", f"{len(df):,}")

# Load zone lookup
zones = pd.read_csv(ZONE_FILE)

# Zone-wise pickup analysis
zone_summary = df.groupby("PULocationID").agg(
    total_trips=("PULocationID", "count"),
    total_revenue=("total_amount", "sum"),
    average_fare=("fare_amount", "mean")
).reset_index()

# Add zone names and borough
zone_summary = zone_summary.merge(
    zones,
    left_on="PULocationID",
    right_on="LocationID",
    how="left"
)

# Sort by total trips
zone_summary = zone_summary.sort_values(
    by="total_trips",
    ascending=False
)

# Select Top 10 zones
top_zones = zone_summary.head(10).copy()

# Select useful columns
top_zones = top_zones[
    [
        "PULocationID",
        "Zone",
        "Borough",
        "total_trips",
        "total_revenue",
        "average_fare"
    ]
]

print("\n========== TOP 10 PICKUP ZONES ==========")
print(top_zones.to_string(index=False))

# Save CSV report
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

csv_file = OUTPUT_FOLDER / "top_10_zones.csv"

top_zones.to_csv(csv_file, index=False)

# Create graph
plt.figure(figsize=(12, 7))

labels = (
    top_zones["Zone"].fillna("Unknown")
    + " ("
    + top_zones["PULocationID"].astype(str)
    + ")"
)

plt.bar(labels, top_zones["total_trips"])

plt.xlabel("Pickup Zone")
plt.ylabel("Total Trips")
plt.title("Top 10 Pickup Zones by Trip Count")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

graph_file = OUTPUT_FOLDER / "top_10_zones.png"

plt.savefig(graph_file, dpi=300)
plt.show()

print("\nZone Analysis Completed!")
print("CSV Report:", csv_file)
print("Graph:", graph_file)
