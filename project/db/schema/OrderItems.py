from db.server import db

class OrderItems(db.Model):
    __tablename__='OrderItems'

    # Define Columns
    OrderItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('Orders.OrderID'), nullable=False)
    ItemQuantity = db.Column(db.Integer)

    # Define Relationship
    order = db.relationship('Orders', back_populates='order_items')
    
    # Constructor
    def __init__(self, newMenuItemID, newItemQuantity):
        self.MenuItemID=newMenuItemID
        self.ItemQuantity=newItemQuantity

    # Debug
    def __repr__ (self):
        #add text to f-string
        return f"""
            Order ID : {self.OrderID}
            Menu Item ID : {self.MenuItemID}
            Item Quantity : {self.ItemQuantity}
        """
    
    def __repr__(self):
        return self.__repr__()