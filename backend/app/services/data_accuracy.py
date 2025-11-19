import pandas as pd
import json
from typing import Dict, Tuple


def ensure_changelog_usage(df: pd.DataFrame, calculation_type: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Ensure changelog data is used when available for maximum accuracy.
    
    Counts issues with usable changelog vs fallback. Calculates changelog usage rate percentage.
    Returns DataFrame unchanged and statistics dictionary.
    
    
    Args:
        df: DataFrame with issues
        calculation_type: Type of calculation ('planned_vs_done', 'weekly_flow', 'qa', 'rework', 'lead_time')
    
    Returns:
        Tuple of (enhanced_df, usage_stats) where usage_stats contains total_issues, issues_using_changelog, issues_using_fallback, changelog_usage_rate
    """
    stats = {
        'total_issues': len(df),
        'issues_using_changelog': 0,
        'issues_using_fallback': 0,
        'changelog_usage_rate': 0.0
    }
    
    if 'Status Transitions' not in df.columns:
        stats['issues_using_fallback'] = len(df)
        stats['changelog_usage_rate'] = 0.0
        return df, stats
    
    for _, row in df.iterrows():
        transitions_json = row.get('Status Transitions')
        if transitions_json:
            try:
                transitions = json.loads(transitions_json) if isinstance(transitions_json, str) else transitions_json
                if transitions and len(transitions) > 0:
                    stats['issues_using_changelog'] += 1
                else:
                    stats['issues_using_fallback'] += 1
            except:
                stats['issues_using_fallback'] += 1
        else:
            stats['issues_using_fallback'] += 1
    
    stats['changelog_usage_rate'] = (
        stats['issues_using_changelog'] / stats['total_issues'] * 100
    ) if stats['total_issues'] > 0 else 0.0
    
    return df, stats
