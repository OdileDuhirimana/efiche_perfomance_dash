import pandas as pd
from datetime import datetime, timezone
from typing import Optional


def filter_by_overall_window(df: pd.DataFrame, earliest_dt, latest_dt) -> pd.DataFrame:
    """
    Filter DataFrame to include issues that have activity within the date window.
    
    Logic: Returns issues where Created, Updated, or Resolved date falls within the window.
    Ensures dates are timezone-aware for accurate comparisons.
    
    Use: Applied to filter data to a specific time range before chart calculations.
    
    Args:
        df: DataFrame with issues
        earliest_dt: Start datetime (timezone-aware)
        latest_dt: End datetime (timezone-aware)
    
    Returns:
        Filtered DataFrame with issues active in the date window
    """
    if earliest_dt.tzinfo is None:
        earliest_dt = earliest_dt.replace(tzinfo=timezone.utc)
    if latest_dt.tzinfo is None:
        latest_dt = latest_dt.replace(tzinfo=timezone.utc)
    
    df = df.copy()
    if 'Created' in df.columns:
        df['Created'] = pd.to_datetime(df['Created'], utc=True, errors='coerce')
    if 'Updated' in df.columns:
        df['Updated'] = pd.to_datetime(df['Updated'], utc=True, errors='coerce')
    if 'Resolved' in df.columns:
        df['Resolved'] = pd.to_datetime(df['Resolved'], utc=True, errors='coerce')
    
    return df[
        ((df['Created'] >= earliest_dt) & (df['Created'] <= latest_dt)) |
        ((df['Updated'] >= earliest_dt) & (df['Updated'] <= latest_dt)) |
        ((df['Resolved'] >= earliest_dt) & (df['Resolved'] <= latest_dt))
    ].copy()


def apply_selection_filters(df: pd.DataFrame, assignees, issue_types) -> pd.DataFrame:
    """
    Apply assignee and issue type filters to DataFrame.
    
    Logic: Filters DataFrame by assignee names and/or issue types if provided.
    Returns original DataFrame if no filters specified.
    
    Use: Applied in API routes to filter data based on user selections.
    
    Args:
        df: DataFrame with issues
        assignees: List of assignee names (or None)
        issue_types: List of issue types (or None)
    
    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()
    if assignees:
        filtered = filtered[filtered['Assignee'].isin(assignees)]
    if issue_types:
        filtered = filtered[filtered['Issue Type'].isin(issue_types)]
    return filtered


def filter_planned_activities(df: pd.DataFrame, start_dt, end_dt) -> pd.DataFrame:
    """
    Filter DataFrame to planned activities: Created OR Updated within period.
    
    Logic: Planned = (Created in period) OR (Updated in period)
    Ensures dates are timezone-aware and converts DataFrame date columns to datetime.
    
    Use: Used in chart calculations to count planned activities for KPIs and charts.
    
    Args:
        df: DataFrame with issues
        start_dt: Period start datetime (timezone-aware)
        end_dt: Period end datetime (timezone-aware)
    
    Returns:
        Filtered DataFrame with planned activities
    """
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    
    df = df.copy()
    if 'Created' in df.columns:
        df['Created'] = pd.to_datetime(df['Created'], utc=True, errors='coerce')
    if 'Updated' in df.columns:
        df['Updated'] = pd.to_datetime(df['Updated'], utc=True, errors='coerce')
    
    return df[
        ((df['Created'] >= start_dt) & (df['Created'] <= end_dt)) |
        ((df['Updated'] >= start_dt) & (df['Updated'] <= end_dt))
    ].copy()


def filter_carry_over_activities(df: pd.DataFrame, start_dt, end_dt) -> pd.DataFrame:
    """
    Filter DataFrame to carry-over activities: Created before period AND (Updated OR Resolved during period).
    
    Logic: Carry-Over = (Created < period_start) AND ((Updated in period) OR (Resolved in period))
    NO status filter applied - includes all statuses.
    Ensures dates are timezone-aware and converts DataFrame date columns to datetime.
    
    Use: Used in chart calculations to count carry-over tasks that were created before the period
    but had activity (update or resolution) during the period.
    
    Args:
        df: DataFrame with issues
        start_dt: Period start datetime (timezone-aware)
        end_dt: Period end datetime (timezone-aware)
    
    Returns:
        Filtered DataFrame with carry-over activities
    """
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    
    df = df.copy()
    if 'Created' in df.columns:
        df['Created'] = pd.to_datetime(df['Created'], utc=True, errors='coerce')
    if 'Updated' in df.columns:
        df['Updated'] = pd.to_datetime(df['Updated'], utc=True, errors='coerce')
    if 'Resolved' in df.columns:
        df['Resolved'] = pd.to_datetime(df['Resolved'], utc=True, errors='coerce')
    
    carry_over_mask = (
        (df['Created'] < start_dt) &
        (
            ((df['Updated'] >= start_dt) & (df['Updated'] <= end_dt)) |
            ((df['Resolved'] >= start_dt) & (df['Resolved'] <= end_dt))
        )
    )
    
    return df[carry_over_mask].copy()


def apply_standard_filters(df: pd.DataFrame, assignee: Optional[str] = None, 
                          issue_type: Optional[str] = None, 
                          start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> pd.DataFrame:
    """
    Apply standard filters to DataFrame in consistent order across all endpoints.
    
    This function ensures data consistency by applying filters in the same order:
    1. Assignee filter (if provided and not "All Assignees")
    2. Issue Type filter (if provided and not "All Types")
    3. Date window filter (if end_date provided)
    
    All endpoints should use this function to ensure they work with the same filtered dataset.
    This guarantees that planned and done calculations use identical data sources.
    
    Args:
        df: Base DataFrame from get_cached_data()
        assignee: Assignee name to filter by (or None/"All Assignees" to skip)
        issue_type: Issue type to filter by (or None/"All Types" to skip)
        start_date: Optional start date for date window filter
        end_date: Optional end date for date window filter (triggers date filtering if provided)
    
    Returns:
        Filtered DataFrame with consistent filtering applied
    """
    filtered_df = df.copy()
    
    if assignee and assignee != "All Assignees" and assignee.strip():
        filtered_df = filtered_df[filtered_df['Assignee'] == assignee].copy()
    
    if issue_type and issue_type != "All Types" and issue_type.strip():
        filtered_df = filtered_df[filtered_df['Issue Type'] == issue_type].copy()
    
    if end_date is not None and start_date is not None:
        filtered_df = filter_by_overall_window(filtered_df, start_date, end_date)
    
    return filtered_df
