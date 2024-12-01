'''

    This file will contain the helper functions to assist the controller in executing logic

'''

from flask import Flask, render_template, request, redirect, url_for, session

import re
import socket
import bcrypt

from db.server import app, db
from sqlalchemy import *

from db.schema import Users, Store, Menu, Orders, OrderItems, MenuItems, UserTypes

def verifySignup():
    # Define allowed user types
    allowed_user_types = ['Driver', 'Customer', 'StoreOwner']

    # Get values from form and remove whitespace
    new_email = request.form["Email"].strip()
    new_password = request.form["Password"].strip()
    new_password_two = request.form["PasswordTwo"].strip()
    new_first_name = request.form["FirstName"].strip()
    new_last_name = request.form["LastName"].strip()
    new_user_type = request.form["UserType"].strip()

    # Backend Check if REGEX was matched
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    password_pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$"
    name_pattern = r"^[A-Za-z]+$"

    if not re.match(email_pattern, new_email):
        return render_template('signup.html', error="Invalid email format.")

    if not re.match(password_pattern, new_password):
        return render_template('signup.html', error= "Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character.")

    if not re.match(name_pattern, new_first_name):
        return render_template('signup.html', error="First name can only contain letters.")

    if not re.match(name_pattern, new_last_name):
        return render_template('signup.html', error="Last name can only contain letters.")

    # Check if email exists 
    if db.session.execute(select(Users).where(Users.Email == new_email)).scalar_one_or_none():
        return render_template('signup.html', error="Email already associated with another user")

    # Check if the user type is valid
    if new_user_type not in allowed_user_types:
        return render_template('signup.html', error="Invalid user type. Please select from Driver, Customer, or Store Owner.")

    # Check if passwords match
    if new_password != new_password_two:
        return render_template('signup.html', error="Passwords Do Not Match")

def createUser():
    # Get values from form and remove whitespace
    new_email = request.form["Email"].strip()
    new_password = request.form["Password"].strip()
    new_password_two = request.form["PasswordTwo"].strip()
    new_first_name = request.form["FirstName"].strip()
    new_last_name = request.form["LastName"].strip()
    new_user_type = request.form["UserType"].strip()

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
        PhoneNumber=None,
        State=None,
        Street=None,
        City=None,
        ZipCode=None,
        CardNumber=None
    )
    # Execute Query and Commit to DB
    db.session.execute(create_user)
    db.session.commit()

    return redirect(url_for('login'))

def resetPassword():
    #checks current password and changes it to new password.
    user_id = session.get('user_id')
    current_password = request.form["CurrentPassword"]
    new_password = request.form["NewPassword"]

    user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()

    # Verify the current password
    if user and bcrypt.checkpw(current_password.encode(), user.Password.encode()):
        # backend check for password matches regex
        if not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$", new_password):
            return render_template('reset.html', error="Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character.")

        # Hash the new password and update it in the database
        hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
        user.Password = hashed_new_password
        db.session.commit()
        return redirect(url_for('account')) 
    else:
        return render_template('reset.html', error="Current password is incorrect.")

def deleteOrderItem():
    order_item_id = request.form.get('order_item_id') # We are removing an item from a potential order
    
    db.session.execute(delete(OrderItems).where(OrderItems.OrderItemID == order_item_id))
    db.session.commit()

    # redirect back with new items
    restaurant_name = request.args.get('restaurant')
    curr_restaurant = Store.query.filter_by(StoreName=restaurant_name).first()
    menu = Menu.query.get(curr_restaurant.StoreID) # Look up menu associated with current restaurant
    menu_items = MenuItems.query.filter(MenuItems.MenuID == menu.MenuID).all() # Look up all menu items associated with the current menu
    potential_order_id = session.get('potential_order_id') # get from session
    potential_items = db.session.execute(select(OrderItems).where(OrderItems.OrderID == potential_order_id)).scalars().all() # find all potential order items

    return render_template('restaurant.html', curr_restaurant=curr_restaurant, potential_items=potential_items, menu_items=menu_items) 

def addOrder(curr_restaurant):
    # We are adding an item or creating a potential order
    requested_quantity = request.form['quantity'] # get requested amount
    requested_item_id = request.form['item_id'] # get requested item id
    requested_item = MenuItems.query.filter_by(MenuItemID=requested_item_id).first() # identify which item is requested

    # if potential order doesnt exist we will create it and add to session
    if 'potential_order_id' not in session:
        # Execute the insert and commit to get the new order's ID
        result = db.session.execute(insert(Orders).values(
            UserID=session.get('user_id') if 'user_id' in session else None,
            DriverID=None,
            StoreID=curr_restaurant.StoreID,
            OrderStatus='potential'
        ))
        db.session.commit()

        # Store the new order ID in the session
        session['potential_order_id'] = result.inserted_primary_key[0] 

    # add the added item to the potential order
    db.session.execute(insert(OrderItems).values(
        OrderID=session.get('potential_order_id'),
        ItemQuantity=requested_quantity,
        OrderItemName=requested_item.MenuItemName,
        UserID=session.get('user_id') if 'user_id' in session else None,
        ItemPrice = int(requested_quantity) * float(requested_item.MenuItemPrice)
    ))
    db.session.commit()

def checkPotentialOrder(curr_restaurant, menu_items):
    # Check potential order and redirect accordingly
    if 'potential_order_id' in session:
        # get from session
        potential_order_id = session.get('potential_order_id')
        
        # Look up the order in the database based on potential_order_id
        potential_order = db.session.execute(select(Orders).where(Orders.OrderID == potential_order_id)).scalar_one_or_none()

        # find all potential order items
        potential_items = db.session.execute(select(OrderItems).where(OrderItems.OrderID == potential_order.OrderID)).scalars().all()
        
        # if we fine none set to none
        if not potential_items:
            potential_items = None

        # if potential order not from this restaurant redirect to checkout
        if potential_order.StoreID != curr_restaurant.StoreID:
            return redirect(url_for('checkout'))
        else:
            # render template with current potential order
            return render_template('restaurant.html', curr_restaurant=curr_restaurant, potential_items=potential_items, menu_items=menu_items) 

    return render_template('restaurant.html', curr_restaurant=curr_restaurant, potential_items=None, menu_items=menu_items)

def deleteOrder():
    # delete order items from db
    db.session.execute(delete(OrderItems).where(OrderItems.OrderID == session.get('potential_order_id')))
    # delete order from db
    db.session.execute(delete(Orders).where(Orders.OrderID == session.get('potential_order_id')))
    db.session.commit()

    # delete potential order from session
    session.pop('potential_order_id', None)

    return redirect(url_for('home'))

def genCheckoutTemplate():
    # get potential order id from session
    potential_order_id = session.get('potential_order_id')
        
    # Look up the order in the database based on potential_order_id
    potential_order = db.session.execute(select(Orders).where(Orders.OrderID == potential_order_id)).scalar_one_or_none()

    # find all potential order items
    potential_items = db.session.execute(select(OrderItems).where(OrderItems.OrderID == potential_order.OrderID)).scalars().all()
    
    # get current restaurant from potential order
    curr_restaurant = db.session.execute(select(Store).where(Store.StoreID == potential_order.StoreID)).scalar_one_or_none()

    return render_template('checkout.html', potential_items=potential_items, potential_order=potential_order, curr_restaurant=curr_restaurant)

# Function to delete a Customer and all its dependency tables
def deleteUser():
    # grad user information
    user_id = session.get('user_id')
    found_user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()

    # prevent deletion while orders are in progress
    if 'order_id' in session:
        return render_template('account.html', user=found_user, error="You Must Complete All In Progress Orders Before Deleting Your Account")
    
    # Delete the user, orders, and associated order items
    db.session.execute(delete(OrderItems).where(OrderItems.UserID == user_id))
    db.session.execute(delete(Orders).where(Orders.UserID == user_id))
    db.session.execute(delete(Users).where(Users.UserID == user_id))
    db.session.commit()

    # Remove the session cookies from the session and redirect to the home page
    session.pop('user_id', None)
    session.pop('potential_order_id', None)
    session.pop('order_id', None)
    return redirect(url_for('index'))

# Function to delete a Driver and all its dependency tables
def deleteDriver():
    # grab user information
    user_id = session.get('user_id')
    found_user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()

    # prevent deletion while orders are in progress
    if 'accepted_order_id' in session:
        return render_template('account.html', user=found_user, error="You Must Complete All In Progress Orders Before Deleting Your Account")

    # Delete the user, remove from existing orders
    db.session.execute(update(Orders).where(Orders.DriverID == user_id).values(DriverID = None))
    db.session.execute(delete(Users).where(Users.UserID == user_id))
    db.session.commit()

    # Remove the session cookies from the session and redirect to the home page
    session.pop('user_id', None)
    session.pop('accepted_order_id', None)
    return redirect(url_for('index'))

# Function to delete a Store Owner and all its dependency tables
def deleteStoreOwner():
    # grab user information
    user_id = session.get('user_id')
    found_user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()

    # grab all users stores
    user_stores = db.session.execute(select(Store).where(Store.UserID == user_id)).scalars().all()

    # determine if any orders are existing that need to be take care of
    for user_store in user_stores:
        if db.session.execute(select(Orders).where(Orders.OrderStatus != "Delivered")).scalars().all(): 
            return render_template('account.html', user=found_user, error="Your Stores Contain Incomplete Orders")

    # for each store delete its menu and menu items
    for user_store in user_stores:
        user_menu = db.session.execute(select(Menu).where(Menu.StoreID == user_store.StoreID)).scalar_one_or_none()
        db.session.execute(delete(MenuItems).where(MenuItems.MenuID == user_menu.MenuID))
        db.session.execute(delete(Menu).where(Menu.MenuID == user_menu.MenuID))
        db.session.execute(update(Orders).where(Orders.StoreID == user_store.StoreID).values(StoreID = None))
        db.session.execute(delete(Store).where(Store.StoreID == user_store.StoreID))
    db.session.execute(delete(Users).where(Users.UserID == user_id))
    db.session.commit()

    session.pop('user_id', None)
    return redirect(url_for('index'))

# check to be done on every page
# we redirect user types to correct page if in wrong page
# ex: user will be redirected from storeOwner page or driver page
def checkUserType(desiredType):
    if session.get('user_id') is None:
        return None
    
    # determine user type
    user_type_id = db.session.execute(select(Users.UserTypeID).where(Users.UserID == session.get('user_id'))).scalar_one()
    user_type = db.session.execute(select(UserTypes.TypeName).where(UserTypes.UserTypeID == user_type_id)).scalar_one_or_none()

    # determine where were going
    # will do an initial check to see if were in the right place
    # if were not in the right place redirect us to that place
    if user_type == desiredType:
        return None
    elif user_type == "Customer":
        return redirect(url_for('home'))
    elif user_type == "StoreOwner":
        return redirect(url_for('storeOwner'))
    elif user_type == "Driver":
        return redirect(url_for('driver'))

# Function to find an available port for flask instance to run on
def find_free_port(start_port, end_port):
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            if result != 0:
                return port
    return None

def findAvailableOrders(orderStatus):
    # Fetch all orders in "Created" status
    orders = db.session.execute(select(Orders).where(Orders.OrderStatus == orderStatus)).scalars().all()
    
    # List to store orders and their associated stores
    available_orders = []

    # Loop through each order and find its store
    for order in orders:
        store = db.session.execute(select(Store).where(Store.StoreID == order.StoreID)).scalar_one_or_none()
        user = db.session.execute(select(Users).where(Users.UserID == order.UserID)).scalar_one_or_none()
        order_items = db.session.execute(select(OrderItems).where(OrderItems.OrderID == order.OrderID)).scalars().all()

        # Append the order and its information to the list
        if store:
            available_orders.append((order, store, user, order_items))
    
    return available_orders

def acceptOrder():
    # add accepted order to session
    session['accepted_order_id'] = request.form.get('orderID')

    # update accepted order's order status
    db.session.execute(update(Orders).where(Orders.OrderID == session.get('accepted_order_id')).values(OrderStatus="Accepted"))
    db.session.commit()

    return redirect(url_for('driverStatus'))

def tryLogin():
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

def deleteAccount():
    # get the type of user which is being deleted
    user_type = db.session.execute(select(UserTypes).where(UserTypes.UserTypeID == request.form.get('userID'))).scalar_one_or_none()

    match user_type.TypeName:
        case "Driver":
            return deleteDriver()
        case "Customer":
            return deleteUser()
        case "StoreOwner":
            return deleteStoreOwner()

def editAccount():
    #get the values of what the user is trying to edit
    user_id=session.get('user_id')

    ##Update User that has the user ID of the current session, update by replaceing values within the form
    db.session.execute(update(Users).where(Users.UserID==user_id).values(
        FirstName=request.form.get('FirstName'), 
        LastName=request.form.get('LastName'),
        Email=request.form.get('Email'),
        PhoneNumber=request.form.get('PhoneNumber'),
        Street=request.form.get('Street'),
        City=request.form.get('City'),
        State=request.form.get('State'),
        ZipCode=request.form.get('ZipCode'),
        CardNumber=request.form.get('CardNumber')
        ))
    ##db.session.execute(update(Users).where(Orders.OrderID == order.OrderID).values(OrderStatus="Pickup"))
    db.session.commit()

    
def updateDriverOrderStatus():
    # Get order ID and desired action from the form data
    order_id = request.form.get('order_id')
    action = request.form.get('action')
    
    if order_id:
        # Fetch the order by ID
        order = db.session.execute(select(Orders).where(Orders.OrderID == order_id)).scalar_one_or_none()

        # Check which action to perform and update the order status accordingly
        if action == "Pickup" and order.OrderStatus == "Ready":
            # update accepted order's order status
            db.session.execute(update(Orders).where(Orders.OrderID == order.OrderID).values(OrderStatus="Pickup"))
            db.session.commit()
        elif action == "Deliver" and order.OrderStatus == "Pickup":
            # update accepted order's order status
            db.session.execute(update(Orders).where(Orders.OrderID == order.OrderID).values(OrderStatus="Delivered"))
            db.session.commit()
            session.pop('accepted_order_id', None)
            return redirect(url_for('driver'))
    return None

def updateStoreOrderStatus():
    # Get order ID and desired action from the form data
    order_id = request.form.get('orderID')
    action = request.form.get('action')
    
    if order_id:
        # Fetch the order by ID
        order = db.session.execute(select(Orders).where(Orders.OrderID == order_id)).scalar_one_or_none()

        # Check which action to perform and update the order status accordingly
        if action == "accept" and order.OrderStatus == "Accepted":
            # update accepted order's order status
            db.session.execute(update(Orders).where(Orders.OrderID == order.OrderID).values(OrderStatus="In Progress"))
            db.session.commit()
        elif action == "complete" and order.OrderStatus == "In Progress":
            # update accepted order's order status
            db.session.execute(update(Orders).where(Orders.OrderID == order.OrderID).values(OrderStatus="Ready"))
            db.session.commit()

def genStoreTemplate():
    # find all "Accpeted" Orders -> A driver has selected it
    waiting_orders = findAvailableOrders("Accepted")
    if len(waiting_orders) == 0: waiting_orders = None

    # find all "In Progress" Orders -> The Store has accepted it
    in_progress_orders = findAvailableOrders("In Progress")
    if len(in_progress_orders) == 0: in_progress_orders = None

    # find all "Ready" order -> Awaiting Pickup
    ready_orders = findAvailableOrders("Ready")
    if len(ready_orders) == 0: ready_orders = None
    
    return render_template('storeOwner.html', waiting_orders=waiting_orders, in_progress_orders=in_progress_orders, ready_orders=ready_orders)

def genSearchTemplate():
    # Get the 'query' parameter from the URL
    query = request.args.get('query')

    if query:
        # Query the database for stores matching the query
        stores = Store.query.filter(Store.StoreName.ilike(f'%{query}%')).all()
    else:
        # pass all stores
        stores = Store.query.all()

    return render_template('search.html', stores=stores)

def genDriverStatusTemplate():
    # get variables for driver status
    current_order = db.session.execute(select(Orders).where(Orders.OrderID == session.get('accepted_order_id'))).scalar_one_or_none()
    curr_restaurant = db.session.execute(select(Store).where(Store.StoreID == current_order.StoreID)).scalar_one_or_none()

    return render_template('driverStatus.html', current_order=current_order, curr_restaurant=curr_restaurant)

def convertOrder():
    if session.get('potential_order_id'):
        session['order_id'] = session.get('potential_order_id')
        session.pop('potential_order_id', None)

        # update order status in db
        db.session.execute(update(Orders).where(Orders.OrderID == session.get('order_id')).values(OrderStatus="Created"))
        db.session.commit()

def commitUserOrder():
    # add the user id to the order if it is not already set in the database
    is_user_null = db.session.execute(select(Orders).where(Orders.OrderID == session.get('potential_order_id'), Orders.UserID == None)).scalar_one_or_none()
    if is_user_null:
        is_user_null.UserID = session.get('user_id')
        db.session.commit()