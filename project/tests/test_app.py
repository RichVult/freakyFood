import os
import pytest
from dotenv import load_dotenv
from app import app, db  # Assuming your Flask app is in app.py
from flask import url_for

# Load environment variables
load_dotenv()

# Ensure test database is used
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('db_owner')}:{os.getenv('db_pass')}"
    f"@localhost:{os.getenv('db_port')}/{os.getenv('db_name')}_test"
)
app.config['TESTING'] = True

@pytest.fixture
def client():
    # Set up the Flask test client
    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.create_all()
        yield client
        # Drop all tables after test
        with app.app_context():
            db.drop_all()


def test_signup(client):
    # Define test data for signup
    signup_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    }

    # Send a POST request to the signup route
    response = client.post('/signup', data=signup_data)

    # Check if the signup was successful (status code 200 or redirect)
    assert response.status_code in (200, 302)

    # Optionally, check if user is added to the database
    with app.app_context():
        user = db.session.execute(
            "SELECT * FROM users WHERE email=:email",
            {'email': signup_data['email']}
        ).fetchone()
        assert user is not None
        assert user.username == signup_data['username']
