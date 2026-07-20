import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "california_energy_weather.csv"
OUTPUT_FILE = PROJECT_ROOT / "public" / "latest_inputs.json"


def main():
    data = pd.read_csv(INPUT_FILE, parse_dates=["timestamp"])
    data = data.sort_values("timestamp").dropna()

    latest = data.iloc[-1]

    values = {
        "timestamp": latest["timestamp"].isoformat(),
        "temperature_c": round(float(latest["temperature_c"]), 1),
        "humidity_percent": round(float(latest["humidity_percent"]), 1),
        "wind_speed_kmh": round(float(latest["wind_speed_kmh"]), 1),
        "hour": int(latest["hour"]),
        "day_of_week": int(latest["day_of_week"]),
        "month": int(latest["month"]),
        "is_weekend": int(latest["is_weekend"]),
        "demand_1_hour_ago": round(
            float(latest["demand_1_hour_ago"])
        ),
        "demand_24_hours_ago": round(
            float(latest["demand_24_hours_ago"])
        ),
        "demand_168_hours_ago": round(
            float(latest["demand_168_hours_ago"])
        ),
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(values, file, indent=2)

    print("Latest real observation exported successfully.")
    print(f"Timestamp: {values['timestamp']}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()