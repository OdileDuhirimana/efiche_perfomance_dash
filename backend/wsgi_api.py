"""
WSGI entry point for the Flask API application.
Run with: gunicorn wsgi_api:application
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.api_app import create_api_app

app = create_api_app()
application = app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)

