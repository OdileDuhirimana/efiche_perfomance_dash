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

interface LeadTimeTrendDataPoint {
  week: string;
  avgLeadTime: number;
}

interface LeadTimeTrendChartProps {
  data: LeadTimeTrendDataPoint[];
  targetValue?: number;
  height?: number;
}

export default function LeadTimeTrendChart({
  data,
  targetValue = 20,
  height = 500,
}: LeadTimeTrendChartProps) {
  // Handle empty data gracefully
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500">
        No data available
      </div>
    );
  }

  // Calculate dynamic Y-axis domain based on data and target value
  const maxValue = Math.max(
    ...data.map(d => d.avgLeadTime || 0),
    targetValue || 0
  );
  const yAxisMax = maxValue > 0 ? Math.ceil(maxValue * 1.15) : 10; // Add 15% padding, minimum 10

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="week"
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            interval={0}
          />
          <YAxis
            label={{ value: "Avg Lead Time (days)", angle: -90, position: "insideLeft", style: { textAnchor: 'middle' } }}
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            width={80}
            domain={[0, yAxisMax]}
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
          
          <ReferenceLine
            y={targetValue}
            stroke="#f97316"
            strokeDasharray="5 5"
          />
          
          <Line
            type="monotone"
            dataKey="avgLeadTime"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ fill: "#3b82f6", r: 5 }}
            activeDot={{ r: 7 }}
            name="Avg Lead Time (days)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}








