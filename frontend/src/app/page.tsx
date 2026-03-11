"use client";

import { UploadForm } from "@/components/UploadForm";
import { SummaryResult } from "@/components/SummaryResult";
import { useState } from "react";
import { BarChart3, Zap, Mail } from "lucide-react";
import type { ChartData } from "@/components/SalesCharts";

type AppState =
  | { phase: "idle" }
  | { phase: "loading" }
  | { phase: "success"; summary: string; message: string; chartData?: ChartData }
  | { phase: "error"; error: string };

export default function Home() {
  const [state, setState] = useState<AppState>({ phase: "idle" });

  const handleUpload = async (file: File, email: string) => {
    setState({ phase: "loading" });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("recipient_email", email);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(err.detail || `Server error (${response.status})`);
      }

      const data = await response.json();
      setState({
        phase: "success",
        summary: data.summary,
        message: data.message,
        chartData: data.chart_data,
      });
    } catch (err) {
      setState({
        phase: "error",
        error: err instanceof Error ? err.message : "An unexpected error occurred.",
      });
    }
  };

  const handleReset = () => setState({ phase: "idle" });

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto max-w-5xl px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 leading-tight">
                SalesInsight AI
              </h1>
              <p className="text-xs text-slate-500">by Rabbitt AI</p>
            </div>
          </div>
          <span className="text-xs font-medium text-slate-400 hidden sm:block">
            Executive Summary Generator
          </span>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-5xl px-4 pt-12 pb-6 text-center">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-3">
          Turn Sales Data into{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
            Actionable Insights
          </span>
        </h2>
        <p className="text-slate-600 max-w-2xl mx-auto text-base sm:text-lg">
          Upload your CSV or Excel sales data and receive a professional
          AI-generated executive summary delivered straight to your inbox.
        </p>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-3 mt-6">
          {[
            { icon: <Zap className="h-4 w-4" />, text: "AI-Powered Analysis" },
            { icon: <BarChart3 className="h-4 w-4" />, text: "Revenue Insights" },
            { icon: <Mail className="h-4 w-4" />, text: "Email Delivery" },
          ].map(({ icon, text }) => (
            <span
              key={text}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white shadow-sm border border-slate-200 text-sm text-slate-700"
            >
              {icon}
              {text}
            </span>
          ))}
        </div>
      </section>

      {/* Main content */}
      <section className="mx-auto max-w-3xl px-4 pb-16">
        {state.phase === "success" ? (
          <SummaryResult
            summary={state.summary}
            message={state.message}
            chartData={state.chartData}
            onReset={handleReset}
          />
        ) : (
          <UploadForm
            onSubmit={handleUpload}
            isLoading={state.phase === "loading"}
            error={state.phase === "error" ? state.error : undefined}
          />
        )}
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white/60">
        <div className="mx-auto max-w-5xl px-4 py-4 text-center text-xs text-slate-400">
          © {new Date().getFullYear()} SalesInsight AI · Built for Rabbitt AI
        </div>
      </footer>
    </main>
  );
}
