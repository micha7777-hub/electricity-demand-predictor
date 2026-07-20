"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type ChartPoint = {
  time: string;
  actual: number;
  prediction: number;
  baseline: number;
};

export default function PredictionChart() {
  const [data, setData] = useState<ChartPoint[]>([]);
  const [range, setRange] = useState(24);

  useEffect(() => {
    fetch("/predictions.json")
      .then((response) => response.json())
      .then((result) => setData(result))
      .catch(() => setData([]));
  }, []);

  const visibleData = data.slice(-range);

  return (
    <section className="chart-section">
      <div className="chart-heading">
        <div>
          <p className="section-number">03 — MODEL PERFORMANCE</p>
          <h2>Predicted vs. actual demand</h2>
          <p>
            Performance on dates the model did not see during training.
          </p>
        </div>

        <div className="range-buttons">
          <button
            type="button"
            className={range === 24 ? "active" : ""}
            onClick={() => setRange(24)}
          >
            24 hours
          </button>

          <button
            type="button"
            className={range === 72 ? "active" : ""}
            onClick={() => setRange(72)}
          >
            3 days
          </button>

          <button
            type="button"
            className={range === 168 ? "active" : ""}
            onClick={() => setRange(168)}
          >
            7 days
          </button>
        </div>
      </div>

      <div className="chart-card">
        {visibleData.length > 0 ? (
          <ResponsiveContainer width="100%" height={420}>
            <LineChart
              data={visibleData}
              margin={{
                top: 10,
                right: 20,
                left: 10,
                bottom: 10,
              }}
            >
              <CartesianGrid
                stroke="#d8d9cf"
                strokeDasharray="4 4"
                vertical={false}
              />

              <XAxis
                dataKey="time"
                tick={{ fill: "#68756e", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                minTickGap={35}
              />

              <YAxis
                tick={{ fill: "#68756e", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                width={70}
                tickFormatter={(value) =>
                  `${Math.round(value / 1000)}k`
                }
              />

              <Tooltip
                formatter={(value) => [
                  `${Number(value).toLocaleString()} MW`,
                ]}
                contentStyle={{
                  border: "1px solid #d8d9cf",
                  borderRadius: "12px",
                  background: "#fbfaf5",
                }}
              />

              <Legend />

              <Line
                type="monotone"
                dataKey="actual"
                name="Actual demand"
                stroke="#14231c"
                strokeWidth={3}
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="prediction"
                name="ML prediction"
                stroke="#72a82f"
                strokeWidth={3}
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="baseline"
                name="Yesterday baseline"
                stroke="#aaa99f"
                strokeWidth={2}
                strokeDasharray="6 6"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p>Loading prediction results...</p>
        )}
      </div>
    </section>
  );
}