import pandas as pd
from datetime import datetime


def was_sprint_active_in_week_primary_only(row, week_start, week_end, df_sprints=None):
    """
    Check if sprint was active during a week using Primary Sprint Id only.
    
    Normalizes all dates to UTC. Checks if sprint dates overlap week (sprint_start <= week_end AND sprint_end >= week_start).
    If sprint has complete date before week start, returns False. If sprint state is active/open, returns True.
    If closed but dates overlap, checks if sprint_end is within or after week.
    
    
    Args:
        row: Issue row with sprint information
        week_start: Week start datetime (timezone-aware UTC)
        week_end: Week end datetime (timezone-aware UTC)
        df_sprints: Optional DataFrame with sprint details (for better accuracy)
    
    Returns:
        bool: True if sprint was active during the week
    """
    primary_sprint_id = row.get('Primary Sprint Id')
    
    if pd.isna(primary_sprint_id):
        return False
    
    if df_sprints is not None and not df_sprints.empty:
        sprint_row = df_sprints[df_sprints['Sprint Id'] == primary_sprint_id]
        if not sprint_row.empty:
            sprint_start = sprint_row.iloc[0].get('Sprint Start Date')
            sprint_end = sprint_row.iloc[0].get('Sprint End Date')
            sprint_complete_date = sprint_row.iloc[0].get('Sprint Complete Date')
            sprint_state = str(sprint_row.iloc[0].get('Sprint State', '')).lower()
        else:
            sprint_start = row.get('Sprint Start Date')
            sprint_end = row.get('Sprint End Date')
            sprint_complete_date = row.get('Sprint Complete Date')
            sprint_state = str(row.get('Sprint State (Full)', '')).lower()
    else:
        sprint_start = row.get('Sprint Start Date')
        sprint_end = row.get('Sprint End Date')
        sprint_complete_date = row.get('Sprint Complete Date')
        sprint_state = str(row.get('Sprint State (Full)', '')).lower()
    
    if pd.isna(sprint_start) or pd.isna(sprint_end):
        return False
    
    sprint_start = _normalize_to_utc(sprint_start)
    sprint_end = _normalize_to_utc(sprint_end)
    week_start = _normalize_to_utc(week_start)
    week_end = _normalize_to_utc(week_end)
    
    sprint_overlaps_week = (sprint_start <= week_end) and (sprint_end >= week_start)
    
    if not sprint_overlaps_week:
        return False
    
    if not pd.isna(sprint_complete_date):
        sprint_complete_date = _normalize_to_utc(sprint_complete_date)
        if sprint_complete_date < week_start:
            return False
        return True
    
    if sprint_state in ['active', 'open']:
        return True
    
    if sprint_state == 'closed' and sprint_overlaps_week:
        if sprint_end > week_end:
            return True
        if sprint_end >= week_start:
            return True
    
    return sprint_overlaps_week


def was_sprint_active_in_period(row, period_start, period_end, df_sprints=None):
    """
    Check if sprint was active during a period for monthly/period-based charts.
    
    Normalizes all dates to UTC. Checks if sprint dates overlap period using overlap logic (sprint_start <= period_end AND sprint_end >= period_start).
    
    
    Args:
        row: Issue row with sprint information
        period_start: Period start datetime (timezone-aware UTC)
        period_end: Period end datetime (timezone-aware UTC)
        df_sprints: Optional DataFrame with sprint details
    
    Returns:
        bool: True if sprint was active during the period
    """
    primary_sprint_id = row.get('Primary Sprint Id')
    
    if pd.isna(primary_sprint_id):
        return False
    
    if df_sprints is not None and not df_sprints.empty:
        sprint_row = df_sprints[df_sprints['Sprint Id'] == primary_sprint_id]
        if not sprint_row.empty:
            sprint_start = sprint_row.iloc[0].get('Sprint Start Date')
            sprint_end = sprint_row.iloc[0].get('Sprint End Date')
        else:
            sprint_start = row.get('Sprint Start Date')
            sprint_end = row.get('Sprint End Date')
    else:
        sprint_start = row.get('Sprint Start Date')
        sprint_end = row.get('Sprint End Date')
    
    if pd.isna(sprint_start) or pd.isna(sprint_end):
        return False
    
    sprint_start = _normalize_to_utc(sprint_start)
    sprint_end = _normalize_to_utc(sprint_end)
    period_start = _normalize_to_utc(period_start)
    period_end = _normalize_to_utc(period_end)
    
    return (sprint_start <= period_end) and (sprint_end >= period_start)


def get_active_sprint_ids_for_period(period_start, period_end, df_sprints):
    """
    Get list of active sprint IDs for a given period.
    
    Filters sprints where sprint_start <= period_end AND sprint_end >= period_start (overlap logic).
    Returns set of sprint IDs that were active during the period.
    
    
    Args:
        period_start: Period start datetime (timezone-aware UTC)
        period_end: Period end datetime (timezone-aware UTC)
        df_sprints: DataFrame with sprint details
    
    Returns:
        set: Set of active sprint IDs
    """
    if df_sprints is None or df_sprints.empty:
        return set()
    
    df_sprints = df_sprints.copy()
    df_sprints['Sprint Start Date'] = pd.to_datetime(df_sprints['Sprint Start Date'], utc=True, errors='coerce')
    df_sprints['Sprint End Date'] = pd.to_datetime(df_sprints['Sprint End Date'], utc=True, errors='coerce')
    
    period_start = _normalize_to_utc(period_start)
    period_end = _normalize_to_utc(period_end)
    
    active_sprints = df_sprints[
        (df_sprints['Sprint Start Date'] <= period_end) & 
        (df_sprints['Sprint End Date'] >= period_start)
    ]
    
    return set(active_sprints['Sprint Id'].tolist())


def _normalize_to_utc(dt):
    """
    Normalize datetime to UTC timezone-aware.
    
    Returns None for None/NaN input.
    
    
    Args:
        dt: Datetime object (can be None, timezone-aware, or naive)
    
    Returns:
        UTC timezone-aware datetime or None
    """
    if dt is None or pd.isna(dt):
        return None
    
    ts = pd.Timestamp(dt)
    
    if ts.tz is not None:
        return ts.tz_convert('UTC')
    else:
        return ts.tz_localize('UTC')
