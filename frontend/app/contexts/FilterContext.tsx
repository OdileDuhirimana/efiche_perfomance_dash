/**
 * Global filter context for dashboard
 * Manages filter state (assignee, issue type, date range) that applies to all charts
 * Default date range: last 90 days (3 months)
 */
"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";

export interface FilterState {
  assignee: string | null;
  issueType: string | null;
  dateRange: {
    start: string | null;
    end: string | null;
  };
}

interface FilterContextType {
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
  resetFilters: () => void;
  getFilterParams: () => URLSearchParams;
}

const FilterContext = createContext<FilterContextType | undefined>(undefined);

// Default date range: today going back 90 days (3 months)
const getDefaultDateRange = () => {
  const today = new Date();
  const daysAgo = new Date();
  daysAgo.setDate(today.getDate() - 90);
  
  // Format as YYYY-MM-DD for date inputs
  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0];
  };
  
  return {
    start: formatDate(daysAgo),
    end: formatDate(today),
  };
};

const defaultDateRange = getDefaultDateRange();

const defaultFilters: FilterState = {
  assignee: null,
  issueType: null,
  dateRange: defaultDateRange,
};

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  const resetFilters = () => {
    const updatedDefaultDateRange = getDefaultDateRange();
    setFilters({
      assignee: null,
      issueType: null,
      dateRange: updatedDefaultDateRange,
    });
  };

  // Convert filter state to URL search params for API calls
  // Excludes "All" values to avoid unnecessary filtering
  const getFilterParams = useCallback((): URLSearchParams => {
    const params = new URLSearchParams();
    
    if (filters.assignee && filters.assignee !== "All Assignees") {
      params.append("assignee", filters.assignee);
    }
    
    if (filters.issueType && filters.issueType !== "All Types") {
      params.append("issueType", filters.issueType);
    }
    
    if (filters.dateRange.start) {
      params.append("startDate", filters.dateRange.start);
    }
    
    if (filters.dateRange.end) {
      params.append("endDate", filters.dateRange.end);
    }
    
    return params;
  }, [filters]);

  return (
    <FilterContext.Provider value={{ filters, setFilters, resetFilters, getFilterParams }}>
      {children}
    </FilterContext.Provider>
  );
}

export function useFilters() {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error("useFilters must be used within a FilterProvider");
  }
  return context;
}

