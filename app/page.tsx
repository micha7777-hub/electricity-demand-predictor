"use client";

import { FormEvent, useEffect, useState } from "react";
import metrics from "../model/metrics.json";
import PredictionChart from "./PredictionChart";

type Prediction = {
  predicted_demand_mw: number;
  model: string;
  region: string;
};

type FormData = {
  temperature_c: number;
  humidity_percent: number;
  wind_speed_kmh: number;
  hour: number;
  day_of_week: number;
  month: number;
  is_weekend: number;
  demand_1_hour_ago: number;
  demand_24_hours_ago: number;
  demand_168_hours_ago: number;
};

const initialForm: FormData = {
  temperature_c: 27,
  humidity_percent: 52,
  wind_speed_kmh: 12,
  hour: 17,
  day_of_week: 0,
  month: 7,
  is_weekend: 0,
  demand_1_hour_ago: 28500,
  demand_24_hours_ago: 27600,
  demand_168_hours_ago: 26900,
};

const days = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export default function Home() {
  const [form, setForm] = useState<FormData>(initialForm);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadedTimestamp, setLoadedTimestamp] = useState("");

  useEffect(() => {
    async function loadLatestInputs() {
      try {
        const response = await fetch("/latest_inputs.json");

        if (!response.ok) {
          return;
        }

        const latest = await response.json();

        setForm({
          temperature_c: latest.temperature_c,
          humidity_percent: latest.humidity_percent,
          wind_speed_kmh: latest.wind_speed_kmh,
          hour: latest.hour,
          day_of_week: latest.day_of_week,
          month: latest.month,
          is_weekend: latest.is_weekend,
          demand_1_hour_ago: latest.demand_1_hour_ago,
          demand_24_hours_ago: latest.demand_24_hours_ago,
          demand_168_hours_ago: latest.demand_168_hours_ago,
        });

        setLoadedTimestamp(latest.timestamp);
      } catch {
        // Keep the default values if the real example cannot be loaded.
      }
    }

    loadLatestInputs();
  }, []);

  function updateField(field: keyof FormData, value: number) {
    setForm((current) => {
      const updated = {
        ...current,
        [field]: value,
      };

      if (field === "day_of_week") {
        updated.is_weekend = value >= 5 ? 1 : 0;
      }

      return updated;
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (form.temperature_c < -20 || form.temperature_c > 60) {
      setError("Temperature must be between -20°C and 60°C.");
      return;
    }

    if (
      form.humidity_percent < 0 ||
      form.humidity_percent > 100
    ) {
      setError("Humidity must be between 0% and 100%.");
      return;
    }

    if (
      form.wind_speed_kmh < 0 ||
      form.wind_speed_kmh > 200
    ) {
      setError("Wind speed must be between 0 and 200 km/h.");
      return;
    }

    const demandValues = [
      form.demand_1_hour_ago,
      form.demand_24_hours_ago,
      form.demand_168_hours_ago,
    ];

    if (
      demandValues.some(
        (value) => value < 5000 || value > 70000
      )
    ) {
      setError(
        "Recent demand values must be between 5,000 and 70,000 MW."
      );
      return;
    }

    setLoading(true);

    const isLocal =
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1";

    const apiUrl = isLocal
      ? "http://127.0.0.1:8001/api/predict"
      : "/api/predict";

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.message || result.error || "Prediction failed"
        );
      }

      setPrediction(result);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to reach the prediction service"
      );
    } finally {
      setLoading(false);
    }
  }

  const demandLevel =
    prediction === null
      ? "Waiting"
      : prediction.predicted_demand_mw >= 35000
        ? "High demand"
        : prediction.predicted_demand_mw >= 25000
          ? "Moderate demand"
          : "Low demand";

  return (
    <main>
      <header className="hero">
        <nav>
          <div className="brand">
            <span className="brand-mark">G</span>
            GridCast
          </div>

          <span className="live-status">
            <span />
            Model online
          </span>
        </nav>

        <div className="hero-copy">
          <p className="eyebrow">CALIFORNIA ENERGY FORECASTING</p>

          <h1>
            Predict the next hour&apos;s
            <em> power demand.</em>
          </h1>

          <p className="intro">
            A machine-learning system trained on real California ISO demand
            and historical weather observations.
          </p>
        </div>
      </header>

      <section className="workspace">
        <form className="panel controls" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <div>
              <p className="section-number">01 — CONDITIONS</p>
              <h2>Forecast inputs</h2>
            </div>

            <span className="data-source">Real EIA data</span>
          </div>

          <div className="input-grid">
            <label>
              <span>Temperature</span>

              <div className="input-with-unit">
                <input
                  type="number"
                  min="-20"
                  max="60"
                  step="0.1"
                  value={form.temperature_c}
                  onChange={(event) =>
                    updateField(
                      "temperature_c",
                      Number(event.target.value)
                    )
                  }
                />
                <small>°C</small>
              </div>
            </label>

            <label>
              <span>Humidity</span>

              <div className="input-with-unit">
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={form.humidity_percent}
                  onChange={(event) =>
                    updateField(
                      "humidity_percent",
                      Number(event.target.value)
                    )
                  }
                />
                <small>%</small>
              </div>
            </label>

            <label>
              <span>Wind speed</span>

              <div className="input-with-unit">
                <input
                  type="number"
                  min="0"
                  max="200"
                  step="0.1"
                  value={form.wind_speed_kmh}
                  onChange={(event) =>
                    updateField(
                      "wind_speed_kmh",
                      Number(event.target.value)
                    )
                  }
                />
                <small>km/h</small>
              </div>
            </label>

            <label>
              <span>Hour</span>

              <select
                value={form.hour}
                onChange={(event) =>
                  updateField("hour", Number(event.target.value))
                }
              >
                {Array.from({ length: 24 }, (_, hour) => (
                  <option key={hour} value={hour}>
                    {String(hour).padStart(2, "0")}:00
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Day</span>

              <select
                value={form.day_of_week}
                onChange={(event) =>
                  updateField(
                    "day_of_week",
                    Number(event.target.value)
                  )
                }
              >
                {days.map((day, index) => (
                  <option key={day} value={index}>
                    {day}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Month</span>

              <select
                value={form.month}
                onChange={(event) =>
                  updateField("month", Number(event.target.value))
                }
              >
                {months.map((month, index) => (
                  <option key={month} value={index + 1}>
                    {month}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="historical-inputs">
            <p>Recent grid demand</p>

            <p className="field-explanation">
              Previous grid demand is the model&apos;s strongest signal.
              These values are loaded from the latest observation in the
              project dataset, but you can change them.
            </p>

            <div className="input-grid">
              <label>
                <span>One hour ago</span>

                <div className="input-with-unit">
                  <input
                    type="number"
                    min="5000"
                    max="70000"
                    value={form.demand_1_hour_ago}
                    onChange={(event) =>
                      updateField(
                        "demand_1_hour_ago",
                        Number(event.target.value)
                      )
                    }
                  />
                  <small>MW</small>
                </div>
              </label>

              <label>
                <span>Same hour yesterday</span>

                <div className="input-with-unit">
                  <input
                    type="number"
                    min="5000"
                    max="70000"
                    value={form.demand_24_hours_ago}
                    onChange={(event) =>
                      updateField(
                        "demand_24_hours_ago",
                        Number(event.target.value)
                      )
                    }
                  />
                  <small>MW</small>
                </div>
              </label>

              <label>
                <span>Same hour last week</span>

                <div className="input-with-unit">
                  <input
                    type="number"
                    min="5000"
                    max="70000"
                    value={form.demand_168_hours_ago}
                    onChange={(event) =>
                      updateField(
                        "demand_168_hours_ago",
                        Number(event.target.value)
                      )
                    }
                  />
                  <small>MW</small>
                </div>
              </label>
            </div>
          </div>

          {loadedTimestamp && (
            <p className="observation-note">
              Real example loaded from{" "}
              {new Date(loadedTimestamp).toLocaleString()}.
            </p>
          )}

          <button type="submit" disabled={loading}>
            {loading
              ? "Running model..."
              : "Generate demand forecast"}
          </button>

          {error && <p className="error">{error}</p>}
        </form>

        <div className="results-column">
          <section className="prediction-panel">
            <div className="prediction-top">
              <p className="section-number">02 — PREDICTION</p>
              <span>{demandLevel}</span>
            </div>

            {prediction ? (
              <>
                <div className="prediction-number">
                  {Math.round(
                    prediction.predicted_demand_mw
                  ).toLocaleString()}
                  <small>MW</small>
                </div>

                <p className="prediction-note">
                  Estimated California ISO electricity demand at{" "}
                  {String(form.hour).padStart(2, "0")}:00.
                </p>

                <div className="meter">
                  <div
                    style={{
                      width: `${Math.min(
                        (prediction.predicted_demand_mw / 50000) * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>
              </>
            ) : (
              <div className="empty-prediction">
                <strong>Ready to forecast</strong>

                <p>
                  Review the automatically loaded conditions and run the
                  trained model.
                </p>
              </div>
            )}
          </section>

          <section className="metrics-grid">
            <article className="metric">
              <p>Test MAE</p>
              <strong>{metrics.model.mae_mw.toLocaleString()}</strong>
              <span>megawatts</span>
            </article>

            <article className="metric">
              <p>Model R²</p>
              <strong>{metrics.model.r2}</strong>
              <span>unseen data</span>
            </article>

            <article className="metric">
              <p>Test MAPE</p>
              <strong>{metrics.model.mape_percent}%</strong>
              <span>average error</span>
            </article>

            <article className="metric accent-metric">
              <p>Baseline improvement</p>
              <strong>
                {metrics.mae_improvement_over_baseline_percent}%
              </strong>
              <span>lower MAE</span>
            </article>
          </section>
        </div>
      </section>

      <PredictionChart />

      <section className="methodology">
        <div>
          <p className="section-number">04 — METHODOLOGY</p>

          <h2>Built like a real forecasting project.</h2>
        </div>

        <div className="method-list">
          <article>
            <span>17K+</span>

            <div>
              <h3>Real observations</h3>

              <p>
                Two years of hourly California ISO demand matched with
                historical Los Angeles weather.
              </p>
            </div>
          </article>

          <article>
            <span>80/20</span>

            <div>
              <h3>Time-based evaluation</h3>

              <p>
                The newest 20% of observations were held out to test the
                model on unseen future dates.
              </p>
            </div>
          </article>

          <article>
            <span>10</span>

            <div>
              <h3>Predictive features</h3>

              <p>
                Weather, calendar signals and demand from one hour, one
                day and one week earlier.
              </p>
            </div>
          </article>
        </div>
      </section>

      <footer>
        <span>GridCast ML</span>

        <p>
          Data: U.S. Energy Information Administration and Open-Meteo
        </p>
      </footer>
    </main>
  );
}