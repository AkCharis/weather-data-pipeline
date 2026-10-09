import numpy as np
import pandas as pd
import requests
import time

def ingest_weather_data(cities):
    city_list = []

    for city in cities:
        # Fetch live data from open-meteo api
        try:
            params = {
                'latitude': city['latitude'],
                'longitude': city['longitude'],
                'hourly': ['temperature_2m' ,'precipitation', 'wind_speed_10m']
            }

            headers = {'User-Agent': 'WeatherPipelineProject/1.0'}
            
            response = requests.get('https://api.open-meteo.com/v1/forecast', params=params, headers=headers, timeout=30)
            response.raise_for_status()

            # Convert extracted data to json
            raw_data = response.json()
    
            # Extract hourly data and convert to dataframe
            data = pd.DataFrame(raw_data['hourly'])
    
            # Format and enrich columns
            data['time'] = pd.to_datetime(data['time'])
            data['city_name'] = city['city']
            data['extracted_at_utc'] = pd.Timestamp.now(tz='UTC')
    
            # Add each city data to the city list
            city_list.append(data)
            print(f"Successfully fetched data for {city['city']}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {city['city']}: {e}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        
        time.sleep(1) # Respect API ratte limits    

    return city_list


def load_data(cities):
    # call the function to get weather data from api
    city_data_list = ingest_weather_data(cities)
    if not city_data_list:
        print('No value extracted from API')
        return pd.DataFrame()

    # merge weather data for different cities into a dataframe
    df = pd.concat([x for x in city_data_list])
    print('Data loaded successfully!')

    return df