from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = PROJECT_ROOT / "model" / "demand_model.joblib"

model_bundle = joblib.load(MODEL_FILE)
model = model_bundle["model"]
features = model_bundle["features"]


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "model": model_bundle["model_name"],
            "region": model_bundle["region"],
        }
    )


@app.post("/api/predict")
def predict():
    try:
        body = request.get_json()

        required_fields = {
            "temperature_c": float,
            "humidity_percent": float,
            "wind_speed_kmh": float,
            "hour": int,
            "day_of_week": int,
            "month": int,
            "is_weekend": int,
            "demand_1_hour_ago": float,
            "demand_24_hours_ago": float,
            "demand_168_hours_ago": float,
        }

        missing = [
            field
            for field in required_fields
            if field not in body
        ]

        if missing:
            return jsonify(
                {
                    "error": "Missing required fields",
                    "missing": missing,
                }
            ), 400

        row = {
            field: converter(body[field])
            for field, converter in required_fields.items()
        }

        input_data = pd.DataFrame([row], columns=features)
        prediction = float(model.predict(input_data)[0])

        return jsonify(
            {
                "predicted_demand_mw": round(prediction, 2),
                "model": model_bundle["model_name"],
                "region": model_bundle["region"],
            }
        )

    except (TypeError, ValueError) as error:
        return jsonify(
            {
                "error": "Invalid input",
                "message": str(error),
            }
        ), 400

    except Exception as error:
        return jsonify(
            {
                "error": "Prediction failed",
                "message": str(error),
            }
        ), 500


if __name__ == "__main__":
    app.run(port=8001, debug=True)
