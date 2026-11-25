
import duckdb
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "fleetsense.duckdb")

con = duckdb.connect(DB_PATH, read_only=True)

print("========== WAREHOUSE VERIFICATION ==========")

tables = [
    "fact_trips",
    "dim_zones",
    "dim_calendar",
    "hourly_demand_by_zone"
]

for table in tables:
    count = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count:,} records")

print("\n========== FACT TABLE CHECKS ==========")

print("Trip ID duplicates:",
      con.execute("""
          SELECT COUNT(*) - COUNT(DISTINCT trip_id)
          FROM fact_trips
      """).fetchone()[0])

print("Missing pickup timestamps:",
      con.execute("""
          SELECT COUNT(*) FROM fact_trips
          WHERE pickup_datetime IS NULL
      """).fetchone()[0])

print("Missing drop-off timestamps:",
      con.execute("""
          SELECT COUNT(*) FROM fact_trips
          WHERE dropoff_datetime IS NULL
      """).fetchone()[0])

print("\n========== HOURLY DEMAND CHECK ==========")

fact_count = con.execute("""
    SELECT COUNT(*)
    FROM fact_trips
    WHERE pickup_datetime IS NOT NULL
      AND pickup_location_id IS NOT NULL
""").fetchone()[0]

hourly_count = con.execute("""
    SELECT SUM(trip_count)
    FROM hourly_demand_by_zone
""").fetchone()[0]

print("Eligible fact trips:", fact_count)
print("Hourly demand trip total:", hourly_count)
print("Difference:", fact_count - (hourly_count or 0))

print("\n========== DATE RANGE ==========")

print(con.execute("""
    SELECT MIN(pickup_datetime), MAX(pickup_datetime)
    FROM fact_trips
""").fetchone())

print("\n========== ZONE VALIDATION ==========")

unknown_zones = con.execute("""
    SELECT COUNT(*)
    FROM fact_trips f
    LEFT JOIN dim_zones z
      ON f.pickup_location_id = z.location_id
    WHERE f.pickup_location_id IS NOT NULL
      AND z.location_id IS NULL
""").fetchone()[0]

print("Unknown pickup zone IDs:", unknown_zones)

print("\n========== VERIFICATION COMPLETED ==========")

con.close()

