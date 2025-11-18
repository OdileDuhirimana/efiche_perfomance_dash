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

/**
 * Hook for fetching throughput data (Planned vs Done and Weekly Flow)
 */
export function useThroughputData(weeks: number = 12) {
  const { filters } = useFilters();
  const [data, setData] = useState<ThroughputData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch both charts in parallel with filters
        const [plannedVsDoneRes, weeklyFlowRes] = await Promise.all([
          getWeeklyPlannedVsDone(
            weeks,
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignee || undefined,
            filters.issueType || undefined
          ),
          getWeeklyFlow(
            weeks,
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignee || undefined,
            filters.issueType || undefined
          ),
        ]);

        if (!plannedVsDoneRes.success) {
          throw new Error(plannedVsDoneRes.error || "Failed to fetch planned vs done data");
        }
        if (!weeklyFlowRes.success) {
          throw new Error(weeklyFlowRes.error || "Failed to fetch weekly flow data");
        }

        // Format week labels: extract week number from full label (e.g., "W01" from "W01 (Jan 01 - Jan 07)")
        const formatWeekLabel = (label: string): string => {
          if (!label) return '';
          const match = label.match(/W(\d+)/);
          if (match) {
            return `W${match[1]}`;
          }
          return label;
        };

        // Transform backend data to component format (preserve all weeks, even with zero values)
        const plannedVsDone = (plannedVsDoneRes.data || []).map((item: any) => {
          if (!item) return { week: '', planned: 0, done: 0 };
          return {
          week: formatWeekLabel(item['Week Label'] || item['Week'] || ''),
            planned: Number(item['Planned'] ?? 0) || 0,
            done: Number(item['Done'] ?? 0) || 0,
          };
        }).filter(item => item.week); // Filter out empty weeks

        const weeklyFlow = (weeklyFlowRes.data || []).map((item: any) => {
          if (!item) return { week: '', done: 0, inProgress: 0, carryOver: 0 };
          return {
          week: formatWeekLabel(item['Week Label'] || item['Week'] || ''),
            done: Number(item['Done'] ?? 0) || 0,
            inProgress: Number(item['In Progress'] ?? 0) || 0,
            carryOver: Number(item['Carry Over'] ?? 0) || 0,
          };
        }).filter(item => item.week); // Filter out empty weeks

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
  }, [weeks, filters.assignee, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

/**
 * Hook for fetching ownership data (Task Load and Execution Success)
 */
export function useOwnershipData() {
  const { filters } = useFilters();
  const [data, setData] = useState<OwnershipData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch both charts in parallel with filters
        const [taskLoadRes, executionSuccessRes] = await Promise.all([
          getTaskLoad(
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignee || undefined,
            filters.issueType || undefined
          ),
          getExecutionSuccess(
            filters.dateRange.start || undefined,
            filters.dateRange.end || undefined,
            filters.assignee || undefined,
            filters.issueType || undefined
          ),
        ]);

        if (!taskLoadRes.success) {
          throw new Error(taskLoadRes.error || "Failed to fetch task load data");
        }
        if (!executionSuccessRes.success) {
          throw new Error(executionSuccessRes.error || "Failed to fetch execution success data");
        }

        // Transform task load data
        const taskLoad = (taskLoadRes.data || []).map((item: any) => {
          if (!item) return { assignee: 'Unknown', tasks: 0 };
          return {
            assignee: String(item['Assignee'] || 'Unknown'),
            tasks: Number(item['Task Count'] ?? 0) || 0,
          };
        }).filter(item => item.assignee && item.assignee !== 'Unknown');

        // Transform execution success data
        const executionSuccess = (executionSuccessRes.data || []).map((item: any) => {
          if (!item) return { assignee: 'Unknown', successRate: 0 };
          return {
            assignee: String(item['Assignee'] || 'Unknown'),
            successRate: Number(item['Success Rate (%)'] ?? 0) || 0,
          };
        }).filter(item => item.assignee && item.assignee !== 'Unknown');

        // Create performance data (trend removed - set to 0 as placeholder)
        const performanceData = executionSuccess.map((item: any) => ({
          name: String(item.assignee || 'Unknown'),
          successRate: Number(item.successRate || 0),
          trend: 0, // Placeholder - trend calculation removed
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
  }, [filters.assignee, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

/**
 * Hook for fetching company trend data
 */
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
          filters.assignee || undefined,
          filters.issueType || undefined
        );

        if (!result.success) {
          throw new Error(result.error || "Failed to fetch company trend data");
        }

        // Transform data to match component expectations - ensure all months are included
        const transformedData = (result.data || []).map((item: any) => {
          // Backend returns 'Month' for month identifier
          // Prioritize per-month fields: 'Average Lead Time (days)' and 'Completion Rate (%)'
          // Fallback to overall averages only if per-month values are missing
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
  }, [months, filters.assignee, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

/**
 * Hook for fetching executive summary data
 * Uses the dedicated /api/executive-summary endpoint for accurate period-based calculations
 */
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
        
        // Use the dedicated executive summary endpoint
        // This calculates metrics for the FULL selected period, not just latest week
        const response = await getExecutiveSummary(
          filters.dateRange.start || undefined,
          filters.dateRange.end || undefined,
          filters.assignee || undefined,
          filters.issueType || undefined
        );

        if (!response.success) {
          throw new Error(response.error || "Failed to fetch executive summary");
        }

        const summaryData = response.data;
        
        // Convert rework_ratio from decimal (0-1) to percentage (0-100)
        const reworkRatioPercent = (summaryData.rework_ratio || 0) * 100;

        // Round to 1 decimal place for display
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
  }, [filters.assignee, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}

/**
 * Hook for fetching quality & rework data
 * Uses weekly lead time data (QA and rework data not available in backend yet)
 */
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
          filters.assignee || undefined,
          filters.issueType || undefined
        );

        if (!result.success) {
          throw new Error(result.error || "Failed to fetch lead time data");
        }

        // Helper to format week labels - just show week number
        const formatWeekLabel = (label: string): string => {
          if (!label) return '';
          // Extract just the week number (e.g., "W01" from "W01 (Jan 01 - Jan 07)")
          const match = label.match(/W(\d+)/);
          if (match) {
            return `W${match[1]}`;
          }
          return label;
        };

        // Transform lead time data - handle null values properly, keep all weeks even with 0 lead time
        const leadTimeTrend = (result.data || []).map((item: any) => {
          if (!item) return { week: '', avgLeadTime: 0 };
          const leadTime = item['Average Lead Time (days)'] ?? item['Average Lead Time (Days)'] ?? 0;
          const weekLabel = formatWeekLabel(item['Week Label'] || item['Week'] || '');
          return {
            week: weekLabel,
            avgLeadTime: leadTime !== null && !isNaN(leadTime) ? Number(leadTime) : 0,
          };
        }).filter(item => item.week); // Filter out empty weeks

        // Fetch QA vs Failed and Rework Ratio data
        // Use Promise.allSettled to prevent one failure from breaking the other
        let qaVsFailed: Array<{ sprint: string; qaExecuted: number; failedQA: number }> = [];
        let reworkRatio: Array<{ week: string; cleanDelivery: number; rework: number }> = [];

        try {
          const [qaVsFailedRes, reworkRatioRes] = await Promise.allSettled([
            getQAVsFailed(
              filters.dateRange.start || undefined,
              filters.dateRange.end || undefined,
              filters.assignee || undefined,
              filters.issueType || undefined,
              'sprint' // Group by sprint
            ),
            getReworkRatio(
              12,
              filters.dateRange.start || undefined,
              filters.dateRange.end || undefined,
              filters.assignee || undefined,
              filters.issueType || undefined
            ),
          ]);

          // Transform QA vs Failed data
          if (qaVsFailedRes.status === 'fulfilled' && qaVsFailedRes.value.success && qaVsFailedRes.value.data) {
            qaVsFailed = (qaVsFailedRes.value.data || []).map((item: any) => {
              // Backend returns 'sprint' or 'sprintName' for sprint grouping, 'week' or 'weekLabel' for week grouping
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

          // Transform rework ratio data
          if (reworkRatioRes.status === 'fulfilled' && reworkRatioRes.value.success && reworkRatioRes.value.data) {
            reworkRatio = (reworkRatioRes.value.data || []).map((item: any) => {
              // Backend returns 'Week Label' or 'week' for week identifier
              // Backend returns cleanDelivery and rework as ratios (0-1), chart expects same format
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
          // If new endpoints fail, continue with empty arrays (graceful degradation)
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
  }, [filters.assignee, filters.issueType, filters.dateRange.start, filters.dateRange.end]);

  return { data, loading, error };
}
