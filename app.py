"""
ENVITA — Personalized Climate Health Resilience Platform
Main Flask application entry point.
"""
from flask import Flask, render_template
from config import Config
from models.user import init_db

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Initialise database
    with app.app_context():
        init_db()

    # Register blueprints
    from routes.home_routes      import home_bp
    from routes.profile_routes   import profile_bp
    from routes.dashboard_routes import dashboard_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(dashboard_bp)

    # ---------------------------------------------------------------------------
    # Error handlers
    # ---------------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Internal server error."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5001)

from config import Config
print(Config.OPENWEATHER_API_KEY)