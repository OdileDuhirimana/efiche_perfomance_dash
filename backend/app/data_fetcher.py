import requests
import pandas as pd
import json
from app.config import AUTH, HEADERS, DOMAIN
from app.services.changelog_processor import (
    extract_status_transitions,
    analyze_qa_transitions,
    analyze_rework_patterns,
    calculate_lead_time_from_transitions,
    map_status_to_category
)


def extract_description(description_field):
    """
    Extract plain text description from Jira's Atlassian Document Format.
    
    Iterates through content array, finds text type sub-blocks, and joins all text parts into single string.
    
    
    Args:
        description_field: Atlassian Document Format dictionary with content structure
    
    Returns:
        Plain text description string or None
    """
    if not description_field:
        return None
    try:
        content = description_field.get("content", [])
        description_parts = []
        for block in content:
            if "content" in block:
                for sub_block in block["content"]:
                    if sub_block.get("type") == "text":
                        description_parts.append(sub_block.get("text", ""))
        return " ".join(description_parts).strip() if description_parts else None
    except Exception as e:
        print(f"Error extracting description: {e}")
        return None


def get_field_id_map():
    """
    Fetch custom field IDs from Jira API.
    
    Creates mapping dictionary from field name to field ID for custom fields like Sprint, Story Points, etc.
    
    
    Returns:
        Dictionary mapping field names to field IDs
    """
    res = requests.get(f"{DOMAIN}/rest/api/3/field", headers=HEADERS, auth=AUTH)
    field_map = {}
    if res.status_code == 200:
        for field in res.json():
            field_map[field["name"]] = field["id"]
    return field_map


def get_boards():
    """
    Fetch all boards from Jira Agile API.
    
    and maxResults parameters. Continues until all boards are fetched or error occurs.
    
    
    Returns:
        List of board dictionaries with id, name, and other board properties
    """
    boards = []
    start_at = 0
    
    while True:
        params = {"startAt": start_at, "maxResults": 50}
        res = requests.get(f"{DOMAIN}/rest/agile/1.0/board", headers=HEADERS, auth=AUTH, params=params)
        
        if res.status_code != 200:
            print(f"Failed to fetch boards: {res.status_code} - {res.text}")
            break
        
        data = res.json()
        values = data.get("values", [])
        if not values:
            break
        
        boards.extend(values)
        start_at += len(values)
        
        if start_at >= data.get("total", 0):
            break
    
    return boards


def get_sprints_from_boards():
    """
    Fetch all sprints from all boards.
    
    Extracts sprint details (id, name, state, dates, goal) and avoids duplicates using sprint_ids_seen set.
    Returns DataFrame with sprint information.
    
    
    Returns:
        DataFrame with columns: Sprint Id, Sprint Name, Sprint State, Sprint Start Date, Sprint End Date,
        Sprint Complete Date, Sprint Goal, Board Id, Board Name
    """
    print("Fetching boards and sprints...")
    boards = get_boards()
    all_sprints = []
    sprint_ids_seen = set()
    
    for board in boards:
        board_id = board.get("id")
        if not board_id:
            continue
        
        print(f"Fetching sprints from board {board_id} ({board.get('name', 'Unknown')})...")
        start_at = 0
        
        while True:
            params = {"startAt": start_at, "maxResults": 50}
            res = requests.get(
                f"{DOMAIN}/rest/agile/1.0/board/{board_id}/sprint",
                headers=HEADERS,
                auth=AUTH,
                params=params
            )
            
            if res.status_code != 200:
                print(f"Warning: Failed to fetch sprints for board {board_id}: {res.status_code}")
                break
            
            data = res.json()
            values = data.get("values", [])
            if not values:
                break
            
            for sprint in values:
                sprint_id = sprint.get("id")
                if sprint_id and sprint_id not in sprint_ids_seen:
                    sprint_ids_seen.add(sprint_id)
                    all_sprints.append({
                        "Sprint Id": sprint_id,
                        "Sprint Name": sprint.get("name", ""),
                        "Sprint State": sprint.get("state", ""),
                        "Sprint Start Date": sprint.get("startDate"),
                        "Sprint End Date": sprint.get("endDate"),
                        "Sprint Complete Date": sprint.get("completeDate"),
                        "Sprint Goal": sprint.get("goal", ""),
                        "Board Id": board_id,
                        "Board Name": board.get("name", "")
                    })
            
            start_at += len(values)
            if start_at >= data.get("total", 0):
                break
    
    print(f"Fetched {len(all_sprints)} unique sprints from {len(boards)} boards")
    return pd.DataFrame(all_sprints)


def fetch_jira_data():
    """
    Fetch all Jira issues and return as DataFrame.
    
    in open or closed sprints. For each issue, extracts fields, changelog, sprint information, and analyzes transitions
    for QA, rework, and lead time. Merges sprint details from Agile API. Creates Primary Sprint Id from first sprint.
    Maps status to category and converts date columns to datetime.
    
    
    Returns:
        DataFrame with all issue fields, sprint information, transition analysis, and calculated metrics
    """
    print("Starting Jira data fetch...")
    
    print("Fetching custom field mappings...")
    custom_fields = get_field_id_map()
    
    FIELD_SPRINT = custom_fields.get("Sprint")
    FIELD_STORY_POINTS = custom_fields.get("Story point estimate")
    FIELD_RANK = custom_fields.get("Rank")
    FIELD_ISSUE_COLOR = custom_fields.get("Issue color")
    FIELD_DEVELOPMENT = custom_fields.get("Development")
    FIELD_START_DATE = custom_fields.get("Start date")
    FIELD_TEAM_ID = custom_fields.get("Team Id")
    FIELD_TEAM_NAME = custom_fields.get("Team Name")
    FIELD_VULNERABILITY = custom_fields.get("Vulnerability")
    
    BASE_URL = f"{DOMAIN}/rest/api/3/search/jql"
    max_results = 100
    all_issues = []
    next_page_token = None
    
    print("Fetching issues from Jira...")
    while True:
        params = {
            "jql": "sprint in (openSprints(), closedSprints()) ORDER BY created DESC",
            "maxResults": max_results,
            "fields": "*all",
            "expand": "renderedFields,changelog"
        }
        
        if next_page_token:
            params["nextPageToken"] = next_page_token
        
        res = requests.get(BASE_URL, headers=HEADERS, auth=AUTH, params=params)
        
        if res.status_code != 200:
            print(f"Failed to fetch issues: {res.status_code} - {res.text}")
            break
        
        json_data = res.json()
        issues = json_data.get("issues", [])
        
        if not issues:
            print("No more issues to fetch")
            break
            
        for issue in issues:
            if "fields" not in issue:
                print(f"Warning: Issue {issue.get('key', 'unknown')} has no fields, skipping...")
                continue
                
            fields = issue["fields"]
            
            attachments = fields.get("attachment", [])
            attachment_names = [a.get("filename") for a in attachments]
            
            comments = fields.get("comment", {}).get("comments", [])
            comment_bodies = []
            for c in comments:
                body = c.get("body", "")
                if isinstance(body, dict):
                    comment_bodies.append(extract_description(body) or "")
                else:
                    comment_bodies.append(str(body) if body else "")
            
            changelog = issue.get("changelog", {})
            issue_key = issue.get("key")
            transitions = extract_status_transitions(changelog, issue_key)
            qa_analysis = analyze_qa_transitions(transitions)
            rework_analysis = analyze_rework_patterns(transitions)
            created = fields.get("created")
            resolved = fields.get("resolutiondate")
            lead_time_analysis = calculate_lead_time_from_transitions(transitions, created, resolved) if created else {}
            
            sprints = fields.get(FIELD_SPRINT)
            sprint_ids = []
            sprint_names = []
            sprint_states = []
            sprint_start_dates = []
            sprint_end_dates = []
            sprint_complete_dates = []
            
            if not sprints:
                sprint_ids = []
                sprint_names = []
                sprint_states = []
            elif isinstance(sprints, dict):
                sprint_ids = [sprints.get("id")]
                sprint_names = [sprints.get("name")]
                sprint_states = [sprints.get("state")]
                sprint_start_dates = [sprints.get("startDate")]
                sprint_end_dates = [sprints.get("endDate")]
                sprint_complete_dates = [sprints.get("completeDate")]
            else:
                for s in sprints:
                    if isinstance(s, dict):
                        sprint_ids.append(s.get("id"))
                        sprint_names.append(s.get("name"))
                        sprint_states.append(s.get("state"))
                        sprint_start_dates.append(s.get("startDate"))
                        sprint_end_dates.append(s.get("endDate"))
                        sprint_complete_dates.append(s.get("completeDate"))

            all_issues.append({
                "Summary": fields.get("summary"),
                "Issue key": issue.get("key"),
                "Issue id": issue.get("id"),
                "Issue Type": fields.get("issuetype", {}).get("name"),
                "Status": fields.get("status", {}).get("name"),
                "Project key": fields.get("project", {}).get("key"),
                "Project name": fields.get("project", {}).get("name"),
                "Project type": fields.get("project", {}).get("projectTypeKey"),
                "Project lead": fields.get("project", {}).get("lead", {}).get("displayName"),
                "Project lead id": fields.get("project", {}).get("lead", {}).get("accountId"),
                "Project description": fields.get("project", {}).get("description"),
                "Priority": fields.get("priority", {}).get("name"),
                "Resolution": fields.get("resolution", {}).get("name") if fields.get("resolution") else None,
                "Assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                "Assignee Id": fields.get("assignee", {}).get("accountId") if fields.get("assignee") else None,
                "Reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
                "Reporter Id": fields.get("reporter", {}).get("accountId") if fields.get("reporter") else None,
                "Creator": fields.get("creator", {}).get("displayName") if fields.get("creator") else None,
                "Creator Id": fields.get("creator", {}).get("accountId") if fields.get("creator") else None,
                "Created": fields.get("created"),
                "Updated": fields.get("updated"),
                "Last Viewed": fields.get("lastViewed"),
                "Resolved": fields.get("resolutiondate"),
                "Due date": fields.get("duedate"),
                "Votes": fields.get("votes", {}).get("votes"),
                "Labels": ", ".join(fields.get("labels", [])),
                "Description": extract_description(fields.get("description")),
                "Environment": fields.get("environment"),
                "Watchers": fields.get("watches", {}).get("watchCount"),
                "Original estimate": fields.get("timeoriginalestimate"),
                "Remaining Estimate": fields.get("timeestimate"),
                "Time Spent": fields.get("timespent"),
                "Work Ratio": fields.get("workratio"),
                "Σ Original Estimate": fields.get("aggregatetimeoriginalestimate"),
                "Σ Remaining Estimate": fields.get("aggregatetimeestimate"),
                "Σ Time Spent": fields.get("aggregatetimespent"),
                "Security Level": fields.get("security", {}).get("name") if fields.get("security") else None,
                "Attachment": ", ".join(attachment_names),
                "Custom field (Development)": fields.get(FIELD_DEVELOPMENT),
                "Custom field (Issue color)": fields.get(FIELD_ISSUE_COLOR),
                "Custom field (Rank)": fields.get(FIELD_RANK),
                "Sprint": ", ".join(sprint_names),
                "Sprint Id": ", ".join([str(sid) for sid in sprint_ids if sid]),
                "Sprint State": ", ".join([str(s) for s in sprint_states if s]),
                "Sprint Start Date": sprint_start_dates[0] if sprint_start_dates and sprint_start_dates[0] else None,
                "Sprint End Date": sprint_end_dates[0] if sprint_end_dates and sprint_end_dates[0] else None,
                "Sprint Complete Date": sprint_complete_dates[0] if sprint_complete_dates and sprint_complete_dates[0] else None,
                "Custom field (Start date)": fields.get(FIELD_START_DATE),
                "Custom field (Story point estimate)": fields.get(FIELD_STORY_POINTS),
                "Team Id": fields.get(FIELD_TEAM_ID),
                "Team Name": fields.get(FIELD_TEAM_NAME),
                "Custom field (Vulnerability)": fields.get(FIELD_VULNERABILITY),
                "Comment": " || ".join(comment_bodies),
                "Parent key": fields.get("parent", {}).get("key") if fields.get("parent") else None,
                "Parent summary": fields.get("parent", {}).get("fields", {}).get("summary") if fields.get("parent") else None,
                "Status Category": fields.get("status", {}).get("statusCategory", {}).get("name"),
                "Status Category Changed": fields.get("statuscategorychangedate"),
                "Status Transitions": json.dumps(transitions) if transitions else None,
                "Num Transitions": len(transitions),
                "QA Entered Count": qa_analysis["qa_count"],
                "QA Failed Count": qa_analysis["failed_qa_count"],
                "Has Rework": rework_analysis["has_rework"],
                "Rework Count": rework_analysis["rework_count"],
                "Lead Time (Changelog)": lead_time_analysis.get("lead_time_days"),
                "Time In Progress (Changelog)": lead_time_analysis.get("time_in_progress"),
                "Time In QA (Changelog)": lead_time_analysis.get("time_in_qa"),
                "Time To First Progress": lead_time_analysis.get("time_to_first_progress"),
            })
        
        is_last = json_data.get("isLast", True)
        if is_last:
            print(f"Reached last page of results")
            break
            
        next_page_token = json_data.get("nextPageToken")
        if not next_page_token:
            print("No next page token, stopping")
            break
            
        print(f"Fetching next page (token: {next_page_token[:20]}...)")
    
    df_issues = pd.DataFrame(all_issues)
    print(f"Fetched {len(df_issues)} issues from Jira")
    
    if 'Status' in df_issues.columns:
        df_issues['Status Category (Mapped)'] = df_issues['Status'].apply(
            lambda status: map_status_to_category(status) if pd.notna(status) else 'Not Done'
        )
    else:
        df_issues['Status Category (Mapped)'] = 'Not Done'
    
    if 'Resolved' in df_issues.columns:
        df_issues['Resolved'] = pd.to_datetime(df_issues['Resolved'], utc=True, errors='coerce')
    if 'Created' in df_issues.columns:
        df_issues['Created'] = pd.to_datetime(df_issues['Created'], utc=True, errors='coerce')
    if 'Updated' in df_issues.columns:
        df_issues['Updated'] = pd.to_datetime(df_issues['Updated'], utc=True, errors='coerce')
    
    df_sprints = get_sprints_from_boards()
    
    if not df_sprints.empty:
        sprint_lookup = {}
        for _, sprint_row in df_sprints.iterrows():
            sprint_id = sprint_row["Sprint Id"]
            sprint_lookup[sprint_id] = {
                "Sprint Name (Full)": sprint_row["Sprint Name"],
                "Sprint State (Full)": sprint_row["Sprint State"],
                "Sprint Start Date (Full)": sprint_row["Sprint Start Date"],
                "Sprint End Date (Full)": sprint_row["Sprint End Date"],
                "Sprint Complete Date (Full)": sprint_row["Sprint Complete Date"],
                "Sprint Goal": sprint_row["Sprint Goal"],
                "Board Id": sprint_row["Board Id"],
                "Board Name": sprint_row["Board Name"]
            }
        
        def get_first_sprint_id(sprint_id_str):
            if pd.isna(sprint_id_str) or sprint_id_str == "":
                return None
            sprint_ids = str(sprint_id_str).split(", ")
            if sprint_ids and sprint_ids[0]:
                try:
                    return int(sprint_ids[0])
                except (ValueError, TypeError):
                    return None
            return None
        
        df_issues["Primary Sprint Id"] = df_issues["Sprint Id"].apply(get_first_sprint_id)
        
        def get_sprint_detail(sprint_id, detail_key):
            if sprint_id is None:
                return None
            sprint_data = sprint_lookup.get(sprint_id, {})
            return sprint_data.get(detail_key, None)
        
        df_issues["Sprint Name (Full)"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Sprint Name (Full)")
        )
        df_issues["Sprint State (Full)"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Sprint State (Full)")
        )
        df_issues["Sprint Start Date (Full)"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Sprint Start Date (Full)")
        )
        df_issues["Sprint End Date (Full)"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Sprint End Date (Full)")
        )
        df_issues["Sprint Complete Date (Full)"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Sprint Complete Date (Full)")
        )
        df_issues["Sprint Goal"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Sprint Goal")
        )
        df_issues["Board Id"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Board Id")
        )
        df_issues["Board Name"] = df_issues["Primary Sprint Id"].apply(
            lambda sid: get_sprint_detail(sid, "Board Name")
        )
        
        df_issues["Sprint Start Date"] = df_issues["Sprint Start Date (Full)"].fillna(df_issues["Sprint Start Date"])
        df_issues["Sprint End Date"] = df_issues["Sprint End Date (Full)"].fillna(df_issues["Sprint End Date"])
        df_issues["Sprint Complete Date"] = df_issues["Sprint Complete Date (Full)"].fillna(df_issues["Sprint Complete Date"])
        
        df_issues = df_issues.drop(columns=["Sprint Start Date (Full)", "Sprint End Date (Full)", "Sprint Complete Date (Full)"], errors='ignore')
        
        print(f"Merged sprint details: {len(df_issues[df_issues['Primary Sprint Id'].notna()])} issues linked to sprints")
    else:
        print("Warning: No sprints fetched, issues will only have sprint data from issue fields")
        df_issues["Primary Sprint Id"] = None
        df_issues["Sprint Goal"] = None
        df_issues["Board Id"] = None
        df_issues["Board Name"] = None
    
    return df_issues


def fetch_jira_data_with_sprints():
    """
    Fetch all Jira issues and sprints, returning both DataFrames separately.
    
    to return both DataFrames. This ensures sprints DataFrame is available separately for sprint filtering utilities.
    
    
    Returns:
        Tuple of (df_issues, df_sprints) DataFrames
    """
    df_issues = fetch_jira_data()
    
    df_sprints = get_sprints_from_boards()
    
    return df_issues, df_sprints