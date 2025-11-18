"""
API routes for the analytics backend.
Provides REST endpoints for all chart data and metrics.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
import traceback
import math
import pandas as pd
import numpy as np

from app.services.data_cache import get_cached_data
from app.services.chart_calculations import (
    calculate_weekly_planned_vs_done,
    calculate_weekly_flow,
    calculate_weekly_lead_time,
    calculate_task_load_per_assignee,
    calculate_execution_success_by_assignee,
    calculate_company_trend,
    calculate_qa_vs_failed,
    calculate_rework_ratio,
    calculate_assignee_completion_trend,
)
from app.api.executive_summary import get_executive_summary
from app.services.filters import apply_selection_filters, filter_by_overall_window, apply_standard_filters


api_bp = Blueprint('api', __name__, url_prefix='/api')


def _dataframe_to_dict(df):
    """
    Convert DataFrame to JSON-serializable dict.
    
    Logic: Converts DataFrame to dict using 'records' orientation. Cleans up non-serializable values:
    converts datetime objects to ISO format strings, converts NaN to None, converts numpy/pandas numeric types
    to native Python types, handles float NaN and inf values.
    
    Use: Used by all API endpoints to convert chart calculation results to JSON response format.
    
    Args:
        df: DataFrame to convert
    
    Returns:
        List of dictionaries with JSON-serializable values
    """
    if df.empty:
        return []
    
    result = df.to_dict('records')
    
    for record in result:
        for key, value in record.items():
            if isinstance(value, (pd.Timestamp, datetime)):
                record[key] = value.isoformat() if pd.notna(value) else None
            elif pd.isna(value):
                record[key] = None
            elif hasattr(value, 'item'):
                try:
                    record[key] = value.item()
                except (AttributeError, ValueError):
                    record[key] = int(value) if isinstance(value, (pd.Int64Dtype, pd.Int32Dtype)) else value
            elif 'int' in str(type(value)) and 'numpy' in str(type(value)):
                record[key] = int(value)
            elif 'float' in str(type(value)) and 'numpy' in str(type(value)):
                record[key] = float(value)
            elif isinstance(value, float):
                if math.isnan(value) or value != value:
                    record[key] = None
                elif math.isinf(value):
                    record[key] = None
                else:
                    record[key] = value
            else:
                record[key] = value
    
    return result


def _parse_date(date_str, default=None):
    """
    Parse date string to UTC datetime.
    
    Logic: Tries to parse date string using ISO format (with Z replacement). Ensures timezone is UTC
    (localizes if None). Returns default on parse failure.
    
    Use: Used by all API endpoints to parse date query parameters from various formats.
    
    Args:
        date_str: Date string in ISO format
        default: Default value to return on parse failure
    
    Returns:
        UTC timezone-aware datetime or default
    """
    if not date_str:
        return default
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return default


def _validate_date_range(start_date, end_date=None):
    """
    Validate date range and ensure logical ordering.
    
    Logic: Clamps start_date to current date if too far in future. Swaps dates if end_date < start_date.
    Clamps end_date to current date if too far in future. Returns validated tuple.
    
    Use: Used by all API endpoints to normalize and validate date ranges from query parameters.
    
    Args:
        start_date: Start datetime
        end_date: Optional end datetime
    
    Returns:
        Tuple of (start_date, end_date) with validated dates
    """
    if start_date is None:
        return None, None
    
    now = datetime.now(timezone.utc)
    if start_date > now + timedelta(days=1):
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if end_date is not None:
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        
        if end_date > now + timedelta(days=1):
            end_date = now
    
    return start_date, end_date


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Logic: Returns simple JSON response indicating service is healthy with current timestamp.
    
    Use: Used for monitoring and health checks to verify API service is running.
    
    Returns:
        JSON response with success status, health status, service name, and timestamp
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'analytics-backend',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })


@api_bp.route('/data/date-range', methods=['GET'])
def get_data_date_range():
    """
    Get the date range of available data.
    
    Logic: Retrieves cached data, extracts min and max dates from Created, Updated, and Resolved columns.
    Returns the overall date range covering all activity dates in the dataset.
    
    Use: Used by frontend to determine available date range for date pickers and filters.
    
    Returns:
        JSON response with min_date and max_date in ISO format
    """
    try:
        df, df_sprints = get_cached_data()
        
        df_copy = df.copy()
        date_columns = ['Created', 'Updated', 'Resolved']
        min_dates = []
        max_dates = []
        
        for col in date_columns:
            if col in df_copy.columns:
                df_copy[col] = pd.to_datetime(df_copy[col], utc=True, errors='coerce')
                valid_dates = df_copy[col].dropna()
                if len(valid_dates) > 0:
                    min_dates.append(valid_dates.min())
                    max_dates.append(valid_dates.max())
        
        if min_dates and max_dates:
            min_date = min(min_dates)
            max_date = max(max_dates)
            
            return jsonify({
                'success': True,
                'data': {
                    'min_date': min_date.isoformat() if hasattr(min_date, 'isoformat') else str(min_date),
                    'max_date': max_date.isoformat() if hasattr(max_date, 'isoformat') else str(max_date),
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'min_date': None,
                    'max_date': None,
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/weekly-planned-vs-done', methods=['GET'])
def get_weekly_planned_vs_done():
    """
    Get weekly planned vs done chart data.
    
    Logic: Retrieves cached data, parses query parameters (num_weeks, start_date/end_date, assignee, issue_type).
    Applies filters, validates date range, defaults to 12 weeks ago if no start date. Calls calculate_weekly_planned_vs_done
    and returns JSON response with weekly metrics.
    
    Use: API endpoint for weekly planned vs done chart showing planned activities and completed work per week.
    
    Returns:
        JSON response with weekly data (Planned, Done, Completion Rate) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        num_weeks = int(request.args.get('num_weeks', 12))
        start_date_str = request.args.get('start_date') or request.args.get('period_start')
        end_date_str = request.args.get('end_date') or request.args.get('period_end')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if start_date_str:
            start_date = _parse_date(start_date_str)
        else:
            start_date = datetime.now(timezone.utc) - timedelta(weeks=num_weeks)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end_date = None
        if end_date_str:
            end_date = _parse_date(end_date_str)
            start_date, end_date = _validate_date_range(start_date, end_date)
        else:
            start_date, _ = _validate_date_range(start_date)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=start_date, end_date=end_date)
        
        weekly_df = calculate_weekly_planned_vs_done(df, start_date, num_weeks=num_weeks, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(weekly_df),
            'metadata': {
                'start_date': start_date.isoformat(),
                'num_weeks': num_weeks
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/weekly-flow', methods=['GET'])
def get_weekly_flow():
    """
    Get weekly flow chart data (Done, In Progress, Carry Over).
    
    Logic: Retrieves cached data, parses query parameters (num_weeks, start_date/end_date, assignee, issue_type).
    Applies filters, validates date range, defaults to 12 weeks ago if no start date. Calls calculate_weekly_flow
    and returns JSON response with weekly flow metrics.
    
    Use: API endpoint for weekly flow chart showing work state distribution (done, in progress, carry-over) per week.
    
    Returns:
        JSON response with weekly data (Done, In Progress, Carry Over, New Issues) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        num_weeks = int(request.args.get('num_weeks', 12))
        start_date_str = request.args.get('start_date') or request.args.get('period_start')
        end_date_str = request.args.get('end_date') or request.args.get('period_end')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if start_date_str:
            start_date = _parse_date(start_date_str)
        else:
            start_date = datetime.now(timezone.utc) - timedelta(weeks=num_weeks)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end_date = None
        if end_date_str:
            end_date = _parse_date(end_date_str)
            start_date, end_date = _validate_date_range(start_date, end_date)
        else:
            start_date, _ = _validate_date_range(start_date)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=start_date, end_date=end_date)
        
        weekly_df = calculate_weekly_flow(df, start_date, num_weeks=num_weeks, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(weekly_df),
            'metadata': {
                'start_date': start_date.isoformat(),
                'num_weeks': num_weeks
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/weekly-lead-time', methods=['GET'])
def get_weekly_lead_time():
    """
    Get weekly lead time chart data.
    
    Logic: Retrieves cached data, parses query parameters (num_weeks, start_date/end_date, assignee, issue_type).
    Applies filters, validates date range, defaults to 12 weeks ago if no start date. Calls calculate_weekly_lead_time
    and returns JSON response with weekly average lead time metrics.
    
    Use: API endpoint for weekly lead time chart showing average lead time per week.
    
    Returns:
        JSON response with weekly data (Average Lead Time, Resolved Issues Count) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        num_weeks = int(request.args.get('num_weeks', 12))
        start_date_str = request.args.get('start_date') or request.args.get('period_start')
        end_date_str = request.args.get('end_date') or request.args.get('period_end')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if start_date_str:
            start_date = _parse_date(start_date_str)
        else:
            start_date = datetime.now(timezone.utc) - timedelta(weeks=num_weeks)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end_date = None
        if end_date_str:
            end_date = _parse_date(end_date_str)
            start_date, end_date = _validate_date_range(start_date, end_date)
        else:
            start_date, _ = _validate_date_range(start_date)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=start_date, end_date=end_date)
        
        weekly_df = calculate_weekly_lead_time(df, start_date, num_weeks=num_weeks, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(weekly_df),
            'metadata': {
                'start_date': start_date.isoformat(),
                'num_weeks': num_weeks
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/task-load', methods=['GET'])
def get_task_load():
    """
    Get task load per assignee chart data.
    
    Logic: Retrieves cached data, parses query parameters (period_start/period_end, assignee, issue_type).
    Applies filters, validates date range, defaults to last 3 months if no dates provided. Calls calculate_task_load_per_assignee
    and returns JSON response with task counts per assignee.
    
    Use: API endpoint for task load chart showing number of planned tasks per assignee.
    
    Returns:
        JSON response with assignee data (Assignee, Task Count) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        period_start_str = request.args.get('period_start') or request.args.get('start_date')
        period_end_str = request.args.get('period_end') or request.args.get('end_date')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if period_start_str and period_end_str:
            period_start = _parse_date(period_start_str)
            period_end = _parse_date(period_end_str)
            period_start, period_end = _validate_date_range(period_start, period_end)
        else:
            period_end = datetime.now(timezone.utc)
            period_start = period_end - timedelta(days=90)
            period_start, period_end = _validate_date_range(period_start, period_end)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=period_start, end_date=period_end)
        
        assignee_df = calculate_task_load_per_assignee(df, period_start, period_end, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(assignee_df),
            'metadata': {
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/execution-success', methods=['GET'])
def get_execution_success():
    """
    Get execution success by assignee chart data.
    
    Logic: Retrieves cached data, parses query parameters (period_start/period_end, assignee, issue_type).
    Applies filters, validates date range, defaults to last 3 months if no dates provided. Calls calculate_execution_success_by_assignee
    and returns JSON response with success rates per assignee.
    
    Use: API endpoint for execution success chart showing completion rate per assignee.
    
    Returns:
        JSON response with assignee data (Assignee, Total Assigned, Done, Success Rate) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        period_start_str = request.args.get('period_start') or request.args.get('start_date')
        period_end_str = request.args.get('period_end') or request.args.get('end_date')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if period_start_str and period_end_str:
            period_start = _parse_date(period_start_str)
            period_end = _parse_date(period_end_str)
            period_start, period_end = _validate_date_range(period_start, period_end)
        else:
            period_end = datetime.now(timezone.utc)
            period_start = period_end - timedelta(days=90)
            period_start, period_end = _validate_date_range(period_start, period_end)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=period_start, end_date=period_end)
        
        assignee_df = calculate_execution_success_by_assignee(df, period_start, period_end, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(assignee_df),
            'metadata': {
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/company-trend', methods=['GET'])
def get_company_trend():
    """
    Get company trend chart data (monthly).
    
    Logic: Retrieves cached data, parses query parameters (num_months, period_start/period_end, assignee, issue_type).
    Applies filters, validates date range, defaults to 6 months ago if no start date. Calls calculate_company_trend
    and returns JSON response with monthly trend metrics.
    
    Use: API endpoint for company trend chart showing monthly completion rate and lead time trends.
    
    Returns:
        JSON response with monthly data (Total Issues, Done Count, Completion Rate, Average Lead Time) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        num_months = int(request.args.get('num_months', 6))
        period_start_str = request.args.get('start_date') or request.args.get('period_start')
        period_end_str = request.args.get('end_date') or request.args.get('period_end')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if period_start_str:
            period_start = _parse_date(period_start_str)
        else:
            period_start = datetime.now(timezone.utc) - timedelta(days=180)
            period_start = period_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        period_end = None
        if period_end_str:
            period_end = _parse_date(period_end_str)
            period_start, period_end = _validate_date_range(period_start, period_end)
        else:
            period_end = datetime.now(timezone.utc)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=period_start, end_date=period_end)
        
        monthly_df = calculate_company_trend(df, period_start, num_months=num_months, period_end=period_end, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(monthly_df),
            'metadata': {
                'period_start': period_start.isoformat(),
                'num_months': num_months
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/qa-vs-failed', methods=['GET'])
def get_qa_vs_failed():
    """
    Get QA vs Failed QA chart data.
    
    Logic: Retrieves cached data, parses query parameters (period_start/period_end, assignee, issue_type, group_by).
    Applies filters, validates date range, defaults to last 3 months if no dates provided. Calls calculate_qa_vs_failed
    with group_by parameter (sprint or week) and returns JSON response with QA metrics.
    
    Use: API endpoint for QA vs failed chart showing QA executed and failed QA counts grouped by sprint or week.
    
    Returns:
        JSON response with QA data (qaExecuted, failedQA) grouped by sprint or week and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        period_start_str = request.args.get('start_date') or request.args.get('period_start')
        period_end_str = request.args.get('end_date') or request.args.get('period_end')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        group_by = request.args.get('group_by', 'sprint')
        
        if period_start_str and period_end_str:
            period_start = _parse_date(period_start_str)
            period_end = _parse_date(period_end_str)
            period_start, period_end = _validate_date_range(period_start, period_end)
        else:
            period_end = datetime.now(timezone.utc)
            period_start = period_end - timedelta(days=90)
            period_start, period_end = _validate_date_range(period_start, period_end)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=period_start, end_date=period_end)
        
        qa_df = calculate_qa_vs_failed(df, period_start, period_end, group_by=group_by, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(qa_df),
            'metadata': {
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'group_by': group_by
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/rework-ratio', methods=['GET'])
def get_rework_ratio():
    """
    Get rework ratio chart data (clean delivery vs rework).
    
    Logic: Retrieves cached data, parses query parameters (num_weeks, start_date/end_date, assignee, issue_type).
    Applies filters, validates date range, defaults to 12 weeks ago if no start date. Calls calculate_rework_ratio
    and returns JSON response with weekly rework metrics.
    
    Use: API endpoint for rework ratio chart showing clean delivery vs rework ratio per week.
    
    Returns:
        JSON response with weekly data (cleanDelivery, rework) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        num_weeks = int(request.args.get('num_weeks', 12))
        start_date_str = request.args.get('start_date') or request.args.get('period_start')
        end_date_str = request.args.get('end_date') or request.args.get('period_end')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if start_date_str:
            start_date = _parse_date(start_date_str)
        else:
            start_date = datetime.now(timezone.utc) - timedelta(weeks=num_weeks)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end_date = None
        if end_date_str:
            end_date = _parse_date(end_date_str)
            start_date, end_date = _validate_date_range(start_date, end_date)
        else:
            start_date, _ = _validate_date_range(start_date)
        
        df = apply_standard_filters(df, assignee=assignee, issue_type=issue_type, 
                                   start_date=start_date, end_date=end_date)
        
        rework_df = calculate_rework_ratio(df, start_date, num_weeks=num_weeks, df_sprints=df_sprints)
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(rework_df),
            'metadata': {
                'start_date': start_date.isoformat(),
                'num_weeks': num_weeks
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/charts/assignee-completion-trend', methods=['GET'])
def get_assignee_completion_trend():
    """
    Get assignee completion trend comparing current period vs previous period.
    
    Logic: Retrieves cached data, parses query parameters (period_start/period_end, compare_period_start/compare_period_end,
    assignee, issue_type). Applies filters, validates date ranges, defaults to last 30 days if no dates provided.
    Calls calculate_assignee_completion_trend and returns JSON response with trend metrics comparing periods.
    
    Use: API endpoint for assignee completion trend chart showing performance comparison between current and previous periods.
    
    Returns:
        JSON response with assignee trend data (completion rates, lead times, trend changes) and metadata
    """
    try:
        df, df_sprints = get_cached_data()
        
        period_start_str = request.args.get('start_date') or request.args.get('period_start')
        period_end_str = request.args.get('end_date') or request.args.get('period_end')
        compare_period_start_str = request.args.get('compare_period_start')
        compare_period_end_str = request.args.get('compare_period_end')
        assignee = request.args.get('assignee')
        issue_type = request.args.get('issueType')
        
        if period_start_str and period_end_str:
            period_start = _parse_date(period_start_str)
            period_end = _parse_date(period_end_str)
            period_start, period_end = _validate_date_range(period_start, period_end)
        else:
            period_end = datetime.now(timezone.utc)
            period_start = period_end - timedelta(days=30)
            period_start, period_end = _validate_date_range(period_start, period_end)
        
        compare_period_start = None
        compare_period_end = None
        if compare_period_start_str and compare_period_end_str:
            compare_period_start = _parse_date(compare_period_start_str)
            compare_period_end = _parse_date(compare_period_end_str)
            compare_period_start, compare_period_end = _validate_date_range(compare_period_start, compare_period_end)
        
        df = apply_standard_filters(df, assignee=None, issue_type=issue_type, 
                                   start_date=period_start, end_date=period_end)
        
        trend_df = calculate_assignee_completion_trend(
            df, 
            period_start, 
            period_end,
            compare_period_start=compare_period_start,
            compare_period_end=compare_period_end,
            assignee=assignee if assignee and assignee != "All Assignees" else None,
            df_sprints=df_sprints
        )
        
        return jsonify({
            'success': True,
            'data': _dataframe_to_dict(trend_df),
            'metadata': {
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'compare_period_start': compare_period_start.isoformat() if compare_period_start else None,
                'compare_period_end': compare_period_end.isoformat() if compare_period_end else None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/executive-summary', methods=['GET'])
def executive_summary():
    """
    Get Executive Summary KPIs.
    
    Logic: Wrapper endpoint that calls get_executive_summary from executive_summary module.
    
    Use: API endpoint for executive summary dashboard showing high-level KPIs for selected period.
    
    Returns:
        JSON response with completion_rate, avg_lead_time, rework_ratio, planned, done counts
    """
    return get_executive_summary()



