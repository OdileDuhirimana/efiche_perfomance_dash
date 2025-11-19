from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
import traceback
import json
import pandas as pd

from app.services.data_cache import get_cached_data
from app.services.resolution_utils import count_done_during_period
from app.services.changelog_processor import calculate_lead_time_from_transitions, analyze_rework_patterns
from app.services.filters import filter_by_overall_window, filter_planned_activities, apply_standard_filters
from app.services.transitions_helper import pre_parse_transitions


def _parse_date(date_str, default=None):
    """Parse date string to UTC datetime. Supports multiple formats."""
    if not date_str:
        return default
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        pass
    
    try:
        dt = datetime.strptime(date_str, '%d-%m-%Y')
        return dt.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        pass
    
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        pass
    
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        pass
    
    return default


def _validate_date_range(start_date, end_date=None):
    """Validate and normalize date range."""
    if start_date is None:
        return None, None
    
    if end_date is not None:
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        
        if end_date.hour == 0 and end_date.minute == 0 and end_date.second == 0:
            end_date = end_date.replace(hour=23, minute=59, second=59)
    
    if start_date.hour != 0 or start_date.minute != 0 or start_date.second != 0:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return start_date, end_date


def get_executive_summary():
    """Get Executive Summary KPIs. Uses apply_standard_filters() for data consistency."""
    try:
        df, df_sprints = get_cached_data()
        
        period_start_str = request.args.get('start_date') or request.args.get('period_start')
        period_end_str = request.args.get('end_date') or request.args.get('period_end')
        assignees = request.args.getlist('assignee')
        if not assignees:
            single_assignee = request.args.get('assignee')
            if single_assignee:
                assignees = [single_assignee]
            else:
                assignees = None
        if assignees:
            valid_assignees = [a for a in assignees if a and a.strip() and a != "All Assignees"]
            assignees = valid_assignees if valid_assignees else None
        issue_type = request.args.get('issueType')
        
        if period_start_str and period_end_str:
            period_start = _parse_date(period_start_str)
            period_end = _parse_date(period_end_str)
            
            if period_end:
                period_end = period_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            if period_start:
                period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            period_start, period_end = _validate_date_range(period_start, period_end)
        else:
            period_end = datetime.now(timezone.utc)
            period_start = period_end - timedelta(days=30)
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            period_start, period_end = _validate_date_range(period_start, period_end)
        
        df = apply_standard_filters(df, assignees=assignees, issue_type=issue_type, 
                                   start_date=period_start, end_date=period_end)
        
        filtered_issues = df.copy()
        
        status_col = 'Status Category (Mapped)' if 'Status Category (Mapped)' in filtered_issues.columns else 'New Status Category'
        
        planned_issues = filter_planned_activities(filtered_issues, period_start, period_end)
        planned = int(len(planned_issues))
        
        done = int(count_done_during_period(
            filtered_issues, 
            period_start, 
            period_end, 
            resolved_col='Resolved',
            status_col=status_col
        ))
        completion_rate = round((done / planned * 100) if planned > 0 else 0, 1)
        
        from app.services.resolution_utils import filter_done_issues
        done_issues = filter_done_issues(
            filtered_issues,
            period_start,
            period_end,
            resolved_col='Resolved',
            status_col=status_col
        )
        
        done_issues['Created'] = pd.to_datetime(done_issues['Created'], utc=True, errors='coerce')
        done_issues['Resolved'] = pd.to_datetime(done_issues['Resolved'], utc=True, errors='coerce')
        done_issues['Lead Time (Days)'] = (done_issues['Resolved'] - done_issues['Created']).dt.days
        
        done_positive_lt = done_issues[done_issues['Lead Time (Days)'] > 0]
        
        avg_lead_time = round(done_positive_lt['Lead Time (Days)'].mean(), 2) if len(done_positive_lt) > 0 else 0.0
        
        rework_count = 0
        total_resolved = int(len(done_issues))
        
        done_issues = pre_parse_transitions(done_issues)
        
        for _, row in done_issues.iterrows():
            transitions = row.get('_parsed_transitions', [])
            if transitions:
                try:
                    if transitions:
                        rework_analysis = analyze_rework_patterns(transitions)
                        if rework_analysis.get('has_rework', False):
                            rework_count += 1
                except:
                    pass
        
        rework_ratio = round(rework_count / total_resolved, 3) if total_resolved > 0 else 0.0
        
        return jsonify({
            'success': True,
            'data': {
                'completion_rate': float(completion_rate),
                'avg_lead_time': float(avg_lead_time),
                'rework_ratio': float(rework_ratio),
                'planned': int(planned),
                'done': int(done),
                'rework_count': int(rework_count),
                'total_resolved': int(total_resolved)
            },
            'metadata': {
                'period_start': period_start.isoformat() if period_start else None,
                'period_end': period_end.isoformat() if period_end else None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
