# import all the required stuff
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask
from flask import request
from flask_bower import Bower
from mongoengine import connect

# set up the data models defined for mongo
from db.mongo_schemata import *

# load environment variables from .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# create a Flask application
app = Flask(__name__)
# inject bower (for front-end resource management)
Bower(app)
# connect to MongoDB
connect(host='mongodb://' + os.environ.get('MONGO_HOST') + '/' + os.environ.get('MONGO_DBNAME'))

from controllers import *


@app.route('/')
def home_page():
    return show_homepage() 


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return register_new_user(request.form)
    elif request.method == 'GET':
        return show_registration_form()
    else: 
        return 404


@app.route('/new-portfolio/<username>', methods=['GET', 'POST'])
def new_portfolio(username):
    if request.method == 'POST':
        if not check_user(username):
            return show_registration_form()
        else:
            return create_new_portfolio(username = username,
                                        name = request.form['portfolio_name'],
                                        tickers = request.form['ticker_selection'])
    elif request.method == 'GET':
        # show the portfolio creation form
        return show_new_portfolio_form(username)
    else: 
        return 404


@app.route('/portfolio/<username>-<portfolio_id>')
def portfolio(username, portfolio_id):
    # show the given portfolio
    return show_portfolio(username, portfolio_id)


@app.route('/test')
def test():
    return matrix_test()

