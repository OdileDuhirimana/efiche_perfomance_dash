"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface TaskLoadDataPoint {
  assignee: string;
  tasks: number;
}

interface TaskLoadChartProps {
  data: TaskLoadDataPoint[];
  height?: number;
}

export default function TaskLoadChart({
  data,
  height = 500,
}: TaskLoadChartProps) {
  // Handle empty data gracefully
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500">
        No data available
      </div>
    );
  }

  // Sort data by tasks descending
  const sortedData = [...data].sort((a, b) => b.tasks - a.tasks);

  // Calculate dynamic X-axis domain (since it's horizontal bar chart)
  const maxValue = Math.max(...data.map(d => d.tasks || 0));
  const xAxisMax = maxValue > 0 ? Math.ceil(maxValue * 1.15) : 10; // Add 15% padding, minimum 10

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            type="number"
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            domain={[0, xAxisMax]}
          />
          <YAxis
            type="category"
            dataKey="assignee"
            tick={{ fill: "#6b7280", fontSize: 12 }}
            axisLine={{ stroke: "#e5e7eb" }}
            width={90}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              padding: "8px 12px",
            }}
            labelStyle={{ fontWeight: 600, marginBottom: 4 }}
            formatter={(value: number) => [`Tasks: ${value}`, ""]}
          />
          
          <Bar dataKey="tasks" radius={[0, 4, 4, 0]}>
            {sortedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill="#14b8a6" />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}








