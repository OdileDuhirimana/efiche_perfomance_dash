import pandas as pd
from datetime import datetime
from typing import Optional


def count_done_during_period(df: pd.DataFrame, period_start: datetime, period_end: datetime, 
                             resolved_col: str = 'Resolved', status_col: str = 'Status Category (Mapped)') -> int:
    """
    Count issues completed during a period using resolution date AND status.
    
    Logic: Filters issues where resolved date exists, falls within period, AND status category is 'Done'.
    Converts resolved column to datetime and checks for status column existence with fallback.
    Returns 0 if required columns don't exist.
    
    Use: Used in chart calculations and KPIs to count done activities in a specific period.
    
    Args:
        df: DataFrame with issues
        period_start: Period start datetime
        period_end: Period end datetime
        resolved_col: Column name for resolved date (default: 'Resolved')
        status_col: Column name for status category (default: 'Status Category (Mapped)')
    
    Returns:
        Count of issues done during period
    """
    if resolved_col not in df.columns:
        return 0
    
    df = df.copy()
    df[resolved_col] = pd.to_datetime(df[resolved_col], utc=True, errors='coerce')
    
    if status_col not in df.columns:
        if 'New Status Category' in df.columns:
            status_col = 'New Status Category'
        else:
            return 0
    
    done_mask = (
        df[resolved_col].notna() &
        (df[resolved_col] >= period_start) &
        (df[resolved_col] <= period_end) &
        (df[status_col] == 'Done')
    )
    
    return done_mask.sum()


def filter_done_issues(df: pd.DataFrame, period_start: datetime, period_end: datetime,
                       resolved_col: str = 'Resolved', status_col: str = 'Status Category (Mapped)') -> pd.DataFrame:
    """
    Filter DataFrame to only include issues done during period.
    
    Logic: Filters issues where resolved date exists, falls within period, AND status category is 'Done'.
    Converts resolved column to datetime and checks for status column existence with fallback.
    Returns empty DataFrame if required columns don't exist.
    
    Use: Used in chart calculations to get DataFrame of done issues for lead time and rework analysis.
    
    Args:
        df: DataFrame with issues
        period_start: Period start datetime
        period_end: Period end datetime
        resolved_col: Column name for resolved date (default: 'Resolved')
        status_col: Column name for status category (default: 'Status Category (Mapped)')
    
    Returns:
        Filtered DataFrame with only done issues
    """
    if resolved_col not in df.columns:
        return pd.DataFrame()
    
    df = df.copy()
    df[resolved_col] = pd.to_datetime(df[resolved_col], utc=True, errors='coerce')
    
    if status_col not in df.columns:
        if 'New Status Category' in df.columns:
            status_col = 'New Status Category'
        else:
            return pd.DataFrame()
    
    done_mask = (
        df[resolved_col].notna() &
        (df[resolved_col] >= period_start) &
        (df[resolved_col] <= period_end) &
        (df[status_col] == 'Done')
    )
    
    return df[done_mask].copy()
