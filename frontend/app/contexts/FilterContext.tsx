/** Global filter context for dashboard */
"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";

export interface FilterState {
  assignees: string[];
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

const getDefaultDateRange = () => {
  const today = new Date();
  const day = today.getDay();
  const diffToMonday = day === 0 ? 6 : day - 1;
  const daysAgo = new Date(today);
  daysAgo.setDate(today.getDate() - diffToMonday);
  
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
  assignees: [],
  issueType: null,
  dateRange: defaultDateRange,
};

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  const resetFilters = () => {
    const updatedDefaultDateRange = getDefaultDateRange();
    setFilters({
      assignees: [],
      issueType: null,
      dateRange: updatedDefaultDateRange,
    });
  };

  const getFilterParams = useCallback((): URLSearchParams => {
    const params = new URLSearchParams();
    
    if (filters.assignees && filters.assignees.length > 0) {
      filters.assignees.forEach(assignee => {
        if (assignee && assignee !== "All Assignees") {
          params.append("assignee", assignee);
        }
      });
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

