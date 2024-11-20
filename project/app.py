"""
app.py: Route controller for the web application.

This file defines the routes and view functions for handling HTTP requests
and rendering appropriate templates. It handles user authentication, session
management, and interaction with the application's database models to manage
users, stores, orders, and other related entities.

Routes include:
- '/' (index): Displays the homepage or handles user signup.
- '/signup': Handles the user signup process.
- '/login': Handles user login and authentication.
- '/account': Displays and manages the user account information.
- '/logout': Logs the user out and clears the session.
- '/reset': Resets the user's password.
- '/home': Displays the homepage for logged-in users.
- '/404': Renders a "Page Not Found" error page.
- '/driver': Allows drivers to accept orders.
- '/driverStatus': Displays and manages the status of accepted orders for drivers.
- '/storeOwner': Allows store owners to manage orders.
- '/search': Allows users to search for stores by name.

This file also handles user role checks and permission management to ensure
that users only access routes relevant to their role (e.g., driver, store owner,
customer).

Imports:
- Flask: For handling HTTP requests and rendering templates.
- SQLAlchemy: For interacting with the database and models.
- bcrypt: For password hashing and verification.
- argparse: For command-line argument parsing (if needed).
- Various database schema models for Users, Store, Menu, Orders, etc.
- Helper functions for tasks like password reset, user verification, and order management.
"""

from flask import Flask, render_template, request, redirect, url_for, session
from db.server import app, db, reset_database
from sqlalchemy import *

import os
import bcrypt
import argparse

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
    """
    Handles the main landing page of the application for both GET and POST requests.

    If the user is logged in (i.e., a 'user_id' is present in the session), they are
    redirected to their account page (home). If not, the function renders the index
    page for new users to sign up or log in.

    For POST requests, the function handles user signup by verifying the input data
    using a helper function (`verifySignup`). If validation fails, it returns the
    validation errors. If validation passes, it creates a new user and redirects the
    user to the login page.

    Methods:
    - GET: Displays the signup page if the user is not logged in, or redirects to the account page if the user is logged in.
    - POST: Handles user signup by verifying the provided data, creating a new user, and redirecting the user to the login page if the signup is successful.

    Returns:
    - A redirect to the home page if the user is logged in.
    - A rendered 'index.html' template for new users to sign up.
    - A redirect to the login page after a successful signup.
    """
    if request.method == 'GET':
        # if logged in redirect to account info
        if 'user_id' in session:
            return redirect(url_for('home'))

        return render_template('index.html')
    else:
        # Backend Check if REGEX was matched -> return any errors found
        if verifySignup(request):
            return verifySignup(request)

        createUser(request)  # Create the new user if no errors

        return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles the user signup process for both GET and POST requests.

    If the request method is GET, the function renders the signup page where 
    users can input their details to create a new account.

    If the request method is POST, the function validates the user's input data 
    using the `verifySignup` helper function. If validation fails, it returns 
    any validation errors. If validation passes, a new user is created using 
    the `createUser` function, and the user is redirected to the login page 
    for authentication.

    Methods:
    - GET: Displays the signup page where a new user can register.
    - POST: Validates the signup form data, creates the new user if valid, and redirects to the login page.

    Returns:
    - A redirect to the login page after a successful signup.
    - A rendered 'signup.html' template for displaying the signup form.
    """
    if request.method == 'POST':
        # Backend Check if REGEX was matched -> return any errors found
        if verifySignup(request):
            return verifySignup(request)

        createUser(request)  # Create the new user if no errors

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles the user login process for both GET and POST requests.

    If the user is already logged in (i.e., a 'user_id' exists in the session), 
    the function redirects the user to their account home page.

    For POST requests, the function extracts the user's email and password 
    from the login form, then queries the database to find the user associated 
    with the provided email. If the user exists and the provided password 
    matches the stored password, the function sets the session with the user's 
    ID and redirects them to their account home page. If the credentials are 
    incorrect, an error message is returned on the login page.

    Methods:
    - GET: Displays the login page for the user to input their credentials.
    - POST: Verifies the user's email and password, sets the session if valid, or returns an error message if invalid.

    Returns:
    - A redirect to the user's home page if login is successful.
    - A rendered 'login.html' template, with an error message if the login fails.
    """
    # if logged in redirect to account info
    if 'user_id' in session:
        return redirect(url_for('home'))

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
    """
    Handles the user's account page for both GET and POST requests.

    For POST requests, the function checks if the form submission is a request to delete a user. 
    If so, it identifies the type of user to be deleted (Driver, Customer, or StoreOwner) and calls 
    the appropriate delete function based on the user type.

    For GET requests, if the user is logged in (i.e., a 'user_id' exists in the session), 
    the function fetches the user's details from the database and renders the 'account.html' page 
    with the user's information.

    If the user is not logged in, they are redirected to the login page.

    Methods:
    - GET: Fetches the user details from the database and renders the account page.
    - POST: Deletes a user based on the selected action (Driver, Customer, or StoreOwner).

    Returns:
    - A redirect to the login page if the user is not logged in.
    - A rendered 'account.html' template with the user's information if logged in.
    - Calls the appropriate delete function if a user deletion is requested.
    """
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            # get the type of user which is being deleted
            user_type = db.session.execute(select(UserTypes).where(
                UserTypes.UserTypeID == request.form.get('userID'))).scalar_one_or_none()
            match user_type.TypeName:
                case "Driver":
                    return deleteDriver()
                case "Customer":
                    return deleteUser()
                case "StoreOwner":
                    return deleteStoreOwner()
    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch user details from the database using the user ID
    user_id = session.get('user_id')
    user = db.session.execute(select(Users).where(
        Users.UserID == user_id)).scalar_one_or_none()
    return render_template('account.html', user=user)


@app.route('/logout')
def logout():
    """
    Logs the user out by clearing their session information.

    This function removes the 'user_id', 'potential_order_id', and 'order_id' 
    from the session, effectively logging the user out and clearing any order 
    information associated with the session. After clearing the session, it 
    redirects the user to the index page.

    Returns:
    - A redirect to the 'index' page after the session data is cleared.
    """
    # Drop any user specific session informaion
    session.pop('user_id', None)
    session.pop('potential_order_id', None)
    session.pop('order_id', None)
    return redirect(url_for('index'))


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    """
    Handles password reset requests.

    If the user is not logged in, they are redirected to the login page.
    If the request method is POST, the password is reset using the 
    resetPassword function. If the request method is GET, the reset password 
    page is rendered.

    Returns:
    - A redirect to the 'login' page if the user is not logged in.
    - A result of the resetPassword function if the request is a POST.
    - The 'reset.html' template if the request is a GET.
    """
    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Reset the passwowrd on POST
    if request.method == 'POST':
        return resetPassword(request)

    return render_template('reset.html')


@app.route('/home')
def home():
    """
    Handles the home page request.

    If the user is not logged in, they are redirected to the login page.
    If the user's type is "Customer", they are redirected based on the 
    checkUserType function.

    Returns:
    - A redirect to the 'login' page if the user is not logged in.
    - A redirect based on the checkUserType function if the user is a "Customer".
    - The 'home.html' template if the user is logged in and has the correct user type.
    """
    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("Customer"):
        return checkUserType("Customer")

    return render_template('home.html')


@app.route('/404')
def invalid_page():
    """
    Renders the 404 error page.

    This function is triggered when the user tries to access a non-existent 
    or invalid page. It returns the '404.html' template to notify the user 
    that the page was not found.

    Returns:
    - The '404.html' template.
    """
    return render_template('404.html')


@app.route('/driver', methods=['GET', 'POST'])
def driver():
    """
    Handles the driver's order acceptance process.

    This function manages the drivers interaction with available orders. If the driver
    has already accepted an order, they are redirected to the driver status page. If the driver
    is not logged in or has the wrong user type, they are redirected to the login page or appropriate user page.
    On a POST request, if the driver accepts an order, it updates the order's status to "Accepted" 
    and stores the order ID in the session.

    If no order is accepted, the driver can view all available orders.

    Returns:
    - Redirects to the 'driverStatus' page if an order is accepted.
    - Renders the 'driver.html' template with a list of available orders if no order is accepted.
    """
    # if we have already accepted an order
    if 'accepted_order_id' in session:
        return redirect(url_for('driverStatus'))

    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("Driver"):
        return checkUserType("Driver")

    # if we accept an order
    if request.method == 'POST':
        # add accepted order to session
        session['accepted_order_id'] = request.form.get('orderID')

        # update accepted order's order status
        db.session.execute(update(Orders).where(Orders.OrderID == session.get(
            'accepted_order_id')).values(OrderStatus="Accepted"))
        db.session.commit()

        return redirect(url_for('driverStatus'))

    # find all available orders
    orders = findAvailableOrders("Created")

    return render_template('driver.html', orders=orders)

# For when a driver accepts an order


@app.route('/driverStatus', methods=['GET', 'POST'])
def driverStatus():
    """
    Manages the driver's current order status and actions.

    This function handles the driver's view and interaction with their accepted order. If the driver
    is not logged in or has not accepted an order, they are redirected to the login page or the driver
    page. If the driver has accepted an order, they can update the order's status (e.g., mark it as "Pickup" 
    or "Delivered") based on the current status of the order.

    On a POST request:
    - If the order is in the "Ready" status, the driver can update it to "Pickup."
    - If the order is in the "Pickup" status, the driver can mark it as "Delivered" and then be redirected back to the driver page.

    If no action is taken, the function displays the current order details and associated restaurant.

    Returns:
    - Redirects to the 'driver' page if the order is delivered.
    - Renders the 'driverStatus.html' template with the current order details and restaurant if no action is taken.
    """
    # ? Potential Implementation here for a chat room with the ordering user

    # if were not logged in redirect
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # if we have not already accepted an order
    if 'accepted_order_id' not in session:
        return redirect(url_for('driver'))

    # Redirect if wrong user type
    if checkUserType("Driver"):
        return checkUserType("Driver")

    # Changing the order status
    if request.method == 'POST':
        # Get order ID and desired action from the form data
        order_id = request.form.get('order_id')
        action = request.form.get('action')

        if order_id:
            # Fetch the order by ID
            order = db.session.execute(select(Orders).where(
                Orders.OrderID == order_id)).scalar_one_or_none()

            # Check which action to perform and update the order status accordingly
            if action == "Pickup" and order.OrderStatus == "Ready":
                # update accepted order's order status
                db.session.execute(update(Orders).where(
                    Orders.OrderID == order.OrderID).values(OrderStatus="Pickup"))
                db.session.commit()
            elif action == "Deliver" and order.OrderStatus == "Pickup":
                # update accepted order's order status
                db.session.execute(update(Orders).where(
                    Orders.OrderID == order.OrderID).values(OrderStatus="Delivered"))
                db.session.commit()
                session.pop('accepted_order_id', None)
                return redirect(url_for('driver'))

    # get variables for driver status
    current_order = db.session.execute(select(Orders).where(
        Orders.OrderID == session.get('accepted_order_id'))).scalar_one_or_none()
    curr_restaurant = db.session.execute(select(Store).where(
        Store.StoreID == current_order.StoreID)).scalar_one_or_none()

    return render_template('driverStatus.html', current_order=current_order, curr_restaurant=curr_restaurant)

# Store owner home page


@app.route('/storeOwner', methods=['GET', 'POST'])
def storeOwner():
    """
    Manages the store owner's ability to accept, update, and complete orders.

    This function allows the store owner to interact with orders in various stages. The store owner can:
    - Accept an order and mark it as "In Progress."
    - Complete an order and mark it as "Ready" for pickup.

    If the store owner is not logged in or has the wrong user type, they are redirected to the login page or 
    the appropriate user page. When a POST request is made, the function processes the order ID and the desired 
    action to update the order status accordingly.

    The function also retrieves and categorizes orders based on their current status:
    - "Accepted": Orders that a driver has accepted but the store has not yet processed.
    - "In Progress": Orders that are being processed by the store.
    - "Ready": Orders that are completed and awaiting pickup by a driver.

    Returns:
    - Renders the 'storeOwner.html' template with categorized orders: waiting orders, in-progress orders, and ready orders.
    """
    # Redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("StoreOwner"):
        return checkUserType("StoreOwner")

    # determine how we are manipulating the orders
    # this will update order status' correctly depending on request information
    if request.method == 'POST':
        # Get order ID and desired action from the form data
        order_id = request.form.get('orderID')
        action = request.form.get('action')

        if order_id:
            # Fetch the order by ID
            order = db.session.execute(select(Orders).where(
                Orders.OrderID == order_id)).scalar_one_or_none()

            # Check which action to perform and update the order status accordingly
            if action == "accept" and order.OrderStatus == "Accepted":
                # update accepted order's order status
                db.session.execute(update(Orders).where(
                    Orders.OrderID == order.OrderID).values(OrderStatus="In Progress"))
                db.session.commit()
            elif action == "complete" and order.OrderStatus == "In Progress":
                # update accepted order's order status
                db.session.execute(update(Orders).where(
                    Orders.OrderID == order.OrderID).values(OrderStatus="Ready"))
                db.session.commit()

    # find all "Accpeted" Orders -> A driver has selected it
    waiting_orders = findAvailableOrders("Accepted")
    if len(waiting_orders) == 0:
        waiting_orders = None

    # find all "In Progress" Orders -> The Store has accepted it
    in_progress_orders = findAvailableOrders("In Progress")
    if len(in_progress_orders) == 0:
        in_progress_orders = None

    # find all "Ready" order -> Awaiting Pickup
    ready_orders = findAvailableOrders("Ready")
    if len(ready_orders) == 0:
        ready_orders = None

    return render_template('storeOwner.html', waiting_orders=waiting_orders, in_progress_orders=in_progress_orders, ready_orders=ready_orders)


@app.route('/search')
def search():
    """
    Handles the search functionality for customers to find stores based on a query.

    This function checks if the current user is a customer and redirects to the appropriate page if so. 
    It also checks if an order ID exists in the session, in which case it redirects to the order status page. 

    If a search query is provided through the URL's `query` parameter, the function queries the database 
    for stores whose names match the search query (case-insensitive). If no query is provided, all stores 
    are returned.

    The results are passed to the 'search.html' template for rendering.

    Returns:
    - Renders the 'search.html' template with the stores that match the search query or all stores if no query is provided.
    """
    # Redirect if wrong user type
    if checkUserType("Customer"):
        return checkUserType("Customer")

    # redirection to order status if order exists
    if 'order_id' in session:
        return redirect(url_for('status'))

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
    """
    Handles the restaurant page where customers can view the menu and add items to their order.

    This function first checks the user's type and redirects if the user is a customer, or if an order already exists in the session. 
    If an order item ID is provided, the function deletes the specified order item.

    It then retrieves the restaurant name from the URL query string and ensures that the restaurant is valid. If the restaurant name 
    is not provided, the user is redirected to the homepage.

    The function looks up the restaurant's details, menu, and associated menu items, and if the user is adding an item to their order, 
    it calls the function to add the item. The function then returns the current or new order to the user.

    Returns:
    - Renders the restaurant's menu and items, either returning the existing order or a new order depending on user interaction.
    """
    # Redirect if wrong user type
    if checkUserType("Customer"):
        return checkUserType("Customer")

    # redirect if existing order
    if 'order_id' in session:
        return redirect(url_for('status'))

    # Request for deleting an order item
    if request.form.get('order_item_id') is not None:
        return deleteOrderItem(request)

    # Get the 'restaurant' parameter from the URL query string
    restaurant_name = request.args.get('restaurant')

    # if restaurant page is accessed without a parameter well redirect to avoid erroring
    if not restaurant_name:
        return redirect(url_for('index'))

    curr_restaurant = Store.query.filter_by(
        StoreName=restaurant_name).first()  # Look up the current restaurant
    # Look up menu associated with current restaurant
    menu = Menu.query.get(curr_restaurant.StoreID)
    # Look up all menu items associated with the current menu
    menu_items = MenuItems.query.filter(MenuItems.MenuID == menu.MenuID).all()

    # if were adding an item to our order
    if request.method == 'POST':
        addOrder(request, curr_restaurant)

    # return existing order or new order
    return checkPotentialOrder(curr_restaurant, menu_items)


@app.route('/status')
def status():
    """
    Handles the order status page where customers can view the current status of their order.

    This function first checks the user's type and redirects if the user is a customer. If the user is not logged in, they are redirected 
    to the login page. It also checks if the order is already associated with the user and assigns the user ID to the order if not.

    On the first visit to the status page, the potential order ID is converted into an actual order and the order status is updated to 
    "Created" in the database. If the order status is "Delivered", the order ID is removed from the session, indicating the completion of 
    the order.

    The function retrieves the current order from the session and fetches the associated restaurant details to display to the user.

    Returns:
    - Renders the 'status.html' template displaying the current order status and associated restaurant details.
    """
    # Redirect if wrong user type
    if checkUserType("Customer"):
        return checkUserType("Customer")

    # add redirection to login if not logged in -> hold potential current order ID
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # add the user id to the order if it is not already set in the database
    is_user_null = db.session.execute(select(Orders).where(Orders.OrderID == session.get(
        'potential_order_id'), Orders.UserID == None)).scalar_one_or_none()
    if is_user_null:
        is_user_null.UserID = session.get('user_id')
        db.session.commit()

    # convert session potential order into order
    # this will execute only on first visit to status
    if session.get('potential_order_id'):
        session['order_id'] = session.get('potential_order_id')
        session.pop('potential_order_id', None)

        # update order status in db
        db.session.execute(update(Orders).where(
            Orders.OrderID == session.get('order_id')).values(OrderStatus="Created"))
        db.session.commit()

    # get current order from session
    current_order = db.session.execute(select(Orders).where(
        Orders.OrderID == session.get('order_id'))).scalar_one_or_none()

    # Remove restrictions if order is completed
    if current_order.OrderStatus == "Delivered":
        session.pop('order_id', None)

    # Remove restrictions if order is completed
    if current_order.OrderStatus == "Delivered":
        session.pop('order_id', None)

    # get resteraunt from current order
    curr_restaurant = db.session.execute(select(Store).where(
        Store.StoreID == current_order.StoreID)).scalar_one_or_none()

    return render_template('status.html', current_order=current_order, curr_restaurant=curr_restaurant)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """
    Handles the checkout process for users placing an order.

    This function first checks if the user is the correct type (non-customer) and redirects them accordingly. If an order already exists 
    in the session, the user is redirected to the status page. If there is no potential order in the session, the user is redirected 
    to the home page.

    If the request method is POST, it checks for an order deletion request and processes it accordingly. Otherwise, it proceeds to 
    display the relevant checkout information.

    Returns:
    - Renders the checkout information if no deletion occurs, or processes an order deletion if a POST request is made.
    """
    # Redirect if wrong user type
    if checkUserType("Customer"):
        return checkUserType("Customer")

    # redirection to order status if order exists
    if 'order_id' in session:
        return redirect(url_for('status'))

    # must have potential order to access checkout
    if 'potential_order_id' not in session:
        return redirect(url_for('home'))

    # check if were deleting an order
    if request.method == 'POST':
        return deleteOrder()

    # return relevent order information
    return checkoutInformation()

# Function to wipe session variables on program start -> Forces user cookie dump


@app.before_request
def clear_session():
    """
    Clears the session data on the first request to the application.

    This function is executed before every request. On the first request, it clears the session data to ensure a clean session 
    state for the user. It also sets a flag to indicate that the first request has been processed, preventing subsequent 
    requests from clearing the session again.

    Returns:
    - None
    """
    # Check if this is the first request
    if not hasattr(app, 'has_run_before'):
        # Clear the session on the first request
        session.clear()
        # Mark that the first request has been processed
        app.has_run_before = True
    pass


if __name__ == "__main__":
    # Parse arguments passed with python execution
    parser = argparse.ArgumentParser(
        description="Run the Flask app with optional database reset.")
    parser.add_argument('--reset-db', action='store_true',
                        help="Reset the database (drop and create tables).")
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