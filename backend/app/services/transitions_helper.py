import json
import pandas as pd
from typing import Any, List, Dict


def parse_transitions(transitions_data: Any) -> List[Dict]:
    """
    Parse transitions from JSON string, list, or None.
    
    Logic: Handles multiple input formats - returns empty list for None/NaN, returns list as-is if already a list,
    parses JSON string to list, handles dict-wrapped JSON. Returns empty list on parse errors.
    
    Use: Used internally by pre_parse_transitions to convert raw transition data into structured list format.
    
    Args:
        transitions_data: Can be None, list, or JSON string
    
    Returns:
        List of transition dictionaries
    """
    if transitions_data is None or pd.isna(transitions_data):
        return []
    
    if isinstance(transitions_data, list):
        return transitions_data
    
    if isinstance(transitions_data, str):
        try:
            parsed = json.loads(transitions_data)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed] if parsed else []
            else:
                return []
        except (json.JSONDecodeError, ValueError):
            return []
    
    return []


def pre_parse_transitions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-parse all transitions and add as '_parsed_transitions' column.
    
    Logic: Copies DataFrame and applies parse_transitions to 'Status Transitions' column for all rows.
    Adds '_parsed_transitions' column with parsed list. Returns DataFrame with None column if 'Status Transitions' missing.
    
    Use: Used in chart calculations to pre-process changelog data for efficient analysis of QA transitions, rework patterns, and lead time calculations.
    
    Args:
        df: DataFrame with 'Status Transitions' column
    
    Returns:
        DataFrame with added '_parsed_transitions' column
    """
    df = df.copy()
    
    if 'Status Transitions' not in df.columns:
        df['_parsed_transitions'] = None
        return df
    
    df['_parsed_transitions'] = df['Status Transitions'].apply(parse_transitions)
    
    return df
