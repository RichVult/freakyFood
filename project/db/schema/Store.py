from db.server import db

class Store(db.Model):
    __tablename__ = 'Store'
    
    # Column definitions
    StoreID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    StoreName = db.Column(db.String(100), nullable=False)

    # Define relationship
    user = db.relationship('Users', back_populates='stores')  # Assuming 'stores' is defined in the Users model

    def __init__(self, newUserID, newStorename):
        self.UserID = newUserID
        self.StoreName = newStorename

    def __repr__(self):
        return f"""
            StoreID : {self.StoreID}
            UserID : {self.UserID}
            StoreName : {self.StoreName}
        """
