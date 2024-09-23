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
    from app import db
    db.init_app(app)

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

if __name__ == '__main__':
    # Create an app instance
    app = create_app()

    # Run the app (set debug mode based on environment variable, default to True for development)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('FLASK_DEBUG', 'True') == 'True')
