import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "california_energy_weather.csv"
OUTPUT_FILE = PROJECT_ROOT / "model" / "web_model.json"

FEATURES = [
    "temperature_c",
    "humidity_percent",
    "wind_speed_kmh",
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "demand_1_hour_ago",
    "demand_24_hours_ago",
    "demand_168_hours_ago",
]


def calculate_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)
    mape = np.mean(
        np.abs((actual - predicted) / actual)
    ) * 100

    return {
        "mae_mw": round(float(mae), 2),
        "rmse_mw": round(float(rmse), 2),
        "r2": round(float(r2), 4),
        "mape_percent": round(float(mape), 2),
    }


def export_tree(tree):
    return {
        "children_left": tree.children_left.tolist(),
        "children_right": tree.children_right.tolist(),
        "feature": tree.feature.tolist(),
        "threshold": tree.threshold.tolist(),
        "value": [
            float(node[0][0])
            for node in tree.value
        ],
    }


def main():
    data = pd.read_csv(
        DATA_FILE,
        parse_dates=["timestamp"],
    )

    data = data.sort_values("timestamp").dropna()

    split_index = int(len(data) * 0.8)

    train = data.iloc[:split_index]
    test = data.iloc[split_index:]

    X_train = train[FEATURES]
    y_train = train["demand_mw"]

    X_test = test[FEATURES]
    y_test = test["demand_mw"]

    print("Training web-compatible gradient boosting model...")

    model = GradientBoostingRegressor(
        n_estimators=250,
        learning_rate=0.05,
        max_depth=3,
        min_samples_leaf=20,
        loss="huber",
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    metrics = calculate_metrics(
        y_test.to_numpy(),
        predictions,
    )

    trees = [
        export_tree(estimator[0].tree_)
        for estimator in model.estimators_
    ]

    exported_model = {
        "model_name": "Gradient Boosting Regressor",
        "region": "California ISO",
        "features": FEATURES,
        "initial_prediction": float(
            np.asarray(model.init_.constant_).ravel()[0]
        ),
        "learning_rate": float(model.learning_rate),
        "trees": trees,
        "metrics": metrics,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(exported_model, file)

    print("Web model exported successfully!")
    print(json.dumps(metrics, indent=2))
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()