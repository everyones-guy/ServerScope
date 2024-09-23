import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate()

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

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints/routes
    from app.routes import main, nfs_bp
    app.register_blueprint(main)
    app.register_blueprint(nfs_bp, url_prefix='/nfs')

    return app
