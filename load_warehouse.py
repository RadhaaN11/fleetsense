
import duckdb
from pathlib import Path

# ==========================================
# FLEETSENSE - LOAD DATA INTO WAREHOUSE
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_FOLDER = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "data" / "fleetsense.duckdb"

def main():

    print("========== FLEETSENSE WAREHOUSE LOADING ==========")

    if not DB_PATH.exists():
        print("Database not found! Run create_warehouse.py first.")
        return

    files = sorted(
        DATA_FOLDER.glob("valid_trips_2025-*.parquet")
    )

    if not files:
        print("No processed Parquet files found!")
        return

    con = duckdb.connect(str(DB_PATH))

    # Add CBD congestion fee column if missing
    con.execute("""
        ALTER TABLE fact_trips
        ADD COLUMN IF NOT EXISTS cbd_congestion_fee DOUBLE
    """)

    # Clear old fact records to avoid duplicates
    con.execute("DELETE FROM fact_trips")

    total_loaded = 0
    trip_id_offset = 0

    for file_path in files:

        print(f"\nLoading: {file_path.name}")

        parquet_path = file_path.as_posix().replace("'", "''")

        row_count = con.execute(f"""
            SELECT COUNT(*)
            FROM read_parquet('{parquet_path}')
        """).fetchone()[0]

        con.execute(f"""
            INSERT INTO fact_trips (
                trip_id,
                pickup_datetime,
                dropoff_datetime,
                pickup_location_id,
                dropoff_location_id,
                trip_distance,
                fare_amount,
                extra,
                mta_tax,
                tip_amount,
                tolls_amount,
                improvement_surcharge,
                total_amount,
                congestion_surcharge,
                airport_fee,
                cbd_congestion_fee
            )
            SELECT
                ROW_NUMBER() OVER () + {trip_id_offset},
                tpep_pickup_datetime,
                tpep_dropoff_datetime,
                PULocationID,
                DOLocationID,
                trip_distance,
                fare_amount,
                extra,
                mta_tax,
                tip_amount,
                tolls_amount,
                improvement_surcharge,
                total_amount,
                congestion_surcharge,
                Airport_fee,
                cbd_congestion_fee
            FROM read_parquet('{parquet_path}')
        """)

        trip_id_offset += row_count
        total_loaded += row_count

        print(f"Records loaded: {row_count:,}")

    print("\n========== LOADING COMPLETED ==========")
    print(f"Total records loaded: {total_loaded:,}")

    con.close()


if __name__ == "__main__":
    main()
