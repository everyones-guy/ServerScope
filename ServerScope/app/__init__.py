# __init__.py(app): Initialize the Flask app and extensions4
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions globally, but don't bind them to the app yet
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # General configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')  # For secure session management
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Environment-specific database configurations
    if app.config.get('FLASK_ENV') == 'development':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DEV_DATABASE_URL', 'sqlite:///dev_serverscope.db')
    elif app.config.get('FLASK_ENV') == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_DATABASE_URL', 'sqlite:///test_serverscope.db')
    else:  # Default to production settings
        # Database configuration: Oracle, MySQL, PostgreSQL, or fallback to SQLite
        db_type = os.getenv('DB_TYPE', 'sqlite')

        if db_type == 'oracle':
            oracle_user = os.getenv('ORACLE_USER')
            oracle_password = os.getenv('ORACLE_PASSWORD')
            oracle_dsn = os.getenv('ORACLE_DSN')

            if not all([oracle_user, oracle_password, oracle_dsn]):
                raise RuntimeError("Missing Oracle DB configuration. Please set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN.")

            app.config['SQLALCHEMY_DATABASE_URI'] = f'oracle+cx_oracle://{oracle_user}:{oracle_password}@{oracle_dsn}'
        elif db_type == 'mysql':
            mysql_user = os.getenv('MYSQL_USER')
            mysql_password = os.getenv('MYSQL_PASSWORD')
            mysql_host = os.getenv('MYSQL_HOST')
            mysql_db = os.getenv('MYSQL_DB')
            app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}'
        elif db_type == 'postgresql':
            postgres_user = os.getenv('POSTGRES_USER')
            postgres_password = os.getenv('POSTGRES_PASSWORD')
            postgres_host = os.getenv('POSTGRES_HOST')
            postgres_db = os.getenv('POSTGRES_DB')
            app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}'
        else:  # Default to SQLite if no DB_TYPE is provided or unknown DB_TYPE
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///serverscope.db'

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Redirect unauthorized users to the login page
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'  # Optional: for styling messages

    # Inject `current_user` into all templates
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

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

