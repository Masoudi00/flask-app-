import os
from flask import Flask

# Import configuration
from config.database import init_database, init_session

# Import routes
from routes.auth import init_auth_routes
from routes.portfolio import init_portfolio_routes
from routes.quote import init_quote_routes
from routes.features import init_features_routes

# Import utilities
from utils.helpers import usd

def create_app():
    """Create and configure the Flask application"""
    # Configure application
    app = Flask(__name__)

    # Custom filter
    app.jinja_env.filters["usd"] = usd

    # Initialize session
    init_session(app)

    # Initialize database
    db = init_database(app)

    # Initialize routes
    init_auth_routes(app, db)
    init_portfolio_routes(app, db)
    init_quote_routes(app)
    init_features_routes(app, db)

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True) 