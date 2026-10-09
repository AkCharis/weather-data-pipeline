from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
import requests

# Import the functions from your module
from ingest import ingest_weather_data, load_data

@pytest.fixture
def sample_cities():
    """Returns a list of sample city dictionaries."""
    return [
        {'city': 'Lagos', 'latitude': 6.5244, 'longitude': 3.3792},
        {'city': 'London', 'latitude': 51.5074, 'longitude': -0.1278},
    ]

@pytest.fixture
def mock_open_meteo_response():
    """Returns a realistic raw JSON dictionary from Open-Meteo API."""
    return {
        "hourly": {
            "time": ["2026-10-09T00:00", "2026-10-09T01:00"],
            "temperature_2m": [28.5, 27.1],
            "precipitation": [0.0, 0.2],
            "wind_speed_10m": [12.1, 10.5],
        }
    }


@patch('requests.get')
@patch('time.sleep', return_value=None)  # Skip real sleep delays during test execution
def test_ingest_weather_data_success(mock_sleep, mock_get, sample_cities, mock_open_meteo_response):
    """Tests successful ingestion across multiple cities."""
    # 1. Setup mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_open_meteo_response
    mock_get.return_value = mock_resp

    # 2. Call function
    city_data_list = ingest_weather_data(sample_cities)

    # 3. Assertions
    assert isinstance(city_data_list, list)
    assert len(city_data_list) == 2  # One DataFrame per city
    assert mock_get.call_count == 2

    # Verify schema of the extracted DataFrames
    df_lagos = city_data_list[0]
    assert isinstance(df_lagos, pd.DataFrame)
    assert df_lagos['city_name'].iloc[0] == 'Lagos'
    assert 'extracted_at_utc' in df_lagos.columns
    assert pd.api.types.is_datetime64_any_dtype(df_lagos['time'])


@patch('requests.get')
@patch('time.sleep', return_value=None)
def test_ingest_weather_data_api_failure(mock_sleep, mock_get, sample_cities, mock_open_meteo_response):
    """Tests how ingestion handles an API network error on one city without crashing the rest."""
    # Mock first request failing with HTTP 500/timeout, second succeeding
    failed_resp = requests.exceptions.RequestException("API Connection Failed")
    
    success_resp = MagicMock()
    success_resp.status_code = 200
    success_resp.json.return_value = mock_open_meteo_response

    mock_get.side_effect = [failed_resp, success_resp]

    # Execute
    city_data_list = ingest_weather_data(sample_cities)

    # Only 1 successful city DataFrame should be returned
    assert len(city_data_list) == 1
    assert city_data_list[0]['city_name'].iloc[0] == 'London'


@patch('ingest.ingest_weather_data')
def test_load_data_success(mock_ingest, sample_cities):
    """Tests concatenation into a single DataFrame when ingestion succeeds."""
    df1 = pd.DataFrame({'time': ['2026-10-09'], 'city_name': ['Lagos']})
    df2 = pd.DataFrame({'time': ['2026-10-09'], 'city_name': ['London']})
    mock_ingest.return_value = [df1, df2]

    merged_df = load_data(sample_cities)

    assert isinstance(merged_df, pd.DataFrame)
    assert len(merged_df) == 2
    assert list(merged_df['city_name']) == ['Lagos', 'London']


@patch('ingest.ingest_weather_data')
def test_load_data_empty_response(mock_ingest, sample_cities):
    """Tests load_data behavior when all API requests fail and return an empty list."""
    mock_ingest.return_value = []

    merged_df = load_data(sample_cities)
    assert isinstance(merged_df, pd.DataFrame)
    assert merged_df.empty