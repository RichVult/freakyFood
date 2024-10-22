from db.server import db

class Orders(db.Model):
    __tablename__ = 'Orders'

    # Define Columns
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    DriverID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    StoreID = db.Column(db.Integer, db.ForeignKey('Store.StoreID'), nullable=False)
    OrderStatus = db.Column(db.String(100), nullable=False)
    OrderDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Define Relationships
    user = db.relationship('Users', foreign_keys=[UserID])
    driver = db.relationship('Users', foreign_keys=[DriverID])
    store = db.relationship('Store', back_populates='orders')
 
    # Constructor
    def __init__(self, newUserID, newDriverID, newStoreID, newOrderStatusID, newOrderDate):
        self.UserID = newUserID
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

    def __repr__(self):
        return self.__repr__()