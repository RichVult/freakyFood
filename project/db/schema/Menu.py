from db.server import db

class Menu(db.Model):
    __tablename__='Menu'

    # Define Columns
    MenuID = db.Column(db.Integer, primary_key = True, autoincrement= True)
    StoreID = db.Column(db.Integer, db.ForeignKey('Store.StoreID'), nullable=False)


    # Define Relationship
    store = db.relationship('Store', back_populates='Menu')

    # Constructor
    def __init__(self, newStoreID):
        self.newStoreID = newStoreID

    # Debug
    def __repr__(self):
        # add text to f-string
        return f"""
            StoreID : {self.StoreID}
            MenuID : {self.MenuID}
        """

    def __repr__(self):
        return self.__repr__()
