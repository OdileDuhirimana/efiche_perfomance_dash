#!/usr/bin/env python3
"""
Debug script to understand why Placide shows 33.3% instead of expected value.
"""
import pandas as pd
from datetime import datetime, timezone

# Read the CSV
df = pd.read_csv('jira_export_23-11-2025_to_27-11-2025.csv')

# Filter Placide's tasks
placide = df[df['Assignee'] == 'Placide'].copy()

# Parse dates
placide['Created'] = pd.to_datetime(placide['Created'], utc=True, errors='coerce')
placide['Resolved'] = pd.to_datetime(placide['Resolved'], utc=True, errors='coerce')
placide['Updated'] = pd.to_datetime(placide['Updated'], utc=True, errors='coerce')

period_start = datetime(2025, 11, 23, 0, 0, 0, tzinfo=timezone.utc)
period_end = datetime(2025, 11, 27, 23, 59, 59, tzinfo=timezone.utc)

print("=" * 100)
print("PLACIDE'S TASKS ANALYSIS")
print("=" * 100)
print(f"\nPeriod: {period_start.date()} to {period_end.date()}\n")

# Check which tasks are "planned activities" (Created OR Updated in period)
planned_mask = (
    (placide['Created'] >= period_start) & (placide['Created'] <= period_end) |
    (placide['Updated'] >= period_start) & (placide['Updated'] <= period_end)
)
planned_tasks = placide[planned_mask]

print(f"Total Planned Activities (Created OR Updated in period): {len(planned_tasks)}")
print(f"\nPlanned Tasks:")
print("-" * 100)

for idx, row in planned_tasks.iterrows():
    resolved_in_period = pd.notna(row['Resolved']) and period_start <= row['Resolved'] <= period_end
    status_category = row.get('Status Category (Mapped)', row.get('Status Category', 'N/A'))
    
    print(f"\n{row['Issue key']:15} | Status: {str(row['Status']):25} | Category: {str(status_category):15}")
    print(f"                 | Created: {str(row['Created'].date()) if pd.notna(row['Created']) else 'N/A':12} | Updated: {str(row['Updated'].date()) if pd.notna(row['Updated']) else 'N/A':12}")
    print(f"                 | Resolved: {str(row['Resolved'].date()) if pd.notna(row['Resolved']) else 'N/A':12} | Resolved in period: {resolved_in_period}")
    print(f"                 | Summary: {str(row['Summary'])[:70]}")

print("\n" + "=" * 100)
print("COUNTING 'DONE' TASKS")
print("=" * 100)

# Check what count_done_during_period would count
status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in planned_tasks.columns else 'New Status Category'
if status_col not in planned_tasks.columns:
    status_col = 'Status Category'

done_mask = (
    planned_tasks['Resolved'].notna() &
    (planned_tasks['Resolved'] >= period_start) &
    (planned_tasks['Resolved'] <= period_end) &
    (planned_tasks[status_col] == 'Done')
)

done_tasks = planned_tasks[done_mask]
print(f"\nTasks counted as 'Done': {len(done_tasks)}")
for idx, row in done_tasks.iterrows():
    print(f"  - {row['Issue key']}: {row['Status']} (Resolved: {row['Resolved'].date()})")

# Check Ready for Deployment tasks
ready_for_deployment = planned_tasks[planned_tasks['Status'].str.contains('Ready', case=False, na=False)]
print(f"\nTasks with 'Ready for deployment' status: {len(ready_for_deployment)}")
for idx, row in ready_for_deployment.iterrows():
    has_resolved = pd.notna(row['Resolved'])
    resolved_in_period = has_resolved and period_start <= row['Resolved'] <= period_end
    print(f"  - {row['Issue key']}: {row['Status']} (Resolved: {row['Resolved'].date() if has_resolved else 'N/A'}, In period: {resolved_in_period})")

# Count all "Done" status regardless of resolved date
all_done_status = planned_tasks[planned_tasks['Status'] == 'Done']
print(f"\nTasks with 'Done' status (regardless of resolved date): {len(all_done_status)}")
for idx, row in all_done_status.iterrows():
    has_resolved = pd.notna(row['Resolved'])
    resolved_in_period = has_resolved and period_start <= row['Resolved'] <= period_end
    print(f"  - {row['Issue key']}: Resolved: {row['Resolved'].date() if has_resolved else 'N/A'}, In period: {resolved_in_period}")

print("\n" + "=" * 100)
print("CALCULATION EXPLANATION")
print("=" * 100)
print(f"""
The execution success calculation:
1. Filters for 'planned activities' (tasks Created OR Updated in period): {len(planned_tasks)} tasks
2. Counts 'Done' tasks where:
   - Status Category = 'Done'
   - Resolved date is within the period
   - Result: {len(done_tasks)} tasks

Current calculation: {len(done_tasks)} / {len(planned_tasks)} = {(len(done_tasks) / len(planned_tasks) * 100) if len(planned_tasks) > 0 else 0:.1f}%

ISSUE IDENTIFIED:
- The column says 'Done/Ready for Deployment' but only counts tasks with status 'Done' AND resolved dates
- Tasks with status 'Ready for deployment' are NOT counted (even though the column name suggests they should be)
- INTEGRAT-89 has status 'Ready for deployment' but no resolved date, so it's not counted

If we count all 'Done' + 'Ready for deployment' status tasks: {len(all_done_status) + len(ready_for_deployment)}
Success rate would be: {(len(all_done_status) + len(ready_for_deployment)) / len(planned_tasks) * 100 if len(planned_tasks) > 0 else 0:.1f}%
""")

