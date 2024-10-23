from sqlalchemy import insert, select

def insert_user_types():
    from db.schema.UserTypes import UserTypes
    from db.server import db
    # Define the allowed user types
    user_types = ['Driver', 'Customer', 'StoreOwner']
    
    # Iterate over each user type
    for user_type in user_types:
        # Add All Instances
        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == user_type)).scalar_one_or_none()
        
        print(f"Inserted User type: {user_type}")

    # Commit the changes to the database
    db.session.commit()