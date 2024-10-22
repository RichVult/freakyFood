from db.server import db

class Store(db.Model):
    __tablename__ = 'Store'
    
    # Define Columns
    StoreID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    StoreName = db.Column(db.String(100), nullable=False)


    # Define Relationship
    user = db.relationship('Users', back_populates='Store')

    # Construction
    def __init__(self, newStorename):
        self.StoreName = newStorename

    # Debug
    def __repr__(self):
        return f"""
            StoreID : {self.StoreID}
            UserID : {self.UserID}
            StoreName : {self.StoreName}
        """

    def __repr__(self):
        return self.__repr__()