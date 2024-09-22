import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)

# Database configuration: Oracle, with fallback to SQLite
db_type = os.getenv('DB_TYPE', 'sqlite')
if db_type == 'oracle':
    oracle_user = os.getenv('ORACLE_USER')
    oracle_password = os.getenv('ORACLE_PASSWORD')
    oracle_dsn = os.getenv('ORACLE_DSN')  # Oracle Data Source Name
    app.config['SQLALCHEMY_DATABASE_URI'] = f'oracle+cx_oracle://{oracle_user}:{oracle_password}@{oracle_dsn}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///serverscope.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
