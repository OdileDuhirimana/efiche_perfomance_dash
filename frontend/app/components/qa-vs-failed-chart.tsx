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
} from "recharts";

interface QAVsFailedDataPoint {
  sprint: string;
  qaExecuted: number;
  failedQA: number;
}

interface QAVsFailedChartProps {
  data: QAVsFailedDataPoint[];
  height?: number;
}

export default function QAVsFailedChart({
  data,
  height = 350,
}: QAVsFailedChartProps) {
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
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="sprint"
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
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
          
          <Bar
            dataKey="qaExecuted"
            fill="#10b981"
            radius={[4, 4, 0, 0]}
            name="QA Executed"
          />
          <Bar
            dataKey="failedQA"
            fill="#ef4444"
            radius={[4, 4, 0, 0]}
            name="Failed QA"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}










