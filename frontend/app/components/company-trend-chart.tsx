"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface CompanyTrendDataPoint {
  month: string;
  avgLeadTime: number;
  completionRate: number;
}

interface CompanyTrendChartProps {
  data: CompanyTrendDataPoint[];
  height?: number;
}

export default function CompanyTrendChart({
  data,
  height = 500,
}: CompanyTrendChartProps) {
  // Handle empty data gracefully
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500">
        No data available
      </div>
    );
  }

  // Calculate dynamic Y-axis domain for lead time (right axis)
  const maxLeadTime = Math.max(...data.map(d => d.avgLeadTime || 0));
  const leadTimeMax = maxLeadTime > 0 ? Math.ceil(maxLeadTime * 1.15) : 10; // Add 15% padding, minimum 10

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{ top: 20, right: 50, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="month"
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            interval={0}
          />
          <YAxis
            yAxisId="left"
            label={{ value: "Completion Rate (%)", angle: -90, position: "insideLeft", style: { textAnchor: 'middle' } }}
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            domain={[0, 100]}
            tickFormatter={(value) => `${value}%`}
            width={80}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{ value: "Avg Lead Time (days)", angle: 90, position: "insideRight", style: { textAnchor: 'middle' } }}
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            width={80}
            domain={[0, leadTimeMax]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              padding: "8px 12px",
            }}
            labelStyle={{ fontWeight: 600, marginBottom: 4 }}
            formatter={(value: number, name: string) => {
              if (name === "Completion Rate (%)") {
                return [`${value}%`, name];
              }
              return [value, name];
            }}
          />
          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            iconType="circle"
          />
          
          <ReferenceLine
            yAxisId="left"
            y={75}
            stroke="#10b981"
            strokeDasharray="5 5"
          />
          <ReferenceLine
            yAxisId="left"
            y={65}
            stroke="#f97316"
            strokeDasharray="5 5"
          />
          
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="avgLeadTime"
            stroke="#9333ea"
            strokeWidth={3}
            dot={{ fill: "#9333ea", r: 5 }}
            activeDot={{ r: 7 }}
            name="Avg Lead Time (days)"
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="completionRate"
            stroke="#10b981"
            strokeWidth={3}
            dot={{ fill: "#10b981", r: 5 }}
            activeDot={{ r: 7 }}
            name="Completion Rate (%)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}








