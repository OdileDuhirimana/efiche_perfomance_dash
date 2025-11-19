# Analytics Backend API

Flask REST API backend for the analytics dashboard. This backend fetches data from Jira, processes it, and provides endpoints for the frontend to display charts and metrics.

## What This Backend Does

The backend:
- Connects to Jira API to fetch issues and sprint data
- Cleans and processes raw Jira data
- Calculates metrics like lead time, completion rates, and rework ratios
- Caches data for improved performance
- Provides REST API endpoints for the frontend dashboard

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Jira API credentials** (email, API token, and domain)

## Project Structure

```
backend/
├── app/
│   ├── api/                          # API route handlers
│   │   ├── routes.py                 # Main chart endpoints
│   │   └── executive_summary.py     # Executive summary endpoint
│   ├── services/                     # Business logic and calculations
│   │   ├── chart_calculations.py     # Chart data calculations
│   │   ├── changelog_processor.py    # Processes Jira changelogs
│   │   ├── data_cache.py             # Data caching service
│   │   ├── data_accuracy.py          # Data accuracy metrics
│   │   ├── filters.py                # Data filtering utilities
│   │   ├── resolution_utils.py      # Issue resolution helpers
│   │   ├── sprint_utils.py           # Sprint-related utilities
│   │   └── transitions_helper.py    # Status transition analysis
│   ├── config.py                     # Configuration management
│   ├── data_fetcher.py               # Jira API data fetching
│   ├── data_cleaner.py               # Data cleaning and formatting
│   └── api_app.py                    # Flask application setup
├── data/                             # Exported CSV files (auto-generated)
├── wsgi_api.py                       # WSGI entry point for running the API
└── requirements.txt                  # Python dependencies
```

## Setup Instructions

### Step 1: Install Dependencies

Make sure you're in the `backend/` directory, then install all required packages:

```bash
pip install -r requirements.txt
```

If you encounter permission issues, use:
```bash
pip install --user -r requirements.txt
```

### Step 2: Configure Jira Credentials

Create a `.env` file in the `backend/` directory with your Jira credentials:

```env
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_DOMAIN=https://your-domain.atlassian.net
```

**How to get your Jira API token:**
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name (e.g., "Analytics Dashboard")
4. Copy the token and paste it in your `.env` file

**Important:** Never commit your `.env` file to version control!

### Step 3: Run the API

**Development Mode:**
```bash
python wsgi_api.py
```

The API will start on `http://localhost:8050`

**Production Mode (using Gunicorn):**
```bash
gunicorn wsgi_api:application --bind 0.0.0.0:8050 --workers 4
```

This runs the API with 4 worker processes for better performance.

## API Endpoints

### Health & Data Information

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check endpoint - returns API status |
| `/api/data/accuracy` | GET | Returns data accuracy metrics |
| `/api/data/date-range` | GET | Returns the available date range of data |

### Chart Data Endpoints

All chart endpoints support query parameters for filtering (see Query Parameters section below).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/charts/weekly-planned-vs-done` | GET | Weekly planned vs done comparison |
| `/api/charts/weekly-flow` | GET | Weekly flow metrics (done, in progress, carry over) |
| `/api/charts/weekly-lead-time` | GET | Weekly lead time trends |
| `/api/charts/task-load` | GET | Task load distribution per assignee |
| `/api/charts/execution-success` | GET | Execution success rates |
| `/api/charts/company-trend` | GET | Company-level trend analysis |
| `/api/charts/qa-vs-failed` | GET | QA vs Failed QA analysis |
| `/api/charts/rework-ratio` | GET | Rework ratio tracking |
| `/api/charts/assignee-completion-trend` | GET | Assignee completion trends over time |

### Executive Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/executive-summary` | GET | Returns executive KPIs: completion rate, lead time, rework ratio, planned, done |

## Query Parameters

Most endpoints support the following query parameters for filtering:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `start_date` | string | Start date for filtering (ISO format or DD-MM-YYYY) | `2024-01-01` or `01-01-2024` |
| `end_date` | string | End date for filtering (ISO format or DD-MM-YYYY) | `2024-12-31` or `31-12-2024` |
| `assignee` | string | Filter by specific assignee | `john.doe@example.com` |
| `issueType` | string | Filter by issue type | `Task`, `Bug`, `Story` |
| `num_weeks` | integer | Number of weeks for weekly charts | `12` |
| `num_months` | integer | Number of months for trend charts | `6` |

**Example Request:**
```
GET /api/charts/weekly-planned-vs-done?start_date=2024-01-01&end_date=2024-12-31&num_weeks=12
```

## Data Export

The backend automatically exports cleaned data to CSV files in the `data/` directory:

- `cleaned_jira_data_latest.csv` - Latest issues data with all cleaned fields
- `cleaned_sprints_data_latest.csv` - Latest sprints data

These files are updated each time data is fetched from Jira. You can use these CSV files for external analysis or reporting.

## Architecture Overview

### Data Flow

1. **Data Fetching** (`data_fetcher.py`)
   - Connects to Jira API using credentials from `.env`
   - Fetches all issues and sprints from your Jira instance
   - Handles pagination and rate limiting

2. **Data Cleaning** (`data_cleaner.py`)
   - Formats dates consistently
   - Maps Jira statuses to standardized status names
   - Prepares data for calculations
   - Exports cleaned data to CSV files

3. **Data Caching** (`data_cache.py`)
   - Caches cleaned data in memory for fast access
   - Reduces API calls and improves response times
   - Automatically refreshes when needed

4. **Chart Calculations** (`chart_calculations.py`)
   - Calculates metrics for all dashboard charts
   - Processes weekly, monthly, and trend data
   - Handles filtering and aggregation
   - Lead time calculation uses simple date difference (Resolved - Created)

5. **Status Transitions** (`transitions_helper.py`)
   - Parses Jira changelogs to track status changes
   - Identifies when issues move between statuses
   - Enables accurate lead time and flow calculations

### Key Services

- **changelog_processor.py**: Processes Jira changelog data to extract status transitions
- **sprint_utils.py**: Utilities for sprint-related calculations
- **resolution_utils.py**: Helpers for issue resolution tracking
- **filters.py**: Data filtering utilities for query parameters
- **data_accuracy.py**: Calculates and reports data quality metrics

## Troubleshooting

### Common Issues

**Problem: "ModuleNotFoundError" when running the API**
- **Solution:** Make sure all dependencies are installed: `pip install -r requirements.txt`
- **Check:** Verify you're using Python 3.8 or higher: `python --version`

**Problem: "Connection refused" or Jira API errors**
- **Solution:** Verify your `.env` file exists and contains correct credentials
- **Check:** Test your Jira API token by making a manual API call
- **Check:** Ensure your Jira domain URL is correct (should end with `.atlassian.net`)

**Problem: API starts but returns empty data**
- **Solution:** Check that you have access to the Jira instance
- **Check:** Verify the date range filters aren't excluding all data
- **Check:** Look at the console output for any error messages

**Problem: "Port already in use" error**
- **Solution:** Either stop the process using port 8050, or change the port in `wsgi_api.py`
- **Check:** Find what's using the port: `lsof -i :8050` (Linux/Mac) or `netstat -ano | findstr :8050` (Windows)

**Problem: Slow API responses**
- **Solution:** The first request may be slow as it fetches data from Jira. Subsequent requests use cached data
- **Check:** Ensure data caching is working properly
- **Check:** Consider using Gunicorn with multiple workers for production

### Debugging Tips

1. **Check logs:** The API prints useful information to the console. Look for error messages or warnings.

2. **Test endpoints manually:** Use `curl` or Postman to test endpoints:
   ```bash
   curl http://localhost:8050/api/health
   ```

3. **Verify data files:** Check if CSV files are being generated in the `data/` directory.

4. **Check Jira access:** Make sure your Jira credentials have permission to read the issues and sprints you're trying to analyze.

## Development

### Adding New Endpoints

1. Add your route handler in `app/api/routes.py` or create a new file in `app/api/`
2. Implement your business logic in `app/services/`
3. Register the route in `app/api_app.py`

### Testing Changes

After making changes, restart the API server:
```bash
# Stop the current server (Ctrl+C)
# Then restart:
python wsgi_api.py
```

## Production Deployment

For production, use Gunicorn with multiple workers:

```bash
gunicorn wsgi_api:application --bind 0.0.0.0:8050 --workers 4 --timeout 120
```

Consider also:
- Setting up a reverse proxy (nginx) in front of Gunicorn
- Using environment variables for configuration
- Setting up logging to files
- Using a process manager like systemd or supervisor
