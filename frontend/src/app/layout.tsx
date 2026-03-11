import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SalesInsight AI — Executive Summary Generator",
  description:
    "Upload your sales data and receive an AI-generated executive summary delivered straight to your inbox.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
