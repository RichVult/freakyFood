from sqlalchemy import insert, select, and_
from sqlalchemy.dialects.postgresql import insert as postgres_insert

# Method to Insert User Types Mock Data
def insert_user_types():
    from db.schema.UserTypes import UserTypes
    from db.server import db
    # Define the allowed user types
    user_types = ['Driver', 'Customer', 'StoreOwner']
    
    # Iterate over each user type
    for user_type in user_types:
        # Check if the user type already exists
        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == user_type)).scalar_one_or_none()
    
        if existing_user_type is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(UserTypes).values(TypeName=user_type))
            print(f"DUMMY DATA: Inserted User type: {user_type}")
        else:
            print(f"DUMMY DATA: User type '{user_type}' already exists. Skipping.")
    db.session.commit()

# Method to Insert User Mock Data
def insert_user():
    from db.schema.Users import Users
    from db.schema.UserTypes import UserTypes
    from db.server import db
    import bcrypt
    users=[
        ["Driver", "CFdefence@gmail.com", "SuperPassword123.", "Christian", "Farrell", "default_profile.png"],
        ["Customer", "socks@gmail.com", "SuperPassword11!", "Alex", "Borelli", "default_profile.png"],
        ["StoreOwner", "dude@gmail.com", "ByteNibbleBit12.", "Guy", "Meyer", "default_profile.png"],
        ["Customer", "test@gmail.com", "HelpMEE!!.", "test", "man", "default_profile.png"],
        ]
    
    for user in users:
        # Check if the user already exists -> Email 
        existing_user = db.session.execute(select(Users).where(Users.Email==user[1])).scalar_one_or_none()

        # find user based on email
        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == user[0])).scalar_one_or_none()

        # if existing user is none that the user DNE
        if existing_user is None:
            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(user[2].encode(), bcrypt.gensalt()).decode('utf-8')

            # create the user
            db.session.execute(insert(Users).values(
                UserTypeID=existing_user_type.UserTypeID, 
                Email=user[1],
                Password=hashed_password, 
                FirstName=user[3], 
                LastName=user[4],
                Address=None, 
                CardNumber=None),
            ),
            db.session.commit()
            print(f"DUMMY DATA: Inserted User: {user}")
        else:
            print(f"DUMMY DATA: User already Exists : {user}")

# Method to Insert Store Mock Data
def insert_store():
    from db.schema.Store import Store
    from db.schema.Users import Users
    from db.server import db
    stores=[
        ["Christian", "Wendys", "wendys.png"],
        ["Alex", "Chipotle", "Chipotle_logo.png"],
        ["Guy", "McDonalds", "mcdonalds.png"]
    ]
    for store in stores:
        # Check if the store already exists--> Store Name
        existing_store = db.session.execute(select(Store).where(Store.StoreName==store[1])).scalar_one_or_none()
        #Find user based on user ID
        existing_user = db.session.execute(select(Users).where(Users.FirstName==store[0])).scalar_one_or_none()

        if existing_store is None:
            # Create a new store
            db.session.execute(insert(Store).values(
                UserID=existing_user.UserID,
                StoreName=store[1],
                StoreImage=store[2]
                ))
            db.session.commit()
            print(f"DUMMY DATA: Inserted Store: {store}")
        else:
            print(f"DUMMY DATA: Store already exists: {store}")

# Method to Insert Orders Mock Data
def insert_orders():
    from db.schema.Orders import Orders
    from db.schema.Users import Users
    from db.schema.Store import Store
    from db.server import db
    orders=[
        [ "Alex", "McDonalds", "Christian", "Ready", "10/20/2005"],
        [ "Guy", "Wendys", "Christian", "Not Ready", "12/31/2004"],
        [ "test", "McDonalds", "Christian", "Ready", "9/12/2021"],

    ]

    for order in orders:
        # Check if the already exists
        existing_order = db.session.execute(select(Orders).where(Orders.OrderDate==order[4])).scalar_one_or_none()
        #Checks for user
        existing_user = db.session.execute(select(Users).where(Users.FirstName==order[0])).scalar_one_or_none()
        #Checks for driver
        existing_driver = db.session.execute(select(Users).where(Users.FirstName==order[2])).scalar_one_or_none()
        #Checks for store
        existing_store = db.session.execute(select(Store).where(Store.StoreName==order[1])).scalar_one_or_none()
    
        if existing_order is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(Orders).values(
                UserID=existing_user.UserID,
                DriverID=existing_driver.UserID,
                StoreID=existing_store.StoreID,
                OrderStatus=order[3],
                OrderDate=order[4]
            ))
            db.session.commit()
            print(f"DUMMY DATA: Inserted Order: {order}")
        else:
            print(f"DUMMY DATA: Order '{order}' already exists. Skipping.")

# Method to Insert Order Items Mock Data
def insert_orderitems():
    from db.schema.OrderItems import OrderItems
    from db.schema.Orders import Orders
    from db.schema.Users import Users
    from db.server import db
    orderitems=[
        ["Alex", "Fries", 22],
        ["test", "Burger", 33],
        ["Guy", "CheeseBurger", 44],
        ["Guy", "Fries", 50],

    ]
    for orderitem in orderitems:
        # Check if order already exists -> should make first and last

        # Grab the userid associated with the firstname
        existing_user=db.session.execute(select(Users).where(Users.FirstName==orderitem[0])).scalar_one_or_none()

        # See if an order exists with existing user id -> can one user have many orders?
        existing_order=db.session.execute(select(Orders).where(Orders.UserID==existing_user.UserID)).scalar_one_or_none()

        # See if the order item is made
        existing_orderitem = db.session.execute(select(OrderItems).where(and_(OrderItems.UserID == existing_user.UserID, OrderItems.OrderItemName == orderitem[1]))).scalar_one_or_none()

        #Takes orderID of order and create new orderitem
        if existing_orderitem is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(OrderItems).values(
                OrderID=existing_order.OrderID,
                ItemQuantity=orderitem[2],
                OrderItemName=orderitem[1],
                UserID = existing_user.UserID,
            ))
            db.session.commit()
            print(f"DUMMY DATA: Inserted Orderitem: {orderitem}")
        else:
            print(f"DUMMY DATA: OrderItem '{orderitem}' already exists. Skipping.")

# Method to Insert Menu Mock Data
def insert_menu():
    from db.schema.Menu import Menu
    from db.schema.Store import Store
    from db.server import db
    menus=[
        ["Wendys"],
        ["Chipotle"],
        ["McDonalds"],
    ]
    for menu in menus:
        # Check if the user type already exists
        existing_store = db.session.execute(select(Store).where(Store.StoreName==menu[0])).scalar_one_or_none()
        existing_menu = db.session.execute(select(Menu).where(Menu.StoreID==existing_store.StoreID )).scalar_one_or_none()
   
        if existing_menu is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(Menu).values(
                StoreID=existing_store.StoreID
            ))
            db.session.commit()
            print(f"DUMMY DATA: Inserted Menu: {menus}")
        else:
            print(f"DUMMY DATA: Menu '{menus}' already exists. Skipping.")


# Method to Insert Menu Items Mock Data
def insert_menuitems():
    from db.schema.MenuItems import MenuItems
    from db.schema.Menu import Menu
    from db.schema.Store import Store
    from db.server import db
    store1 = select(Menu.MenuID).join(Store).where(Store.StoreName == "Wendys")
    store2 = select(Menu.MenuID).join(Store).where(Store.StoreName == "Chipotle")
    store3 = select(Menu.MenuID).join(Store).where(Store.StoreName == "McDonalds")
    menu_items=[

        #Wendys
        { "MenuItemName":"Baconator", "MenuItemDesc" : "Burger", "MenuItemCal" : 590, "MenuItemPrice": 8.00, "MenuID": db.session.scalar(store1)},
        { "MenuItemName":"Fries", "MenuItemDesc" : "Potato", "MenuItemCal" : 320, "MenuItemPrice": 5.00,"MenuID": db.session.scalar(store1)},
        { "MenuItemName":"Frosty", "MenuItemDesc" : "Ice Cream and Oreo", "MenuItemCal" : 570, "MenuItemPrice": 5.00,"MenuID": db.session.scalar(store1)},

        #Chipotle
        { "MenuItemName":"Cheese Quesedilla", "MenuItemDesc" : "Cheese", "MenuItemCal" : 120, "MenuItemPrice": 10.00, "MenuID": db.session.scalar(store2)},
        { "MenuItemName":"Chicken Burito", "MenuItemDesc" : "Chicken", "MenuItemCal" : 1350, "MenuItemPrice": 14.00,"MenuID": db.session.scalar(store2)},
        { "MenuItemName":"Steak Taco", "MenuItemDesc" : "Steak", "MenuItemCal" : 1500, "MenuItemPrice": 16.00,"MenuID": db.session.scalar(store2)},

        #McDonalds
        { "MenuItemName":"Big Mac", "MenuItemDesc" : "Burger", "MenuItemCal" : 590, "MenuItemPrice": 8.00, "MenuID": db.session.scalar(store3)},
        { "MenuItemName":"Fries", "MenuItemDesc" : "Potato", "MenuItemCal" : 320, "MenuItemPrice": 5.20,"MenuID": db.session.scalar(store3)},
        { "MenuItemName":"Oreo McFlurry", "MenuItemDesc" : "Ice Cream and Oreo", "MenuItemCal" : 570, "MenuItemPrice": 5.00,"MenuID": db.session.scalar(store3)},
    ]
    insert_menu_items = postgres_insert(MenuItems).values(menu_items)
    db.session.execute(insert_menu_items)
    # Commit the changes to the database
    db.session.commit()

    # Confirm the success of the insert
    for item in menu_items:
        print(f"DUMMY DATA: Inserted Menu Item: {item['MenuItemName']} at ${item['MenuItemPrice']:.2f} for MenuID {item['MenuID']}")