"use client";

import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface PlannedVsDoneDataPoint {
  week: string;
  planned: number;
  done: number;
}

interface PlannedVsDoneChartProps {
  data: PlannedVsDoneDataPoint[];
  height?: number;
}

export default function PlannedVsDoneChart({
  data,
  height = 500,
}: PlannedVsDoneChartProps) {
  // Handle empty data gracefully
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500">
        No data available
      </div>
    );
  }

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="week"
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            interval={0}
          />
          <YAxis
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              padding: "8px 12px",
            }}
            labelStyle={{ fontWeight: 600, marginBottom: 4 }}
          />
          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            iconType="circle"
          />
          
          {/* Bars for Planned */}
          <Bar
            dataKey="planned"
            fill="#9ca3af"
            radius={[4, 4, 0, 0]}
            name="Planned"
          />
          
          {/* Line for Done */}
          <Line
            type="monotone"
            dataKey="done"
            stroke="#10b981"
            strokeWidth={3}
            dot={{ fill: "#10b981", r: 5 }}
            activeDot={{ r: 7 }}
            name="Done"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
