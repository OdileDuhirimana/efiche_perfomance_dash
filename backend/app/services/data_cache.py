import time
import pandas as pd

from app.data_fetcher import fetch_jira_data_with_sprints
from app.data_cleaner import clean_jira_data, prepare_dashboard_data


def _ensure_data_format(df):
    """
    Ensure DataFrame date columns are properly formatted as UTC datetime.
    
    Logic: Converts date columns to datetime if not already, ensures UTC timezone (localizes if None, converts if different).
    Converts Primary Sprint Id to int or None. Returns empty DataFrame as-is.
    
    Use: Internal helper to standardize data format before caching.
    
    Args:
        df: DataFrame with issues
    
    Returns:
        DataFrame with formatted date columns and sprint IDs
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    date_columns = ['Created', 'Updated', 'Resolved', 'Status Category Changed',
                    'Sprint Start Date', 'Sprint End Date', 'Sprint Complete Date']
    for col in date_columns:
        if col in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col], utc=True, errors='coerce')
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                if df[col].dt.tz is None:
                    df[col] = df[col].dt.tz_localize('UTC')
                elif str(df[col].dt.tz) != 'UTC':
                    df[col] = df[col].dt.tz_convert('UTC')
    
    if 'Primary Sprint Id' in df.columns:
        df['Primary Sprint Id'] = df['Primary Sprint Id'].apply(
            lambda x: int(x) if pd.notna(x) else None
        )
    
    return df


def _ensure_sprints_format(df_sprints):
    """
    Ensure sprints DataFrame date columns are properly formatted as UTC datetime.
    
    Logic: Converts sprint date columns to datetime if not already, ensures UTC timezone (localizes if None, converts if different).
    Converts Sprint Id to int or None. Returns empty DataFrame as-is.
    
    Use: Internal helper to standardize sprints format before caching.
    
    Args:
        df_sprints: DataFrame with sprints
    
    Returns:
        DataFrame with formatted date columns and sprint IDs
    """
    if df_sprints.empty:
        return df_sprints
    
    df_sprints = df_sprints.copy()
    
    date_columns = ['Sprint Start Date', 'Sprint End Date', 'Sprint Complete Date']
    for col in date_columns:
        if col in df_sprints.columns:
            if not pd.api.types.is_datetime64_any_dtype(df_sprints[col]):
                df_sprints[col] = pd.to_datetime(df_sprints[col], utc=True, errors='coerce')
            if pd.api.types.is_datetime64_any_dtype(df_sprints[col]):
                if df_sprints[col].dt.tz is None:
                    df_sprints[col] = df_sprints[col].dt.tz_localize('UTC')
                elif str(df_sprints[col].dt.tz) != 'UTC':
                    df_sprints[col] = df_sprints[col].dt.tz_convert('UTC')
    
    if 'Sprint Id' in df_sprints.columns:
        df_sprints['Sprint Id'] = df_sprints['Sprint Id'].astype('Int64').apply(
            lambda x: int(x) if pd.notna(x) else None
        )
    
    return df_sprints


class DataCache:
    """
    Singleton cache for JIRA data.
    
    Logic: Implements singleton pattern to maintain single cache instance. Stores issues and sprints DataFrames with timestamp.
    Uses lock to prevent concurrent fetches. Returns cached data if available and not forcing refresh, otherwise fetches fresh data.
    
    Use: Used by all API endpoints to get cached JIRA data, avoiding repeated API calls.
    """
    
    _instance = None
    _data = None
    _sprints = None
    _timestamp = 0
    _lock = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataCache, cls).__new__(cls)
        return cls._instance
    
    def get_data(self, force_refresh=False):
        """
        Get cached data or fetch fresh if cache is empty or force_refresh is True.
        
        Logic: Returns cached data if exists and not forcing refresh. If lock is active, waits up to 60 seconds for completion.
        Otherwise fetches fresh data from JIRA, cleans and formats it, then caches and returns copies.
        
        Use: Called by get_cached_data() to retrieve JIRA data for chart calculations.
        
        Args:
            force_refresh: If True, force a fresh fetch even if cache exists
        
        Returns:
            tuple: (df_issues, df_sprints)
        """
        if not force_refresh and self._data is not None and self._sprints is not None:
            cache_age = time.time() - self._timestamp
            print(f"✅ Using cached data (age: {cache_age:.0f}s, {len(self._data)} issues, {len(self._sprints)} sprints)")
            return self._data.copy(), self._sprints.copy()
        
        if self._lock:
            print("⏳ Data fetch already in progress, waiting...")
            wait_time = 0
            while self._lock and wait_time < 60:
                time.sleep(0.5)
                wait_time += 0.5
            if self._data is not None and self._sprints is not None:
                return self._data.copy(), self._sprints.copy()
        
        self._lock = True
        try:
            print("=== FETCHING FRESH JIRA DATA ===")
            fetch_start = time.time()
            
            raw_df, df_sprints = fetch_jira_data_with_sprints()
            
            df = clean_jira_data(raw_df)
            df = prepare_dashboard_data(df)
            
            df = _ensure_data_format(df)
            if df_sprints is not None and not df_sprints.empty:
                df_sprints = _ensure_sprints_format(df_sprints)
            
            self._data = df
            self._sprints = df_sprints
            self._timestamp = time.time()
            
            fetch_time = time.time() - fetch_start
            print(f"✅ Data cached successfully. {len(df)} issues, {len(df_sprints)} sprints. (Fetch: {fetch_time:.2f}s)")
            
            return df.copy(), df_sprints.copy()
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            raise
        finally:
            self._lock = False


_data_cache = DataCache()


def get_cached_data(force_refresh=False):
    """
    Get cached JIRA data.
    
    Logic: Wrapper function that calls DataCache singleton instance to get cached or fresh JIRA data.
    
    Use: Called by all API endpoints and chart calculations to retrieve JIRA data efficiently.
    
    Args:
        force_refresh: If True, force a fresh fetch
    
    Returns:
        tuple: (df_issues, df_sprints)
    """
    return _data_cache.get_data(force_refresh=force_refresh)
