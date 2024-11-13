from flask import Flask, render_template, request, redirect, url_for, session
from db.server import app, db, reset_database
from sqlalchemy import *

import os
import bcrypt
import argparse
import re

from db.schema.Users import Users
from db.schema.Store import Store
from db.schema.Menu import Menu
from db.schema.Orders import Orders
from db.schema.OrderItems import OrderItems

from db.schema.MenuItems import MenuItems
from db.schema.UserTypes import UserTypes

from helper import *

# Import need a SECRET KEY -> Please Store one in your .env file really doesnt matter what it is set to mine is buttcheeks
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key_here')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # if logged in redirect to account info
        if 'user_id' in session: return redirect(url_for('home'))

        return render_template('index.html')
    else:
        # Backend Check if REGEX was matched -> return any errors found
        if verifySignup(request): return verifySignup(request)
        
        createUser(request) # Create the new user if no errors

        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Backend Check if REGEX was matched -> return any errors found
        if verifySignup(request): return verifySignup(request)
        
        createUser(request) # Create the new user if no errors

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

# ! needs logic for deleting store owner and drivers
@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            return deleteUser()
    
    # Redirect to login if not logged in
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # Fetch user details from the database using the user ID
    user_id = session.get('user_id')
    user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()
    return render_template('account.html', user=user)

@app.route('/logout')
def logout():
    # Drop any user specific session informaion
    session.pop('user_id', None)
    session.pop('potential_order_id', None)
    session.pop('order_id', None)
    return redirect(url_for('index'))

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    # Redirect to login if not logged in
    if 'user_id' not in session: return redirect(url_for('login'))

    # Reset the passwowrd on POST
    if request.method == 'POST': return resetPassword(request)

    return render_template('reset.html')

@app.route('/home')
def home():
    # Redirect to login if not logged in
    if 'user_id' not in session: return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")
    
    return render_template('home.html')

@app.route('/404')
def invalid_page():
    return render_template('404.html')

# ! Needs backend logic
@app.route('/driver')
def driver():
    # if no one is logged in dont allow access
    if 'user_id' not in session:
        return redirect(url_for('index'))

    # Redirect if wrong user type
    if checkUserType("Driver"): return checkUserType("Driver")

    # find all available orders
    orders = findAvailableOrders()
    
    return render_template('driver.html', orders=orders)

# ! Needs frontend and backend logic
@app.route('/storeOwner')
def storeOwner():
    # Redirect if wrong user type
    if checkUserType("StoreOwner"): return checkUserType("StoreOwner")

    return render_template('storeOwner.html')

@app.route('/search')
def search():
    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # redirection to order status if order exists
    if 'order_id' in session: return redirect(url_for('status'))

    # Get the 'query' parameter from the URL
    query = request.args.get('query')

    if query:
        # Query the database for stores matching the query
        stores = Store.query.filter(Store.StoreName.ilike(f'%{query}%')).all()
    else:
        # pass all stores
        stores = Store.query.all()

    return render_template('search.html', stores=stores)

@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # redirect if existing order
    if 'order_id' in session: return redirect(url_for('status'))

    # Request for deleting an order item
    if request.form.get('order_item_id') is not None: return deleteOrderItem(request)
        
    # Get the 'restaurant' parameter from the URL query string
    restaurant_name = request.args.get('restaurant')

    # if restaurant page is accessed without a parameter well redirect to avoid erroring
    if not restaurant_name: return redirect(url_for('index'))

    curr_restaurant = Store.query.filter_by(StoreName=restaurant_name).first() # Look up the current restaurant
    menu = Menu.query.get(curr_restaurant.StoreID) # Look up menu associated with current restaurant
    menu_items = MenuItems.query.filter(MenuItems.MenuID == menu.MenuID).all() # Look up all menu items associated with the current menu

    # if were adding an item to our order
    if request.method == 'POST': addOrder(request, curr_restaurant)

    # return existing order or new order
    return checkPotentialOrder(curr_restaurant, menu_items)

@app.route('/status')
def status():
    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # add redirection to login if not logged in -> hold potential current order ID
    if 'user_id' not in session: return redirect(url_for('login'))

    # add the user id to the order if it is not already set in the database
    is_user_null = db.session.execute(select(Orders).where(Orders.OrderID == session.get('potential_order_id'), Orders.UserID == None)).scalar_one_or_none()
    if is_user_null:
        is_user_null.UserID = session.get('user_id')
        db.session.commit()

    # convert session potential order into order
    # this will execute only on first visit to status
    if session.get('potential_order_id'):
        session['order_id'] = session.get('potential_order_id')
        session.pop('potential_order_id', None)

        # update order status in db
        db.session.execute(update(Orders).where(Orders.OrderID == session.get('order_id')).values(OrderStatus="Created"))
        db.session.commit()

    # get current order from session
    current_order = db.session.execute(select(Orders).where(Orders.OrderID == session.get('order_id'))).scalar_one_or_none()

    # get resteraunt from current order
    curr_restaurant = db.session.execute(select(Store).where(Store.StoreID == current_order.StoreID)).scalar_one_or_none()

    return render_template('status.html', current_order=current_order, curr_restaurant=curr_restaurant)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # redirection to order status if order exists
    if 'order_id' in session: return redirect(url_for('status'))

    # must have potential order to access checkout
    if 'potential_order_id' not in session: return redirect(url_for('home'))

    # check if were deleting an order
    if request.method == 'POST': return deleteOrder()

    # return relevent order information
    return checkoutInformation()

# Function to wipe session variables on program start -> Forces user cookie dump
@app.before_request
def clear_session():
    # Check if this is the first request
    if not hasattr(app, 'has_run_before'):
        # Clear the session on the first request
        session.clear()
        # Mark that the first request has been processed
        app.has_run_before = True
    pass

if __name__ == "__main__":
    # Parse arguments passed with python execution
    parser = argparse.ArgumentParser(description="Run the Flask app with optional database reset.")
    parser.add_argument('--reset-db', action='store_true', help="Reset the database (drop and create tables).")
    args = parser.parse_args()

    # if we find the reset db flag has been passed we will execute reset
    if args.reset_db:
        with app.app_context():
            reset_database()
    
    # Find a free port from 5000-5004
    # dont need any more for our use cases at the moment
    free_port = find_free_port(5000, 5004)

    if free_port:
        print(f"App Running on port: {free_port}")
        app.run(debug=False, port=free_port)
    else:
        print(f"No free port found in range {start_port}-{end_port}")