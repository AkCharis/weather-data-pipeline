# End-to-End Weather Data Ingestion & Quality Pipeline

An end-to-end, production-grade ETL pipeline built in Python that fetches hourly forecast metrics from the Open-Meteo API, performs vector-based row-level data quality validation, quarantines invalid records with diagnostic messages, and persists clean records into a PostgreSQL data warehouse.

📐 Pipeline Architecture
```
               ┌────────────────────────┐
               │    Open-Meteo API      │
               └───────────┬────────────┘
                           │ (JSON Extraction)
                           ▼
               ┌────────────────────────┐
               │     src/ingest.py      │
               │  Fetch & Flatten JSON  │
               └───────────┬────────────┘
                           │ (Raw DataFrame)
                           ▼
               ┌────────────────────────┐
               │    src/validate.py     │
               │ Vectorized Quality Gate│
               └─────┬────────────┬─────┘
                     │            │
         [Valid Data]│            │[Corrupted / Out-of-Bounds]
                     ▼            ▼
   ┌───────────────────┐        ┌────────────────────────────────┐
   │    src/db.py      │        │      quarantine_logs/          │
   │ PostgreSQL Store  │        │ CSV Logs + Error Diagnostics   │
   └───────────────────┘        └────────────────────────────────┘
```


## Key Features

1. Resilient API Extraction: Robust network exception handling and rate-limiting safeguards when pulling hourly metrics (temperature_2m, precipitation, wind_speed_10m).

2. Lineage & Auditability: Enriches raw payloads with extraction timestamps (extracted_at_utc) and geographical identifiers.

3. Vectorized Data Quality Gateway: Employs high-performance Pandas and NumPy operations (np.select) to check data types, missing fields, and physical boundaries (-50°C to 60°C for temperature, non-negative values for precipitation and wind speed).

4. Automated Quarantine System: Separates rejected rows and logs them into timestamped CSV files with explicit failure messages (Missing critical identifier, Temperature out of bounds, etc.).

5. Relational Persistence: Automatically creates database schemas and persists clean records into PostgreSQL using SQLAlchemy and psycopg2.

6. Automated Test Suite: Full unit and integration test coverage using pytest and unittest.mock to simulate API behavior without making network calls.

## Tech Stack & Tools

* Language: Python 3.10+

* Package Management: uv

* Data Transformation: Pandas, NumPy

* Database & ORM: PostgreSQL, SQLAlchemy, Psycopg2

* Testing Framework: pytest

* Environment Management: python-dotenv

## Project Structure

```
weather-data-pipeline/
├── quarantine_logs/            # Export folder for rejected records
│   └── .gitkeep
├── src/
│   ├── __init__.py            # Package entry exporter
│   ├── ingest.py              # API extraction & JSON normalization
│   ├── validate.py            # Row validation & quarantine logger
│   └── db.py                  # PostgreSQL connection & loading
├── tests/                     # Test suite
│   ├── test_ingest.py
│   ├── test_validate.py
│   └── test_db.py
├── .env.example               # Template for environment configuration
├── .gitignore                 # Excludes secrets, cache, and log CSVs
├── main.py                    # Root orchestrator script
├── pyproject.toml             # Project dependencies and tool configurations
└── README.md                  # Project documentation
```


## Getting Started

### Prerequisites

* Python 3.10 or higher

* PostgreSQL running locally or in a container

* uv package manager (optional, but recommended)

### Clone the Repository

```
git clone https://github.com/your-username/weather-data-pipeline.git
cd weather-data-pipeline
```


### Environment Setup

Set up a virtual environment and install dependencies defined in pyproject.toml:

**Using uv (Recommended):**

Automatically creates .venv and syncs dependencies from pyproject.toml
`uv sync`


**Using standard Python venv & pip:**
```
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```


### Configure Credentials

Copy the example environment file and update it with your local PostgreSQL credentials:

`cp .env.example .env`


Edit .env:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather_db
DB_USER=postgres
DB_PASSWORD=your_password_here
```


### Initialize Database Schema

Ensure PostgreSQL is running, then create the target database:

`CREATE DATABASE weather_db;`


## Running the Pipeline

To execute the full end-to-end ingestion, validation, and persistence pipeline:

`uv run python main.py`


### Sample Output

```
...Starting Weather Data Pipeline...
Successfully fetched data for Lagos
Successfully fetched data for London
Successfully fetched data for New York
Successfully fetched data for Ibadan
Data loaded successfully!
Validated 384 records out of 384
Inserted 672 new unique records.
✅ Pipeline finished successfully! Inserted 672 rows into PostgreSQL.
```


## Running Automated Tests

Run the full pytest suite with mocking enabled:

`uv run pytest`


## Sample SQL Queries

Once the data is ingested, you can query your metrics directly inside PostgreSQL:

***-- Average temperature and wind speed per city***
```
SELECT 
    city_name,
    ROUND(AVG(temperature_2m)::numeric, 2) AS avg_temp_c,
    ROUND(AVG(wind_speed_10m)::numeric, 2) AS avg_wind_speed
FROM weather_metrics
GROUP BY city_name
ORDER BY avg_temp_c DESC;
```

