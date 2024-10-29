"""MenuItems.py: create a table named MenuItems in the freakyfood database"""
from db.server import db


class MenuItems(db.Model):
    __tablename__ = 'MenuItems'
    MenuItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MenuID = db.Column(db.Integer, db.ForeignKey(
        'Menu.MenuID'), nullable=False)
    MenuItemName = db.Column(db.String(120), nullable=False)
    MenuItemDesc = db.Column(db.String(255), nullable=False)
    MenuItemCal = db.Column(db.Integer, nullable=False)
    MenuItemPrice = db.Column(db.Float, nullable=False)

    # Define relationship
    menu = db.relationship('Menu', back_populates='menu_items')

    def __init__(self, newMenuID, newMIName, newMIDesc, newMICal, newMIPrice):
        self.MenuID = newMenuID
        self.MIName = newMIName
        self.MIDesc = newMIDesc
        self.MICal = newMICal
        self.MIPrice = newMIPrice

    def __repr__(self):
        return f"""
        MenuItemID : {self.MenuItemID}
        MenuID : {self.MenuID}
        MIName : {self.MIName}
        MIDesc : {self.MIDesc}
        MICal : {self.MICal}
        MIPrice : {self.MIPrice}
    """