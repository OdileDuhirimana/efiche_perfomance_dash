"use client";

import { useState, useEffect } from "react";
import {
  getWeeklyPlannedVsDone,
  getWeeklyFlow,
  getWeeklyLeadTime,
  getTaskLoad,
  getExecutionSuccess,
  getCompanyTrend,
  getDataAccuracy,
  getQAVsFailed,
  getReworkRatio,
  getExecutiveSummary,
} from "@/lib/api-client";
import { useFilters } from "@/app/contexts/FilterContext";

interface ThroughputData {
  plannedVsDone: Array<{ week: string; planned: number; done: number }>;
  weeklyFlow: Array<{ week: string; done: number; inProgress: number; carryOver: number }>;
}

interface OwnershipData {
  taskLoad: Array<{ assignee: string; tasks: number }>;
  executionSuccess: Array<{ assignee: string; successRate: number }>;
  performanceData: Array<{ name: string; successRate: number; trend: number }>;
}

interface CompanyTrendData {
  month: string;
  avgLeadTime: number;
  completionRate: number;
}

export function useThroughputData(weeks: number = 12) {
  const { filters } = useFilters();
  const [data, setData] = useState<ThroughputData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [plannedVsDoneRes, weeklyFlowRes] = await Promise.all([
          getWeeklyPlannedVsDone(
            weeks,
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
            filters.issueType || undefined
          ),
          getWeeklyFlow(
            weeks,
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
            filters.issueType || undefined
          ),
        ]);

        if (!plannedVsDoneRes.success) {
          throw new Error(plannedVsDoneRes.error || "Failed to fetch planned vs done data");
        }
        if (!weeklyFlowRes.success) {
          throw new Error(weeklyFlowRes.error || "Failed to fetch weekly flow data");
        }

        const formatWeekLabel = (label: string): string => {
          if (!label) return '';
          const match = label.match(/W(\d+)/);
          if (match) {
            return `W${match[1]}`;
          }
          return label;
        };

        const plannedVsDone = (plannedVsDoneRes.data || []).map((item: any) => {
          if (!item) return { week: '', planned: 0, done: 0 };
          return {
          week: formatWeekLabel(item['Week Label'] || item['Week'] || ''),
            planned: Number(item['Planned'] ?? 0) || 0,
            done: Number(item['Done'] ?? 0) || 0,
          };
        }).filter(item => item.week);

        const weeklyFlow = (weeklyFlowRes.data || []).map((item: any) => {
          if (!item) return { week: '', done: 0, inProgress: 0, carryOver: 0 };
          return {
          week: formatWeekLabel(item['Week Label'] || item['Week'] || ''),
            done: Number(item['Done'] ?? 0) || 0,
            inProgress: Number(item['In Progress'] ?? 0) || 0,
            carryOver: Number(item['Carry Over'] ?? 0) || 0,
          };
        }).filter(item => item.week);

        setData({
          plannedVsDone,
          weeklyFlow,
        });
        setError(null);
      } catch (err: any) {
        setError(err.message);
        console.error("Error fetching throughput data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [weeks, filters.assignees, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

export function useOwnershipData() {
  const { filters } = useFilters();
  const [data, setData] = useState<OwnershipData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [taskLoadRes, executionSuccessRes] = await Promise.all([
          getTaskLoad(
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
            filters.issueType || undefined
          ),
          getExecutionSuccess(
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
            filters.issueType || undefined
          ),
        ]);

        if (!taskLoadRes.success) {
          throw new Error(taskLoadRes.error || "Failed to fetch task load data");
        }
        if (!executionSuccessRes.success) {
          throw new Error(executionSuccessRes.error || "Failed to fetch execution success data");
        }

        const taskLoad = (taskLoadRes.data || []).map((item: any) => {
          if (!item) return { assignee: 'Unknown', tasks: 0 };
          return {
            assignee: String(item['Assignee'] || 'Unknown'),
            tasks: Number(item['Task Count'] ?? 0) || 0,
          };
        }).filter(item => item.assignee && item.assignee !== 'Unknown');

        const executionSuccess = (executionSuccessRes.data || []).map((item: any) => {
          if (!item) return { assignee: 'Unknown', successRate: 0 };
          return {
            assignee: String(item['Assignee'] || 'Unknown'),
            successRate: Number(item['Success Rate (%)'] ?? 0) || 0,
          };
        }).filter(item => item.assignee && item.assignee !== 'Unknown');

        const performanceData = executionSuccess.map((item: any) => ({
          name: String(item.assignee || 'Unknown'),
          successRate: Number(item.successRate || 0),
          trend: 0,
        }));

        setData({
          taskLoad,
          executionSuccess,
          performanceData,
        });
        setError(null);
      } catch (err: any) {
        setError(err.message);
        console.error("Error fetching ownership data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters.assignees, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

export function useCompanyTrend(months: number = 6) {
  const { filters } = useFilters();
  const [data, setData] = useState<CompanyTrendData[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await getCompanyTrend(
          months,
          filters.dateRange.start || undefined,
          filters.dateRange.end || undefined,
          filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
          filters.issueType || undefined
        );

        if (!result.success) {
          throw new Error(result.error || "Failed to fetch company trend data");
        }

        const transformedData = (result.data || []).map((item: any) => {
          const month = item['Month'] || '';
          const avgLeadTime = Number(item['Average Lead Time (days)'] ?? item['Overall Avg Lead Time (days)'] ?? 0);
          const completionRate = Number(item['Completion Rate (%)'] ?? item['Overall Avg Completion (%)'] ?? 0);
          
          return {
            month,
            avgLeadTime: isNaN(avgLeadTime) ? 0 : avgLeadTime,
            completionRate: isNaN(completionRate) ? 0 : completionRate,
          };
        });

        setData(transformedData);
        setError(null);
      } catch (err: any) {
        setError(err.message);
        console.error("Error fetching company trend data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [months, filters.assignees, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

export function useExecutiveSummary() {
  const { filters } = useFilters();
  const [data, setData] = useState<{
    completionRate: number;
    avgLeadTime: number;
    reworkRatio: number;
    planned: number;
    done: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const response = await getExecutiveSummary(
          filters.dateRange.start || undefined,
          filters.dateRange.end || undefined,
          filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
          filters.issueType || undefined
        );

        if (!response.success) {
          throw new Error(response.error || "Failed to fetch executive summary");
        }

        const summaryData = response.data;
        const reworkRatioPercent = (summaryData.rework_ratio || 0) * 100;

        setData({
          completionRate: Math.round((summaryData.completion_rate || 0) * 10) / 10,
          avgLeadTime: Math.round((summaryData.avg_lead_time || 0) * 10) / 10,
          reworkRatio: Math.round(reworkRatioPercent * 10) / 10,
          planned: summaryData.planned || 0,
          done: summaryData.done || 0,
        });
        setError(null);
      } catch (err: any) {
        setError(err.message);
        console.error("Error fetching executive summary:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters.assignees, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

export function useQualityReworkData() {
  const { filters } = useFilters();
  const [data, setData] = useState<{
    qaVsFailed: Array<{ sprint: string; qaExecuted: number; failedQA: number }>;
    leadTimeTrend: Array<{ week: string; avgLeadTime: number }>;
    reworkRatio: Array<{ week: string; cleanDelivery: number; rework: number }>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await getWeeklyLeadTime(
          12,
          filters.dateRange.start || undefined,
          filters.dateRange.end || undefined,
          filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
          filters.issueType || undefined
        );

        if (!result.success) {
          throw new Error(result.error || "Failed to fetch lead time data");
        }

        const formatWeekLabel = (label: string): string => {
          if (!label) return '';
          const match = label.match(/W(\d+)/);
          if (match) {
            return `W${match[1]}`;
          }
          return label;
        };

        const leadTimeTrend = (result.data || []).map((item: any) => {
          if (!item) return { week: '', avgLeadTime: 0 };
          const leadTime = item['Average Lead Time (days)'] ?? item['Average Lead Time (Days)'] ?? 0;
          const weekLabel = formatWeekLabel(item['Week Label'] || item['Week'] || '');
          return {
            week: weekLabel,
            avgLeadTime: leadTime !== null && !isNaN(leadTime) ? Number(leadTime) : 0,
          };
        }).filter(item => item.week);

        let qaVsFailed: Array<{ sprint: string; qaExecuted: number; failedQA: number }> = [];
        let reworkRatio: Array<{ week: string; cleanDelivery: number; rework: number }> = [];

        try {
          const [qaVsFailedRes, reworkRatioRes] = await Promise.allSettled([
            getQAVsFailed(
              filters.dateRange.start || undefined,
              filters.dateRange.end || undefined,
              filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
              filters.issueType || undefined,
              'week' // Group by week
            ),
            getReworkRatio(
              12,
              filters.dateRange.start || undefined,
              filters.dateRange.end || undefined,
              filters.assignees && filters.assignees.length > 0 ? filters.assignees : undefined,
              filters.issueType || undefined
            ),
          ]);

          if (qaVsFailedRes.status === 'fulfilled' && qaVsFailedRes.value.success && qaVsFailedRes.value.data) {
            qaVsFailed = (qaVsFailedRes.value.data || []).map((item: any) => {
              const sprintOrWeek = item['sprint'] || item['sprintName'] || item['week'] || item['weekLabel'] || '';
              return {
                sprint: sprintOrWeek,
                qaExecuted: Number(item['qaExecuted'] ?? 0),
                failedQA: Number(item['failedQA'] ?? 0),
              };
            });
          } else if (qaVsFailedRes.status === 'rejected') {
            console.warn("QA vs Failed endpoint error (continuing without it):", qaVsFailedRes.reason);
          }

          if (reworkRatioRes.status === 'fulfilled' && reworkRatioRes.value.success && reworkRatioRes.value.data) {
            reworkRatio = (reworkRatioRes.value.data || []).map((item: any) => {
              const weekLabel = formatWeekLabel(item['Week Label'] || item['week'] || item['Week'] || '');
              return {
                week: weekLabel,
                cleanDelivery: Number(item['cleanDelivery'] ?? 0),
                rework: Number(item['rework'] ?? 0),
              };
            });
          } else if (reworkRatioRes.status === 'rejected') {
            console.warn("Rework Ratio endpoint error (continuing without it):", reworkRatioRes.reason);
          }
        } catch (apiError) {
          console.warn("QA/Rework data not available (this is OK):", apiError);
        }

        setData({
          qaVsFailed,
          leadTimeTrend,
          reworkRatio,
        });
        setError(null);
      } catch (err: any) {
        setError(err.message);
        console.error("Error fetching quality & rework data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters.assignees, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}
