from sqlalchemy import insert, select

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
        [],
        ]
    
    for user in users:
        # Check if the user already exists -> Email 
        existing_user = db.session.execute(select(Users).where(Users.Email==user[1])).scalar_one_or_none()

        # find user based on email
        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == user[0])).scalar_one_or_none()

        # if existing user is none that the user DNE
        if existing_user is not None:
            # create the user
            db.session.execute(insert(Users).values(
                UserTypeID=existing_user_type.UserTypeID, 
                Email=user[1],
                Password=user[2], 
                FirstName=user[3], 
                LastName=user[4],
                Address=None, 
                CardNumber=None))
            print(f"DUMMY DATA: Inserted User : {user}")
        else:
            print(f"DUMMY DATA: User already Exists : {user}")
def insert_store():
    from db.schema.Store import Store
    from db.server import db
    store=['444', '', 'Wendys']
    for stores in store:
        # Check if the user type already exists
        existing_store= db.session.execute(select(Store).where(Store.StoreID==stores)).scalar_one_or_none()
    
        if existing_store is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(Store).values(StoreID=stores))
            print(f"DUMMY DATA: Inserted Store: {stores}")
        else:
            print(f"DUMMY DATA: Store '{stores}' already exists. Skipping.")

def insert_orders():
    from db.schema.Orders import Orders
    from db.server import db
    order=['332', '', '3', '', 'Ready', '2024']
    for orders in order:
        # Check if the user type already exists
        existing_order= db.session.execute(select(Orders).where(Orders.OrderID==orders)).scalar_one_or_none()
    
        if existing_order is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(Orders).values(OrderID=orders))
            print(f"DUMMY DATA: Inserted Order: {orders}")
        else:
            print(f"DUMMY DATA: Order '{orders}' already exists. Skipping.")

def insert_orderitems():
    from db.schema.OrderItems import OrderItems
    from db.server import db
    orderitem=['','','100']
    for orderitem in orderitem:
        # Check if the user type already exists
        existing_orderitems= db.session.execute(select(OrderItems).where(OrderItems.OrderID==orderitem)).scalar_one_or_none()
    
        if existing_orderitems is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(OrderItems).values(OrderID=orderitem))
            print(f"DUMMY DATA: Inserted Orderitem: {orderitem}")
        else:
            print(f"DUMMY DATA: OrderItem '{orderitem}' already exists. Skipping.")

def insert_menuitems():
    from db.schema.MenuItems import MenuItems
    from db.server import db
    orderitem=['1212', '', 'Dessert', 'Meat', '10000', '20.00']
    for menuitems in orderitem:
        # Check if the user type already exists
        existing_menuitems= db.session.execute(select(MenuItems).where(MenuItems.MenuItemID==menuitems)).scalar_one_or_none()
    
        if existing_menuitems is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(MenuItems).values(MenuItemID=menuitems))
            print(f"DUMMY DATA: Inserted Menuitem: {menuitems}")
        else:
            print(f"DUMMY DATA: Menuitem '{menuitems}' already exists. Skipping.")

def insert_menu():
    from db.schema.Menu import Menu
    from db.server import db
    menu=['222', '']
    for menus in menu:
        # Check if the user type already exists
        existing_menu= db.session.execute(select(Menu).where(Menu.MenuID==menus)).scalar_one_or_none()
    
        if existing_menu is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(Menu).values(MenuID=menus))
            print(f"DUMMY DATA: Menu: {menus}")
        else:
            print(f"DUMMY DATA: Menu '{menus}' already exists. Skipping.")
# Commit the changes to the database
    db.session.commit()