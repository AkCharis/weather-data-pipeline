import os
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv


def save_to_db(df):
    load_dotenv()

    # Load environment variables
    DB_HOST=os.getenv('DB_HOST', 'localhost')
    DB_PORT=os.getenv('DB_PORT', 5432)
    DB_NAME=os.getenv('DB_NAME')
    DB_USERNAME=os.getenv('DB_USERNAME')
    DB_PASSWORD=os.getenv('DB_PASSWORD')

    url = f'postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # Connect database engine
    engine = sqlalchemy.create_engine(url)

    # Write dataframe to database
    #df.to_sql(name='weather_metrics', con=engine, if_exists='append', index=False)

    existing_records = pd.read_sql(
        "SELECT city_name, time FROM weather_metrics", con=engine
    )
    
    if not existing_records.empty:
        existing_records['time'] = pd.to_datetime(existing_records['time'])
        # Perform anti-join to keep only new records
        cond = df.set_index(['city_name', 'time']).index.isin(
            existing_records.set_index(['city_name', 'time']).index
        )
        new_df = df[~cond].copy()
    else:
        new_df = df.copy()

    if not new_df.empty:
        new_df.to_sql(name='weather_metrics', con=engine, if_exists='append', index=False)
        print(f"✅ Pipeline finished successfully! Inserted {len(new_df)} rows into PostgreSQL.")
    else:
        print("No new records to insert.")

    return len(df)