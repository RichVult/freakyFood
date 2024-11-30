from flask import Flask, render_template, request, redirect, url_for, session
from db.server import app, db, reset_database
from sqlalchemy import *

import os, bcrypt, argparse, re

from db.schema import Users, Store, Menu, Orders, OrderItems, MenuItems, UserTypes

from controller import *

'''
    Access: Logged Out | Purpose: Learn about freaky food and login or signup | TODO: Nothing
'''
@app.route('/', methods=['GET', 'POST'])
def index():
    return handleIndex()

'''
    Access: Logged Out | Purpose: Create an account with freaky food | TODO: Nothing
'''
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return handleSignup()

'''
    Access: Logged Out | Purpose: Login to freaky food | TODO: Nothing
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    return handleLogin()

'''
    Access: Logged In | Purpose: See/Change/Delete account info and logout | TODO: Frontend, User specific logic, updating information
'''
@app.route('/account', methods=['GET', 'POST'])
def account():
    return handleAccount()
'''
    Access: Logged In | Purpose: Logout of current account | TODO: Nothing
'''
@app.route('/logout')
def logout():
    return handleLogout()

'''
    Access: Logged In | Purpose: Reset current account password | TODO: Nothing
'''
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    return handleReset()

'''
    Access: Logged In as USER | Purpose: Home page for users to see restaurants and start order | TODO: Nothing
'''
@app.route('/home')
def home():
    return handleHome()

'''
    Access: ALL | Purpose: 404 Page For Temporary Use | TODO: Implement redirect to this page when we search for bad URL
'''
@app.route('/404')
def invalid_page():
    return render_template('404.html')

'''
    Access: Logged In as DRIVER | Purpose: Driver home page to accept orders | TODO: Frontend
'''
@app.route('/driver', methods=['GET', 'POST'])
def driver():
    return handleDriver()

'''
    Access: Logged In as DRIVER | Purpose: Fullfill an order | TODO: Frontend and Chat with Users
'''
@app.route('/driverStatus', methods=['GET', 'POST'])
def driverStatus():
    return handleDriverStatus()

'''
    Access: Logged In as STORE OWNER | Purpose: Store Owner home page to see all current orders | TODO: Frontend
'''
@app.route('/storeOwner', methods=['GET', 'POST'])
def storeOwner():
    return handleStoreOwner()

'''
    Access: Logged In as USER | Purpose: Search for restaurants | TODO: Frontend
'''
@app.route('/search')
def search():
    return handleSearch()

'''
    Access: Logged In as USER | Purpose: View a restaurant and create an order | TODO: Frontend
'''
@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    return handleRestaurant()

'''
    Access: Logged In as USER | Purpose: View an in progress order | TODO: Frontend
'''
@app.route('/status')
def status():
    return handleStatus()

'''
    Access: Logged in as USER | Purpose: Checkout a created order | TODO: Ensure information and payments
'''
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return handleCheckout()

'''
    To be called ONCE per session to clear the session for new use
'''
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