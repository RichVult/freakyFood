from flask import request, render_template
from db.server import *  # import all from server
from sqlalchemy import text

from db.server import app, db

from db.schema.Users import Users


app = Flask(__name__, template_folder='templates')  # Set the template folder


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])  # +
def login():
    if request.method == 'POST':

        try:

            username = request.form.get("email")
            password = request.form.get("password")

            db_password = db.session.execute(text("""SELECT "Password" FROM "Users" WHERE "Email" = :username"""), {
                "username": username}).fetchone()

            if db_password is None:
                return render_template('fail.html')

            if db_password[0] == password:
                print("Login Successful")
                return render_template('success.html')

        except Exception as e:
            print(f"An error occurred: {e}")

    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
