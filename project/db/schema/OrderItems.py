"""OrderItems.py: create a table named OrderItems in the freakyfood database"""
from db.server import db

class OrderItems(db.Model):
    __tablename__='OrderItems'
    OrderID=db.Column(db.Integer,primary_key=True,autoincrement=True)
    MenuItemID=db.Column(db.Integer) #db.ForeignKey('MenuItems.MenuItemID'), nullable=False) for when that table is ready
    ItemQuantity=db.Column(db.Integer)

    #when other is ready
    #menu_item_id=db.relationship('MenuItemID', back_populates='OrderItems')

    def __init__(self, newOrderID, newMenuItemID, newItemQuantity):
        self.OrderID=newOrderID
        self.MenuItemID=newMenuItemID
        self.ItemQuantity=newItemQuantity
        pass

    def __repr__ (self):
        #add text to f-string
        return f"""
            Order ID : {self.OrderID}
            Menu Item ID : {self.MenuItemID}
            Item Quantity : {self.ItemQuantity}
        """
    
    def __repr__(self):
        return self.__repr__()