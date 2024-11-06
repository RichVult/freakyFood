from flask import Flask, render_template, request, redirect, url_for, session
from db.server import app, db
from sqlalchemy import *

import os
import bcrypt
import re

from db.schema.Users import Users
from db.schema.Store import Store
from db.schema.Menu import Menu
from db.schema.MenuItems import MenuItems
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
            CardNumber=None,
            ProfileImage="default_profile.png"
        )
        # Execute Query and Commit to DB
        db.session.execute(create_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ! ADD if session contains a potential order ID and we become logged in redirect back to order page to complete order
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

@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            user_id = session['user_id']
            # Delete the user from the database
            db.session.execute(delete(Users).where(Users.UserID == user_id))
            db.session.commit()

            # Remove the user from the session and redirect to the home page
            session.pop('user_id', None)
            return redirect(url_for('index'))
    
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

@app.route('/search')
def search():
    # redirection to order status if order exists
    if 'order_id' in session:
        return redirect(url_for('status'))

    # redirection to checkout if potential order id exists
    if 'potential_order_id' in session:
        return redirect(url_for('checkout'))

    # Get the 'query' parameter from the URL
    query = request.args.get('query')

    if query:
        # Query the database for stores matching the query
        stores = Store.query.filter(Store.StoreName.ilike(f'%{query}%')).all()
    else:
        # pass all stores
        stores = Store.query.all()

    return render_template('search.html', stores=stores)

@app.route('/restaurant', methods=['GET', 'POST', 'DELETE'])
def restaurant():
    if request.method == 'POST':
        # We are adding an item or creating a potential order
        # look up item_id of requested item 
        requested_quantity = request.form['quantity']
        requested_item = MenuItems.query.filter_by(MenuItemID=request.form['item_id']).first()
        print(requested_item)
        # if potential order doesnt exist we will create it and add to session

        # add the added item to the potential order

    elif request.method =='DELETE':
        # We are removing an item from a potential order
        print(request.form)

    # GET Always occurs to display updated order and information

    # Get the 'restaurant' parameter from the URL query string
    restaurant_name = request.args.get('restaurant')

    # Look up the current restaurant
    curr_restaurant = Store.query.filter_by(StoreName=restaurant_name).first()

    # Look up menu associated with current restaurant
    menu = Menu.query.get(curr_restaurant.StoreID)

    # Look up all menu items associated with the current menu
    menu_items = MenuItems.query.filter(MenuItems.MenuID == menu.MenuID).all()

    # redirection to order status if order exists
    if 'order_id' in session:
        return redirect(url_for('status'))

    # ! NEEDS TESTING Check potential order and redirect accordingly
    if 'potential_order_id' in session:
        # get from session
        potential_order_id = session['potential_order_id']
        
        # Look up the order in the database based on potential_order_id
        potential_order = Orders.query.get(potential_order_id)
        
        # if potential order not from this restaurant redirect to checkout
        if potential_order.StoreID != curr_restaurant.StoreID:
            return redirect(url_for('checkout'))
        else:
            # render template with current potential order
            return render_template('resteraunt.html', curr_restaurant=curr_restaurant, potential_order=potential_order, menu_items=menu_items) 

    print(menu)
    return render_template('restaurant.html',curr_restaurant=curr_restaurant, menu_items=menu_items)

@app.route('/status')
def status():
    # ! add redirection to login if not logged in -> hold potential current order ID
    return render_template('status.html')

@app.route('/checkout')
def checkout():
    # ! add redirection to order status if order exists

    # ! add redirection if missing account info

    return render_template('checkout.html')

if __name__ == "__main__":
    app.run(debug=True)