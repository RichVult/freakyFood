import os
import bcrypt
import re
from flask import Flask, render_template, request, redirect, url_for, session
from db.server import app, db
from sqlalchemy import *
from db.schema.Users import Users
from db.schema.UserTypes import UserTypes

# Import need a SECRET KEY -> Please Store one in your .env file really doesnt matter what it is set to mine is buttcheeks
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key_here')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # if logged in redirect to account info
        if 'user_id' in session:
            return redirect(url_for('account'))
        return render_template('index.html')
    else:
        # Define allowed user types
        allowed_user_types = ['Driver', 'Customer', 'StoreOwner']

        # Get values from form and remove whitespace
        new_email = request.form["Email"].strip()
        new_password = request.form["Password"].strip()
        new_password_two = request.form["PasswordTwo"].strip()
        new_first_name = request.form["FirstName"].strip()
        new_last_name = request.form["LastName"].strip()
        new_user_type = request.form["UserType"].strip()

        # INPUT SANITIZATION & VERIFICATION

        # Backend Check if REGEX was matched
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        password_pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$"
        name_pattern = r"^[A-Za-z]+$"

        if not re.match(email_pattern, new_email):
            return "Invalid email format.", 400

        if not re.match(password_pattern, new_password):
            return "Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character.", 400

        if not re.match(name_pattern, new_first_name):
            return "First name can only contain letters.", 400

        if not re.match(name_pattern, new_last_name):
            return "Last name can only contain letters.", 400

        # Check if email exists 
        if db.session.execute(select(Users).where(Users.Email == new_email)).scalar_one_or_none():
            return "Email already associated to another user.", 400

        # Check if the user type is valid
        if new_user_type not in allowed_user_types:
            return "Invalid user type. Please select from Driver, Customer, or Store Owner.", 400

        # Check if passwords match
        if new_password != new_password_two:
            return "Passwords do not match.", 400
        
        # Grab usertype ID of user type selected
        user_type_id = db.session.execute(select(UserTypes.UserTypeID).where(UserTypes.TypeName == new_user_type)).scalar_one()

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')

        # Create a new user
        create_user = insert(Users).values(
            UserTypeID=user_type_id,
            Email=new_email,
            Password=hashed_password,
            FirstName=new_first_name,
            LastName=new_last_name,
            Address=None,
            CardNumber=None
        )

        # Execute Query and Commit to DB
        db.session.execute(create_user)
        db.session.commit()
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Define allowed user types
        allowed_user_types = ['Driver', 'Customer', 'StoreOwner']

        # Get values from form and remove whitespace
        new_email = request.form["Email"].strip()
        new_password = request.form["Password"].strip()
        new_password_two = request.form["PasswordTwo"].strip()
        new_first_name = request.form["FirstName"].strip()
        new_last_name = request.form["LastName"].strip()
        new_user_type = request.form["UserType"].strip()

        # INPUT SANITIZATION & VERIFICATION

        # Backend Check if REGEX was matched
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        password_pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$"
        name_pattern = r"^[A-Za-z]+$"

        if not re.match(email_pattern, new_email):
            return "Invalid email format.", 400

        if not re.match(password_pattern, new_password):
            return "Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character.", 400

        if not re.match(name_pattern, new_first_name):
            return "First name can only contain letters.", 400

        if not re.match(name_pattern, new_last_name):
            return "Last name can only contain letters.", 400

        # Check if email exists 
        if db.session.execute(select(Users).where(Users.Email == new_email)).scalar_one_or_none():
            return "Email already associated to another user.", 400

        # Check if the user type is valid
        if new_user_type not in allowed_user_types:
            return "Invalid user type. Please select from Driver, Customer, or Store Owner.", 400

        # Check if passwords match
        if new_password != new_password_two:
            return "Passwords do not match.", 400
        
        # Grab usertype ID of user type selected
        user_type_id = db.session.execute(select(UserTypes.UserTypeID).where(UserTypes.TypeName == new_user_type)).scalar_one()

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')

        # Create a new user
        create_user = insert(Users).values(
            UserTypeID=user_type_id,
            Email=new_email,
            Password=hashed_password,
            FirstName=new_first_name,
            LastName=new_last_name,
            Address=None,
            CardNumber=None
        )

        # Execute Query and Commit to DB
        db.session.execute(create_user)
        db.session.commit()
        return redirect(url_for('login'))

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
        if user and bcrypt.checkpw(entered_pass.encode(), user.Password.encode()):

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
    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        #checks current password and changes it to new password.
        user_id = session['user_id']
        current_password = request.form["CurrentPassword"]
        new_password = request.form["NewPassword"]

        user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()

        # Verify the current password
        if user and bcrypt.checkpw(current_password.encode(), user.Password.encode()):
            # backend check for password matches regex
            if not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$", new_password):
                return "Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character.", 400

            # Hash the new password and update it in the database
            hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
            user.Password = hashed_new_password
            db.session.commit()
            return redirect(url_for('account')) 
        else:
            return render_template('reset.html', error="Current password is incorrect.")

    return render_template('reset.html')

@app.route('/home')
def home():
    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('home.html')

@app.route('/404')
def invalid_page():
    return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)
