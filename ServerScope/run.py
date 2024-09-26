from flask import Flask
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from environment variable or use DevelopmentConfig as fallback
    config_type = os.getenv('FLASK_CONFIG', 'config.DevelopmentConfig')
    app.config.from_object(config_type)

    # Initialize database plugin
    from app import db, migrate, login_manager

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

if __name__ == '__main__':
    # Create an app instance
    app = create_app()

    # Set debug mode based on environment variable (default to True for development)
    debug_mode = os.getenv('FLASK_DEBUG', 'True') == 'True'
    port = int(os.getenv('PORT', 5000))

    # Run the app on specified host, port, and debug mode
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
