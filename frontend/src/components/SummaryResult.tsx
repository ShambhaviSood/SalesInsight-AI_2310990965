"use client";

import ReactMarkdown from "react-markdown";
import { CheckCircle2, RotateCcw, Mail, AlertTriangle } from "lucide-react";
import { SalesCharts, type ChartData } from "./SalesCharts";

interface SummaryResultProps {
  summary: string;
  message: string;
  chartData?: ChartData;
  onReset: () => void;
}

export function SummaryResult({ summary, message, chartData, onReset }: SummaryResultProps) {
  const emailFailed = message.toLowerCase().includes("failed");

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden">
      {/* Status header */}
      <div className={`border-b px-6 py-4 flex items-center gap-3 ${
        emailFailed
          ? "bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200"
          : "bg-gradient-to-r from-green-50 to-emerald-50 border-green-200"
      }`}>
        {emailFailed ? (
          <AlertTriangle className="h-6 w-6 text-amber-600 shrink-0" />
        ) : (
          <CheckCircle2 className="h-6 w-6 text-green-600 shrink-0" />
        )}
        <div>
          <p className={`font-semibold ${emailFailed ? "text-amber-800" : "text-green-800"}`}>
            Summary Generated Successfully
          </p>
          <p className={`text-sm flex items-center gap-1 ${emailFailed ? "text-amber-700" : "text-green-700"}`}>
            <Mail className="h-3.5 w-3.5" />
            {message}
          </p>
        </div>
      </div>

      {/* Charts */}
      {chartData && (
        <div className="px-6 py-5 border-b border-slate-200">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
            Data Visualizations
          </h3>
          <SalesCharts data={chartData} />
        </div>
      )}

      {/* Summary content */}
      <div className="px-6 py-5">
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
          Executive Summary
        </h3>
        <div className="prose prose-sm prose-slate max-w-none
          prose-headings:text-slate-800 prose-h2:text-lg prose-h3:text-base
          prose-p:text-slate-600 prose-li:text-slate-600
          prose-strong:text-slate-800">
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      </div>

      {/* Actions */}
      <div className="border-t border-slate-200 px-6 py-4 flex justify-end">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-300
            bg-white px-4 py-2 text-sm font-medium text-slate-700
            hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500
            transition-colors"
        >
          <RotateCcw className="h-4 w-4" />
          Analyze Another File
        </button>
      </div>
    </div>
  );
}
