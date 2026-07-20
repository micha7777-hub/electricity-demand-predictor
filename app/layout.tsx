import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://electricity-demand-predictor-rntb.vercel.app"),
  title: "GridCast ML | Electricity Demand Forecasting",
  description:
    "Machine learning application that forecasts hourly California electricity demand using CAISO grid and weather data.",
  openGraph: {
    title: "GridCast ML | Electricity Demand Forecasting",
    description:
      "Explore a live machine learning forecast of hourly California electricity demand.",
    url: "https://electricity-demand-predictor-rntb.vercel.app",
    siteName: "GridCast ML",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "GridCast ML | Electricity Demand Forecasting",
    description:
      "Explore a live machine learning forecast of hourly California electricity demand.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
