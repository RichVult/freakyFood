"""professor.py: create a table named professors in the marist database"""
from db.server import db

class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer,primary_key=True, autoincrement=True)
    UserTypeID = db.relationship('UserTypeID', back_populates='UserTypeID')
    Email = db.Column(db.String)
    Password = db.Column(db.String)
    FirstName = db.Column(db.String)
    LastName = db.Column(db.String)
    Address = db.Column(db.String)
    CardNumber = db.Column(db.String)

    def __init__(self, newUserID, newUserTypeID, newEmail, newPassword, newFirstName, newLastName, newAddress, newCardNumber):
        self.UserID = newUserID
        self.UserTypeID = newUserTypeID 
        self.Email = newEmail
        self.Password = newPassword
        self.newFirstName
        self.newLastName
        self.newAddress
        self.newCardNumber
        pass

    def __repr__    (self):
        # add text to the f-string
        return f"""
            UserID : {self.UserID}
            UserTypeID : {self.UserTypeID}
            Email : {self.Email}
            Password : {self.Password}
            FirstName : {self.FirstName}
            LastName : {self.LastName}
            Address : {self.Address}
            CardNumber : {self.CardNumber}
        """
    
    def __repr__(self):
        return self.__repr__()



    # ex 1:1  user = db.relationship('User', back_populates='profile'), and profile = db.relationship('Profile', back_populates='user', uselist=False)

    # ex 1:many posts = db.relationship('Post', backref='author', lazy=True) user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # In User, db.relationship('Post', backref='author', lazy=True) allows each user to have multiple posts. The backref creates a reverse relationship in Post called author.