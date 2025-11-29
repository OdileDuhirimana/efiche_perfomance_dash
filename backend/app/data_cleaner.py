"""Data cleaning and preparation module."""
import pandas as pd
import datetime
import numpy as np
from app.services.changelog_processor import map_status_to_category


def get_week_date_range(week_str):
    """
    Convert week string to date range.
    
    using datetime.strptime with ISO week format. Returns formatted date range string.
    
    
    Args:
        week_str: Week string in format 'YYYY-WW' (e.g., '2024-15')
    
    Returns:
        Formatted date range string (e.g., '01 Apr 2024 - 07 Apr 2024') or None
    """
    if pd.isna(week_str):
        return None
    try:
        year, week_num = map(int, week_str.split('-'))
        start_of_week = datetime.datetime.strptime(f'{year}-W{week_num:02d}-1', "%Y-W%W-%w").date()
        end_of_week = start_of_week + datetime.timedelta(days=6)
        return f"{start_of_week.strftime('%d %b %Y')} - {end_of_week.strftime('%d %b %Y')}"
    except ValueError:
        return None


def clean_jira_data(df):
    """
    Clean and prepare Jira data for dashboard.
    
    without keys. Fills missing assignees with 'Unassigned'. Converts all date columns to UTC datetime.
    Adds 'Status Category (Mapped)' by mapping Status using map_status_to_category. Calculates Lead Time (Days)
    as (Resolved - Created) in days. Converts numpy types to native Python types. Validates critical columns
    and changelog data availability.
    
    data for chart calculations.
    
    Args:
        df: Raw DataFrame from JIRA API
    
    Returns:
        Cleaned DataFrame with standardized columns, UTC dates, and calculated fields
    """
    print("Starting data cleaning...")
    
    core_columns = [
        'Issue key',
        'Summary',
        'Issue Type',
        'Status',
        'Status Category',
        'Created',
        'Updated',
        'Resolved',
        'Status Category Changed',
        'Assignee',
    ]
    
    sprint_columns = [
        'Sprint',
        'Sprint Id',
        'Sprint State',
        'Sprint Start Date',
        'Sprint End Date',
        'Sprint Complete Date',
        'Primary Sprint Id',
        'Sprint State (Full)',
    ]
    
    changelog_columns = [
        'Status Transitions',
        'Num Transitions',
        'QA Entered Count',
        'QA Failed Count',
        'Has Rework',
        'Rework Count',
        'Lead Time (Changelog)',
        'Time In Progress (Changelog)',
        'Time In QA (Changelog)',
        'Time To First Progress',
    ]
    
    metadata_columns = [
        'Project name',
    ]
    
    relevant_columns = core_columns + sprint_columns + changelog_columns + metadata_columns
    
    columns_to_keep = [col for col in relevant_columns if col in df.columns]
    missing_columns = [col for col in relevant_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Warning: Missing columns: {', '.join(missing_columns)}")
    
    if not columns_to_keep:
        print("Warning: No relevant columns found, returning empty DataFrame")
        return pd.DataFrame(columns=relevant_columns)
    
    cleaned_df = df[columns_to_keep].copy()
    
    print("Performing data cleaning...")
    
    cleaned_df = cleaned_df.dropna(subset=['Issue key']).copy()
    
    cleaned_df['Assignee'] = cleaned_df['Assignee'].fillna('Unassigned')
    
    date_columns = ['Created', 'Updated', 'Resolved', 'Status Category Changed']
    for col in date_columns:
        if col in cleaned_df.columns:
            if pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                if cleaned_df[col].dt.tz is None:
                    cleaned_df[col] = cleaned_df[col].dt.tz_localize('UTC')
                else:
                    cleaned_df[col] = cleaned_df[col].dt.tz_convert('UTC')
            else:
                try:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], format='ISO8601', utc=True, errors='coerce')
                except:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], utc=True, errors='coerce')
    
    sprint_date_columns = ['Sprint Start Date', 'Sprint End Date', 'Sprint Complete Date']
    for col in sprint_date_columns:
        if col in cleaned_df.columns:
            if pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                if cleaned_df[col].dt.tz is None:
                    cleaned_df[col] = cleaned_df[col].dt.tz_localize('UTC')
                else:
                    cleaned_df[col] = cleaned_df[col].dt.tz_convert('UTC')
            else:
                try:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], format='ISO8601', utc=True, errors='coerce')
                except:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], utc=True, errors='coerce')
    
    print("Adding Status Category (Mapped)...")
    if 'Status' in cleaned_df.columns:
        cleaned_df['Status Category (Mapped)'] = cleaned_df['Status'].apply(
            lambda status: map_status_to_category(status)
        )
    else:
        print("Warning: 'Status' column not found, cannot add Status Category (Mapped)")
        cleaned_df['Status Category (Mapped)'] = 'Not Done'
    
    print("Calculating Lead Time...")
    if 'Resolved' in cleaned_df.columns and 'Created' in cleaned_df.columns:
        cleaned_df['Lead Time (Days)'] = (
            cleaned_df['Resolved'] - cleaned_df['Created']
        ).dt.total_seconds() / (60 * 60 * 24)
        cleaned_df['Lead Time (Days)'].fillna(0, inplace=True)
        cleaned_df['Lead Time (Days)'] = cleaned_df['Lead Time (Days)'].round(2)
    
    print("Converting numpy types...")
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype.name.startswith('int'):
            cleaned_df[col] = cleaned_df[col].astype('Int64')
            cleaned_df[col] = cleaned_df[col].apply(lambda x: int(x) if pd.notna(x) else None)
        elif cleaned_df[col].dtype.name.startswith('float'):
            cleaned_df[col] = cleaned_df[col].astype('float64')
    
    if 'Primary Sprint Id' in cleaned_df.columns:
        cleaned_df['Primary Sprint Id'] = cleaned_df['Primary Sprint Id'].apply(
            lambda x: int(x) if pd.notna(x) else None
        )
    
    critical_columns = ['Issue key', 'Created', 'Resolved', 'Status Category (Mapped)']
    missing_critical = [col for col in critical_columns if col not in cleaned_df.columns]
    if missing_critical:
        print(f"ERROR: Missing critical columns: {', '.join(missing_critical)}")
    
    if 'Status Transitions' in cleaned_df.columns:
        transitions_count = cleaned_df['Status Transitions'].notna().sum()
        print(f"Changelog data: {transitions_count}/{len(cleaned_df)} issues have status transitions")
    else:
        print("WARNING: 'Status Transitions' column not found - changelog-based calculations will use fallback")
    
    print("Validating dates...")
    for col in date_columns + sprint_date_columns:
        if col in cleaned_df.columns:
            if not pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], utc=True, errors='coerce')
            if pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                if cleaned_df[col].dt.tz is None:
                    cleaned_df[col] = cleaned_df[col].dt.tz_localize('UTC')
                elif str(cleaned_df[col].dt.tz) != 'UTC':
                    cleaned_df[col] = cleaned_df[col].dt.tz_convert('UTC')
    
    print(f"Data cleaning complete. {len(cleaned_df)} records ready for dashboard")
    return cleaned_df


def prepare_dashboard_data(df):
    """
    Prepare data for dashboard display.
    
    Ensures 'Status Category (Mapped)' exists (adds if missing for backward compatibility). Returns empty DataFrame
    with required columns if input is empty.
    
    
    Args:
        df: Cleaned DataFrame from clean_jira_data
    
    Returns:
        DataFrame with added week labels and date ranges for display
    """
    print("Preparing dashboard data...")
    
    if df.empty:
        print("Warning: DataFrame is empty, returning empty DataFrame with required columns")
        empty_df = pd.DataFrame(columns=[
            'Issue key', 'Summary', 'Issue Type', 'Status', 'Status Category',
            'Created', 'Updated', 'Resolved', 'Status Category Changed',
            'Assignee', 'Sprint', 'Project name', 'Lead Time (Days)',
            'Resolved Week', 'Created Week', 'Updated Week',
            'Status Category (Mapped)',
            'Resolved Date Range', 'Created Date Range', 'Updated Date Range'
        ])
        return empty_df
    
    if 'Resolved' in df.columns:
        df['Resolved Week'] = df['Resolved'].dt.strftime('%Y-%W')
        df['Resolved Date Range'] = df['Resolved Week'].apply(get_week_date_range)
    
    if 'Created' in df.columns:
        df['Created Week'] = df['Created'].dt.strftime('%Y-%W')
        df['Created Date Range'] = df['Created Week'].apply(get_week_date_range)
    
    if 'Updated' in df.columns:
        df['Updated Week'] = df['Updated'].dt.strftime('%Y-%W')
        df['Updated Date Range'] = df['Updated Week'].apply(get_week_date_range)
    
    if 'Status Category (Mapped)' not in df.columns and 'Status' in df.columns:
        df['Status Category (Mapped)'] = df['Status'].apply(map_status_to_category)
    
    return df