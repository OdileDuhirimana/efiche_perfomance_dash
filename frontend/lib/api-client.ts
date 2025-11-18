/**
 * Backend API Client
 * Connects to the Python Flask backend API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  metadata?: Record<string, any>;
  error?: string;
}

export interface ChartDataPoint {
  [key: string]: any;
}

/**
 * Generic API fetch function
 */
async function fetchApi<T>(
  endpoint: string,
  params?: Record<string, string | number>
): Promise<ApiResponse<T>> {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, String(value));
    });
  }

  try {
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.error || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
  
    if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError')) {
      console.error(` API Connection Error (${endpoint}):`, {
        url: url.toString(),
        error: errorMessage,
        hint: 'Check if backend is running on ' + API_BASE_URL
      });
    } else {
      console.error(`❌ API Error (${endpoint}):`, {
        url: url.toString(),
        error: errorMessage
      });
    }
    
    return {
      success: false,
      data: [] as T,
      error: errorMessage,
    };
  }
}

/**
 * Health check endpoint
 */
export async function checkHealth(): Promise<ApiResponse<{ status: string; service: string; timestamp: string }>> {
  return fetchApi('/api/health');
}

/**
 * Get data accuracy metrics
 */
export async function getDataAccuracy(): Promise<ApiResponse<{
  accuracy_score: number;
  sprint_accuracy: number;
  status_accuracy: number;
  date_accuracy: number;
  meets_target: boolean;
  warnings: string[];
}>> {
  return fetchApi('/api/data/accuracy');
}

/**
 * Get the date range of available data
 */
export async function getDataDateRange(): Promise<ApiResponse<{
  min_date: string | null;
  max_date: string | null;
}>> {
  return fetchApi('/api/data/date-range');
}

/**
 * Get weekly planned vs done chart data
 */
export async function getWeeklyPlannedVsDone(
  numWeeks: number = 12,
  startDate?: string,
  endDate?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string | number> = { num_weeks: numWeeks };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/weekly-planned-vs-done', params);
}

/**
 * Get weekly flow chart data (Done, In Progress, Carry Over)
 */
export async function getWeeklyFlow(
  numWeeks: number = 12,
  startDate?: string,
  endDate?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string | number> = { num_weeks: numWeeks };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/weekly-flow', params);
}

/**
 * Get weekly lead time chart data
 */
export async function getWeeklyLeadTime(
  numWeeks: number = 12,
  startDate?: string,
  endDate?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string | number> = { num_weeks: numWeeks };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/weekly-lead-time', params);
}

/**
 * Get task load per assignee chart data
 */
export async function getTaskLoad(
  periodStart?: string,
  periodEnd?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string> = {};
  if (periodStart) params.start_date = periodStart;
  if (periodEnd) params.end_date = periodEnd;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/task-load', params);
}

/**
 * Get execution success by assignee chart data
 */
export async function getExecutionSuccess(
  periodStart?: string,
  periodEnd?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string> = {};
  if (periodStart) params.start_date = periodStart;
  if (periodEnd) params.end_date = periodEnd;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/execution-success', params);
}

/**
 * Get company trend chart data (monthly)
 */
export async function getCompanyTrend(
  numMonths: number = 6,
  periodStart?: string,
  periodEnd?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string | number> = { num_months: numMonths };
  if (periodStart) params.start_date = periodStart;
  if (periodEnd) params.end_date = periodEnd;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/company-trend', params);
}

/**
 * Get QA vs Failed QA chart data
 */
export async function getQAVsFailed(
  periodStart?: string,
  periodEnd?: string,
  assignee?: string,
  issueType?: string,
  groupBy: 'sprint' | 'week' = 'sprint'
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string> = { group_by: groupBy };
  if (periodStart) params.start_date = periodStart;
  if (periodEnd) params.end_date = periodEnd;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/qa-vs-failed', params);
}

/**
 * Get rework ratio chart data (clean delivery vs rework)
 */
export async function getReworkRatio(
  numWeeks: number = 12,
  startDate?: string,
  endDate?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string | number> = { num_weeks: numWeeks };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/rework-ratio', params);
}

/**
 * Get assignee completion trend (period comparison)
 */
export async function getAssigneeCompletionTrend(
  periodStart: string,
  periodEnd: string,
  comparePeriodStart?: string,
  comparePeriodEnd?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<ChartDataPoint[]>> {
  const params: Record<string, string> = {
    start_date: periodStart,
    end_date: periodEnd,
  };
  if (comparePeriodStart) params.compare_period_start = comparePeriodStart;
  if (comparePeriodEnd) params.compare_period_end = comparePeriodEnd;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi<ChartDataPoint[]>('/api/charts/assignee-completion-trend', params);
}

/**
 * Get executive summary KPIs
 * Returns: completion_rate, avg_lead_time, rework_ratio, planned, done
 */
export async function getExecutiveSummary(
  periodStart?: string,
  periodEnd?: string,
  assignee?: string,
  issueType?: string
): Promise<ApiResponse<{
  completion_rate: number;
  avg_lead_time: number;
  rework_ratio: number;
  planned: number;
  done: number;
  rework_count?: number;
  total_resolved?: number;
}>> {
  const params: Record<string, string> = {};
  if (periodStart) params.start_date = periodStart;
  if (periodEnd) params.end_date = periodEnd;
  if (assignee) params.assignee = assignee;
  if (issueType) params.issueType = issueType;
  return fetchApi('/api/executive-summary', params);
}

