from flask import Flask, render_template, request, redirect, url_for
from db.server import app, db  # import all from server
from sqlalchemy import *

from db.schema.Users import Users
from db.schema.UserTypes import UserTypes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        # Get values from form
        new_email = request.form["Email"]
        new_password = request.form["Password"]
        new_first_name = request.form["FirstName"]
        new_last_name = request.form["LastName"]
        new_user_type = request.form["UserType"]

        # Define allowed user types
        allowed_user_types = ['Driver', 'Customer', 'StoreOwner']

        # Check if the user type is valid
        if new_user_type not in allowed_user_types:
            return "Invalid user type. Please select from Driver, Customer, or Store Owner.", 400

        # Check if the user type exists in the database
        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == new_user_type)).scalar_one_or_none()

        # If it doesn't exist, create a new user type
        if existing_user_type is None:
            create_user_type = insert(UserTypes).values(TypeName=new_user_type)
            db.session.execute(create_user_type)
            db.session.commit()

            # Grab the created user type's ID
            user_type_id = db.session.execute(select(UserTypes.UserTypeID).where(UserTypes.TypeName == new_user_type)).scalar_one()
        else:
            # Use the existing user type's ID
            user_type_id = existing_user_type.UserTypeID

        # Create a new user
        create_user = insert(Users).values(
            UserTypeID=user_type_id,
            Email=new_email,
            Password=new_password,
            FirstName=new_first_name,
            LastName=new_last_name,
            Address=None,
            CardNumber=None
        )
        db.session.execute(create_user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('signup.html')
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
    # from request.form extract password and Email
        entered_pass = request.form["Password"]
        entered_email = request.form["Email"]

        # select password from users where Email == entered_email and compare to input password
        pass_query = select(Users.Password).where(Users.Email == entered_email)

        # return redirect if accepted to new page to be created for login
        user_pass = db.session.execute(pass_query).fetchone()

        # return to homepage/maybe send message of failure
        if user_pass[0] == entered_pass:
            return redirect(url_for('index'))
        else:
            # redirect to login
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/users')
def users():
    return render_template('users.html')

if __name__ == "__main__":
    app.run(debug=True)