"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface WeeklyFlowDataPoint {
  week: string;
  done: number;
  inProgress: number;
  carryOver: number;
}

interface WeeklyFlowChartProps {
  data: WeeklyFlowDataPoint[];
  height?: number;
}

export default function WeeklyFlowChart({
  data,
  height = 500,
}: WeeklyFlowChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500">
        No data available
      </div>
    );
  }

  const maxValue = Math.max(
    ...data.map(d => (d.done || 0) + (d.inProgress || 0) + (d.carryOver || 0))
  );
  const yAxisMax = maxValue > 0 ? Math.ceil(maxValue * 1.15) : 10;

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
        >
          <defs>
            <linearGradient id="colorDone" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.9} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0.2} />
            </linearGradient>
            <linearGradient id="colorInProgress" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.9} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.2} />
            </linearGradient>
            <linearGradient id="colorCarryOver" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.9} />
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0.2} />
            </linearGradient>
          </defs>
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
          
          {/* In Progress - Light Blue (bottom layer) */}
          <Area
            type="monotone"
            dataKey="inProgress"
            stackId="1"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#colorInProgress)"
            name="In Progress"
          />
          {/* Carry-Over - Purple/Magenta (middle layer) */}
          <Area
            type="monotone"
            dataKey="carryOver"
            stackId="1"
            stroke="#a855f7"
            strokeWidth={2}
            fill="url(#colorCarryOver)"
            name="Carry-Over"
          />
          {/* Done - Green (top layer) */}
          <Area
            type="monotone"
            dataKey="done"
            stackId="1"
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#colorDone)"
            name="Done"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}


