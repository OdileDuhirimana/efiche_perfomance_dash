"""Chart calculation services."""
import pandas as pd
import json
from datetime import datetime, timedelta, timezone
from app.services.changelog_processor import (
    get_status_at_date,
    is_in_progress_at_date,
    was_completed_during_period,
    extract_status_transitions,
    calculate_lead_time_from_transitions,
    analyze_rework_patterns,
    analyze_qa_transitions,
    is_active_status
)
from app.services.resolution_utils import (
    count_done_during_period
)
from app.services.filters import filter_planned_activities, filter_carry_over_activities
from app.services.data_accuracy import (
    ensure_changelog_usage
)
from app.services.transitions_helper import (
    pre_parse_transitions
)


def _normalize_date_to_utc(dt):
    """Normalize a date/datetime to UTC timezone-aware datetime."""
    if dt is None:
        return None

    ts = pd.Timestamp(dt)

    if ts.tz is not None:
        return ts.tz_convert('UTC').to_pydatetime()
    else:
        return ts.tz_localize('UTC').to_pydatetime()


DONE_STATUSES = ['Resolved', 'Done', 'Ready for Deployment', 'Ready For Deployment',
                 'READY FOR DEPLOYMENT', 'Ready for deployment', 'Deployed',
                 'IN REVIEW', 'In Review', 'QA', 'Bug Fix', 'BUG FIX', 'Bug FIX']
IN_PROGRESS_STATUSES = ['In Progress', 'IN PROGRESS', 'In progress', 'In Progress',
                        'Active', 'ACTIVE', 'Development', 'DEVELOPMENT', 'Doing', 'DOING']


def calculate_weekly_planned_vs_done(df_issues, start_date, num_weeks=12, df_sprints=None, period_end=None):
    """Calculate weekly planned vs done data. Expects pre-filtered df_issues."""
    start_date = _normalize_date_to_utc(start_date)
    weeks_data = []
    current_date = start_date
    
    if period_end:
        period_end = _normalize_date_to_utc(period_end)
        week_num = 1
        
        while current_date <= period_end:
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)
            
            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            
            if period_end <= week_end:
                break
            
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)
            week_num += 1
    else:
        for week_num in range(1, num_weeks + 1):
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)

            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)

    weekly_results = []

    status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in df_issues.columns else 'New Status Category'

    for week_info in weeks_data:
        week_start = week_info['Start Date']
        week_end = week_info['End Date']
        effective_week_end = week_end
        if period_end:
            effective_week_end = min(week_end, period_end)
        week_issues = df_issues.copy()

        planned_activities = filter_planned_activities(week_issues, week_start, effective_week_end)
        planned = len(planned_activities)

        done = count_done_during_period(
            week_issues,
            week_start,
            effective_week_end,
            resolved_col='Resolved',
            status_col=status_col
        )

        weekly_results.append({
            'Week': week_info['Week'],
            'Week Label': week_info['Week Label'],
            'Week Number': week_info['Week Number'],
            'Start Date': week_start,
            'End Date': week_end,
            'Planned': planned,
            'Done': done,
            'Completion Rate': round((done / planned * 100) if planned > 0 else 0, 1)
        })

    result_df = pd.DataFrame(weekly_results)
    return result_df


def calculate_weekly_flow(df_issues, start_date, num_weeks=12, df_sprints=None, period_end=None):
    """Calculate weekly flow data (Done, In Progress, Carry Over). Expects pre-filtered df_issues."""
    df_issues, usage_stats = ensure_changelog_usage(df_issues, 'weekly_flow')


    start_date = _normalize_date_to_utc(start_date)
    weeks_data = []
    current_date = start_date
    
    if period_end:
        period_end = _normalize_date_to_utc(period_end)
        week_num = 1
        
        while current_date <= period_end:
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)
            
            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            
            if period_end <= week_end:
                break
            
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)
            week_num += 1
    else:
        for week_num in range(1, num_weeks + 1):
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)

            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)


    weekly_results = []
    previous_week_active_issues = set()


    status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in df_issues.columns else 'New Status Category'

    for week_idx, week_info in enumerate(weeks_data):
        week_start = week_info['Start Date']
        week_end = week_info['End Date']
        effective_week_end = week_end
        if period_end:
            effective_week_end = min(week_end, period_end)
        week_issues = df_issues.copy()

        issue_key_col = 'Issue key' if 'Issue key' in week_issues.columns else 'Key'
        if issue_key_col in week_issues.columns:
            current_week_issue_keys = set(week_issues[issue_key_col].tolist())
        else:
            current_week_issue_keys = set()


        done = count_done_during_period(
            week_issues,
            week_start,
            effective_week_end,
            resolved_col='Resolved',
            status_col=status_col
        )


        carry_over = filter_carry_over_activities(week_issues, week_start, effective_week_end)
        carry_over_count = len(carry_over)

        in_progress_count = 0
        if 'Status Transitions' in week_issues.columns:
            week_issues = pre_parse_transitions(week_issues)
            for _, row in week_issues.iterrows():

                resolved_date = row.get('Resolved')
                resolved_dt = None
                if resolved_date:
                    resolved_dt = pd.to_datetime(resolved_date, utc=True, errors='coerce')


                if resolved_dt is not None and not pd.isna(resolved_dt):
                    if week_start <= resolved_dt <= effective_week_end:
                        continue


                transitions = row.get('_parsed_transitions', [])
                if transitions:
                    try:

                        status_at_end = get_status_at_date(transitions, effective_week_end)


                        if status_at_end:
                            status_lower = str(status_at_end).lower()
                            if 'in progress' in status_lower or 'development' in status_lower or 'dev' in status_lower:
                                in_progress_count += 1
                    except:
                        pass
        else:

            week_issues['Resolved'] = pd.to_datetime(week_issues['Resolved'], utc=True, errors='coerce')
            not_resolved = week_issues[
                (week_issues['Resolved'].isna()) |
                (week_issues['Resolved'] > effective_week_end)
            ]

            if 'Status Category (Mapped)' in not_resolved.columns:
                in_progress_count = (not_resolved['Status Category (Mapped)'] == 'In Progress').sum()
            elif 'Status' in not_resolved.columns:
                status_lower = not_resolved['Status'].astype(str).str.lower()
                in_progress_count = status_lower.str.contains('in progress|development|dev', case=False, na=False).sum()

        week_issues['Created'] = pd.to_datetime(week_issues['Created'], utc=True, errors='coerce')
        new_issues = week_issues[
            (week_issues['Created'] >= week_start) &
            (week_issues['Created'] <= effective_week_end) &
            (week_issues['Created'].notna())
        ]
        new_issues_count = len(new_issues)


        weekly_results.append({
            'Week': week_info['Week'],
            'Week Label': week_info['Week Label'],
            'Week Number': week_info['Week Number'],
            'Start Date': week_start,
            'End Date': week_end,
            'Done': done,
            'In Progress': in_progress_count,
            'Carry Over': carry_over_count,
            'New Issues': new_issues_count,
            'Total Active': len(week_issues)
        })



        week_issues['Resolved'] = pd.to_datetime(week_issues['Resolved'], utc=True, errors='coerce')
        active_issues = week_issues[week_issues['Resolved'].isna()]
        if issue_key_col in active_issues.columns:
            previous_week_active_issues = set(active_issues[issue_key_col].tolist())
        else:
            previous_week_active_issues = current_week_issue_keys

    result_df = pd.DataFrame(weekly_results)
    return result_df


def calculate_weekly_lead_time(df_issues, start_date, num_weeks=12, df_sprints=None, period_end=None):
    """
    Calculate average lead time per week.
    PRIORITIZES CHANGELOG DATA for maximum accuracy.
    Uses changelog-based lead time when available (starts from "To Do" transition).

    Args:
        df_issues: Issues DataFrame
        start_date: Start date for analysis
        num_weeks: Number of weeks to analyze (default 12, ignored if period_end is provided)
        df_sprints: Optional sprint DataFrame
        period_end: Optional end date - if provided, includes all weeks that overlap with period

    Returns:
        DataFrame with columns: Week, Week Label, Average Lead Time (days), Resolved Issues Count, Overall Average
    """

    df_issues, usage_stats = ensure_changelog_usage(df_issues, 'lead_time')


    start_date = _normalize_date_to_utc(start_date)
    weeks_data = []
    current_date = start_date
    
    if period_end:
        period_end = _normalize_date_to_utc(period_end)
        week_num = 1
        
        while current_date <= period_end:
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)
            
            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            
            if period_end <= week_end:
                break
            
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)
            week_num += 1
    else:
        for week_num in range(1, num_weeks + 1):
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)

            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)


    df_issues = df_issues.copy()
    df_issues['Created'] = pd.to_datetime(df_issues['Created'], utc=True, errors='coerce')
    df_issues['Resolved'] = pd.to_datetime(df_issues['Resolved'], utc=True, errors='coerce')


    status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in df_issues.columns else 'New Status Category'


    weekly_lead_time = []
    all_lead_times = []

    for week_info in weeks_data:
        week_start = week_info['Start Date']
        week_end = week_info['End Date']
        effective_week_end = week_end
        if period_end:
            effective_week_end = min(week_end, period_end)
        week_issues = df_issues.copy()


        from app.services.resolution_utils import filter_done_issues
        week_resolved = filter_done_issues(
            week_issues,
            week_start,
            effective_week_end,
            resolved_col='Resolved',
            status_col=status_col
        )



        week_resolved['Created'] = pd.to_datetime(week_resolved['Created'], utc=True, errors='coerce')
        week_resolved['Resolved'] = pd.to_datetime(week_resolved['Resolved'], utc=True, errors='coerce')
        week_resolved['Lead Time (Days)'] = (week_resolved['Resolved'] - week_resolved['Created']).dt.days

        done_positive_lt = week_resolved[week_resolved['Lead Time (Days)'] > 0]

        if len(done_positive_lt) > 0:
            avg_lead_time = done_positive_lt['Lead Time (Days)'].mean()
            avg_lead_time = round(float(avg_lead_time), 2) if pd.notna(avg_lead_time) else 0.0
            count = len(done_positive_lt)
            all_lead_times.extend(done_positive_lt['Lead Time (Days)'].tolist())
        else:
            avg_lead_time = 0.0
            count = 0

        weekly_lead_time.append({
            'Week': week_info['Week'],
            'Week Number': week_info['Week Number'],
            'Week Label': week_info['Week Label'],
            'Start Date': week_start,
            'End Date': week_end,
            'Average Lead Time (days)': avg_lead_time,
            'Resolved Issues Count': count
        })

    df_weekly_lead_time = pd.DataFrame(weekly_lead_time)


    overall_avg_lead_time = sum(all_lead_times) / len(all_lead_times) if all_lead_times else 0
    overall_avg_lead_time = round(float(overall_avg_lead_time), 2) if overall_avg_lead_time else 0
    df_weekly_lead_time['Overall Average'] = overall_avg_lead_time

    return df_weekly_lead_time


def calculate_task_load_per_assignee(df_issues, period_start, period_end, df_sprints=None):
    """
    Calculate task load per assignee.

    SIMPLIFIED LOGIC:
    - Filter: Issues in period (date range filter)
    - Count: Tasks per assignee (simple count, no changelog needed)

    Args:
        df_issues: Issues DataFrame
        period_start: Period start date
        period_end: Period end date
        df_sprints: Optional sprint DataFrame

    Returns:
        DataFrame with columns: Assignee, Task Count
    """

    period_start_utc = _normalize_date_to_utc(period_start)
    period_end_utc = _normalize_date_to_utc(period_end)
    period_issues = df_issues.copy()


    planned_activities = filter_planned_activities(period_issues, period_start_utc, period_end_utc)


    if 'Assignee' in planned_activities.columns:
        assigned_issues = planned_activities[planned_activities['Assignee'].notna()].copy()
        assignee_counts = assigned_issues['Assignee'].value_counts().reset_index()
        assignee_counts.columns = ['Assignee', 'Task Count']
        assignee_counts = assignee_counts.sort_values('Task Count', ascending=False).reset_index(drop=True)
        return assignee_counts

    return pd.DataFrame(columns=['Assignee', 'Task Count'])


def calculate_execution_success_by_assignee(df_issues, period_start, period_end, df_sprints=None):
    """
    Calculate execution success by assignee.

    SIMPLIFIED LOGIC:
    - Filter: Issues in period (date range filter)
    - Group by: Assignee
    - Done: Count issues with resolution date in period (simple and fast)
    - Success Rate: (Done / Total Assigned) × 100

    Args:
        df_issues: Issues DataFrame
        period_start: Period start date
        period_end: Period end date
        df_sprints: Optional sprint DataFrame

    Returns:
        DataFrame with columns: Assignee, Total Assigned, Done/Ready for Deployment, Success Rate (%)
    """

    period_start_utc = _normalize_date_to_utc(period_start)
    period_end_utc = _normalize_date_to_utc(period_end)
    period_issues = df_issues.copy()


    status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in period_issues.columns else 'New Status Category'


    planned_activities = filter_planned_activities(period_issues, period_start_utc, period_end_utc)


    if 'Assignee' in planned_activities.columns:
        assigned_issues = planned_activities[planned_activities['Assignee'].notna()].copy()

        assignee_success = []

        for assignee in assigned_issues['Assignee'].unique():
            assignee_tasks = assigned_issues[assigned_issues['Assignee'] == assignee]
            total_assigned = len(assignee_tasks)


            done = count_done_during_period(
                assignee_tasks,
                period_start_utc,
                period_end_utc,
                resolved_col='Resolved',
                status_col=status_col
            )

            success_rate = (done / total_assigned * 100) if total_assigned > 0 else 0

            assignee_success.append({
                'Assignee': assignee,
                'Total Assigned': total_assigned,
                'Done/Ready for Deployment': done,
                'Success Rate (%)': round(success_rate, 1)
            })

        df_assignee_success = pd.DataFrame(assignee_success)
        df_assignee_success = df_assignee_success.sort_values('Success Rate (%)', ascending=False).reset_index(drop=True)
        return df_assignee_success

    return pd.DataFrame(columns=['Assignee', 'Total Assigned', 'Done/Ready for Deployment', 'Success Rate (%)'])


def calculate_company_trend(df_issues, period_start, num_months=6, period_end=None, df_sprints=None):
    """
    Calculate company trend (completion rate and lead time) over months.
    Based on notebook Step 21 logic.

    Args:
        df_issues: Issues DataFrame
        period_start: Start date for analysis (used as fallback)
        num_months: Number of months to analyze (default 6)
        period_end: End date for analysis (if provided, starts from this month and goes backwards)
        df_sprints: Optional sprint DataFrame

    Returns:
        DataFrame with columns: Month, Total Issues, Done Count, Completion Rate (%),
                               Average Lead Time (days), Resolved Issues Count,
                               Overall Avg Completion (%), Overall Avg Lead Time (days)
        Only includes months with valid data (Total Issues > 0)
    """

    df_issues = df_issues.copy()
    df_issues['Created'] = pd.to_datetime(df_issues['Created'], utc=True, errors='coerce')
    df_issues['Resolved'] = pd.to_datetime(df_issues['Resolved'], utc=True, errors='coerce')
    df_issues['Lead Time (days)'] = (df_issues['Resolved'] - df_issues['Created']).dt.days


    if period_end:
        end_date = _normalize_date_to_utc(period_end)
    else:
        end_date = datetime.now(timezone.utc)


    period_start_utc = _normalize_date_to_utc(period_start) if period_start else None


    # Start from the month containing end_date
    current_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_date = _normalize_date_to_utc(current_date)
    if period_start_utc:
        period_start_month = period_start_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_start_month = _normalize_date_to_utc(period_start_month)
        # Start from the earlier of end_date month or period_start month
        if period_start_month < current_date:
            current_date = period_start_month

    monthly_trend = []
    all_completion_rates = []
    all_lead_times = []
    done_statuses_lower = [s.lower() for s in DONE_STATUSES]

    # Always start from end_date month and go backwards num_months
    # Start from the month containing end_date
    current_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_date = _normalize_date_to_utc(current_date)
    
    # Build list of months going backwards from end_date
    months_to_process = []
    temp_date = current_date
    for _ in range(num_months):
        months_to_process.append(temp_date)
        # Move to previous month
        if temp_date.month == 1:
            temp_date = datetime(temp_date.year - 1, 12, 1, tzinfo=temp_date.tzinfo)
        else:
            temp_date = datetime(temp_date.year, temp_date.month - 1, 1, tzinfo=temp_date.tzinfo)
        temp_date = _normalize_date_to_utc(temp_date)
    
    # Reverse to get chronological order (oldest first)
    months_to_process.reverse()

    for current_date in months_to_process:
        month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start = _normalize_date_to_utc(month_start)


        if month_start.month == 12:
            month_end = datetime(month_start.year + 1, 1, 1, tzinfo=month_start.tzinfo) - timedelta(days=1)
        else:
            month_end = datetime(month_start.year, month_start.month + 1, 1, tzinfo=month_start.tzinfo) - timedelta(days=1)
        month_end = month_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        month_end = _normalize_date_to_utc(month_end)

        month_start_utc = _normalize_date_to_utc(month_start)
        month_end_utc = _normalize_date_to_utc(month_end)
        month_issues = df_issues.copy()


        status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in month_issues.columns else 'New Status Category'


        planned_activities = filter_planned_activities(month_issues, month_start_utc, month_end_utc)
        total_issues = len(planned_activities)


        done_count = count_done_during_period(
            month_issues,
            month_start_utc,
            month_end_utc,
            resolved_col='Resolved',
            status_col=status_col
        )

        completion_rate = (done_count / total_issues * 100) if total_issues > 0 else 0



        from app.services.resolution_utils import filter_done_issues
        month_resolved = filter_done_issues(
            month_issues,
            month_start_utc,
            month_end_utc,
            resolved_col='Resolved',
            status_col=status_col
        )



        month_resolved['Created'] = pd.to_datetime(month_resolved['Created'], utc=True, errors='coerce')
        month_resolved['Resolved'] = pd.to_datetime(month_resolved['Resolved'], utc=True, errors='coerce')
        month_resolved['Lead Time (Days)'] = (month_resolved['Resolved'] - month_resolved['Created']).dt.days

        done_positive_lt = month_resolved[month_resolved['Lead Time (Days)'] > 0]

        if len(done_positive_lt) > 0:
            avg_lead_time = done_positive_lt['Lead Time (Days)'].mean()
            avg_lead_time = round(float(avg_lead_time), 2) if pd.notna(avg_lead_time) else 0.0
            all_lead_times.extend(done_positive_lt['Lead Time (Days)'].tolist())
        else:
            avg_lead_time = 0.0


        # Only include months with data (total_issues > 0)
        # This way we stop showing months when there's no data
        if total_issues > 0:
            monthly_trend.append({
                'Month': month_start.strftime('%b %Y'),
                'Month Start': month_start,
                'Month End': month_end,
                'Planned': total_issues,
                'Total Issues': total_issues,  # Keep for backward compatibility
                'Done Count': done_count,
                'Completion Rate (%)': round(completion_rate, 1),
                'Average Lead Time (days)': round(avg_lead_time, 2) if avg_lead_time is not None and pd.notna(avg_lead_time) else 0.0,
                'Resolved Issues Count': len(month_resolved)
            })
            all_completion_rates.append(completion_rate)

    df_company_trend = pd.DataFrame(monthly_trend)


    overall_avg_completion = sum(all_completion_rates) / len(all_completion_rates) if all_completion_rates else 0
    overall_avg_lead_time = sum(all_lead_times) / len(all_lead_times) if all_lead_times else 0

    df_company_trend['Overall Avg Completion (%)'] = overall_avg_completion
    df_company_trend['Overall Avg Lead Time (days)'] = overall_avg_lead_time

    return df_company_trend


def calculate_qa_vs_failed(df_issues, period_start, period_end, group_by='sprint', df_sprints=None):
    """
    Calculate QA executed vs failed QA metrics using changelog transitions for accuracy.
    PRIORITIZES CHANGELOG DATA for maximum accuracy.

    Args:
        df_issues: Issues DataFrame
        period_start: Period start date
        period_end: Period end date
        group_by: 'sprint' or 'week' (default: 'sprint')
        df_sprints: Optional sprint DataFrame

    Returns:
        DataFrame with columns: Sprint/Week, Sprint Name/Week Label, qaExecuted, failedQA
    """
    from app.services.changelog_processor import analyze_qa_transitions


    df_issues, usage_stats = ensure_changelog_usage(df_issues, 'qa_vs_failed')


    period_start_utc = _normalize_date_to_utc(period_start)
    period_end_utc = _normalize_date_to_utc(period_end)
    period_issues = df_issues.copy()


    period_issues['Created'] = pd.to_datetime(period_issues['Created'], utc=True, errors='coerce')
    period_issues['Updated'] = pd.to_datetime(period_issues['Updated'], utc=True, errors='coerce')
    period_issues['Resolved'] = pd.to_datetime(period_issues['Resolved'], utc=True, errors='coerce')

    if group_by == 'sprint':

        qa_results = []


        sprint_issues = period_issues.copy()


        if 'Sprint' in sprint_issues.columns:
            unique_sprints = sprint_issues['Sprint'].dropna().unique()

            for sprint_name in unique_sprints:
                sprint_issues_filtered = sprint_issues[sprint_issues['Sprint'] == sprint_name].copy()

                qa_executed_count = 0
                failed_qa_count = 0


                sprint_issues_filtered = pre_parse_transitions(sprint_issues_filtered)


                for _, row in sprint_issues_filtered.iterrows():
                    transitions = row.get('_parsed_transitions', [])
                    if transitions:
                        try:
                            if transitions:

                                qa_analysis = analyze_qa_transitions(transitions)


                                entered_qa = qa_analysis.get('entered_qa', [])
                                for qa_entry in entered_qa:
                                    qa_timestamp = qa_entry.get('timestamp')
                                    if qa_timestamp:
                                        try:
                                            qa_date = datetime.fromisoformat(qa_timestamp.replace('Z', '+00:00'))

                                            if period_start_utc <= qa_date <= period_end_utc:
                                                qa_executed_count += 1
                                        except:
                                            pass


                                failed_qa_list = qa_analysis.get('failed_qa', [])
                                for qa_failure in failed_qa_list:
                                    failure_timestamp = qa_failure.get('timestamp')
                                    if failure_timestamp:
                                        try:
                                            failure_date = datetime.fromisoformat(failure_timestamp.replace('Z', '+00:00'))

                                            if period_start_utc <= failure_date <= period_end_utc:
                                                failed_qa_count += 1
                                        except:
                                            pass
                        except:

                            pass


                    if 'QA Entered Count' in row and qa_executed_count == 0:
                        qa_executed_count = max(qa_executed_count, row.get('QA Entered Count', 0) or 0)
                    if 'QA Failed Count' in row and failed_qa_count == 0:
                        failed_qa_count = max(failed_qa_count, row.get('QA Failed Count', 0) or 0)

                qa_results.append({
                    'sprint': str(sprint_name),
                    'sprintName': str(sprint_name),
                    'qaExecuted': qa_executed_count,
                    'failedQA': failed_qa_count
                })

        result_df = pd.DataFrame(qa_results)

        return result_df

    else:

        weeks_data = []
        current_date = period_start_utc
        week_num = 1

        while current_date <= period_end_utc:
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)
            week_issues = period_issues.copy()

            qa_executed_count = 0
            failed_qa_count = 0


            week_issues = pre_parse_transitions(week_issues)


            for _, row in week_issues.iterrows():
                transitions = row.get('_parsed_transitions', [])
                if transitions:
                    try:
                        if transitions:

                            qa_analysis = analyze_qa_transitions(transitions)


                            entered_qa = qa_analysis.get('entered_qa', [])
                            for qa_entry in entered_qa:
                                qa_timestamp = qa_entry.get('timestamp')
                                if qa_timestamp:
                                    try:
                                        qa_date = datetime.fromisoformat(qa_timestamp.replace('Z', '+00:00'))
                                        if current_date <= qa_date <= week_end:
                                            qa_executed_count += 1
                                    except:
                                        pass


                            failed_qa_list = qa_analysis.get('failed_qa', [])
                            for qa_failure in failed_qa_list:
                                failure_timestamp = qa_failure.get('timestamp')
                                if failure_timestamp:
                                    try:
                                        failure_date = datetime.fromisoformat(failure_timestamp.replace('Z', '+00:00'))
                                        if current_date <= failure_date <= week_end:
                                            failed_qa_count += 1
                                    except:
                                        pass
                    except:
                        pass

            weeks_data.append({
                'week': f'W{week_num:02d}',
                'weekLabel': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})',
                'qaExecuted': qa_executed_count,
                'failedQA': failed_qa_count
            })

            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)
            week_num += 1

        result_df = pd.DataFrame(weeks_data)

        return result_df


def calculate_rework_ratio(df_issues, start_date, num_weeks=12, df_sprints=None, period_end=None):
    """
    Calculate rework ratio (clean delivery vs rework) per week.
    Uses changelog transitions for accurate rework detection based on workflow backward movement.
    PRIORITIZES CHANGELOG DATA for maximum accuracy.

    Rework is detected when an issue moves backward in the workflow (e.g., Done -> In Progress, QA -> To Do).

    Args:
        df_issues: Issues DataFrame
        start_date: Start date for analysis
        num_weeks: Number of weeks to analyze (default 12, ignored if period_end is provided)
        df_sprints: Optional sprint DataFrame
        period_end: Optional end date - if provided, includes all weeks that overlap with period

    Returns:
        DataFrame with columns: Week, Week Label, cleanDelivery, rework
    """
    from app.services.changelog_processor import analyze_rework_patterns


    df_issues, usage_stats = ensure_changelog_usage(df_issues, 'rework_ratio')


    start_date = _normalize_date_to_utc(start_date)
    weeks_data = []
    current_date = start_date
    
    if period_end:
        period_end = _normalize_date_to_utc(period_end)
        week_num = 1
        
        while current_date <= period_end:
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)
            
            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            
            if period_end <= week_end:
                break
            
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)
            week_num += 1
    else:
        for week_num in range(1, num_weeks + 1):
            week_end = current_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            week_end = _normalize_date_to_utc(week_end)

            weeks_data.append({
                'Week': f'W-{week_num:02d}',
                'Week Number': week_num,
                'Start Date': current_date,
                'End Date': week_end,
                'Week Label': f'W{week_num:02d} ({current_date.strftime("%b %d")} - {week_end.strftime("%b %d")})'
            })
            next_day = week_end + timedelta(days=1)
            current_date = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = _normalize_date_to_utc(current_date)


    df_issues = df_issues.copy()
    df_issues['Created'] = pd.to_datetime(df_issues['Created'], utc=True, errors='coerce')
    df_issues['Updated'] = pd.to_datetime(df_issues['Updated'], utc=True, errors='coerce')
    df_issues['Resolved'] = pd.to_datetime(df_issues['Resolved'], utc=True, errors='coerce')


    status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in df_issues.columns else 'New Status Category'


    weekly_results = []

    for week_info in weeks_data:
        week_start = week_info['Start Date']
        week_end = week_info['End Date']
        effective_week_end = week_end
        if period_end:
            effective_week_end = min(week_end, period_end)
        week_issues = df_issues.copy()


        from app.services.resolution_utils import filter_done_issues
        week_resolved = filter_done_issues(
            week_issues,
            week_start,
            effective_week_end,
            resolved_col='Resolved',
            status_col=status_col
        )

        if len(week_resolved) == 0:

            weekly_results.append({
                'Week': week_info['Week'],
                'Week Label': week_info['Week Label'],
                'week': f'W{week_info["Week Number"]:02d}',
                'cleanDelivery': 1.0,
                'rework': 0.0,
                'Rework Count': 0,
                'Resolved Count': 0
            })
            continue


        week_resolved = pre_parse_transitions(week_resolved)


        rework_issues = set()
        total_resolved = len(week_resolved)

        for idx, issue in week_resolved.iterrows():
            issue_key = issue.get('Issue key', idx)
            transitions = issue.get('_parsed_transitions', [])


            if transitions:
                try:
                    if transitions:

                        rework_analysis = analyze_rework_patterns(transitions)


                        if rework_analysis.get('has_rework', False):

                            rework_transitions = rework_analysis.get('rework_transitions', [])
                            for rework_trans in rework_transitions:
                                rework_timestamp = rework_trans.get('timestamp')
                                if rework_timestamp:
                                    try:
                                        rework_date = datetime.fromisoformat(rework_timestamp.replace('Z', '+00:00'))

                                        if rework_date <= week_end:
                                            rework_issues.add(issue_key)
                                            break
                                    except:
                                        pass
                except:

                    if issue.get('Has Rework', False):
                        rework_issues.add(issue_key)
                    pass

        rework_count = len(rework_issues)
        rework_ratio = rework_count / total_resolved if total_resolved > 0 else 0.0
        clean_delivery_ratio = 1.0 - rework_ratio

        weekly_results.append({
            'Week': week_info['Week'],
            'Week Label': week_info['Week Label'],
            'week': f'W{week_info["Week Number"]:02d}',
            'cleanDelivery': round(clean_delivery_ratio, 3),
            'rework': round(rework_ratio, 3),
            'Rework Count': rework_count,
            'Resolved Count': total_resolved
        })

    result_df = pd.DataFrame(weekly_results)

    return result_df


def calculate_assignee_completion_trend(df_issues, period_start, period_end,
                                       compare_period_start=None, compare_period_end=None,
                                       assignee=None, df_sprints=None):
    """
    Calculate assignee completion trend comparing current period vs previous period.

    Args:
        df_issues: Issues DataFrame
        period_start: Current period start date
        period_end: Current period end date
        compare_period_start: Previous period start date (auto-calculated if None)
        compare_period_end: Previous period end date (auto-calculated if None)
        assignee: Optional assignee filter (if None, return all assignees)
        df_sprints: Optional sprint DataFrame

    Returns:
        DataFrame with columns: assignee, currentPeriod metrics, previousPeriod metrics, trend metrics
    """

    period_start_utc = _normalize_date_to_utc(period_start)
    period_end_utc = _normalize_date_to_utc(period_end)


    if compare_period_start is None or compare_period_end is None:
        period_duration = period_end_utc - period_start_utc
        compare_period_end_utc = period_start_utc - timedelta(days=1)
        compare_period_start_utc = compare_period_end_utc - period_duration
    else:
        compare_period_start_utc = _normalize_date_to_utc(compare_period_start)
        compare_period_end_utc = _normalize_date_to_utc(compare_period_end)


    df_issues = df_issues.copy()
    df_issues['Created'] = pd.to_datetime(df_issues['Created'], utc=True, errors='coerce')
    df_issues['Updated'] = pd.to_datetime(df_issues['Updated'], utc=True, errors='coerce')
    df_issues['Resolved'] = pd.to_datetime(df_issues['Resolved'], utc=True, errors='coerce')


    if 'Status Category (Mapped)' not in df_issues.columns:
        from app.services.changelog_processor import map_status_to_category
        if 'Status' in df_issues.columns:
            df_issues['Status Category (Mapped)'] = df_issues['Status'].apply(map_status_to_category)
        elif 'New Status Category' in df_issues.columns:
            df_issues['Status Category (Mapped)'] = df_issues['New Status Category']
        else:
            df_issues['Status Category (Mapped)'] = 'Not Done'


    if assignee and assignee != "All Assignees" and assignee.strip():
        df_issues = df_issues[df_issues['Assignee'] == assignee].copy()


    if 'Assignee' in df_issues.columns:
        unique_assignees = df_issues[df_issues['Assignee'].notna()]['Assignee'].unique()
    else:
        return pd.DataFrame()

    trend_results = []

    for assignee_name in unique_assignees:
        assignee_issues = df_issues[df_issues['Assignee'] == assignee_name].copy()


        current_period_issues = assignee_issues[
            ((assignee_issues['Created'] >= period_start_utc) & (assignee_issues['Created'] <= period_end_utc)) |
            ((assignee_issues['Updated'] >= period_start_utc) & (assignee_issues['Updated'] <= period_end_utc)) |
            ((assignee_issues['Resolved'] >= period_start_utc) & (assignee_issues['Resolved'] <= period_end_utc))
        ].copy()

        current_total_assigned = len(current_period_issues)
        current_done = current_period_issues[
            (current_period_issues['Status Category (Mapped)'] == 'Done') &
            (current_period_issues['Resolved'] >= period_start_utc) &
            (current_period_issues['Resolved'] <= period_end_utc)
        ]
        current_total_done = len(current_done)
        current_completion_rate = (current_total_done / current_total_assigned * 100) if current_total_assigned > 0 else 0.0



        current_done = pre_parse_transitions(current_done)

        current_lead_times = []
        for _, row in current_done.iterrows():
            transitions = row.get('_parsed_transitions', [])
            created = row.get('Created')
            resolved = row.get('Resolved')

            if transitions and created and resolved:
                try:
                    if transitions:
                        created_str = created.isoformat() if hasattr(created, 'isoformat') else str(created)
                        resolved_str = resolved.isoformat() if hasattr(resolved, 'isoformat') else str(resolved)

                        lead_time_result = calculate_lead_time_from_transitions(
                            transitions,
                            created_str,
                            resolved_str
                        )
                        lead_time_days = lead_time_result.get('lead_time_days')
                        if lead_time_days is not None and lead_time_days > 0:
                            current_lead_times.append(lead_time_days)
                except:
                    pass

        current_avg_lead_time = sum(current_lead_times) / len(current_lead_times) if len(current_lead_times) > 0 else 0.0
        current_avg_lead_time = round(float(current_avg_lead_time), 2) if pd.notna(current_avg_lead_time) else 0.0


        previous_period_issues = assignee_issues[
            ((assignee_issues['Created'] >= compare_period_start_utc) & (assignee_issues['Created'] <= compare_period_end_utc)) |
            ((assignee_issues['Updated'] >= compare_period_start_utc) & (assignee_issues['Updated'] <= compare_period_end_utc)) |
            ((assignee_issues['Resolved'] >= compare_period_start_utc) & (assignee_issues['Resolved'] <= compare_period_end_utc))
        ].copy()

        previous_total_assigned = len(previous_period_issues)
        previous_done = previous_period_issues[
            (previous_period_issues['Status Category (Mapped)'] == 'Done') &
            (previous_period_issues['Resolved'] >= compare_period_start_utc) &
            (previous_period_issues['Resolved'] <= compare_period_end_utc)
        ]
        previous_total_done = len(previous_done)
        previous_completion_rate = (previous_total_done / previous_total_assigned * 100) if previous_total_assigned > 0 else 0.0



        previous_done = pre_parse_transitions(previous_done)

        previous_lead_times = []
        for _, row in previous_done.iterrows():
            transitions = row.get('_parsed_transitions', [])
            created = row.get('Created')
            resolved = row.get('Resolved')

            if transitions and created and resolved:
                try:
                    if transitions:
                        created_str = created.isoformat() if hasattr(created, 'isoformat') else str(created)
                        resolved_str = resolved.isoformat() if hasattr(resolved, 'isoformat') else str(resolved)

                        lead_time_result = calculate_lead_time_from_transitions(
                            transitions,
                            created_str,
                            resolved_str
                        )
                        lead_time_days = lead_time_result.get('lead_time_days')
                        if lead_time_days is not None and lead_time_days > 0:
                            previous_lead_times.append(lead_time_days)
                except:
                    pass

        previous_avg_lead_time = sum(previous_lead_times) / len(previous_lead_times) if len(previous_lead_times) > 0 else 0.0
        previous_avg_lead_time = round(float(previous_avg_lead_time), 2) if pd.notna(previous_avg_lead_time) else 0.0


        completion_rate_change = current_completion_rate - previous_completion_rate
        completion_rate_change_percent = ((current_completion_rate - previous_completion_rate) / previous_completion_rate * 100) if previous_completion_rate > 0 else 0.0

        lead_time_change = current_avg_lead_time - previous_avg_lead_time
        lead_time_change_percent = ((current_avg_lead_time - previous_avg_lead_time) / previous_avg_lead_time * 100) if previous_avg_lead_time > 0 else 0.0


        productivity_change = completion_rate_change

        trend_results.append({
            'assignee': assignee_name,
            'currentPeriod_completionRate': round(current_completion_rate, 1),
            'currentPeriod_totalAssigned': current_total_assigned,
            'currentPeriod_totalDone': current_total_done,
            'currentPeriod_avgLeadTime': current_avg_lead_time,
            'previousPeriod_completionRate': round(previous_completion_rate, 1),
            'previousPeriod_totalAssigned': previous_total_assigned,
            'previousPeriod_totalDone': previous_total_done,
            'previousPeriod_avgLeadTime': previous_avg_lead_time,
            'trend_completionRateChange': round(completion_rate_change, 1),
            'trend_completionRateChangePercent': round(completion_rate_change_percent, 1),
            'trend_leadTimeChange': round(lead_time_change, 2),
            'trend_leadTimeChangePercent': round(lead_time_change_percent, 1),
            'trend_productivityChange': round(productivity_change, 1)
        })

    return pd.DataFrame(trend_results)

