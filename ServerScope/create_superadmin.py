from app import db, create_app
from app.models import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the Flask app
app = create_app()

with app.app_context():
    # Create a super admin user
    super_admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('superadmin_password'),
        approved=True,  # Assuming you have an 'approved' field in your User model
        role='super_admin'
    )

    # Add the super admin user to the database
    db.session.add(super_admin)
    db.session.commit()

    print("Super admin created successfully!")
