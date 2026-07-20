# GridCast ML

GridCast is a machine-learning application that predicts hourly California electricity demand using real grid-demand and weather observations.

The project combines data engineering, time-series feature engineering, machine learning, API development, model evaluation, and a responsive web interface.

## Model performance

The model was evaluated on the newest 20% of observations, which were excluded from training.

| Metric | Result |
|---|---:|
| Mean Absolute Error | 409.8 MW |
| Mean Absolute Percentage Error | 1.54% |
| R² | 0.9844 |
| MAE improvement over baseline | 66.74% |

The baseline assumes electricity demand will equal demand from the same hour one day earlier.

## Features

- Real hourly California ISO electricity-demand data
- Historical temperature, humidity, and wind data
- Chronological train/test split
- Histogram Gradient Boosting regression model
- Comparison against a historical baseline
- Interactive demand-prediction interface
- Actual-versus-predicted performance graph
- 24-hour, three-day, and seven-day chart views
- Client-side and API input validation
- Python prediction API
- Responsive Next.js interface

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
7. Compare the model against a same-hour-yesterday baseline.
8. Save the trained model and evaluation results.
9. Serve predictions through a Python API.
10. Display predictions and test results in a Next.js application.

## Predictive features

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

## Technology

- Next.js
- React
- TypeScript
- Python
- Flask
- Pandas
- Scikit-learn
- Recharts
- EIA Open Data API
- Open-Meteo API
- Vercel

## Local setup

### Install website dependencies

```bash
npm install
```

### Create a Python environment

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

Never commit this file.

### Download and prepare the data

```bash
python scripts/download_data.py
```

### Train the model

```bash
python scripts/train_model.py
```

### Export website data

```bash
python scripts/export_chart_data.py
python scripts/export_latest_inputs.py
```

### Start the prediction API

```bash
python api/predict.py
```

The local API runs at `http://127.0.0.1:8001`.

### Start the website

In a second terminal:

```bash
npm run dev
```

Open `http://localhost:3000`.

## Limitations

- The current weather signal represents Los Angeles rather than every part of the CAISO region.
- The application predicts one selected hour instead of generating a complete day-ahead forecast.
- Prediction quality depends on the accuracy of recent-demand and weather inputs.
- Reported performance comes from one chronological holdout period.
- The model should be retrained as additional grid data becomes available.

## Future improvements

- Combine weather observations from several California cities.
- Automatically retrieve current CAISO demand.
- Generate complete 24-hour forecasts.
- Add rolling time-series cross-validation.
- Compare gradient boosting with XGBoost and neural-network models.
- Schedule periodic model retraining.
- Add prediction intervals to communicate uncertainty.

## Disclaimer

This project is an educational forecasting application and should not be used for real-world grid-operation decisions.
