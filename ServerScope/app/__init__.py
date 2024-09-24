import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Database configuration: Oracle, with fallback to SQLite
    db_type = os.getenv('DB_TYPE', 'sqlite')
    if db_type == 'oracle':
        oracle_user = os.getenv('ORACLE_USER')
        oracle_password = os.getenv('ORACLE_PASSWORD')
        oracle_dsn = os.getenv('ORACLE_DSN')  # Oracle Data Source Name

        if not all([oracle_user, oracle_password, oracle_dsn]):
            raise RuntimeError("Missing Oracle DB configuration. Please set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN.")

        app.config['SQLALCHEMY_DATABASE_URI'] = f'oracle+cx_oracle://{oracle_user}:{oracle_password}@{oracle_dsn}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///serverscope.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')  # For secure session management

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Redirect unauthorized users to the login page
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'  # Optional: for styling messages

    # Import and register blueprints/routes
    from app.routes import main, nfs_bp
    app.register_blueprint(main)
    app.register_blueprint(nfs_bp, url_prefix='/nfs')

    # Register the auth blueprint
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Optional: Error handling
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Register custom error handlers for common HTTP errors."""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
