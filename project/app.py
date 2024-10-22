from flask import Flask, render_template
from db.server import *  # import all from server

app = Flask(__name__, template_folder='templates')  # Set the template folder

@app.route('/')
def index():
    return render_template('FFHomePage.html')

if __name__ == "__main__":
    app.run(debug=True)