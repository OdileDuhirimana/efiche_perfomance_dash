import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


def extract_status_transitions(changelog: Dict, issue_key: str) -> List[Dict]:
    """
    Extract all status transitions from a changelog.
    
    For each status change, creates transition dict with issue_key, timestamp, from_status, to_status, and author.
    Sorts transitions by timestamp and returns list.
    
    
    Args:
        changelog: JIRA changelog dictionary with histories
        issue_key: Issue key identifier
    
    Returns:
        List of transition dictionaries sorted by timestamp
    """
    transitions = []
    
    if not changelog or "histories" not in changelog:
        return transitions
    
    for history in changelog.get("histories", []):
        timestamp = history.get("created")
        if not timestamp:
            continue
        
        author = history.get("author", {}).get("displayName", "Unknown")
        
        for item in history.get("items", []):
            if item.get("field") == "status":
                from_status = item.get("fromString", "")
                to_status = item.get("toString", "")
                
                transitions.append({
                    "issue_key": issue_key,
                    "timestamp": timestamp,
                    "from_status": from_status,
                    "to_status": to_status,
                    "author": author
                })
    
    transitions.sort(key=lambda x: x.get("timestamp", ""))
    
    return transitions


def analyze_qa_transitions(transitions: List[Dict]) -> Dict:
    """
    Analyze transitions to identify QA-related patterns.
    
    (from_status is QA and to_status is dev/in progress/to do). Returns counts and lists of entered_qa and failed_qa transitions.
    
    
    Args:
        transitions: List of status transition dictionaries
    
    Returns:
        Dictionary with entered_qa list, failed_qa list, qa_count, and failed_qa_count
    """
    qa_statuses = ["qa", "testing", "test", "review", "in review", "quality"]
    dev_statuses = ["in progress", "development", "dev", "to do", "backlog", "bug fix"]
    
    entered_qa = []
    failed_qa = []
    
    for transition in transitions:
        to_status = (transition.get("to_status", "") or "").strip().lower()
        from_status = (transition.get("from_status", "") or "").strip().lower()
        
        if any(qa_status in to_status for qa_status in qa_statuses):
            entered_qa.append({
                "timestamp": transition.get("timestamp"),
                "from_status": transition.get("from_status"),
                "to_status": transition.get("to_status")
            })
        
        if any(qa_status in from_status for qa_status in qa_statuses):
            if any(dev_term in to_status for dev_term in dev_statuses):
                failed_qa.append({
                    "timestamp": transition.get("timestamp"),
                    "from_status": transition.get("from_status"),
                    "to_status": transition.get("to_status")
                })
    
    return {
        "entered_qa": entered_qa,
        "failed_qa": failed_qa,
        "qa_count": len(entered_qa),
        "failed_qa_count": len(failed_qa)
    }


def analyze_rework_patterns(transitions: List[Dict]) -> Dict:
    """
    Analyze transitions to identify rework patterns.
    
    For each transition, calculates workflow positions of from_status and to_status. Detects rework when to_pos < from_pos
    (moving backward in workflow). Returns rework count, transitions list, and has_rework flag.
    
    
    Args:
        transitions: List of status transition dictionaries
    
    Returns:
        Dictionary with rework_count, rework_transitions list, and has_rework boolean
    """
    workflow_order = {
        "backlog": 0,
        "to do": 1,
        "not done": 1,
        "in progress": 2,
        "development": 2,
        "dev": 2,
        "qa": 3,
        "testing": 3,
        "test": 3,
        "review": 3,
        "in review": 3,
        "ready for deployment": 4,
        "done": 5,
        "resolved": 5,
        "closed": 6
    }
    
    def get_workflow_position(status: str) -> int:
        """
        Get workflow position for a status.
        
            Returns 0 for unknown statuses.
        
            
        Args:
            status: Status string
        
        Returns:
            Workflow position integer (0-6)
        """
        status_lower = (status or "").lower().strip()
        for key, pos in workflow_order.items():
            if key in status_lower:
                return pos
        return 0
    
    rework_transitions = []
    
    for transition in transitions:
        from_status = transition.get("from_status", "")
        to_status = transition.get("to_status", "")
        
        from_pos = get_workflow_position(from_status)
        to_pos = get_workflow_position(to_status)
        
        if to_pos < from_pos and from_pos > 0:
            rework_transitions.append({
                "timestamp": transition.get("timestamp"),
                "from_status": from_status,
                "to_status": to_status,
                "from_position": from_pos,
                "to_position": to_pos,
                "backward_steps": from_pos - to_pos
            })
    
    return {
        "rework_count": len(rework_transitions),
        "rework_transitions": rework_transitions,
        "has_rework": len(rework_transitions) > 0
    }


def map_status_to_category(status: str, from_status: str = None) -> str:
    """
    Map Jira status to one of 4 categories: Not Done, In Progress, In QA, or Done.
    
    Maps statuses to categories: qa/testing/review -> In QA, to do/backlog/open -> Not Done, in progress/development -> In Progress,
    done/closed/resolved -> Done. Returns 'Not Done' as default for unknown statuses.
    
    
    Args:
        status: JIRA status string
        from_status: Optional previous status for context (used for bug fix rework detection)
    
    Returns:
        Category string: 'Not Done', 'In Progress', 'In QA', or 'Done'
    """
    if not status or pd.isna(status):
        return 'Not Done'
    
    status_lower = str(status).lower().strip()
    from_status_lower = str(from_status).lower().strip() if from_status else ""
    
    if status_lower in ['bug fix', 'bugfix']:
        if from_status_lower in ['qa', 'quality assurance', 'testing', 'test', 'review', 'in review', 'qa testing']:
            return 'In Progress'
    
    if status_lower in ['qa', 'quality assurance', 'testing', 'bugfix', 
                    'review', 'in review', 'qa testing', 'test']:
        return 'In QA'
    elif status_lower in ['bug fix', 'bugfix']:
        return 'In QA'
    elif status_lower in ['to do', 'backlog', 'open', 'new', 'todo', 'not done', "won't do", "wont do"]:
        return 'Not Done'
    elif status_lower in ['in progress', 'inprogress', 'active', 'development', 'doing']:
        return 'In Progress'
    elif status_lower in ['done', 'closed', 'ready for deployment', 'resolved', 'deployed', 
                    'completed', 'finished']:
        return 'Done'
    else:
        return 'Not Done'


def calculate_lead_time_from_transitions(transitions: List[Dict], created_date: str, resolved_date: Optional[str]) -> Dict:
    """
    Calculate lead time metrics from changelog transitions.
    
    (first work-related status transition), calculates time between transitions, tracks time in each status/category,
    calculates time from last transition to resolved. Computes total lead time from work start to resolved,
    time in progress, time in QA, and time to first progress. Returns comprehensive metrics dictionary.
    
    not just creation date.
    
    Args:
        transitions: List of status transition dictionaries
        created_date: Issue creation date string (ISO format)
        resolved_date: Optional issue resolution date string (ISO format)
    
    Returns:
        Dictionary with lead_time_days, time_in_progress, time_in_qa, time_to_first_progress, status_breakdown, category_breakdown
    """
    if not transitions:
        try:
            created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            resolved = None
            if resolved_date:
                resolved = datetime.fromisoformat(resolved_date.replace('Z', '+00:00'))
                lead_time_days = (resolved - created).total_seconds() / 86400
            else:
                lead_time_days = None
            
            return {
                "lead_time_days": round(lead_time_days, 2) if lead_time_days else None,
                "time_in_progress": None,
                "time_in_qa": None,
                "time_to_first_progress": None,
                "status_breakdown": {}
            }
        except:
            return {
                "lead_time_days": None,
                "time_in_progress": None,
                "time_in_qa": None,
                "time_to_first_progress": None,
                "status_breakdown": {}
            }
    
    try:
        created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        sorted_transitions = sorted(transitions, key=lambda x: x.get("timestamp", ""))
        
        work_start_date = None
        work_start_status = None
        work_start_statuses = ["to do", "todo", "not done", "open", "new", "backlog", 
                              "in progress", "inprogress", "development", "dev"]
        
        for transition in sorted_transitions:
            to_status = (transition.get("to_status", "") or "").lower()
            from_status = (transition.get("from_status", "") or "").lower()
            
            if any(work_status in to_status for work_status in work_start_statuses):
                try:
                    work_start_date = datetime.fromisoformat(transition.get("timestamp", "").replace('Z', '+00:00'))
                    work_start_status = transition.get("to_status", "")
                    break
                except:
                    continue
        
        if work_start_date is None:
            if sorted_transitions:
                try:
                    first_transition = sorted_transitions[0]
                    work_start_date = datetime.fromisoformat(first_transition.get("timestamp", "").replace('Z', '+00:00'))
                    work_start_status = first_transition.get("to_status", "")
                except:
                    work_start_date = created
                    work_start_status = "Unknown"
            else:
                    work_start_date = created
                    work_start_status = "Unknown"
        
        first_progress = None
        for transition in sorted_transitions:
            to_status = transition.get("to_status", "").lower()
            if "in progress" in to_status or "development" in to_status or "dev" in to_status:
                try:
                    first_progress = datetime.fromisoformat(transition.get("timestamp").replace('Z', '+00:00'))
                    break
                except:
                    continue
        
        status_times = {}
        category_times = {}
        
        if sorted_transitions:
            try:
                first_transition_time = datetime.fromisoformat(sorted_transitions[0].get("timestamp").replace('Z', '+00:00'))
                initial_status = sorted_transitions[0].get("from_status", "Unknown")
                
                if first_transition_time > work_start_date:
                    initial_duration = (first_transition_time - work_start_date).total_seconds() / 86400
                    if initial_status not in status_times:
                        status_times[initial_status] = 0
                    status_times[initial_status] += initial_duration
                    
                    initial_category = map_status_to_category(initial_status)
                    if initial_category not in category_times:
                        category_times[initial_category] = 0
                    category_times[initial_category] += initial_duration
            except:
                pass
        
        for i in range(len(sorted_transitions) - 1):
            try:
                current = datetime.fromisoformat(sorted_transitions[i].get("timestamp").replace('Z', '+00:00'))
                next_time = datetime.fromisoformat(sorted_transitions[i + 1].get("timestamp").replace('Z', '+00:00'))
                status = sorted_transitions[i].get("to_status", "")
                from_status = sorted_transitions[i].get("from_status", "")
                duration = (next_time - current).total_seconds() / 86400
                
                if status not in status_times:
                    status_times[status] = 0
                status_times[status] += duration
                
                category = map_status_to_category(status, from_status)
                if category not in category_times:
                    category_times[category] = 0
                category_times[category] += duration
            except:
                continue
        
        resolved = None
        if resolved_date:
            try:
                resolved = datetime.fromisoformat(resolved_date.replace('Z', '+00:00'))
            except:
                pass
        
        if resolved and sorted_transitions:
            try:
                last_transition_time = datetime.fromisoformat(sorted_transitions[-1].get("timestamp").replace('Z', '+00:00'))
                final_status = sorted_transitions[-1].get("to_status", "")
                final_from_status = sorted_transitions[-1].get("from_status", "")
                if resolved > last_transition_time:
                    final_duration = (resolved - last_transition_time).total_seconds() / 86400
                    if final_status not in status_times:
                        status_times[final_status] = 0
                    status_times[final_status] += final_duration
                    
                    final_category = map_status_to_category(final_status, final_from_status)
                    if final_category not in category_times:
                        category_times[final_category] = 0
                    category_times[final_category] += final_duration
            except:
                pass
        
        if not resolved:
            if sorted_transitions:
                try:
                    last_transition = sorted_transitions[-1]
                    resolved = datetime.fromisoformat(last_transition.get("timestamp").replace('Z', '+00:00'))
                except:
                    resolved = created
            else:
                resolved = created
        
        lead_time_days = (resolved - work_start_date).total_seconds() / 86400
        lead_time_from_created = (resolved - created).total_seconds() / 86400
        
        time_in_progress = category_times.get('In Progress', 0)
        time_in_qa = category_times.get('In QA', 0)
        time_in_not_done = category_times.get('Not Done', 0)
        time_in_done = category_times.get('Done', 0)
        
        return {
            "lead_time_days": round(lead_time_days, 2),
            "lead_time_from_created": round(lead_time_from_created, 2),
            "work_start_date": work_start_date.isoformat() if work_start_date else None,
            "work_start_status": work_start_status,
            "time_in_progress": round(time_in_progress, 2),
            "time_in_qa": round(time_in_qa, 2),
            "time_in_not_done": round(time_in_not_done, 2),
            "time_in_done": round(time_in_done, 2),
            "time_to_first_progress": round((first_progress - work_start_date).total_seconds() / 86400, 2) if first_progress and work_start_date else None,
            "status_breakdown": {k: round(v, 2) for k, v in status_times.items()},
            "category_breakdown": {k: round(v, 2) for k, v in category_times.items()}
        }
    except Exception as e:
        return {
            "lead_time_days": None,
            "time_in_progress": None,
            "time_in_qa": None,
            "time_to_first_progress": None,
            "error": str(e)
        }


def get_status_at_date(transitions: List[Dict], target_date: datetime) -> Optional[str]:
    """
    Get the status of an issue at a specific date.
    
    If no transitions before target_date, returns first transition's from_status. Returns None if no transitions.
    
    
    Args:
        transitions: List of status transition dictionaries sorted by timestamp
        target_date: Target datetime to check status at
    
    Returns:
        Status string at target date, or None
    """
    if not transitions:
        return None
    
    for transition in reversed(transitions):
        try:
            trans_date = datetime.fromisoformat(transition.get("timestamp", "").replace('Z', '+00:00'))
            if trans_date <= target_date:
                return transition.get("to_status")
        except:
            continue
    
    if transitions:
        return transitions[0].get("from_status")
    
    return None


def is_in_progress_at_date(transitions: List[Dict], target_date: datetime) -> bool:
    """
    Check if issue was in progress at a specific date.
    
    
    
    Args:
        transitions: List of status transition dictionaries
        target_date: Target datetime to check
    
    Returns:
        True if issue was in progress at target_date, False otherwise
    """
    status = get_status_at_date(transitions, target_date)
    if not status:
        return False
    
    status_lower = status.lower()
    return "in progress" in status_lower or "development" in status_lower


def was_completed_during_period(transitions: List[Dict], start_date: datetime, end_date: datetime) -> bool:
    """
    Check if issue was completed (moved to Done) during a specific period.
    
    and to_status contains done/resolved/closed keywords. Returns True if such transition found.
    
    
    Args:
        transitions: List of status transition dictionaries
        start_date: Period start datetime
        end_date: Period end datetime
    
    Returns:
        True if issue was completed during period, False otherwise
    """
    for transition in transitions:
        try:
            trans_date = datetime.fromisoformat(transition.get("timestamp", "").replace('Z', '+00:00'))
            if start_date <= trans_date <= end_date:
                to_status = (transition.get("to_status", "") or "").lower()
                if "done" in to_status or "resolved" in to_status or "closed" in to_status:
                    return True
        except:
            continue
    
    return False


def is_active_status(status: str) -> bool:
    """
    Check if a status represents active work (not done, not backlog).
    
    Returns True for all other statuses (in progress, qa, etc.).
    
    
    Args:
        status: Status string to check
    
    Returns:
        True if status represents active work, False otherwise
    """
    if not status:
        return False
    
    status_lower = status.lower()
    
    if any(term in status_lower for term in ["done", "resolved", "closed", "deployed", "completed"]):
        return False
    
    if any(term in status_lower for term in ["backlog", "new", "open"]):
        return False
    
    return True
