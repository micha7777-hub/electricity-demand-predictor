export async function GET() {
  return Response.json({
    status: "healthy",
    model: "Gradient Boosting Regressor",
    region: "California ISO",
    runtime: "Next.js",
  });
}