"""db.py: connect to Postgres database and create tables"""
import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# import environment variables from .env
load_dotenv()

# create the flask application with the same name as the file
app = Flask(__name__)

# tell flask which database you want to connect to. pulls values from .env
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{os.getenv('db_owner')}:{os.getenv('db_pass')}@localhost/{os.getenv('db_name')}"

# flask-sqlalchemy instance; used for all database interactions
db = SQLAlchemy(app)

# this import is here because we need to initialize db before importing it into
# the classes
#from db.schema.course import Course
# uncomment the line below after creating the professor class
#from db.schema.professor import Professor
# uncomment the line below after reviewing the assoc table
#from db.schema.assoc import ProfessorCourse

from db.schema import Store
from db.schema import Users
from db.schema import UserTypes

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
    
    # create all database tables
    db.create_all()

