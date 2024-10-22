"""Menu.py: create a table named Menu in the freakyfood database"""
from db.server import db


class Menu(db.Model):
    __tablename__ = 'Menu'
    MenuID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StoreID = db.Column(db.Integer, db.ForeignKey(
        'Store.StoreID'), nullable=False)

    # define relationship
    menu_id = db.relationship('StoreID', back_populates='Menu')

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
