"""
Flask API application for analytics backend.
This is the main entry point for the REST API.
"""
from flask import Flask
from app.api.routes import api_bp
from app.services.data_cache import get_cached_data

# Try to import CORS, but make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️  flask-cors not installed. CORS disabled. Install with: pip install flask-cors")


def create_api_app():
    """Create and configure the Flask API application."""
    app = Flask(__name__)
    
    # Enable CORS for frontend integration (if available)
    if CORS_AVAILABLE:
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
    else:
        # Manual CORS headers if flask-cors is not available
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            return response
    
    # Register API routes
    app.register_blueprint(api_bp)
    
    # Initialize data cache on startup
    def initialize_data():
        """Pre-load data cache on startup."""
        try:
            print("Initializing data cache...")
            df, df_sprints = get_cached_data()
            print("✅ API server initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Error initializing data cache: {e}")
            print("   Data will be fetched on first request")
    
    # Initialize data on app creation
    with app.app_context():
        initialize_data()
    
    # Health check at root
    @app.route('/')
    def root():
        from flask import jsonify
        return jsonify({
            'service': 'analytics-backend',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'executive_summary': '/api/executive-summary',
                'weekly_planned_vs_done': '/api/charts/weekly-planned-vs-done',
                'weekly_flow': '/api/charts/weekly-flow',
                'weekly_lead_time': '/api/charts/weekly-lead-time',
                'task_load': '/api/charts/task-load',
                'execution_success': '/api/charts/execution-success',
                'company_trend': '/api/charts/company-trend',
                'qa_vs_failed': '/api/charts/qa-vs-failed',
                'rework_ratio': '/api/charts/rework-ratio',
                'assignee_completion_trend': '/api/charts/assignee-completion-trend'
            }
        })
    
    return app

