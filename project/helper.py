from flask import Flask, render_template, request, redirect, url_for, session

import re
import socket
import bcrypt

from db.server import app, db
from sqlalchemy import *

from db.schema.Users import Users
from db.schema.UserTypes import UserTypes
from db.schema.Orders import Orders
from db.schema.OrderItems import OrderItems
from db.schema.Store import Store
from db.schema.Menu import Menu
from db.schema.MenuItems import MenuItems

def verifySignup(request):
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

def createUser(request):
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

def resetPassword(request):
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

def deleteOrderItem(request):
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

def addOrder(reqeust, curr_restaurant):
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

def checkoutInformation():
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
    user_id = session.get('user_id')
    
    # Delete the user and users stores and orders from the database
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
    user_id = session.get('user_id')

    # Delete the user and the users dependencies

# Function to delete a Store Owner and all its dependency tables
def deleteStoreOwner():
    user_id = session.get('user_id')

    # Delete the user and the users dependencies




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
