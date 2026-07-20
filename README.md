# GridCast ML

GridCast is a full-stack machine-learning application that predicts hourly California electricity demand using real grid-demand and weather observations.

**Live application:** [https://electricity-demand-predictor-rntb.vercel.app](https://electricity-demand-predictor-rntb.vercel.app)

## Project overview

Electricity demand changes based on weather, time, calendar patterns, and recent grid activity. GridCast combines these signals to estimate California ISO electricity demand for a selected hour.

The project demonstrates:

- Data collection from public APIs
- Time-series feature engineering
- Machine-learning model training
- Chronological model evaluation
- Model export for web inference
- Full-stack API development
- Interactive data visualization
- GitHub and Vercel deployment

## Model performance

The production model was evaluated on the newest 20% of observations, which were excluded from training.

| Metric | Result |
|---|---:|
| Mean Absolute Error | 462.23 MW |
| Root Mean Squared Error | 631.51 MW |
| Mean Absolute Percentage Error | 1.71% |
| R² | 0.9802 |
| MAE improvement over baseline | 62.49% |

The baseline predicts that demand will equal demand from the same hour one day earlier.

The reported results apply to the chronologically held-out test period and do not guarantee the same accuracy for every future prediction.

## Features

- Real hourly California ISO demand data
- Historical weather observations
- Chronological 80/20 train/test split
- Gradient Boosting regression model
- Comparison against a historical baseline
- Interactive prediction interface
- Actual-versus-predicted chart
- 24-hour, three-day, and seven-day chart views
- Automatic real-example inputs
- Input validation
- Native Next.js prediction API
- Responsive interface
- Production deployment on Vercel

## Data sources

Electricity-demand data comes from the U.S. Energy Information Administration’s Hourly Electric Grid Monitor.

Weather observations come from the Open-Meteo Historical Weather API.

- [U.S. Energy Information Administration](https://www.eia.gov/opendata/)
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)

## Machine-learning pipeline

1. Download hourly California ISO demand from the EIA API.
2. Download historical Los Angeles weather from Open-Meteo.
3. Match electricity and weather observations by UTC timestamp.
4. Create calendar and lag-based features.
5. Train on the oldest 80% of observations.
6. Evaluate on the newest 20%.
7. Compare against a same-hour-yesterday baseline.
8. Export the trained gradient-boosting trees to JSON.
9. Run inference through a native Next.js API route.
10. Display forecasts and evaluation results in the web application.

## Predictive features

The model uses ten features:

- Temperature
- Relative humidity
- Wind speed
- Hour of day
- Day of week
- Month
- Weekend indicator
- Demand one hour earlier
- Demand 24 hours earlier
- Demand 168 hours earlier

Recent-demand features provide important information about short-term grid behavior.

## Technology

### Machine learning and data

- Python
- Pandas
- NumPy
- Scikit-learn
- Joblib

### Web application

- Next.js
- React
- TypeScript
- Recharts
- CSS

### Infrastructure

- GitHub
- Vercel
- EIA Open Data API
- Open-Meteo API

## Project structure

```text
electricity-demand-predictor/
├── app/
│   ├── api/
│   │   ├── health/
│   │   │   └── route.ts
│   │   └── predict/
│   │       └── route.ts
│   ├── PredictionChart.tsx
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── model/
│   ├── demand_model.joblib
│   ├── feature_importance.csv
│   ├── metrics.json
│   └── web_model.json
├── public/
│   ├── latest_inputs.json
│   └── predictions.json
├── scripts/
│   ├── download_data.py
│   ├── export_chart_data.py
│   ├── export_latest_inputs.py
│   ├── train_model.py
│   └── train_web_model.py
├── requirements.txt
└── package.json
```

## Local setup

### Install website dependencies

```bash
npm install
```

### Create and activate a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Configure the EIA API key

Create `.env.local` in the project root:

```text
EIA_API_KEY=your_eia_api_key
```

Never commit `.env.local`.

### Download the data

```bash
python scripts/download_data.py
```

### Train the original Python model

```bash
python scripts/train_model.py
```

### Train and export the production web model

```bash
python scripts/train_web_model.py
```

### Export graph and example data

```bash
python scripts/export_chart_data.py
python scripts/export_latest_inputs.py
```

### Start the application

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The Next.js application serves both the interface and the prediction API.

## API

### Health check

```text
GET /api/health
```

Example response:

```json
{
  "status": "healthy",
  "model": "Gradient Boosting Regressor",
  "region": "California ISO",
  "runtime": "Next.js"
}
```

### Prediction

```text
POST /api/predict
```

Example request:

```json
{
  "temperature_c": 27,
  "humidity_percent": 52,
  "wind_speed_kmh": 12,
  "hour": 17,
  "day_of_week": 0,
  "month": 7,
  "is_weekend": 0,
  "demand_1_hour_ago": 28500,
  "demand_24_hours_ago": 27600,
  "demand_168_hours_ago": 26900
}
```

## Limitations

- The weather signal currently represents Los Angeles rather than the entire CAISO region.
- The application predicts one selected hour instead of a full day-ahead demand curve.
- Prediction quality depends on accurate weather and recent-demand inputs.
- Results come from one chronological holdout period.
- The model does not currently provide prediction intervals.
- The model must be retrained as grid behavior changes.

## Future improvements

- Combine weather data from multiple California cities.
- Retrieve live CAISO demand automatically.
- Retrieve forecast weather automatically.
- Produce complete 24-hour forecasts.
- Add rolling time-series cross-validation.
- Compare additional boosting and neural-network models.
- Add prediction intervals.
- Schedule automatic model retraining.

## Disclaimer

GridCast is an educational portfolio project. Its predictions should not be used for real-world grid-operation, trading, or infrastructure decisions.