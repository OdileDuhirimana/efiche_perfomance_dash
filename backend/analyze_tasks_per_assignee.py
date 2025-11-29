#!/usr/bin/env python3
"""
Analyze tasks per assignee from JIRA export CSV.
"""
import pandas as pd
import sys
import os

def analyze_tasks_per_assignee(csv_file):
    """
    Analyze and display tasks per assignee from the CSV file.
    """
    print(f"=== Analyzing tasks per assignee from {csv_file} ===\n")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    print(f"Total issues in CSV: {len(df)}\n")
    
    # Group by assignee and count tasks
    assignee_counts = df['Assignee'].value_counts().sort_values(ascending=False)
    
    print("=" * 60)
    print("TASKS PER ASSIGNEE")
    print("=" * 60)
    print(f"{'Assignee':<40} {'Task Count':>10}")
    print("-" * 60)
    
    for assignee, count in assignee_counts.items():
        print(f"{str(assignee):<40} {count:>10}")
    
    print("-" * 60)
    print(f"{'TOTAL':<40} {len(df):>10}")
    print("=" * 60)
    
    # Additional breakdown: Tasks by status per assignee
    print("\n" + "=" * 60)
    print("BREAKDOWN BY STATUS PER ASSIGNEE")
    print("=" * 60)
    
    # Create a pivot table
    status_by_assignee = pd.crosstab(df['Assignee'], df['Status'], margins=True)
    print(status_by_assignee.to_string())
    
    # Also show by Issue Type
    print("\n" + "=" * 60)
    print("BREAKDOWN BY ISSUE TYPE PER ASSIGNEE")
    print("=" * 60)
    
    type_by_assignee = pd.crosstab(df['Assignee'], df['Issue Type'], margins=True)
    print(type_by_assignee.to_string())
    
    # Export to CSV
    output_file = csv_file.replace('.csv', '_tasks_per_assignee.csv')
    
    # Create summary data
    summary_data = []
    for assignee, count in assignee_counts.items():
        assignee_df = df[df['Assignee'] == assignee]
        summary_data.append({
            'Assignee': assignee,
            'Total Tasks': count,
            'Done': len(assignee_df[assignee_df['Status'] == 'Done']),
            'In Progress': len(assignee_df[assignee_df['Status'] == 'In Progress']),
            'To Do': len(assignee_df[assignee_df['Status'] == 'To Do']),
            'Ready for deployment': len(assignee_df[assignee_df['Status'] == 'Ready for deployment']),
            'Tasks': len(assignee_df[assignee_df['Issue Type'] == 'Task']),
            'Bugs': len(assignee_df[assignee_df['Issue Type'] == 'Bug']),
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Summary exported to: {output_file}")
    
    return summary_df

if __name__ == '__main__':
    csv_file = 'jira_export_23-11-2025_to_27-11-2025.csv'
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found!")
        sys.exit(1)
    
    try:
        summary = analyze_tasks_per_assignee(csv_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

