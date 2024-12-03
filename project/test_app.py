import pytest
from flask import Flask,request
from db.server import app, db
from helper import verifySignup,createUser,addOrder,deleteOrderItem
from db.schema.Users import Users
from db.schema.Orders import Orders
from db.schema.OrderItems import OrderItems
from db.schema.Store import Store
from db.schema.Menu import Menu
from db.schema.MenuItems import MenuItems
from sqlalchemy import *
import bcrypt
from db.scripts.testData import * 

app.secret_key = 'ewe'

def test_signup():
    with app.test_client() as client:
        with app.test_request_context('/signup', method='POST', data=good_data):
            #code copied from app.py and slightly modified, but should be logically equivelent 
            result = verifySignup(request) #verifySignup returns None if there are no errors and data is good
            assert result is None

            if(result is None):
                createUser(request)
            user = Users.query.filter_by(FirstName="Steve").first()
            assert user is not None #make sure user was inserted

@pytest.mark.xfail
def test_bad_signup():
    db.session.begin_nested()
    with app.test_client() as client:
        with app.test_request_context('/signup', method='POST', data=bad_data):
            #code copied from app.py and slightly modified, but should be logically equivelent
            result = verifySignup(request) #verifySignup returns None if there are no errors and data is good
            assert result is None

            if(result is None):
                createUser(request)
            user = Users.query.filter_by(FirstName="S").first()
            assert user is not None #make sure user was inserted
    db.session.rollback() 
    db.session.close()


@pytest.mark.xfail
def test_blank_signup():
    db.session.begin_nested()
    with app.test_client() as client:
        with app.test_request_context('/signup', method='POST', data=no_data):
            #code copied from app.py and slightly modified, but should be logically equivelent
            result = verifySignup(request) #verifySignup returns None if there are no errors and data is good
            assert result is None

            if(result is None):
                createUser(request)
            user = Users.query.filter_by(FirstName="S").first()
            assert user is not None #make sure user was inserted
    db.session.rollback() 
    db.session.close()


def test_login():
    with app.test_client() as client:
        with app.test_request_context('/signup', method='POST', data=good_data):
            #code copied from app.py and slightly modified, but should be logically equivelent 
            result = verifySignup(request) #verifySignup returns None if there are no errors and data is good
            if(result is None):
                createUser(request)
            user = Users.query.filter_by(FirstName="Steve").first()
            assert user is not None #make sure user was inserted
            with app.test_request_context('/login', method='POST', data=good_data):
            #code copied from app.py and slightly modified, but should be logically equivelent 
                # from request.form extract password and Email - Now getting it from mock data
                entered_pass = good_data.get("Password")
                entered_email = good_data.get("Email")

                # find user associated with email
                user_query = select(Users).where(Users.Email == entered_email)
                user = db.session.execute(user_query).scalar_one_or_none()

                # Check if the user exists and the password matches
                assert user and bcrypt.checkpw(entered_pass.encode(), user.Password.encode())

@pytest.mark.xfail
def test_login_without_signup():
    db.session.begin_nested()
    with app.test_client() as client:
        with app.test_request_context('/login', method='POST', data=good_data):
        #code copied from app.py and slightly modified, but should be logically equivelent 
            # from request.form extract password and Email - Now getting it from mock data
            entered_pass = good_data.get("Password")
            entered_email = good_data.get("Email")

            # find user associated with email
            user_query = select(Users).where(Users.Email == entered_email)
            user = db.session.execute(user_query).scalar_one_or_none()

            # Check if the user exists and the password matches
            assert user and bcrypt.checkpw(entered_pass.encode(), user.Password.encode())
    db.session.rollback() 
    db.session.close()

@pytest.mark.xfail
def test_login_bad_pass():
    with app.test_client() as client:
        with app.test_request_context('/signup', method='POST', data=good_data):
            #code copied from app.py and slightly modified, but should be logically equivelent 
            result = verifySignup(request) #verifySignup returns None if there are no errors and data is good
            if(result is None):
                createUser(request)
            user = Users.query.filter_by(FirstName="Steve").first()
            assert user is not None #make sure user was inserted
            with app.test_request_context('/login', method='POST', data=good_data):
            #code copied from app.py and slightly modified, but should be logically equivelent 
                # from request.form extract password and Email - Now getting it from mock data, and giving wrong pass for existing account
                entered_pass = "wrongPass@1"
                entered_email = good_data.get("Email")

                # find user associated with email
                user_query = select(Users).where(Users.Email == entered_email)
                user = db.session.execute(user_query).scalar_one_or_none()

                # Check if the user exists and the password matches
                assert user and bcrypt.checkpw(entered_pass.encode(), user.Password.encode())

def test_delete_user():
    #db.session.begin_nested()
    with app.test_client() as client:
        with app.test_request_context('/signup', method='POST', data=good_data):
            #code copied from app.py and slightly modified, but should be logically equivelent 
            result = verifySignup(request) #verifySignup returns None if there are no errors and data is good
            if(result is None):
                createUser(request)
            user = Users.query.filter_by(FirstName="Steve").first()
            assert user is not None #make sure user was inserted
            
            #testing the deleteUser function, copied from helper file and slightly modified
            user_id = user.UserID ##only modification, grabbing the user id directly
    
            # Delete the user and users stores and orders from the database
            db.session.execute(delete(OrderItems).where(OrderItems.UserID == user_id))
            db.session.execute(delete(Orders).where(Orders.UserID == user_id))
            db.session.execute(delete(Users).where(Users.UserID == user_id))
            db.session.commit()

            deleted_user = Users.query.filter_by(FirstName="Steve").first()
            assert deleted_user is None
    #db.session.rollback() 
    #db.session.close()


def test_add_order():
    
    with app.test_client() as client:
        with app.test_request_context('/restaurant', method='POST', data=order_data):
            
            db.session.begin_nested()
            insert_user = insert(Users).values(good_data_raw)

            db.session.execute(insert_user)

            user_test = Users.query.filter_by(FirstName=good_data.get("FirstName")).first()

            good_data_store = {
                "UserID": user_test.UserID,
                "StoreName" : "Kurger Bing",
                "StoreImage" : "somePic.jpg"
            }
            
            insert_store = insert(Store).values(good_data_store)

            db.session.execute(insert_store)

            store_test = Store.query.filter_by(StoreName=good_data_store.get("StoreName")).first()

            insert_menu = insert(Menu).values({"StoreID":store_test.StoreID})

            db.session.execute(insert_menu)

            menu_test = Menu.query.filter_by(StoreID=store_test.StoreID).first()

            menuitems_data = {
                "MenuID" : menu_test.MenuID,
                "MenuItemName" : "Lunch Menu",
                "MenuItemDesc" : "Food!",
                "MenuItemCal" : 20,
                "MenuItemPrice" : 5.0

            }

            insert_menu_items = insert(MenuItems).values(menuitems_data)

            db.session.execute(insert_menu_items)

            db.session.commit()

            #code copied from app.py and slightly modified, but should be logically equivelent 

            curr_restaurant = Store.query.filter_by(StoreName="Kurger Bing").first() # Look up the current restaurant
            menu = Menu.query.get(curr_restaurant.StoreID) # Look up menu associated with current restaurant
            menu_items = MenuItems.query.filter(MenuItems.MenuID == menu.MenuID).all() # Look up all menu items associated with the current menu

            # if were adding an item to our order
            if request.method == 'POST':
                addOrder(request, curr_restaurant)
            
            check_for_order = OrderItems.query.filter_by(ItemQuantity=2).first()
            assert check_for_order is not None
            db.session.rollback() 
            db.session.close()


@pytest.mark.xfail
def test_add_order_no_restaraunt():
    with app.test_client() as client:
        with app.test_request_context('/restaurant', method='POST', data=order_data):

            db.session.begin_nested()
            #code copied from app.py and slightly modified, but should be logically equivelent 

            curr_restaurant = Store.query.filter_by(StoreName="Lick Bonalds").first() # Look up the current restaurant - no restaurant created 
            menu = Menu.query.get(curr_restaurant.StoreID) # Look up menu associated with current restaurant
            menu_items = MenuItems.query.filter(MenuItems.MenuID == menu.MenuID).all() # Look up all menu items associated with the current menu

            # if were adding an item to our order
            if request.method == 'POST':
                addOrder(request, curr_restaurant)
            
            check_for_order = OrderItems.query.filter_by(ItemQuantity=2).first()
            assert check_for_order is not None
            db.session.rollback() 
            db.session.close()

def test_404_page():
    with app.test_client() as client:
        response = client.get('/invalid_route')
        assert response.status_code == 404 