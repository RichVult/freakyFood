from sqlalchemy import insert, select

# Function to populate user types with the 3 acceptable user types if they dont already exist in the db
def insert_user_types():
    from db.schema.UserTypes import UserTypes
    from db.server import db
    # Define the allowed user types
    user_types = ['Driver', 'Customer', 'StoreOwner']
    
    # Iterate over each user type
    for user_type in user_types:
        # Check if the user type already exists
        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == user_type)).scalar_one_or_none()
    
        if existing_user_type is None:
            # Create a new UserTypes instance and add it to the session
            db.session.execute(insert(UserTypes).values(TypeName=user_type))
            print(f"DUMMY DATA: Inserted User type: {user_type}")
        else:
            print(f"DUMMY DATA: User type '{user_type}' already exists. Skipping.")

# Commit the changes to the database
    db.session.commit()