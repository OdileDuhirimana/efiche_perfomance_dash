#!/usr/bin/env python3
"""
Script to export JIRA data to CSV for a specific date range.
Usage: python export_csv.py <start_date> <end_date> [output_file]
Date format: DD/MM/YYYY (e.g., 23/11/2025)
"""
import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_cache import get_cached_data
from app.services.filters import filter_by_overall_window


def parse_date(date_str, default_hour=0):
    """Parse date string in DD/MM/YYYY format to UTC datetime."""
    try:
        # Parse DD/MM/YYYY format
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        # Set to UTC timezone
        dt = dt.replace(hour=default_hour, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        return dt
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Expected DD/MM/YYYY format. Error: {e}")


def export_to_csv(start_date_str, end_date_str, output_file=None):
    """
    Export JIRA data to CSV for the specified date range.
    
    Args:
        start_date_str: Start date in DD/MM/YYYY format
        end_date_str: End date in DD/MM/YYYY format
        output_file: Optional output file path. If not provided, generates filename from dates.
    """
    print(f"=== Exporting CSV for date range: {start_date_str} to {end_date_str} ===")
    
    # Parse dates
    start_date = parse_date(start_date_str, default_hour=0)
    # End date should include the full day, so set to 23:59:59
    end_date = parse_date(end_date_str, default_hour=23)
    end_date = end_date.replace(minute=59, second=59, microsecond=999999)
    
    print(f"Parsed start date: {start_date}")
    print(f"Parsed end date: {end_date}")
    
    # Get cached data
    print("\nFetching data from cache...")
    df_issues, df_sprints = get_cached_data()
    print(f"Retrieved {len(df_issues)} issues from cache")
    
    # Filter by date range
    print(f"\nFiltering issues with activity between {start_date.date()} and {end_date.date()}...")
    filtered_df = filter_by_overall_window(df_issues, start_date, end_date)
    print(f"Found {len(filtered_df)} issues in the date range")
    
    if len(filtered_df) == 0:
        print("\n⚠️  No issues found for the specified date range.")
        return
    
    # Generate output filename if not provided
    if output_file is None:
        start_str = start_date_str.replace('/', '-')
        end_str = end_date_str.replace('/', '-')
        output_file = f"jira_export_{start_str}_to_{end_str}.csv"
    
    # Ensure CSV directory exists
    output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Export to CSV
    print(f"\nExporting to CSV: {output_file}")
    
    # Convert datetime columns to strings for CSV export
    df_export = filtered_df.copy()
    datetime_columns = df_export.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns
    for col in datetime_columns:
        df_export[col] = df_export[col].apply(
            lambda x: x.isoformat() if pd.notna(x) else ''
        )
    
    # Handle list/array columns
    for col in df_export.columns:
        if df_export[col].dtype == 'object':
            # Convert any remaining non-serializable objects to strings
            df_export[col] = df_export[col].astype(str).replace('nan', '')
    
    # Write to CSV
    df_export.to_csv(output_file, index=False, encoding='utf-8')
    
    file_size = os.path.getsize(output_file)
    print(f"✅ Successfully exported {len(filtered_df)} issues to {output_file}")
    print(f"   File size: {file_size / 1024:.2f} KB")
    print(f"   Columns: {len(df_export.columns)}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python export_csv.py <start_date> <end_date> [output_file]")
        print("Date format: DD/MM/YYYY (e.g., 23/11/2025)")
        sys.exit(1)
    
    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        export_to_csv(start_date_str, end_date_str, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

