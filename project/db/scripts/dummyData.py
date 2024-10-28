from sqlalchemy import insert, select, and_

# Function to populate user types with the 3 acceptable user types if they dont already exist in the db
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

def insert_user():
    from db.schema.Users import Users
    from db.schema.UserTypes import UserTypes
    from db.server import db
    users=[
        ["Driver", "CFdefence@gmail.com", "Password", "Christian", "Farrell"],
        ["Customer", "socks@gmail.com", "4444", "Alex", "Borelli"],
        ["StoreOwner", "dude@gmail.com", "777", "Guy", "Meyer"],
        ["Customer", "test@gmail.com", "222", "test", "man"],
        ]
    
    for user in users:
        # Check if the user already exists -> Email 
        existing_user = db.session.execute(select(Users).where(Users.Email==user[1])).scalar_one_or_none()

        # find user based on email
        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == user[0])).scalar_one_or_none()

        # if existing user is none that the user DNE
        if existing_user is None:
            # create the user
            db.session.execute(insert(Users).values(
                UserTypeID=existing_user_type.UserTypeID, 
                Email=user[1],
                Password=user[2], 
                FirstName=user[3], 
                LastName=user[4],
                Address=None, 
                CardNumber=None))
            db.session.commit()
            print(f"DUMMY DATA: Inserted User : {user}")
        else:
            print(f"DUMMY DATA: User already Exists : {user}")
def insert_store():
    from db.schema.Store import Store
    from db.schema.Users import Users
    from db.server import db
    stores=[
        ["Christian", "Wendys"],
        ["Alex", "Chipotle"],
        ["Guy", "McDonalds"]
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
                StoreName=store[1]
                ))
            db.session.commit()
            print(f"DUMMY DATA: Inserted Store: {store}")
        else:
            print(f"DUMMY DATA: Store already exists: {store}")

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

def insert_menuitems():
    from db.schema.MenuItems import MenuItems
    from db.schema.Menu import Menu 
    from db.server import db
    menuitems=[
        ["10", "14", "Dessert", "Cookie", "10000", "20.00"],
        ["6", "3", "Lunch", "Chicken", "500", "10.00"],
        ["7", "5", "Dinner", "Pasta", "30000", "16.00"],
    ]
    for menuitem in menuitems:
        # Check if the user type already exists
        existing_menuitem= db.session.execute(select(MenuItems).where(MenuItems.MenuItemID==menuitem[0])).scalar_one_or_none()
        existing_menu= db.session.execute(select(Menu).where(Menu.MenuID==menuitem[1])).scalar_one_or_none()
    
        if existing_menuitem is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(MenuItems).values(
                MenuItemID=menuitem[0],
                MenuID=existing_menu.MenuID,
                MIName=menuitem[2],
                MIDesc=menuitem[3],
                MICal=menuitem[4],
                MIPrice=menuitem[5]
            ))
            db.session.commit()
            print(f"DUMMY DATA: Inserted Menuitem: {menuitem}")
        else:
            print(f"DUMMY DATA: Menuitem '{menuitem}' already exists. Skipping.")

def insert_menu():
    from db.schema.Menu import Menu
    from db.schema.Store import Store
    from db.server import db
    menus=[
        ["14", "45"],
        ["3", "33",],
        ["5", "22"],
    ]
    for menu in menus:
        # Check if the user type already exists
        existing_menu= db.session.execute(select(Menu).where(Menu.MenuID==menu[0])).scalar_one_or_none()
        existing_store = db.session.execute(select(Store).where(Store.StoreID==menu[1])).scalar_one_or_none()
    
        if existing_menu is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(Menu).values(
                MenuID=menu[0],
                StoreID=existing_store.StoreID
            ))
            db.session.commit()
            print(f"DUMMY DATA: Menu: {menus}")
        else:
            print(f"DUMMY DATA: Menu '{menus}' already exists. Skipping.")
# Commit the changes to the database
    db.session.commit()