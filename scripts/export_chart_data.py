import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "model" / "test_predictions.csv"
OUTPUT_FILE = PROJECT_ROOT / "public" / "predictions.json"


def main():
    predictions = pd.read_csv(
        INPUT_FILE,
        parse_dates=["timestamp"],
    )

    # Display the most recent seven days.
    predictions = predictions.tail(168).copy()

    predictions["time"] = predictions["timestamp"].dt.strftime(
        "%b %d, %H:%M"
    )

    chart_data = []

    for _, row in predictions.iterrows():
        chart_data.append(
            {
                "time": row["time"],
                "actual": round(float(row["demand_mw"])),
                "prediction": round(
                    float(row["predicted_demand_mw"])
                ),
                "baseline": round(
                    float(row["baseline_demand_mw"])
                ),
            }
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(chart_data, file, indent=2)

    print(f"Exported {len(chart_data)} chart observations.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()