import pandas as pd
from datetime import datetime, timezone
from typing import Optional


def filter_by_overall_window(df: pd.DataFrame, earliest_dt, latest_dt) -> pd.DataFrame:
    """Filter DataFrame to include issues with activity within the date window."""
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
    """Apply assignee and issue type filters to DataFrame."""
    filtered = df.copy()
    if assignees:
        filtered = filtered[filtered['Assignee'].isin(assignees)]
    if issue_types:
        filtered = filtered[filtered['Issue Type'].isin(issue_types)]
    return filtered


def filter_planned_activities(df: pd.DataFrame, start_dt, end_dt) -> pd.DataFrame:
    """Filter DataFrame to planned activities: Created OR Updated within period."""
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
    """Filter DataFrame to carry-over activities: Created before period AND Updated during period."""
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    
    df = df.copy()
    if 'Created' in df.columns:
        df['Created'] = pd.to_datetime(df['Created'], utc=True, errors='coerce')
    if 'Updated' in df.columns:
        df['Updated'] = pd.to_datetime(df['Updated'], utc=True, errors='coerce')
    
    status_col = None
    if 'Status Category (Mapped)' in df.columns:
        status_col = 'Status Category (Mapped)'
    elif 'New Status Category' in df.columns:
        status_col = 'New Status Category'
    elif 'Status Category' in df.columns:
        status_col = 'Status Category'

    created_before = df['Created'] < start_dt
    
    if status_col and 'Resolved' in df.columns:
        df['Resolved'] = pd.to_datetime(df['Resolved'], utc=True, errors='coerce')
        
        updated_in_period = (df['Updated'] >= start_dt) & (df['Updated'] <= end_dt)
        not_done = df[status_col].astype(str) != 'Done'
        
        resolved_in_period = (df['Resolved'] >= start_dt) & (df['Resolved'] <= end_dt)
        is_done = df[status_col].astype(str) == 'Done'
        
        carry_over_mask = created_before & (
            (updated_in_period & not_done) |
            (resolved_in_period & is_done)
        )
    else:
        carry_over_mask = (
            created_before &
            ((df['Updated'] >= start_dt) & (df['Updated'] <= end_dt))
        )
    
    return df[carry_over_mask].copy()


def apply_standard_filters(df: pd.DataFrame, assignee: Optional[str] = None, 
                          assignees: Optional[list] = None,
                          issue_type: Optional[str] = None, 
                          start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> pd.DataFrame:
    """Apply standard filters to DataFrame in consistent order across all endpoints."""
    filtered_df = df.copy()
    
    assignee_list = assignees
    if assignee_list is None and assignee:
        assignee_list = [assignee]
    
    if assignee_list:
        valid_assignees = [a for a in assignee_list if a and a != "All Assignees" and str(a).strip()]
        if valid_assignees:
            filtered_df = filtered_df[filtered_df['Assignee'].isin(valid_assignees)].copy()
    
    if issue_type and issue_type != "All Types" and issue_type.strip():
        filtered_df = filtered_df[filtered_df['Issue Type'] == issue_type].copy()
    
    if end_date is not None and start_date is not None:
        filtered_df = filter_by_overall_window(filtered_df, start_date, end_date)
    
    return filtered_df
