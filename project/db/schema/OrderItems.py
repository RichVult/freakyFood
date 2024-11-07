from db.server import db

class OrderItems(db.Model):
    __tablename__='OrderItems'

    # Define Columns
    OrderItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('Orders.OrderID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=True)
    OrderItemName = db.Column(db.String)
    ItemQuantity = db.Column(db.Integer)
    ItemPrice = db.Column(db.Float, nullable=True)
    
    # Define Relationship
    order = db.relationship('Orders', back_populates='order_items')
    user = db.relationship('Users', back_populates='order_items')
    
    # Constructor
    def __init__(self, newMenuItemID, newItemQuantity, newOrderItemName, newUserID, newItemPrice):
        self.MenuItemID = newMenuItemID
        self.ItemQuantity = newItemQuantity
        self.OrderItemName = newOrderItemName
        self.UserID = newUserID
        self.ItemPrice = newItemPrice

    # Debug
    def __repr__ (self):
        #add text to f-string
        return f"""
            Order ID : {self.OrderID}
            User ID : {self.UserID}
            Item Quantity : {self.ItemQuantity}
            Order Item Name : {self.OrderItemName}
            Order Item Price : {self.ItemPrice}
        """