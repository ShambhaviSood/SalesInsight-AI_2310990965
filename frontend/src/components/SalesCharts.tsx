"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

export interface ChartData {
  primary_total: number;
  primary_numeric_col: string;
  breakdowns: Record<string, Record<string, number>>;
  numeric_summary: Record<string, Record<string, number>>;
  // Legacy
  total_revenue: number;
  revenue_by_region: Record<string, number>;
  revenue_by_product: Record<string, number>;
}

const COLORS = [
  "#3b82f6", "#6366f1", "#8b5cf6", "#ec4899",
  "#f59e0b", "#10b981", "#06b6d4", "#f43f5e",
  "#84cc16", "#a855f7", "#14b8a6", "#f97316",
];

function formatNumber(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function humanize(col: string): string {
  return col
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function SalesCharts({ data }: { data: ChartData }) {
  const breakdowns = data.breakdowns ?? {};
  const numericSummary = data.numeric_summary ?? {};

  const breakdownEntries = Object.entries(breakdowns).filter(
    ([, v]) => v && Object.keys(v).length > 0
  );
  const hasBreakdowns = breakdownEntries.length > 0;
  const hasNumeric = Object.keys(numericSummary).length > 0;
  const primaryLabel = data.primary_numeric_col
    ? humanize(data.primary_numeric_col)
    : "Total";

  if (!hasBreakdowns && !hasNumeric && data.primary_total === 0) {
    return null;
  }

  // KPI cards: primary total + top value from first two breakdowns
  const kpis: { label: string; value: string }[] = [];
  if (data.primary_total > 0) {
    kpis.push({ label: `Total ${primaryLabel}`, value: formatNumber(data.primary_total) });
  }
  for (const [catCol, grouped] of breakdownEntries.slice(0, 2)) {
    const entries = Object.entries(grouped).sort((a, b) => b[1] - a[1]);
    if (entries.length > 0) {
      kpis.push({ label: `Top ${humanize(catCol)}`, value: entries[0][0] });
    }
  }

  // Decide which breakdowns to render as bar vs pie
  // First breakdown → bar chart, second → pie chart, rest → additional bar charts
  const barBreakdowns = breakdownEntries.filter((_, i) => i !== 1);
  const pieBreakdown = breakdownEntries.length > 1 ? breakdownEntries[1] : null;

  return (
    <div className="space-y-6">
      {/* KPI cards */}
      {kpis.length > 0 && (
        <div className={`grid gap-3 ${kpis.length >= 3 ? "grid-cols-2 sm:grid-cols-3" : kpis.length === 2 ? "grid-cols-2" : "grid-cols-1"}`}>
          {kpis.map((kpi) => (
            <KpiCard key={kpi.label} label={kpi.label} value={kpi.value} />
          ))}
        </div>
      )}

      {/* Charts */}
      {hasBreakdowns && (
        <div className={`grid gap-4 ${barBreakdowns.length > 0 && pieBreakdown ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1"}`}>
          {/* Bar charts */}
          {barBreakdowns.map(([catCol, grouped]) => {
            const chartData = Object.entries(grouped)
              .map(([name, value]) => ({ name, value }))
              .sort((a, b) => b.value - a.value);

            return (
              <div key={catCol} className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-700 mb-3">
                  {primaryLabel} by {humanize(catCol)}
                </h4>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} />
                    <YAxis tick={{ fontSize: 12, fill: "#64748b" }} tickFormatter={formatNumber} />
                    <Tooltip
                      formatter={(value) => [formatNumber(Number(value ?? 0)), primaryLabel]}
                      contentStyle={{ borderRadius: 8, borderColor: "#e2e8f0", fontSize: 13 }}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            );
          })}

          {/* Pie chart for second breakdown */}
          {pieBreakdown && (() => {
            const [catCol, grouped] = pieBreakdown;
            const pieData = Object.entries(grouped)
              .map(([name, value]) => ({ name, value }))
              .sort((a, b) => b.value - a.value);

            return (
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-700 mb-3">
                  {primaryLabel} by {humanize(catCol)}
                </h4>
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      innerRadius={50}
                      paddingAngle={3}
                      label={(props: any) => `${props.name ?? ""} ${((props.percent ?? 0) * 100).toFixed(0)}%`}
                      labelLine={{ strokeWidth: 1 }}
                    >
                      {pieData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value) => [formatNumber(Number(value ?? 0)), primaryLabel]}
                      contentStyle={{ borderRadius: 8, borderColor: "#e2e8f0", fontSize: 13 }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      iconType="circle"
                      wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            );
          })()}
        </div>
      )}

      {/* Numeric stats table */}
      {hasNumeric && (
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 overflow-x-auto">
          <h4 className="text-sm font-semibold text-slate-700 mb-3">Key Metrics Summary</h4>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-slate-200">
                <th className="pb-2 pr-4 font-medium">Metric</th>
                <th className="pb-2 pr-4 font-medium text-right">Sum</th>
                <th className="pb-2 pr-4 font-medium text-right">Average</th>
                <th className="pb-2 pr-4 font-medium text-right">Min</th>
                <th className="pb-2 font-medium text-right">Max</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(numericSummary).map(([metric, vals]) => (
                <tr key={metric} className="border-b border-slate-100 last:border-0">
                  <td className="py-2 pr-4 font-medium text-slate-700">{humanize(metric)}</td>
                  <td className="py-2 pr-4 text-right text-slate-600">{vals.sum?.toLocaleString()}</td>
                  <td className="py-2 pr-4 text-right text-slate-600">{vals.mean?.toLocaleString()}</td>
                  <td className="py-2 pr-4 text-right text-slate-600">{vals.min?.toLocaleString()}</td>
                  <td className="py-2 text-right text-slate-600">{vals.max?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function KpiCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 px-4 py-3 shadow-sm">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</p>
      <p className="text-xl font-bold text-slate-800 mt-0.5">{value}</p>
    </div>
  );
}
