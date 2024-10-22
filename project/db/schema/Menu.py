from db.server import db

class Menu(db.Model):
    __tablename__='Menu'

    # Define Columns
    MenuID=db.Column(db.Integer,primary_key=True,autoincrement=True)
    MenuID=db.Column(db.Integer, db.ForeignKey('Store.StoreID'), nullable=False)
    StoreID=db.Column(db.String)

    #Define Relationship
    menu_id=db.relationship('StoreID', back_populates='Menu')

    def __init__(self, newStoreID, newMenuID):
        self.MenuID = newMenuID
        self.newStoreID = newStoreID

        pass

    def __repr__(self):
        # add text to f-string
        return f"""
            StoreID : {self.StoreID}
            MenuID : {self.MenuID}
        """

    def __repr__(self):
        return self.__repr__()
