#!/usr/bin/env python3
"""
Get execution success data with corrected logic to include "Ready for deployment" tasks.
Usage: python get_execution_success_corrected.py <start_date> <end_date> [output_file]
Date format: DD/MM/YYYY (e.g., 23/11/2025)
"""
import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_cache import get_cached_data
from app.services.filters import filter_planned_activities, apply_standard_filters


def parse_date(date_str, default_hour=0):
    """Parse date string in DD/MM/YYYY format to UTC datetime."""
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        dt = dt.replace(hour=default_hour, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        return dt
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Expected DD/MM/YYYY format. Error: {e}")


def normalize_date_to_utc(dt):
    """Normalize a date/datetime to UTC timezone-aware datetime."""
    if dt is None:
        return None
    ts = pd.Timestamp(dt)
    if ts.tz is not None:
        return ts.tz_convert('UTC').to_pydatetime()
    else:
        return ts.tz_localize('UTC').to_pydatetime()


def count_done_and_ready_for_deployment(df, period_start, period_end):
    """
    Count tasks that are Done OR Ready for Deployment.
    Includes tasks with resolved dates in period OR Ready for deployment status.
    """
    df = df.copy()
    
    # Parse dates
    if 'Resolved' in df.columns:
        df['Resolved'] = pd.to_datetime(df['Resolved'], utc=True, errors='coerce')
    if 'Updated' in df.columns:
        df['Updated'] = pd.to_datetime(df['Updated'], utc=True, errors='coerce')
    
    status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in df.columns else 'New Status Category'
    if status_col not in df.columns:
        status_col = 'Status Category'
    
    # Count tasks with resolved dates in period and status Done
    done_with_resolved = (
        df['Resolved'].notna() &
        (df['Resolved'] >= period_start) &
        (df['Resolved'] <= period_end) &
        (df[status_col] == 'Done')
    )
    
    # Count tasks with "Ready for deployment" status (even without resolved dates)
    ready_for_deployment = df['Status'].str.contains('Ready', case=False, na=False)
    
    # Combine both conditions (avoid double counting)
    completed = done_with_resolved | ready_for_deployment
    
    return completed.sum()


def get_execution_success_corrected(start_date_str, end_date_str, output_file=None):
    """
    Get execution success data with corrected logic to include Ready for Deployment.
    """
    print(f"=== Getting Execution Success (CORRECTED) for date range: {start_date_str} to {end_date_str} ===\n")
    
    # Parse dates
    start_date = parse_date(start_date_str, default_hour=0)
    end_date = parse_date(end_date_str, default_hour=23)
    end_date = end_date.replace(minute=59, second=59, microsecond=999999)
    
    start_date_utc = normalize_date_to_utc(start_date)
    end_date_utc = normalize_date_to_utc(end_date)
    
    print(f"Parsed start date: {start_date_utc}")
    print(f"Parsed end date: {end_date_utc}")
    
    # Get cached data
    print("\nFetching data from cache...")
    df_issues, df_sprints = get_cached_data()
    print(f"Retrieved {len(df_issues)} issues from cache")
    
    # Apply standard filters
    print(f"\nFiltering issues for the date range...")
    filtered_df = apply_standard_filters(df_issues, start_date=start_date_utc, end_date=end_date_utc)
    print(f"Found {len(filtered_df)} issues in the date range")
    
    # Filter planned activities
    planned_activities = filter_planned_activities(filtered_df, start_date_utc, end_date_utc)
    
    if 'Assignee' not in planned_activities.columns:
        print("\n⚠️  No assignee column found.")
        return
    
    assigned_issues = planned_activities[planned_activities['Assignee'].notna()].copy()
    
    print("\nCalculating execution success by assignee (including Ready for Deployment)...")
    
    assignee_success = []
    
    for assignee in assigned_issues['Assignee'].unique():
        assignee_tasks = assigned_issues[assigned_issues['Assignee'] == assignee]
        total_assigned = len(assignee_tasks)
        
        # Count done AND ready for deployment
        done_count = count_done_and_ready_for_deployment(
            assignee_tasks,
            start_date_utc,
            end_date_utc
        )
        
        success_rate = (done_count / total_assigned * 100) if total_assigned > 0 else 0
        
        assignee_success.append({
            'Assignee': assignee,
            'Total Assigned': total_assigned,
            'Done/Ready for Deployment': done_count,
            'Success Rate (%)': round(success_rate, 1)
        })
    
    execution_success_df = pd.DataFrame(assignee_success)
    execution_success_df = execution_success_df.sort_values('Success Rate (%)', ascending=False).reset_index(drop=True)
    
    if len(execution_success_df) == 0:
        print("\n⚠️  No execution success data found.")
        return
    
    print(f"\nFound execution success data for {len(execution_success_df)} assignees")
    
    # Display results
    print("\n" + "=" * 80)
    print("EXECUTION SUCCESS BY ASSIGNEE (CORRECTED - Includes Ready for Deployment)")
    print("=" * 80)
    print(f"{'Assignee':<40} {'Total Assigned':>15} {'Done/Ready':>15} {'Success Rate':>15}")
    print("-" * 80)
    
    for _, row in execution_success_df.iterrows():
        assignee = str(row['Assignee'])
        total = int(row['Total Assigned'])
        done = int(row['Done/Ready for Deployment'])
        success_rate = float(row['Success Rate (%)'])
        print(f"{assignee:<40} {total:>15} {done:>15} {success_rate:>14.1f}%")
    
    print("-" * 80)
    print("=" * 80)
    
    # Generate output filename if not provided
    if output_file is None:
        start_str = start_date_str.replace('/', '-')
        end_str = end_date_str.replace('/', '-')
        output_file = f"execution_success_corrected_{start_str}_to_{end_str}.csv"
    
    # Export to CSV
    print(f"\nExporting to CSV: {output_file}")
    execution_success_df.to_csv(output_file, index=False, encoding='utf-8')
    
    file_size = os.path.getsize(output_file)
    print(f"✅ Successfully exported corrected execution success data to {output_file}")
    print(f"   File size: {file_size / 1024:.2f} KB")
    
    # Show Placide's breakdown specifically
    placide_row = execution_success_df[execution_success_df['Assignee'] == 'Placide']
    if len(placide_row) > 0:
        print(f"\n📊 Placide's Corrected Metrics:")
        print(f"   Total Assigned: {placide_row.iloc[0]['Total Assigned']}")
        print(f"   Done/Ready for Deployment: {placide_row.iloc[0]['Done/Ready for Deployment']}")
        print(f"   Success Rate: {placide_row.iloc[0]['Success Rate (%)']:.1f}%")
        print(f"   (This should now match your expectation of 4 completed tasks)")
    
    return execution_success_df

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python get_execution_success_corrected.py <start_date> <end_date> [output_file]")
        print("Date format: DD/MM/YYYY (e.g., 23/11/2025)")
        sys.exit(1)
    
    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        result = get_execution_success_corrected(start_date_str, end_date_str, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

