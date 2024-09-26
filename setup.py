
import os
from pathlib import Path

# Constants for .env file
env_content = """
# Flask settings
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=True

# Secret key for session management, CSRF protection, etc.
SECRET_KEY=mysecretkey

# Database settings
DB_TYPE=sqlite
SQLITE_DATABASE_URI=sqlite:///serverscope_dummy.db

# Dummy Database for MySQL
MYSQL_USER=dummy_user
MYSQL_PASSWORD=dummy_password
MYSQL_HOST=localhost
MYSQL_DB=dummy_db

# Dummy Database for PostgreSQL
POSTGRES_USER=dummy_user
POSTGRES_PASSWORD=dummy_password
POSTGRES_HOST=localhost
POSTGRES_DB=dummy_db

# Twilio settings (optional)
TWILIO_ACCOUNT_SID=dummy_sid
TWILIO_AUTH_TOKEN=dummy_token
TWILIO_PHONE_NUMBER=+1234567890

# Splunk API settings (optional)
SPLUNK_URL=https://dummy_splunk.com
SPLUNK_TOKEN=dummy_token
SPLUNK_INDEX=dummy_index
SPLUNK_SOURCE=dummy_source

# Nmap settings (optional)
NMAP_PATH=/usr/bin/nmap

# Other optional settings
PORT=5000
"""

# Step 1: Create the .env file
def create_env_file():
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(".env file created successfully.")
    else:
        print(".env file already exists.")

# Step 2: Create dummy SQLite databases
def create_dummy_databases():
    db_path = Path('serverscope_dummy.db')
    if not db_path.exists():
        # Create a new SQLite database file
        os.system('sqlite3 serverscope_dummy.db ".databases"')
        print("SQLite dummy database created successfully.")
    else:
        print("SQLite dummy database already exists.")

# Step 3: Ensure run.py exists and is ready for the app
def check_run_py():
    run_py = Path('run.py')
    if run_py.exists():
        print("run.py exists and is ready for the application.")
    else:
        print("run.py is missing! Ensure your project structure is correct.")

# Step 4: Run migrations to set up the database schema (if Flask-Migrate is used)
def run_migrations():
    # Run Flask db migrations to set up the initial database schema
    print("Running database migrations...")
    os.system('flask db upgrade')

# Step 5: Set up complete message
def setup_complete():
    print("\nSetup complete!")
    print("To start the application, run:")
    print("    flask run")

# Step 6: Run the setup process
def setup():
    print("Setting up the environment...")
    create_env_file()
    create_dummy_databases()
    check_run_py()
    run_migrations()
    setup_complete()

if __name__ == '__main__':
    setup()
