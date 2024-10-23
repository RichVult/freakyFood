from flask import Flask, render_template, request, redirect, url_for, session
from db.server import app, db
from sqlalchemy import *
import os
from db.schema.Users import Users
from db.schema.UserTypes import UserTypes

app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key_here')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('account'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_email = request.form["Email"]
        new_password = request.form["Password"]
        new_first_name = request.form["FirstName"]
        new_last_name = request.form["LastName"]
        new_user_type = request.form["UserType"]

        allowed_user_types = ['Driver', 'Customer', 'StoreOwner']

        if new_user_type not in allowed_user_types:
            return "Invalid user type. Please select from Driver, Customer, or Store Owner.", 400

        existing_user_type = db.session.execute(select(UserTypes).where(UserTypes.TypeName == new_user_type)).scalar_one_or_none()

        if existing_user_type is None:
            create_user_type = insert(UserTypes).values(TypeName=new_user_type)
            db.session.execute(create_user_type)
            db.session.commit()
            user_type_id = db.session.execute(select(UserTypes.UserTypeID).where(UserTypes.TypeName == new_user_type)).scalar_one()
        else:
            user_type_id = existing_user_type.UserTypeID

        create_user = insert(Users).values(
            UserTypeID=user_type_id,
            Email=new_email,
            Password=new_password,
            FirstName=new_first_name,
            LastName=new_last_name,
            Address=None,
            CardNumber=None
        )
        db.session.execute(create_user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_pass = request.form["Password"]
        entered_email = request.form["Email"]
        user_query = select(Users).where(Users.Email == entered_email)
        user = db.session.execute(user_query).scalar_one_or_none()

        if user and user.Password == entered_pass:  
            session['user_id'] = user.UserID 
            return redirect(url_for('account'))  
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db.session.execute(select(Users).where(Users.UserID == user_id)).scalar_one_or_none()
    return render_template('account.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    return render_template('reset.html')

if __name__ == "__main__":
    app.run(debug=True)
