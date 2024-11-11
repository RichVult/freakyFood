from db.server import db

class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserTypeID = db.Column(db.Integer, db.ForeignKey('UserTypes.UserTypeID'), nullable=False) 
    Email = db.Column(db.String(120), nullable=False) 
    Password = db.Column(db.String(256), nullable=False)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    PhoneNumber = db.Column(db.String(50), nullable=True)
    Street = db.Column(db.String(250), nullable=True)
    City = db.Column(db.String(250), nullable=True)
    State = db.Column(db.String(250), nullable=True)
    ZipCode = db.Column(db.String(250), nullable=True)
    CardNumber = db.Column(db.String(16), nullable=True)
    ProfileImage = db.Column(db.String(100), nullable=False, default='default_profile.png')

    # Define relationship
    user_type = db.relationship('UserTypes', back_populates='Users')
    stores = db.relationship('Store', back_populates='user')
    order_items = db.relationship('OrderItems', back_populates='user')

    # Constructor
    def __init__(self, newUserTypeID, newEmail, newPassword, newFirstName, newLastName, newPhoneNumber, newStreet, newCity, newState, newZipCode, newCardNumber, newProfileImage):
        self.UserTypeID = newUserTypeID 
        self.Email = newEmail
        self.Password = newPassword
        self.FirstName = newFirstName
        self.LastName = newLastName
        self.PhoneNumber = newPhoneNumber
        self.Street = newStreet
        self.City = newCity
        self.State = newState
        self.ZipCode = newZipCode
        self.CardNumber = newCardNumber
        self.ProfileImage = newProfileImage

    # Debug
    def __repr__(self):
        return f"""
            UserID : {self.UserID}
            UserTypeID : {self.UserTypeID}
            Email : {self.Email}
            Password : {self.Password}
            FirstName : {self.FirstName}
            LastName : {self.LastName}
            PhoneNumber : {self.PhoneNumber}
            Street : {self.Street}
            City : {self.City}
            State : {self.State}
            ZipCode : {self.ZipCode}
            CardNumber : {self.CardNumber}
            ProfileImage : {self.ProfileImage}
        """