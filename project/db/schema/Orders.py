from db.server import db
from datetime import datetime

class Orders(db.Model):
    __tablename__ = 'Orders'

    # Define Columns
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=True)
    DriverID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=True)
    StoreID = db.Column(db.Integer, db.ForeignKey('Store.StoreID'), nullable=False)
    OrderStatus = db.Column(db.String(100), nullable=False)
    OrderDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Define Relationships
    user = db.relationship('Users', foreign_keys=[UserID])
    driver = db.relationship('Users', foreign_keys=[DriverID])
    store = db.relationship('Store', back_populates='orders')
 
    order_items = db.relationship('OrderItems', back_populates='order')

    # Constructor
    def __init__(self, newDriverID, newStoreID, newOrderStatusID, newOrderDate):
        self.DriverID = newDriverID
        self.StoreID = newStoreID
        self.OrderStatusID = newOrderStatusID
        self.OrderDate = newOrderDate

    # Debug
    def __repr__(self):
        return f"""
            OrderID : {self.OrderID}
            UserID : {self.UserID}
            DriverID : {self.DriverID}
            StoreID : {self.StoreID}
            OrderStatusID : {self.OrderStatusID}
            OrderDate : {self.OrderDate}
        """