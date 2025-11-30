"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface ReworkRatioDataPoint {
  week: string;
  cleanDelivery: number;
  rework: number;
}

interface ReworkRatioChartProps {
  data: ReworkRatioDataPoint[];
  height?: number;
}

export default function ReworkRatioChart({
  data,
  height = 350,
}: ReworkRatioChartProps) {
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
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
          stackOffset="expand"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="week"
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
          />
          <YAxis
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              padding: "8px 12px",
            }}
            labelStyle={{ fontWeight: 600, marginBottom: 4 }}
            formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
          />
          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            iconType="circle"
          />
          
          <Bar
            dataKey="cleanDelivery"
            stackId="1"
            fill="#3b82f6"
            name="Clean Delivery %"
          />
          <Bar
            dataKey="rework"
            stackId="1"
            fill="#f97316"
            name="Rework %"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}









