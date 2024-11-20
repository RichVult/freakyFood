"""server.py: connect to Postgres database and create tables"""

import os
from dotenv import load_dotenv
import random
import string
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# import our queries
from db.scripts.dummyData import insert_user_types
from db.scripts.dummyData import insert_user
from db.scripts.dummyData import insert_store
from db.scripts.dummyData import insert_orders
from db.scripts.dummyData import insert_orderitems
from db.scripts.dummyData import insert_menuitems 
from db.scripts.dummyData import insert_menu

# import environment variables from .env
load_dotenv()

db_name: str = os.getenv('db_name')
db_owner: str = os.getenv('db_owner')
db_pass: str = os.getenv('db_pass')
db_uri: str = f"postgresql://{db_owner}:{db_pass}@localhost/{db_name}"

def generate_random_session_name():
    return 'session_' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Adjust the path to be absolute from the project root
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'project/templates'), static_folder=os.path.join(os.getcwd(), 'project/static'))

# Set a unique session cookie name
app.config.update(SESSION_COOKIE_NAME=generate_random_session_name())
app.config['SECRET_KEY'] = os.urandom(24)  # Secure key for signing cookies (ensure it's random and kept secret)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

# Secret Key Needed for Session Control
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key_here')

db = SQLAlchemy(app)

# import table to be created in postgres
from db.schema.Menu import Menu
from db.schema.MenuItems import MenuItems
from db.schema.OrderItems import OrderItems
from db.schema.Orders import Orders
from db.schema.Store import Store
from db.schema.UserTypes import UserTypes
from db.schema.Users import Users

# verify the db connection is successful
with app.app_context():
    # attempt to connect to db, print msgs if successful
    try:
        # run SQL query to verify connection (see how we use the db instance?)
        db.session.execute(text("SELECT 1"))
        print(f"\n\n----------- Connection successful!")
        print(f" * Connected to database: {os.getenv('db_name')}")
    # failed to connect to db, provide msgs & error
    except Exception as error:
        print(f"\n\n----------- Connection failed!")
        print(f" * Unable to connect to database: {os.getenv('db_name')}")
        print(f" * ERROR: {error}")

# Function to handle argument to reset the database
def reset_database():
    db.drop_all()
    print("DB: DROPPED ALL TABLES")
    db.create_all()
    print("DB: CREATED ALL TABLES")
    # Insert dummy data
    insert_user_types()
    insert_user()
    insert_store()
    insert_orders()
    insert_orderitems()
    insert_menu()
    insert_menuitems()
    db.session.commit()
    print("Database reset complete.")