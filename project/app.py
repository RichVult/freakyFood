from flask import Flask, render_template, request, redirect, url_for, session
from db.server import app, db
from sqlalchemy import *
import os
from db.schema.Users import Users
from db.schema.UserTypes import UserTypes

# Import need a SECRET KEY -> Please Store one in your .env file really doesnt matter what it is set to mine is buttcheeks
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key_here')

@app.route('/')
def index():
    # if logged in redirect to account info
    if 'user_id' in session:
        return redirect(url_for('account'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # from request.form extract password and Email
        entered_pass = request.form["Password"]
        entered_email = request.form["Email"]

        # find user associated with email
        user_query = select(Users).where(Users.Email == entered_email)
        user = db.session.execute(user_query).scalar_one_or_none()

        # Check if the user exists and the password matches
        if user and user.Password == entered_pass:  

            # set our session user id -> this allows for us to keep track of the current user throughout pages
            session['user_id'] = user.UserID 
            return redirect(url_for('home'))  
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/account')
def account():
    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch user details from the database using the user ID
    user_id = session['user_id']
    user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()
    return render_template('account.html', user=user)

@app.route('/logout')
def logout():
    # Remove the user ID from the session
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/reset', methods=['GET', 'POST'])
def reset():

    if request.method == 'POST':
        #checks current password and changes it to new password.
        user_id = session['user_id']
        current_password = request.form["CurrentPassword"]
        new_password = request.form["NewPassword"]


        user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()

        if user and user.Password == current_password:
            user.Password = new_password
            db.session.commit()
            return redirect(url_for('account')) 
        else:
            return render_template('reset.html', error="Current password is incorrect.")

    return render_template('reset.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
