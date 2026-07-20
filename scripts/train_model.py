import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "california_energy_weather.csv"
MODEL_FILE = PROJECT_ROOT / "model" / "demand_model.joblib"
METRICS_FILE = PROJECT_ROOT / "model" / "metrics.json"
PREDICTIONS_FILE = PROJECT_ROOT / "model" / "test_predictions.csv"
IMPORTANCE_FILE = PROJECT_ROOT / "model" / "feature_importance.csv"

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

TARGET = "demand_mw"


def calculate_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)

    nonzero = actual != 0
    mape = np.mean(
        np.abs(
            (actual[nonzero] - predicted[nonzero])
            / actual[nonzero]
        )
    ) * 100

    return {
        "mae_mw": round(float(mae), 2),
        "rmse_mw": round(float(rmse), 2),
        "r2": round(float(r2), 4),
        "mape_percent": round(float(mape), 2),
    }


def main():
    print("Loading real electricity and weather data...")

    data = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    data = data.sort_values("timestamp").dropna().reset_index(drop=True)

    # Keep time order intact. Never randomly shuffle time-series data.
    split_index = int(len(data) * 0.8)

    train = data.iloc[:split_index].copy()
    test = data.iloc[split_index:].copy()

    X_train = train[FEATURES]
    y_train = train[TARGET]

    X_test = test[FEATURES]
    y_test = test[TARGET]

    print(f"Training observations: {len(train):,}")
    print(f"Testing observations:  {len(test):,}")
    print(
        f"Training period: {train['timestamp'].min()} "
        f"to {train['timestamp'].max()}"
    )
    print(
        f"Testing period:  {test['timestamp'].min()} "
        f"to {test['timestamp'].max()}"
    )

    # Baseline: assume demand equals the same hour yesterday.
    baseline_predictions = test["demand_24_hours_ago"].to_numpy()
    baseline_metrics = calculate_metrics(
        y_test.to_numpy(),
        baseline_predictions,
    )

    print("\nTraining Histogram Gradient Boosting model...")

    model = HistGradientBoostingRegressor(
        learning_rate=0.07,
        max_iter=350,
        max_leaf_nodes=31,
        min_samples_leaf=25,
        l2_regularization=1.0,
        random_state=42,
    )

    model.fit(X_train, y_train)
    model_predictions = model.predict(X_test)

    model_metrics = calculate_metrics(
        y_test.to_numpy(),
        model_predictions,
    )

    improvement = (
        (
            baseline_metrics["mae_mw"]
            - model_metrics["mae_mw"]
        )
        / baseline_metrics["mae_mw"]
        * 100
    )

    metrics = {
        "model_name": "Histogram Gradient Boosting Regressor",
        "region": "California ISO",
        "training_rows": len(train),
        "testing_rows": len(test),
        "training_start": str(train["timestamp"].min()),
        "training_end": str(train["timestamp"].max()),
        "testing_start": str(test["timestamp"].min()),
        "testing_end": str(test["timestamp"].max()),
        "features": FEATURES,
        "baseline": baseline_metrics,
        "model": model_metrics,
        "mae_improvement_over_baseline_percent": round(
            float(improvement),
            2,
        ),
    }

    print("\nCalculating feature importance...")

    importance_sample_size = min(2500, len(X_test))
    X_importance = X_test.iloc[-importance_sample_size:]
    y_importance = y_test.iloc[-importance_sample_size:]

    importance_result = permutation_importance(
        model,
        X_importance,
        y_importance,
        scoring="neg_mean_absolute_error",
        n_repeats=5,
        random_state=42,
        n_jobs=-1,
    )

    importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": importance_result.importances_mean,
        }
    ).sort_values("importance", ascending=False)

    model_bundle = {
        "model": model,
        "features": FEATURES,
        "model_name": metrics["model_name"],
        "region": metrics["region"],
    }

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model_bundle, MODEL_FILE)

    with open(METRICS_FILE, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    predictions = test[
        ["timestamp", "demand_mw"]
    ].copy()

    predictions["predicted_demand_mw"] = model_predictions
    predictions["baseline_demand_mw"] = baseline_predictions
    predictions.to_csv(PREDICTIONS_FILE, index=False)

    importance.to_csv(IMPORTANCE_FILE, index=False)

    print("\nTraining complete!")
    print("\nBaseline performance:")
    print(json.dumps(baseline_metrics, indent=2))

    print("\nMachine-learning performance:")
    print(json.dumps(model_metrics, indent=2))

    print(
        "\nMAE improvement over baseline: "
        f"{improvement:.2f}%"
    )

    print("\nMost important features:")
    print(importance.head(10).to_string(index=False))

    print(f"\nSaved model: {MODEL_FILE}")
    print(f"Saved metrics: {METRICS_FILE}")
    print(f"Saved predictions: {PREDICTIONS_FILE}")


if __name__ == "__main__":
    main()