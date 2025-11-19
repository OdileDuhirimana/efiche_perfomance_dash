#!/usr/bin/env python3
"""
Comprehensive Dashboard Data Accuracy Test

Tests multiple date ranges to verify data consistency across all charts
and the executive summary.
"""

import requests
import json
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8050/api"

def test_date_range(start_date, end_date, description):
    """Test a specific date range and verify all data is consistent"""
    print("\n" + "=" * 80)
    print(f"TESTING: {description}")
    print("=" * 80)
    print(f"Date Range: {start_date} to {end_date}\n")
    
    results = {
        'executive_summary': None,
        'weekly_planned_vs_done': None,
        'weekly_flow': None,
        'weekly_lead_time': None,
        'rework_ratio': None,
        'task_load': None,
        'execution_success': None,
        'company_trend': None,
        'qa_vs_failed': None,
        'errors': []
    }
    
    # 1. Executive Summary
    try:
        exec_summary = requests.get(
            f"{BASE_URL}/executive-summary?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if exec_summary['success']:
            results['executive_summary'] = exec_summary['data']
        else:
            results['errors'].append(f"Executive Summary: {exec_summary.get('error')}")
    except Exception as e:
        results['errors'].append(f"Executive Summary: {str(e)}")
    
    if not results['executive_summary']:
        print("❌ Cannot continue - Executive Summary failed")
        return results
    
    es = results['executive_summary']
    
    # 2. Weekly Planned vs Done
    try:
        weekly_pvd = requests.get(
            f"{BASE_URL}/charts/weekly-planned-vs-done?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if weekly_pvd['success']:
            data = weekly_pvd['data']
            total_done = sum(w.get('Done', 0) for w in data)
            total_planned = sum(w.get('Planned', 0) for w in data)
            results['weekly_planned_vs_done'] = {
                'total_done': total_done,
                'total_planned': total_planned,
                'done_matches': total_done == es['done'],
                'planned_matches': total_planned == es['planned'],
                'weeks': len(data)
            }
        else:
            results['errors'].append(f"Weekly Planned vs Done: {weekly_pvd.get('error')}")
    except Exception as e:
        results['errors'].append(f"Weekly Planned vs Done: {str(e)}")
    
    # 3. Weekly Flow
    try:
        weekly_flow = requests.get(
            f"{BASE_URL}/charts/weekly-flow?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if weekly_flow['success']:
            data = weekly_flow['data']
            total_done = sum(w.get('Done', 0) for w in data)
            results['weekly_flow'] = {
                'total_done': total_done,
                'done_matches': total_done == es['done'],
                'weeks': len(data)
            }
        else:
            results['errors'].append(f"Weekly Flow: {weekly_flow.get('error')}")
    except Exception as e:
        results['errors'].append(f"Weekly Flow: {str(e)}")
    
    # 4. Weekly Lead Time
    try:
        weekly_lt = requests.get(
            f"{BASE_URL}/charts/weekly-lead-time?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if weekly_lt['success']:
            data = weekly_lt['data']
            total_count = sum(w.get('Resolved Issues Count', 0) for w in data)
            total_lt = sum(
                w.get('Average Lead Time (days)', 0) * w.get('Resolved Issues Count', 0)
                for w in data if w.get('Resolved Issues Count', 0) > 0
            )
            avg_lt = total_lt / total_count if total_count > 0 else 0
            results['weekly_lead_time'] = {
                'count': total_count,
                'avg_lead_time': avg_lt,
                'count_valid': total_count <= es['done'],
                'lt_matches': abs(avg_lt - es['avg_lead_time']) < 0.1
            }
        else:
            results['errors'].append(f"Weekly Lead Time: {weekly_lt.get('error')}")
    except Exception as e:
        results['errors'].append(f"Weekly Lead Time: {str(e)}")
    
    # 5. Rework Ratio
    try:
        rework = requests.get(
            f"{BASE_URL}/charts/rework-ratio?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if rework['success']:
            data = rework['data']
            total_rework = sum(w.get('Rework Count', 0) for w in data)
            total_resolved = sum(w.get('Resolved Count', 0) for w in data)
            ratio = total_rework / total_resolved if total_resolved > 0 else 0
            results['rework_ratio'] = {
                'rework_count': total_rework,
                'resolved_count': total_resolved,
                'ratio': ratio,
                'rework_matches': total_rework == es['rework_count'],
                'resolved_matches': total_resolved == es['total_resolved'],
                'ratio_matches': abs(ratio - es['rework_ratio']) < 0.001
            }
        else:
            results['errors'].append(f"Rework Ratio: {rework.get('error')}")
    except Exception as e:
        results['errors'].append(f"Rework Ratio: {str(e)}")
    
    # 6. Task Load
    try:
        task_load = requests.get(
            f"{BASE_URL}/charts/task-load?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if task_load['success']:
            data = task_load['data']
            total_planned = sum(a.get('Task Count', 0) for a in data)
            results['task_load'] = {
                'total_planned': total_planned,
                'planned_matches': total_planned == es['planned']
            }
        else:
            results['errors'].append(f"Task Load: {task_load.get('error')}")
    except Exception as e:
        results['errors'].append(f"Task Load: {str(e)}")
    
    # 7. Execution Success
    try:
        exec_success = requests.get(
            f"{BASE_URL}/charts/execution-success?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if exec_success['success']:
            data = exec_success['data']
            total_planned = sum(a.get('Total Assigned', 0) for a in data)
            total_done = sum(a.get('Done/Ready for Deployment', 0) for a in data)
            results['execution_success'] = {
                'total_planned': total_planned,
                'total_done': total_done,
                'planned_matches': total_planned == es['planned'],
                'done_matches': total_done == es['done']
            }
        else:
            results['errors'].append(f"Execution Success: {exec_success.get('error')}")
    except Exception as e:
        results['errors'].append(f"Execution Success: {str(e)}")
    
    # 8. Company Trend
    try:
        company_trend = requests.get(
            f"{BASE_URL}/charts/company-trend?start_date={start_date}&end_date={end_date}",
            timeout=15
        ).json()
        if company_trend['success']:
            data = company_trend['data']
            results['company_trend'] = {
                'num_months': len(data),
                'months': [m.get('Month', 'N/A') for m in data]
            }
        else:
            results['errors'].append(f"Company Trend: {company_trend.get('error')}")
    except Exception as e:
        results['errors'].append(f"Company Trend: {str(e)}")
    
    # 9. QA vs Failed
    try:
        qa_failed = requests.get(
            f"{BASE_URL}/charts/qa-vs-failed?start_date={start_date}&end_date={end_date}&group_by=week",
            timeout=15
        ).json()
        if qa_failed['success']:
            data = qa_failed['data']
            total_qa = sum(w.get('qaExecuted', 0) for w in data)
            total_failed = sum(w.get('failedQA', 0) for w in data)
            results['qa_vs_failed'] = {
                'total_qa': total_qa,
                'total_failed': total_failed,
                'num_weeks': len(data)
            }
        else:
            results['errors'].append(f"QA vs Failed: {qa_failed.get('error')}")
    except Exception as e:
        results['errors'].append(f"QA vs Failed: {str(e)}")
    
    # Print results
    print("EXECUTIVE SUMMARY (Source of Truth):")
    print(f"  Planned: {es['planned']}")
    print(f"  Done: {es['done']}")
    print(f"  Completion Rate: {es['completion_rate']}%")
    print(f"  Avg Lead Time: {es['avg_lead_time']} days")
    print(f"  Rework Ratio: {es['rework_ratio']:.3f} ({es['rework_ratio'] * 100:.1f}%)")
    print(f"  Rework Count: {es['rework_count']}")
    print(f"  Total Resolved: {es['total_resolved']}")
    
    print("\nDATA CONSISTENCY CHECKS:")
    print("-" * 80)
    
    all_good = True
    
    if results['weekly_planned_vs_done']:
        wpvd = results['weekly_planned_vs_done']
        done_match = wpvd['done_matches']
        planned_match = wpvd['planned_matches']
        status_done = "✅" if done_match else "❌"
        status_planned = "✅" if planned_match else "⚠️"
        print(f"{status_done} Weekly Planned vs Done - Done: {wpvd['total_done']} (ES: {es['done']}, Match: {done_match})")
        print(f"{status_planned} Weekly Planned vs Done - Planned: {wpvd['total_planned']} (ES: {es['planned']}, Match: {planned_match})")
        print(f"   Note: Planned may differ due to issues counted in multiple weeks (Created OR Updated)")
        if not done_match:
            all_good = False
    
    if results['weekly_flow']:
        match = results['weekly_flow']['done_matches']
        status = "✅" if match else "❌"
        print(f"{status} Weekly Flow - Done: {results['weekly_flow']['total_done']} (ES: {es['done']}, Match: {match})")
        if not match:
            all_good = False
    
    if results['rework_ratio']:
        rw = results['rework_ratio']
        match = rw['rework_matches'] and rw['resolved_matches'] and rw['ratio_matches']
        status = "✅" if match else "❌"
        print(f"{status} Rework Ratio: Rework={rw['rework_count']}, Resolved={rw['resolved_count']}, Ratio={rw['ratio']:.3f}")
        if not match:
            all_good = False
    
    if results['task_load']:
        match = results['task_load']['planned_matches']
        status = "✅" if match else "❌"
        print(f"{status} Task Load - Planned: {results['task_load']['total_planned']} (ES: {es['planned']}, Match: {match})")
        if not match:
            all_good = False
    
    if results['execution_success']:
        es_data = results['execution_success']
        match = es_data['planned_matches'] and es_data['done_matches']
        status = "✅" if match else "❌"
        print(f"{status} Execution Success - Planned: {es_data['total_planned']}, Done: {es_data['total_done']}")
        if not match:
            all_good = False
    
    # 6. QA vs Failed QA
    if results['qa_vs_failed']:
        qa_data = results['qa_vs_failed']
        status = "✅"
        print(f"{status} QA vs Failed QA - Total QA Executed: {qa_data['total_qa']}, Total Failed QA: {qa_data['total_failed']}")
        print(f"   Weeks included: {qa_data['num_weeks']}")
        print(f"   Note: QA counts are verified for data consistency (no direct ES comparison)")
        # QA vs Failed doesn't have a direct comparison in executive summary, but we verify it's calculated
        # The total_failed should be <= total_qa (logical check)
        if qa_data['total_failed'] > qa_data['total_qa']:
            print(f"   ⚠️  WARNING: Failed QA ({qa_data['total_failed']}) > QA Executed ({qa_data['total_qa']}) - this seems incorrect")
            all_good = False
    
    if results['errors']:
        print(f"\n⚠️  ERRORS:")
        for error in results['errors']:
            print(f"  - {error}")
        all_good = False
    
    print(f"\n{'✅ ALL CRITICAL CHECKS PASSED' if all_good else '❌ SOME CRITICAL CHECKS FAILED'}")
    
    return results


if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    # Get current date or use a reference date
    base_date = datetime(2025, 11, 19, tzinfo=timezone.utc)  # Use Nov 19 as reference
    
    # Test multiple date ranges of different lengths
    test_ranges = []
    
    # 1 week range (7 days)
    end_date = base_date
    start_date = end_date - timedelta(days=6)  # 7 days total
    test_ranges.append((
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        f"1 Week Range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"
    ))
    
    # 2 weeks range (14 days)
    start_date = end_date - timedelta(days=13)
    test_ranges.append((
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        f"2 Weeks Range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"
    ))
    
    # 3 weeks range (21 days)
    start_date = end_date - timedelta(days=20)
    test_ranges.append((
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        f"3 Weeks Range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"
    ))
    
    # 1 month range (approximately 30 days)
    start_date = end_date - timedelta(days=29)
    test_ranges.append((
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        f"1 Month Range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"
    ))
    
    # 2 months range (approximately 60 days)
    start_date = end_date - timedelta(days=59)
    test_ranges.append((
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        f"2 Months Range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"
    ))
    
    # 3 months range (approximately 90 days)
    start_date = end_date - timedelta(days=89)
    test_ranges.append((
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        f"3 Months Range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"
    ))
    
    # 4 months range (approximately 120 days)
    start_date = end_date - timedelta(days=119)
    test_ranges.append((
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        f"4 Months Range ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"
    ))
    
    # Test ranges that partially include weeks (mid-week starts/ends)
    # Start mid-week, end mid-week
    mid_week_start = base_date - timedelta(days=base_date.weekday() + 3)  # Wednesday
    mid_week_end = base_date - timedelta(days=base_date.weekday() - 3)  # Wednesday
    if mid_week_start < mid_week_end:
        test_ranges.append((
            mid_week_start.strftime('%Y-%m-%d'),
            mid_week_end.strftime('%Y-%m-%d'),
            f"Mid-Week Range ({mid_week_start.strftime('%b %d')} - {mid_week_end.strftime('%b %d')})"
        ))
    
    # Start mid-week, end at month boundary
    month_end = datetime(2025, 10, 31, tzinfo=timezone.utc)
    mid_start = month_end - timedelta(days=10)
    test_ranges.append((
        mid_start.strftime('%Y-%m-%d'),
        month_end.strftime('%Y-%m-%d'),
        f"Mid-Week to Month End ({mid_start.strftime('%b %d')} - {month_end.strftime('%b %d')})"
    ))
    
    # Original test ranges
    test_ranges.extend([
        ("2025-08-21", "2025-11-19", "Original Range (Aug 21 - Nov 19)"),
        ("2025-09-01", "2025-10-31", "September-October (Sep 1 - Oct 31)"),
        ("2025-10-01", "2025-10-31", "October Only (Oct 1 - Oct 31)"),
        ("2025-08-01", "2025-08-31", "August Only (Aug 1 - Aug 31)"),
        ("2025-11-01", "2025-11-30", "November Only (Nov 1 - Nov 30)"),
    ])
    
    print("=" * 80)
    print("COMPREHENSIVE DASHBOARD DATA ACCURACY TEST")
    print("=" * 80)
    print("Testing multiple date ranges to verify data consistency...")
    
    all_results = []
    for start_date, end_date, description in test_ranges:
        result = test_date_range(start_date, end_date, description)
        all_results.append((description, result))
    
    # Summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    for desc, result in all_results:
        if result['errors']:
            print(f"❌ {desc}: {len(result['errors'])} errors")
        else:
            critical_checks = [
                result.get('weekly_planned_vs_done', {}).get('done_matches', False),
                result.get('weekly_flow', {}).get('done_matches', False),
                result.get('rework_ratio', {}).get('rework_matches', False),
                result.get('task_load', {}).get('planned_matches', False),
                result.get('execution_success', {}).get('planned_matches', False),
            ]
            checks_passed = sum(critical_checks)
            print(f"{'✅' if checks_passed == 5 else '⚠️'} {desc}: {checks_passed}/5 critical checks passed")
    
    print("\n" + "=" * 80)
    print("NOTE: Planned counts may differ between weekly charts and executive summary")
    print("because weekly charts count issues in each week where they were Created OR Updated,")
    print("while executive summary counts each issue only once. This is expected behavior.")
    print("=" * 80)

