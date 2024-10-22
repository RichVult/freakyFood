"""professor.py: create a table named professors in the marist database"""
from db.server import db

class UserTypes(db.Model):
    __tablename__ = 'UserTypes'

    # Define Columns
    UserTypeID = db.Column(db.Integer,primary_key=True, autoincrement=True)
    TypeName = db.Column(db.String)

    # Constructor
    def __init__(self, newUserTypeID, newTypeName):
        self.UserTypeID = newUserTypeID
        self.TypeName = newTypeName

    # Debug
    def __repr__(self):
        return f"""
            UserTypeID : {self.UserTypeID}
            TypeName : {self.TypeName}
        """
    
    def __repr__(self):
        return self.__repr__()