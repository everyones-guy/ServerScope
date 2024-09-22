from flask import Flask
import os
from dotenv import load_dotenv
from app import app, db  # Ensure this import reflects your project's structure


# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from environment variable
    config_type = os.getenv('FLASK_CONFIG', 'config.DevelopmentConfig')
    app.config.from_object(config_type)

    # Initialize plugins
    db.init_app(app)

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


if __name__ == '__main__':
    # Create an app instance
    app = create_app()

    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)  # Set debug to False in production
