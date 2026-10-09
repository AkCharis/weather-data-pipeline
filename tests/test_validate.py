import os
import numpy as np
import pandas as pd
import pytest
from validate import filter_data, get_valid_data, is_numeric_type, log_bad_data


@pytest.fixture
def valid_dataframe():
    return pd.DataFrame(
        {
            'time': pd.to_datetime(['2026-10-09 00:00:00', '2026-10-09 01:00:00']),
            'city_name': ['Lagos', 'London'],
            'temperature_2m': [30.0, 15.0],
            'precipitation': [0.0, 1.2],
            'wind_speed_10m': [5.5, 12.0],
        }
    )


@pytest.fixture
def invalid_dataframe():
    return pd.DataFrame(
        {
            'time': [pd.NaT, '2026-10-09 01:00:00'],
            'city_name': ['Lagos', None],
            'temperature_2m': [150.0, np.nan],  # Out of bounds & missing
            'precipitation': [-2.0, 0.0],  # Negative precipitation
            'wind_speed_10m': [5.5, -10.0],  # Negative wind speed
        }
    )


def test_is_numeric_type(valid_dataframe):
    assert is_numeric_type(valid_dataframe) is True

    # Bad type test
    invalid_type_df = valid_dataframe.copy()
    invalid_type_df['precipitation'] = invalid_type_df['precipitation'].astype(str)
    assert is_numeric_type(invalid_type_df) is False


def test_filter_data(valid_dataframe, invalid_dataframe):
    valid_mask = filter_data(valid_dataframe)
    assert valid_mask.all() == True  # All rows should pass

    invalid_mask = filter_data(invalid_dataframe)
    assert invalid_mask.any() == False  # All rows should fail


def test_get_valid_data(valid_dataframe, invalid_dataframe):
    clean_df = get_valid_data(valid_dataframe)
    assert len(clean_df) == 2

    bad_df = get_valid_data(invalid_dataframe)
    assert len(bad_df) == 0


def test_log_bad_data_creates_csv(invalid_dataframe, tmp_path):
    # Patch quarantine folder to use temporary directory
    os.makedirs("quarantine_logs", exist_ok=True)

    log_bad_data(invalid_dataframe)

    # Verify log folder exists and CSV was created
    logs = os.listdir("quarantine_logs")
    assert len(logs) > 0