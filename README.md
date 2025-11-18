# Analytics Dashboard

A comprehensive team performance analytics dashboard with Jira integration. This dashboard provides real-time insights into team productivity, quality metrics, and project progress through interactive charts and KPIs.

## What This Project Does

This dashboard helps teams track and analyze their work performance by:
- Monitoring completion rates and planned vs done metrics
- Tracking lead times and execution success
- Analyzing quality metrics and rework ratios
- Providing company-level trend analysis
- Visualizing task distribution across team members

## Project Structure

```
new_dashboard/
├── backend/          # Flask REST API backend
│   ├── app/         # Application code
│   ├── wsgi_api.py  # API entry point
│   └── requirements.txt
└── frontend/         # Next.js frontend application
    ├── app/         # React components and pages
    └── package.json
```

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.8+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **Jira API credentials** (email, API token, and domain)

## Quick Start

### Step 1: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the `backend/` directory with your Jira credentials:
   ```
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   JIRA_DOMAIN=https://your-domain.atlassian.net
   ```
   
   > **Note:** To get your Jira API token, go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens) and create a new API token.

4. Start the backend server:
   ```bash
   python wsgi_api.py
   ```

   The backend will run on `http://localhost:8050`

### Step 2: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file in the `frontend/` directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8050
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:3000` to view the dashboard.

## Configuration

### Backend Configuration

The backend requires a `.env` file in the `backend/` directory with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `JIRA_EMAIL` | Your Jira account email | `user@example.com` |
| `JIRA_API_TOKEN` | Your Jira API token | `ATATT3xFfGF0...` |
| `JIRA_DOMAIN` | Your Jira instance URL | `https://company.atlassian.net` |

### Frontend Configuration

The frontend requires a `.env.local` file in the `frontend/` directory:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8050` |

## Features

The dashboard includes the following features:

- **Executive Summary** - High-level KPIs including completion rate, lead time, rework ratio, planned, and done metrics
- **Weekly Planned vs Done** - Track how well the team meets their weekly commitments
- **Weekly Flow Analysis** - Monitor work flow including done, in progress, and carry-over items
- **Lead Time Metrics** - Analyze how long tasks take from start to completion
- **Task Load per Assignee** - See work distribution across team members
- **Execution Success Rates** - Track how often tasks are completed successfully
- **Company-Level Trends** - View monthly trends for completion rates and lead times
- **QA vs Failed QA Analysis** - Monitor quality assurance metrics
- **Rework Ratio Tracking** - Identify how much work needs to be redone

## Troubleshooting

### Backend Issues

**Problem:** Backend won't start
- **Solution:** Make sure Python 3.8+ is installed and all dependencies are installed correctly
- **Check:** Verify your `.env` file exists and contains valid Jira credentials

**Problem:** "Connection refused" or API errors
- **Solution:** Ensure the backend is running on port 8050 and check firewall settings
- **Check:** Verify Jira credentials are correct and the API token is valid

### Frontend Issues

**Problem:** Frontend can't connect to backend
- **Solution:** Verify `NEXT_PUBLIC_API_URL` in `.env.local` matches your backend URL
- **Check:** Make sure the backend is running before starting the frontend

**Problem:** "Module not found" errors
- **Solution:** Run `npm install` again to ensure all dependencies are installed
- **Check:** Make sure you're using Node.js 18 or higher

### General Issues

**Problem:** No data showing in charts
- **Solution:** Check that your Jira credentials are correct and you have access to the Jira instance
- **Check:** Verify the date range filters aren't excluding all data

## Documentation

For more detailed information, see:

- [Backend README](backend/README.md) - Complete backend API documentation, endpoints, and architecture
- [Frontend README](frontend/README.md) - Frontend setup, components, and development guide

## Production Deployment

### Backend Production

For production, use a WSGI server like Gunicorn:

```bash
gunicorn wsgi_api:application --bind 0.0.0.0:8050 --workers 4
```

### Frontend Production

Build and start the production server:

```bash
npm run build
npm start
```

## Support

If you encounter issues not covered in this README, please check the individual README files in the `backend/` and `frontend/` directories for more specific troubleshooting steps.
