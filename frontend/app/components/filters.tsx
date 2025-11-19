"use client";

import { useState, useEffect, useRef } from "react";
import { ChevronDown, ChevronUp, RotateCcw, Filter, RefreshCw, Download, MoveRight, X, Check } from "lucide-react";
import { useFilters } from "../contexts/FilterContext";

export default function Filters() {
  const { filters, setFilters, resetFilters, getFilterParams } = useFilters();
  const [isExpanded, setIsExpanded] = useState(true);
  const [assignees, setAssignees] = useState<string[]>([]);
  const [issueTypes, setIssueTypes] = useState<string[]>([]);
  const [dataDateRange, setDataDateRange] = useState<{ min: string | null; max: string | null }>({ min: null, max: null });
  const [isAssigneeDropdownOpen, setIsAssigneeDropdownOpen] = useState(false);
  const assigneeDropdownRef = useRef<HTMLDivElement>(null);
  const [localFilters, setLocalFilters] = useState<{
    assignees: string[];
    issueType: string;
    startDate: string;
    endDate: string;
  }>({
    assignees: filters.assignees || [],
    issueType: filters.issueType || "",
    startDate: filters.dateRange.start || "",
    endDate: filters.dateRange.end || "",
  });

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
        
        const taskLoadRes = await fetch(`${API_BASE_URL}/api/charts/task-load`);
        if (taskLoadRes.ok) {
          const taskLoadData = await taskLoadRes.json();
          if (taskLoadData.success && taskLoadData.data) {
            const assigneeList: string[] = taskLoadData.data
              .map((item: any) => {
                const assignee = item['Assignee'] || item.assignee;
                return assignee ? String(assignee) : '';
              })
              .filter((val: string) => Boolean(val)) as string[];
            setAssignees(["All Assignees", ...new Set(assigneeList)]);
          }
        }

        const dateRangeRes = await fetch(`${API_BASE_URL}/api/data/date-range`);
        if (dateRangeRes.ok) {
          const dateRangeData = await dateRangeRes.json();
          if (dateRangeData.success && dateRangeData.data) {
            setDataDateRange({
              min: dateRangeData.data.min_date ? dateRangeData.data.min_date.split('T')[0] : null,
              max: dateRangeData.data.max_date ? dateRangeData.data.max_date.split('T')[0] : null,
            });
          }
        }

        setIssueTypes(["All Types", "Bug", "Task", "Story", "Epic", "Subtask"]);
      } catch (error) {
        console.error("Error fetching filter options:", error);
        setAssignees(["All Assignees"]);
        setIssueTypes(["All Types", "Bug", "Task", "Story", "Epic"]);
      }
    };

    fetchOptions();
  }, []);

  useEffect(() => {
    setLocalFilters({
      assignees: filters.assignees || [],
      issueType: filters.issueType || "",
      startDate: filters.dateRange.start || "",
      endDate: filters.dateRange.end || "",
    });
  }, [filters]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (assigneeDropdownRef.current && !assigneeDropdownRef.current.contains(event.target as Node)) {
        setIsAssigneeDropdownOpen(false);
      }
    };

    if (isAssigneeDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isAssigneeDropdownOpen]);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleReset = () => {
    resetFilters();
    setLocalFilters({
      assignees: [],
      issueType: "",
      startDate: "",
      endDate: "",
    });
  };

  const handleApply = () => {
    let startDate = localFilters.startDate || null;
    let endDate = localFilters.endDate || null;
    
    if (dataDateRange.min && startDate && startDate < dataDateRange.min) {
      startDate = dataDateRange.min;
      setLocalFilters(prev => ({ ...prev, startDate: startDate || "" }));
    }
    
    if (dataDateRange.max && endDate && endDate > dataDateRange.max) {
      endDate = dataDateRange.max;
      setLocalFilters(prev => ({ ...prev, endDate: endDate || "" }));
    }
    
    if (startDate && endDate && startDate > endDate) {
      [startDate, endDate] = [endDate, startDate];
      setLocalFilters(prev => ({ ...prev, startDate: startDate || "", endDate: endDate || "" }));
    }
    
    const validAssignees = localFilters.assignees.filter(
      a => a && a !== "All Assignees" && a.trim()
    );
    
    setFilters({
      assignees: validAssignees,
      issueType: localFilters.issueType && localFilters.issueType !== "All Types" ? localFilters.issueType : null,
      dateRange: {
        start: startDate,
        end: endDate,
      },
    });
  };

  const handleRefresh = () => {
    setFilters({ ...filters });
    window.location.reload();
  };

  const handleDownload = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
      const params = new URLSearchParams();
      
      if (filters.dateRange.start) params.append('start_date', filters.dateRange.start);
      if (filters.dateRange.end) params.append('end_date', filters.dateRange.end);
      if (filters.assignees && filters.assignees.length > 0) {
        filters.assignees.forEach(assignee => {
          if (assignee && assignee !== "All Assignees") {
            params.append('assignee', assignee);
          }
        });
      }
      if (filters.issueType && filters.issueType !== "All Types") {
        params.append('issueType', filters.issueType);
      }

      const endpoints = [
        '/api/charts/weekly-planned-vs-done',
        '/api/charts/weekly-flow',
        '/api/charts/weekly-lead-time',
        '/api/charts/task-load',
        '/api/charts/execution-success',
        '/api/charts/company-trend',
      ];

      const allData: any[] = [];
      
      for (const endpoint of endpoints) {
        try {
          const url = `${API_BASE_URL}${endpoint}?${params.toString()}`;
          const response = await fetch(url);
          if (response.ok) {
            const result = await response.json();
            if (result.success && result.data) {
              const chartName = endpoint.split('/').pop()?.replace(/-/g, ' ') || 'data';
              result.data.forEach((item: any) => {
                allData.push({ ...item, source: chartName });
              });
            }
          }
        } catch (err) {
          console.warn(`Failed to fetch ${endpoint}:`, err);
        }
      }

      if (allData.length === 0) {
        alert('No data available to export');
        return;
      }

      const { exportToCSV } = await import('@/lib/utils/export');
      exportToCSV(allData, 'dashboard-export');
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data. Please try again.');
    }
  };

  const activeFiltersCount = [
    filters.assignees.length > 0 ? filters.assignees : null,
    filters.issueType,
    filters.dateRange.start,
    filters.dateRange.end,
  ].filter(Boolean).length;

  const removeFilter = (type: "assignees" | "assignee" | "issueType" | "dateRange", value?: string) => {
    if (type === "dateRange") {
      setFilters({
        ...filters,
        dateRange: { start: null, end: null },
      });
      setLocalFilters(prev => ({
        ...prev,
        startDate: "",
        endDate: "",
      }));
    } else if (type === "assignees" || type === "assignee") {
      if (value) {
        const updatedAssignees = filters.assignees.filter(a => a !== value);
        setFilters({
          ...filters,
          assignees: updatedAssignees,
        });
        setLocalFilters(prev => ({
          ...prev,
          assignees: updatedAssignees,
        }));
      } else {
        setFilters({
          ...filters,
          assignees: [],
        });
        setLocalFilters(prev => ({
          ...prev,
          assignees: [],
        }));
      }
    } else {
      setFilters({
        ...filters,
        [type]: null,
      });
      setLocalFilters({
        ...localFilters,
        [type]: "",
      });
    }
  };

  return (
    <section className="bg-white rounded-xl border border-gray-200/50 shadow-md hover:shadow-lg transition-shadow p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-50 shadow-sm">
              <Filter className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900 tracking-tight">
                Filters & Controls
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {activeFiltersCount > 0 ? `${activeFiltersCount} active filter${activeFiltersCount > 1 ? 's' : ''}` : 'Customize your dashboard view'}
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            className="p-2.5 rounded-lg hover:bg-blue-50 transition-colors group border border-gray-200 hover:border-blue-200"
            aria-label="Refresh"
            title="Refresh Data"
          >
            <RefreshCw className="w-5 h-5 text-blue-600 group-hover:text-blue-700 group-hover:rotate-180 transition-transform duration-500" />
          </button>
          <button
            onClick={handleDownload}
            className="p-2.5 rounded-lg hover:bg-blue-50 transition-colors group border border-gray-200 hover:border-blue-200"
            aria-label="Download"
            title="Export All Data"
          >
            <Download className="w-5 h-5 text-blue-600 group-hover:text-blue-700" />
          </button>
          <button
            onClick={toggleExpand}
            className="p-2.5 rounded-lg hover:bg-blue-50 transition-colors group border border-gray-200 hover:border-blue-200"
            aria-label={isExpanded ? "Collapse" : "Expand"}
            title={isExpanded ? "Collapse Filters" : "Expand Filters"}
          >
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-blue-600 group-hover:text-blue-700" />
            ) : (
              <ChevronDown className="w-5 h-5 text-blue-600 group-hover:text-blue-700" />
            )}
          </button>
        </div>
      </div>

      {/* Filter Content */}
      {isExpanded && (
        <div className="space-y-6 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6 items-end">
            {/* Assignee Filter - Multi-Select Dropdown */}
            <div className="lg:col-span-3">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-2">
                Assignee(s)
                {localFilters.assignees.length > 0 && (
                  <span className="text-xs font-normal text-blue-600">
                    ({localFilters.assignees.length} selected)
                  </span>
                )}
              </label>
              <div className="relative" ref={assigneeDropdownRef}>
                <button
                  type="button"
                  onClick={() => setIsAssigneeDropdownOpen(!isAssigneeDropdownOpen)}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 bg-white text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all hover:border-gray-300 shadow-sm flex items-center justify-between min-h-[48px]"
                >
                  <span className="text-left flex-1 truncate">
                    {localFilters.assignees.length === 0
                      ? 'Select assignee(s)...'
                      : localFilters.assignees.length === 1
                      ? localFilters.assignees[0]
                      : `${localFilters.assignees.length} assignees selected`}
                  </span>
                  <ChevronDown 
                    className={`w-4 h-4 text-gray-400 transition-transform ${isAssigneeDropdownOpen ? 'rotate-180' : ''}`}
                  />
                </button>
                
                {isAssigneeDropdownOpen && (
                  <div className="absolute z-50 w-full mt-1 bg-white border-2 border-gray-200 rounded-xl shadow-lg max-h-64 overflow-y-auto">
                    <div className="p-2">
                      {assignees.filter(a => a !== "All Assignees").length === 0 ? (
                        <div className="px-3 py-2 text-sm text-gray-500">No assignees available</div>
                      ) : (
                        assignees.filter(a => a !== "All Assignees").map((assignee) => {
                          const isSelected = localFilters.assignees.includes(assignee);
                          return (
                            <div
                              key={assignee}
                              onClick={() => {
                                if (isSelected) {
                                  setLocalFilters({
                                    ...localFilters,
                                    assignees: localFilters.assignees.filter(a => a !== assignee)
                                  });
                                } else {
                                  setLocalFilters({
                                    ...localFilters,
                                    assignees: [...localFilters.assignees, assignee]
                                  });
                                }
                              }}
                              className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
                            >
                              <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                                isSelected 
                                  ? 'bg-blue-600 border-blue-600' 
                                  : 'border-gray-300 bg-white'
                              }`}>
                                {isSelected && <Check className="w-3 h-3 text-white" />}
                              </div>
                              <span className={`text-sm flex-1 ${isSelected ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
                                {assignee}
                              </span>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Issue Type Filter */}
            <div className="lg:col-span-3">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-2">
                Issue Type
              </label>
              <div className="relative">
                <select
                  value={localFilters.issueType}
                  onChange={(e) => setLocalFilters({ ...localFilters, issueType: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 bg-white text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all hover:border-gray-300 shadow-sm"
                >
                  <option value="">Select Issue Type(s)</option>
                  {issueTypes.map((type) => (
                    <option key={type} value={type === "All Types" ? "" : type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Date Range Filter */}
            <div className="lg:col-span-4">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-2">
                Date Range
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="date"
                  value={localFilters.startDate}
                  min={dataDateRange.min || undefined}
                  max={dataDateRange.max || undefined}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (dataDateRange.min && value < dataDateRange.min) {
                      return;
                    }
                    if (dataDateRange.max && value > dataDateRange.max) {
                      return;
                    }
                    setLocalFilters({ ...localFilters, startDate: value });
                  }}
                  className="flex-1 min-w-0 px-4 py-3 rounded-xl border-2 border-gray-200 bg-white text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all hover:border-gray-300 shadow-sm"
                />
                <span className="text-gray-400 shrink-0">
                  <MoveRight className="w-5 h-5" />
                </span>
                <input
                  type="date"
                  value={localFilters.endDate}
                  min={dataDateRange.min || undefined}
                  max={dataDateRange.max || undefined}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (dataDateRange.min && value < dataDateRange.min) {
                      return;
                    }
                    if (dataDateRange.max && value > dataDateRange.max) {
                      return;
                    }
                    setLocalFilters({ ...localFilters, endDate: value });
                  }}
                  className="flex-1 min-w-0 px-4 py-3 rounded-xl border-2 border-gray-200 bg-white text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all hover:border-gray-300 shadow-sm"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="lg:col-span-2 flex gap-2">
              <button
                onClick={handleReset}
                className="flex-1 px-4 py-3 rounded-xl bg-gray-100 text-gray-700 text-sm font-semibold hover:bg-gray-200 transition-colors shadow-sm border-2 border-transparent hover:border-gray-300 flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
              <button
                onClick={handleApply}
                className="flex-1 px-4 py-3 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg flex items-center justify-center gap-2"
              >
                <Filter className="w-4 h-4" />
                Apply
              </button>
            </div>
          </div>

          {/* Active Filters Badge */}
          {activeFiltersCount > 0 && (
            <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
              <span className="text-xs font-medium text-gray-600">Active filters:</span>
              <div className="flex items-center gap-2 flex-wrap">
                {filters.assignees && filters.assignees.length > 0 && (
                  <>
                    {filters.assignees.map((assignee) => (
                      <span key={assignee} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200">
                        Assignee: {assignee}
                        <button
                          onClick={() => removeFilter("assignees", assignee)}
                          className="hover:bg-blue-100 rounded p-0.5 transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </>
                )}
                {filters.issueType && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200">
                    Type: {filters.issueType}
                    <button
                      onClick={() => removeFilter("issueType")}
                      className="hover:bg-blue-100 rounded p-0.5 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                )}
                {(filters.dateRange.start || filters.dateRange.end) && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200">
                    Date: {filters.dateRange.start || "..."} to {filters.dateRange.end || "..."}
                    <button
                      onClick={() => removeFilter("dateRange")}
                      className="hover:bg-blue-100 rounded p-0.5 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
