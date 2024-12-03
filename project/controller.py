'''

    This file will contain the main functions in which are executed for a given app route

'''

from helper import *

def handleDriver():
    # if we have already accepted an order
    if 'accepted_order_id' in session: return redirect(url_for('driverStatus'))

    # Redirect to login if not logged in
    if 'user_id' not in session: return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("Driver"): return checkUserType("Driver")

    # if we accept an order
    if request.method == 'POST': return acceptOrder()

    # find all available orders
    orders = findAvailableOrders("Created")

    return render_template('driver.html', orders=orders)

def handleIndex():
    if request.method == 'GET':
        # if logged in redirect to account info
        if 'user_id' in session: return redirect(url_for('home'))

        return render_template('index.html')
    else:
        # Backend Check if REGEX was matched -> return any errors found
        if verifySignup(): return verifySignup()
        
        # Create the new user if REGEX good
        return createUser()

def handleSignup():
    # if logged in redirect to account info
    if 'user_id' in session: return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Backend Check if REGEX was matched -> return any errors found
        if verifySignup(): return verifySignup()
        
        # Create the new user if no errors
        return createUser()

    return render_template('signup.html')

def handleLogin():
    # if logged in redirect to account info
    if 'user_id' in session: return redirect(url_for('home'))

    # try the inputted information against DB
    if request.method == 'POST': return tryLogin()

    return render_template('login.html')

def handleAccount():
    # flag to determine if were erroring out
    editError = None

    if request.method == 'POST' and request.form.get('action') == 'delete': deleteAccount()
    if request.method == 'POST' and request.form.get('action') == 'edit': 
        if editAccount() == False:
            editError = "Incorrect Information Format, Please Follow Highlighted Requirements"
    if request.method == 'POST' and request.form.get('action') == 'picture': updateProfilePic()
    # Redirect to login if not logged inhandleAccount
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # Fetch user details from the database using the user ID
    user_id = session.get('user_id')
    user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()

    return render_template('account.html', user=user, error=editError)

def handleLogout():
    # Drop any user specific session informaion
    session.pop('user_id', None)
    session.pop('potential_order_id', None)
    session.pop('order_id', None)
    return redirect(url_for('index'))

def handleReset():
    # Redirect to login if not logged in
    if 'user_id' not in session: return redirect(url_for('login'))

    # Reset the passwowrd on POST
    if request.method == 'POST': return resetPassword()

    return render_template('reset.html')

def handleHome():
    #Redirect to login if not logged in
    if 'user_id' not in session: return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")
    
    return render_template('home.html')

def handleDriverStatus():
    # if were not logged in redirect
    if 'user_id' not in session: return redirect(url_for('login'))

    # if we have not already accepted an order
    if 'accepted_order_id' not in session: return redirect(url_for('driver'))

    # Redirect if wrong user type
    if checkUserType("Driver"): return checkUserType("Driver")

    # Changing the order status 
    if request.method == 'POST':
        result = updateDriverOrderStatus()
        if result is not None: return result

    return genDriverStatusTemplate()

def handleStoreOwner():
    # Redirect to login if not logged in
    if 'user_id' not in session: return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("StoreOwner"): return checkUserType("StoreOwner")

    # this will update order status' correctly depending on request information
    if request.method == 'POST': updateStoreOrderStatus()

    return genStoreTemplate()

def handleSearch():
    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # redirection to order status if order exists
    if 'order_id' in session: return redirect(url_for('status'))

    return genSearchTemplate()

def handleRestaurant():
    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # redirect if existing order
    if 'order_id' in session: return redirect(url_for('status'))

    # Request for deleting an order item
    if request.form.get('order_item_id') is not None: return deleteOrderItem()
        
    # Get the 'restaurant' parameter from the URL query string
    restaurant_name = request.args.get('restaurant')

    # if restaurant page is accessed without a parameter well redirect to avoid erroring
    if not restaurant_name: return redirect(url_for('index'))

    curr_restaurant = Store.query.filter_by(StoreName=restaurant_name).first() # Look up the current restaurant
    menu = Menu.query.get(curr_restaurant.StoreID) # Look up menu associated with current restaurant
    menu_items = MenuItems.query.filter(MenuItems.MenuID == menu.MenuID).all() # Look up all menu items associated with the current menu

    # if were adding an item to our order
    if request.method == 'POST': addOrder(curr_restaurant)

    # return existing order or new order
    return checkPotentialOrder(curr_restaurant, menu_items)

def handleStatus():
    # redirect if no orders ready
    if 'order_id' not in session and 'potential_order_id' not in session: return redirect(url_for('home'))

    # add redirection to login if not logged in -> hold potential current order ID
    if 'user_id' not in session: return redirect(url_for('login'))

    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # add the user id to the order if it is not already set in the database
    commitUserOrder()

    # convert session potential order into order
    convertOrder()

    # get current order from session
    current_order = db.session.execute(select(Orders).where(Orders.OrderID == session.get('order_id'))).scalar_one_or_none()

    # get resteraunt from current order
    curr_restaurant = db.session.execute(select(Store).where(Store.StoreID == current_order.StoreID)).scalar_one_or_none()

    # get current orders' order items
    order_items = OrderItems.query.filter(OrderItems.OrderID == current_order.OrderID).all()

    # Remove restrictions if order is completed
    if current_order.OrderStatus == "Delivered": session.pop('order_id', None)

    return render_template('status.html', current_order=current_order, curr_restaurant=curr_restaurant, order_items=order_items)

def handleCheckout():
    # Redirect if wrong user type
    if checkUserType("Customer"): return checkUserType("Customer")

    # redirection to order status if order exists
    if 'order_id' in session: return redirect(url_for('status'))

    # must have potential order to access checkout
    if 'potential_order_id' not in session: return redirect(url_for('home'))

    # check if were deleting an order
    if request.method == 'POST': return deleteOrder()

    # return relevent order information
    return genCheckoutTemplate()