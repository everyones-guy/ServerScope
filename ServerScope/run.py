from app import create_app
import os

if __name__ == '__main__':
    # Create an app instance using the factory method
    app = create_app()

    # Set debug mode based on environment variable (default to True for development)
    debug_mode = app.config.get('DEBUG', True)
    port = int(os.getenv('PORT', 5000))

    # Run the app on specified host, port, and debug mode
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
