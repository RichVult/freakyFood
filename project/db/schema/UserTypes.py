"""professor.py: create a table named professors in the marist database"""
from db.server import db

class UserTypes(db.Model):
    __tablename__ = 'UserTypes'
    UserTypeID = db.Column(db.Integer,primary_key=True, autoincrement=True)
    TypeName = db.Column(db.String)

    def __init__(self, newUserTypeID, newTypeName):
        self.UserTypeID = newUserTypeID
        self.TypeName = newTypeName
        pass

    def __repr__    (self):
        # add text to the f-string
        return f"""
            UserTypeID : {self.UserTypeID}
            TypeName : {self.TypeName}
        """
    
    def __repr__(self):
        return self.__repr__()