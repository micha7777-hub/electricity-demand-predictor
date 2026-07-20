import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = PROJECT_ROOT / "model" / "demand_model.joblib"

model_bundle = joblib.load(MODEL_FILE)
model = model_bundle["model"]
features = model_bundle["features"]


class handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS",
        )
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS",
        )
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )

            raw_body = self.rfile.read(content_length)
            body = json.loads(raw_body.decode("utf-8"))

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
                self.send_json(
                    {
                        "error": "Missing required fields",
                        "missing": missing,
                    },
                    400,
                )
                return

            row = {
                field: converter(body[field])
                for field, converter in required_fields.items()
            }

            if not -20 <= row["temperature_c"] <= 60:
                raise ValueError(
                    "Temperature must be between -20°C and 60°C."
                )

            if not 0 <= row["humidity_percent"] <= 100:
                raise ValueError(
                    "Humidity must be between 0% and 100%."
                )

            if not 0 <= row["wind_speed_kmh"] <= 200:
                raise ValueError(
                    "Wind speed must be between 0 and 200 km/h."
                )

            input_data = pd.DataFrame(
                [row],
                columns=features,
            )

            prediction = float(
                model.predict(input_data)[0]
            )

            self.send_json(
                {
                    "predicted_demand_mw": round(
                        prediction,
                        2,
                    ),
                    "model": model_bundle["model_name"],
                    "region": model_bundle["region"],
                }
            )

        except (json.JSONDecodeError, TypeError, ValueError) as error:
            self.send_json(
                {
                    "error": "Invalid input",
                    "message": str(error),
                },
                400,
            )

        except Exception as error:
            self.send_json(
                {
                    "error": "Prediction failed",
                    "message": str(error),
                },
                500,
            )
