from db.server import db

class Menu(db.Model):
    __tablename__='Menu'

    # Define Columns
    MenuID = db.Column(db.Integer, primary_key = True, autoincrement= True)
    StoreID = db.Column(db.Integer, db.ForeignKey('Store.StoreID'), nullable=False)


    # Define Relationships
    store = db.relationship('Store', back_populates='menus')
    menu_items = db.relationship('MenuItems', back_populates='menu')

    # Constructor
    def __init__(self, newStoreID):
        self.StoreID = newStoreID

    # Debug
    def __repr__(self):
        # add text to f-string
        return f"""
            StoreID : {self.StoreID}
            MenuID : {self.MenuID}
        """