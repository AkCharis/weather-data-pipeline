import numpy as np
import pandas as pd


def is_numeric_type(data):
    # A list of columns to validate
    cols_to_check = ['temperature_2m', 'precipitation', 'wind_speed_10m']

    # Check if all provided columns are of the numeric type
    return all(pd.api.types.is_numeric_dtype(data[col]) for col in cols_to_check)


def filter_data(data):
    # Return a boolean mask of false values if invalid numeric columns
    if not is_numeric_type(data):
        print("One or more numeric columns have invalid types") 
        return pd.Series(False, index=data.index)

    # Define valid mask variables
    valid_time = data['time'].notna()
    valid_temp_not_null = data['temperature_2m'].notna()
    valid_city = data['city_name'].notna()
    valid_wind_not_null = data['wind_speed_10m'].notna()
    valid_precipitation_not_null = data['precipitation'].notna()

    valid_temp_range = data['temperature_2m'].between(-50, 60)
    valid_wind = data['wind_speed_10m'] >= 0
    valid_precipitation = data['precipitation'] >= 0

    # Create a mask of valid parameters
    valid_mask = (
        valid_time & valid_temp_not_null & valid_city &
        valid_wind_not_null & valid_precipitation_not_null &
        valid_temp_range & valid_wind & valid_precipitation
        )

    return valid_mask


def get_valid_data(data):
    valid_mask = filter_data(data)

    valid_data = data[valid_mask].copy()

    print(f'Validated {len(valid_data)} records out of {len(data)}')

    return valid_data


def log_bad_data(data):
    valid_mask = filter_data(data)

    quarantine_data = data[~valid_mask].copy()

    current_time = pd.Timestamp.today(tz='UTC').strftime('%Y-%m-%d-%H-%M-%S')

    # Output quarantine logs for invalid numeric columns
    if not is_numeric_type(quarantine_data):
        print("Cannot log data due to invalid numeric columns")
        
        return quarantine_data[quarantine_data.map(type)==str].to_csv(f"quarantine_logs/invalid_record_type_{current_time}.csv", index=False)

    if not quarantine_data.empty:
        conditions = [
            quarantine_data['time'].isna() | quarantine_data['city_name'].isna(),
            quarantine_data['temperature_2m'].isna(),
            ~quarantine_data['temperature_2m'].between(-50, 60),
            quarantine_data['wind_speed_10m'] < 0,
            quarantine_data['precipitation'] < 0
        ]

        choices = [
            'Missing critical identifier values (time/city)',
            'Missing temperature value',
            'Temperature value out of bounds',
            'Invalid wind speed value',
            'Invalid precipitation value'
        ]

        # Output quarantine logs with failure messages in YYYY=MM-DD-HH-MM-SS format
        quarantine_data['failure_message'] = np.select(conditions, choices, default='Multiple or Unknown Errors')
        quarantine_data.to_csv(f"quarantine_logs/invalid_records_{current_time}.csv", index=False)
        print(f"Quarantined {len(quarantine_data)} records")