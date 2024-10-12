import os
from dotenv import load_dotenv
from app import db, create_app
from app.models import User
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Explicitly set FLASK_ENV if not already set
os.environ.setdefault('FLASK_ENV', 'development')

# Create the Flask app and push the context
app = create_app()

with app.app_context():
    # Check if the super admin already exists
    existing_admin = User.query.filter_by(username='admin').first()

    if existing_admin:
        print("Super admin already exists!")
    else:
        # Create a new super admin user
        super_admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('your_superadmin_password'),  # Replace with a real password
            approved=True,  # Assuming you have an 'approved' field in your User model
            role='super_admin'
        )

        # Add the super admin user to the database
        db.session.add(super_admin)
        db.session.commit()

        print("Super admin created successfully!")
