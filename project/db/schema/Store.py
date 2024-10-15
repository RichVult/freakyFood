"""Store.py: create a table named Store in the freakyfood database"""
from db.server import db

class Store(db.Model):
    __tablename__='Store'
    StoreID=db.Column(db.Integer,primary_key=True,autoincrement=True)
    UserID=db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    StoreName=db.Column(db.String)

    #define relationship
    user_id=db.relationship('UserID', back_populates='Store')

    def __init__(self, newStoreID, newUserID, newStorename):
        self.StoreID=newStoreID
        self.newUserID=newUserID
        self.StoreName=newStorename
        pass

    def __repr__ (self):
        #add text to f-string
        return f"""
            StoreID : {self.StoreID}
            UserID : {self.UserID}
            StoreName : {self.StoreName}
        """
    
    def __repr__(self):
        return self.__repr__()