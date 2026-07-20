import webModel from "../../../model/web_model.json";

export const runtime = "nodejs";

type Tree = {
  children_left: number[];
  children_right: number[];
  feature: number[];
  threshold: number[];
  value: number[];
};

type InputData = {
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

const requiredFields: (keyof InputData)[] = [
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
];

function predictTree(tree: Tree, values: number[]) {
  let node = 0;

  while (tree.feature[node] >= 0) {
    const featureIndex = tree.feature[node];
    const threshold = tree.threshold[node];

    node =
      values[featureIndex] <= threshold
        ? tree.children_left[node]
        : tree.children_right[node];
  }

  return tree.value[node];
}

function predictDemand(input: InputData) {
  const values = webModel.features.map(
    (feature) => input[feature as keyof InputData]
  );

  let prediction = webModel.initial_prediction;

  for (const tree of webModel.trees) {
    prediction +=
      webModel.learning_rate *
      predictTree(tree as Tree, values);
  }

  return prediction;
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as Partial<InputData>;

    const missing = requiredFields.filter(
      (field) =>
        body[field] === undefined ||
        body[field] === null ||
        !Number.isFinite(Number(body[field]))
    );

    if (missing.length > 0) {
      return Response.json(
        {
          error: "Missing or invalid fields",
          missing,
        },
        { status: 400 }
      );
    }

    const input = Object.fromEntries(
      requiredFields.map((field) => [
        field,
        Number(body[field]),
      ])
    ) as unknown as InputData;

    if (
      input.temperature_c < -20 ||
      input.temperature_c > 60
    ) {
      return Response.json(
        {
          error:
            "Temperature must be between -20°C and 60°C.",
        },
        { status: 400 }
      );
    }

    if (
      input.humidity_percent < 0 ||
      input.humidity_percent > 100
    ) {
      return Response.json(
        {
          error: "Humidity must be between 0% and 100%.",
        },
        { status: 400 }
      );
    }

    if (
      input.wind_speed_kmh < 0 ||
      input.wind_speed_kmh > 200
    ) {
      return Response.json(
        {
          error:
            "Wind speed must be between 0 and 200 km/h.",
        },
        { status: 400 }
      );
    }

    const prediction = predictDemand(input);

    return Response.json({
      predicted_demand_mw: Math.round(prediction * 100) / 100,
      model: webModel.model_name,
      region: webModel.region,
    });
  } catch (error) {
    return Response.json(
      {
        error: "Prediction failed",
        message:
          error instanceof Error
            ? error.message
            : "Unknown error",
      },
      { status: 500 }
    );
  }
}