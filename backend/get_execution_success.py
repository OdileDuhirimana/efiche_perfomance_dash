#!/usr/bin/env python3
"""
Get execution success data for a specific date range.
This shows completion rates per assignee - what should appear on the dashboard.
Usage: python get_execution_success.py <start_date> <end_date> [output_file]
Date format: DD/MM/YYYY (e.g., 23/11/2025)
"""
import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_cache import get_cached_data
from app.services.chart_calculations import calculate_execution_success_by_assignee
from app.services.filters import apply_standard_filters


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


def get_execution_success_data(start_date_str, end_date_str, output_file=None):
    """
    Get execution success data for the specified date range.
    
    Args:
        start_date_str: Start date in DD/MM/YYYY format
        end_date_str: End date in DD/MM/YYYY format
        output_file: Optional output file path. If not provided, generates filename from dates.
    """
    print(f"=== Getting Execution Success data for date range: {start_date_str} to {end_date_str} ===\n")
    
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
    
    # Apply standard filters (this includes date range filtering)
    print(f"\nFiltering issues for the date range...")
    filtered_df = apply_standard_filters(df_issues, start_date=start_date, end_date=end_date)
    print(f"Found {len(filtered_df)} issues in the date range")
    
    # Calculate execution success
    print("\nCalculating execution success by assignee...")
    execution_success_df = calculate_execution_success_by_assignee(
        filtered_df, 
        start_date, 
        end_date, 
        df_sprints=df_sprints
    )
    
    if len(execution_success_df) == 0:
        print("\n⚠️  No execution success data found for the specified date range.")
        print("   This might mean no planned activities were assigned to team members in this period.")
        return
    
    print(f"\nFound execution success data for {len(execution_success_df)} assignees")
    
    # Display results
    print("\n" + "=" * 80)
    print("EXECUTION SUCCESS BY ASSIGNEE")
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
        output_file = f"execution_success_{start_str}_to_{end_str}.csv"
    
    # Ensure CSV directory exists
    output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Export to CSV
    print(f"\nExporting to CSV: {output_file}")
    execution_success_df.to_csv(output_file, index=False, encoding='utf-8')
    
    file_size = os.path.getsize(output_file)
    print(f"✅ Successfully exported execution success data to {output_file}")
    print(f"   File size: {file_size / 1024:.2f} KB")
    print(f"   Assignees: {len(execution_success_df)}")
    
    # Additional statistics
    if len(execution_success_df) > 0:
        avg_success_rate = execution_success_df['Success Rate (%)'].mean()
        total_assigned = execution_success_df['Total Assigned'].sum()
        total_done = execution_success_df['Done/Ready for Deployment'].sum()
        overall_success = (total_done / total_assigned * 100) if total_assigned > 0 else 0
        
        print(f"\n📊 Summary Statistics:")
        print(f"   Average Success Rate: {avg_success_rate:.1f}%")
        print(f"   Overall Success Rate: {overall_success:.1f}% ({total_done}/{total_assigned})")
        print(f"   Target: ≥75% (Executive Success target)")
        
        above_target = execution_success_df[execution_success_df['Success Rate (%)'] >= 75]
        below_target = execution_success_df[execution_success_df['Success Rate (%)'] < 75]
        print(f"\n   Assignees meeting target (≥75%): {len(above_target)}/{len(execution_success_df)}")
        if len(below_target) > 0:
            print(f"   Assignees below target: {len(below_target)}")
            print(f"      {', '.join(below_target['Assignee'].tolist())}")
    
    return execution_success_df

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python get_execution_success.py <start_date> <end_date> [output_file]")
        print("Date format: DD/MM/YYYY (e.g., 23/11/2025)")
        sys.exit(1)
    
    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        result = get_execution_success_data(start_date_str, end_date_str, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

