import sys
from src import (
    load_data,
    get_valid_data,
    log_bad_data,
    save_to_db,
)

CITIES = [
    {'city': 'Lagos', 'latitude': 6.5244, 'longitude': 3.3792},
    {'city': 'London', 'latitude': 51.5074, 'longitude': -0.1278},
    {'city': 'New York', 'latitude': 40.7128, 'longitude': -74.0060},
    {'city': 'Ibadan', 'latitude': 7.3776, 'longitude': 3.9059},
]

def run_pipeline():
    print("...Starting Weather Data Pipeline...")

    # Ingestion
    raw_df = load_data(CITIES)
    if raw_df.empty:
        print("❌ No data ingested. Exiting pipeline.")
        sys.exit(1)

    # Validation & Quarantine Logging
    log_bad_data(raw_df)
    clean_df = get_valid_data(raw_df)

    if clean_df.empty:
        print("⚠️ No valid records passed validation. Pipeline complete.")
        return

    # Saving to database
    inserted_rows = save_to_db(clean_df)

if __name__ == "__main__":
    run_pipeline()