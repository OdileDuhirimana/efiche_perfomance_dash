import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
load_dotenv()

# Jira Configuration
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
DOMAIN = os.getenv("JIRA_DOMAIN", "https://bzigalarissa.atlassian.net")

if not all([EMAIL, API_TOKEN, DOMAIN]):
    raise ValueError("Missing Jira credentials. Check your .env file has JIRA_EMAIL, JIRA_API_TOKEN, and JIRA_DOMAIN set.")

AUTH = HTTPBasicAuth(EMAIL, API_TOKEN)
HEADERS = {"Accept": "application/json"}

# Dashboard Configuration
COMPANY_NAME = "eFiche Ltd"

# Color Scheme
PRIMARY_BACKGROUND = '#F8F8F8'
SECONDARY_BACKGROUND = '#FFFFFF'
TEXT_COLOR = '#34495E'
MUTED_TEXT_COLOR = '#7F8C8D'
BORDER_COLOR = '#E0E0E0'

# KPI Colors
KPI_HEADER_PLANNED = '#2C3E50'
KPI_HEADER_NOT_DONE = '#C0392B'
KPI_HEADER_IN_PROGRESS = '#F39C12'
KPI_HEADER_IN_QA = '#D35400'
KPI_HEADER_DONE = '#27AE60'
KPI_HEADER_LEAD_TIME = '#7F8C8D'

KPI_VALUE_PLANNED = '#3498DB'
KPI_VALUE_NOT_DONE = '#E74C3C'
KPI_VALUE_IN_PROGRESS = '#F1C40F'
KPI_VALUE_IN_QA = '#E67E22'
KPI_VALUE_DONE = '#2ECC71'
KPI_VALUE_LEAD_TIME = '#95A5A6'

# Status Color Mapping
STATUS_COLOR_MAP = {
    'Not Done': KPI_VALUE_NOT_DONE,
    'In Progress': KPI_VALUE_IN_PROGRESS,
    'In QA': KPI_VALUE_IN_QA,
    'Done': KPI_VALUE_DONE
}

# Chart Colors
import plotly.express as px
CHART_COLOR_PALETTE = px.colors.qualitative.D3