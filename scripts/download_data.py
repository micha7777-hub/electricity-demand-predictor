import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "california_energy_weather.csv"

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

# California ISO is the balancing authority whose demand we will predict.
EIA_RESPONDENT = "CISO"

# Los Angeles coordinates for the initial weather signal.
LATITUDE = 34.0522
LONGITUDE = -118.2437


def download_electricity_data(api_key: str) -> pd.DataFrame:
    print("Downloading real CAISO electricity-demand data...")

    endpoint = (
        "https://api.eia.gov/v2/electricity/"
        "rto/region-data/data/"
    )

    all_rows = []
    offset = 0
    page_size = 5000

    while True:
        params = {
            "api_key": api_key,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": EIA_RESPONDENT,
            "facets[type][]": "D",
            "start": f"{START_DATE}T00",
            "end": f"{END_DATE}T23",
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": page_size,
        }

        response = requests.get(endpoint, params=params, timeout=60)
        response.raise_for_status()

        payload = response.json()

        if "response" not in payload:
            raise RuntimeError(f"Unexpected EIA response: {payload}")

        rows = payload["response"].get("data", [])

        if not rows:
            break

        all_rows.extend(rows)
        print(f"Downloaded {len(all_rows):,} electricity records")

        if len(rows) < page_size:
            break

        offset += page_size

    if not all_rows:
        raise RuntimeError(
            "The EIA API returned no electricity data. "
            "Check your API key and request settings."
        )

    electricity = pd.DataFrame(all_rows)

    electricity["timestamp"] = pd.to_datetime(
        electricity["period"],
        utc=True,
        errors="coerce",
    )

    electricity["demand_mw"] = pd.to_numeric(
        electricity["value"],
        errors="coerce",
    )

    electricity = electricity[
        ["timestamp", "demand_mw"]
    ].dropna()

    electricity = (
        electricity.groupby("timestamp", as_index=False)["demand_mw"]
        .mean()
        .sort_values("timestamp")
    )

    return electricity


def download_weather_data() -> pd.DataFrame:
    print("Downloading real historical weather data...")

    endpoint = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "timezone": "UTC",
    }

    response = requests.get(endpoint, params=params, timeout=60)
    response.raise_for_status()

    payload = response.json()
    hourly = payload.get("hourly")

    if not hourly:
        raise RuntimeError(
            f"Unexpected Open-Meteo response: {payload}"
        )

    weather = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                hourly["time"],
                utc=True,
                errors="coerce",
            ),
            "temperature_c": hourly["temperature_2m"],
            "humidity_percent": hourly["relative_humidity_2m"],
            "wind_speed_kmh": hourly["wind_speed_10m"],
        }
    )

    return weather.dropna(subset=["timestamp"])


def build_dataset(
    electricity: pd.DataFrame,
    weather: pd.DataFrame,
) -> pd.DataFrame:
    print("Combining electricity and weather data...")

    dataset = pd.merge(
        electricity,
        weather,
        on="timestamp",
        how="inner",
    ).sort_values("timestamp")

    # Convert UTC timestamps to California local time.
    local_time = dataset["timestamp"].dt.tz_convert(
        "America/Los_Angeles"
    )

    dataset["hour"] = local_time.dt.hour
    dataset["day_of_week"] = local_time.dt.dayofweek
    dataset["month"] = local_time.dt.month
    dataset["is_weekend"] = (
        dataset["day_of_week"] >= 5
    ).astype(int)

    # Previous demand values provide strong time-series signals.
    dataset["demand_1_hour_ago"] = dataset[
        "demand_mw"
    ].shift(1)

    dataset["demand_24_hours_ago"] = dataset[
        "demand_mw"
    ].shift(24)

    dataset["demand_168_hours_ago"] = dataset[
        "demand_mw"
    ].shift(168)

    dataset = dataset.dropna().reset_index(drop=True)

    return dataset


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env.local")

    api_key = os.getenv("EIA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "EIA_API_KEY was not found. "
            "Add it to the .env.local file."
        )

    electricity = download_electricity_data(api_key)
    weather = download_weather_data()
    dataset = build_dataset(electricity, weather)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(OUTPUT_FILE, index=False)

    print()
    print("Dataset created successfully!")
    print(f"File: {OUTPUT_FILE}")
    print(f"Rows: {len(dataset):,}")
    print(f"Columns: {len(dataset.columns)}")
    print()
    print(dataset.head())


if __name__ == "__main__":
    main()