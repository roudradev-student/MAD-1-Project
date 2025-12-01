from flask import Flask
from flask_login import LoginManager
from database import db

import datetime

app = None

login_manager = LoginManager()  

def create_app():
    app = Flask(__name__)
    app.debug = True

    app.config['SECRET KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rdbdata.db'
    db.init_app(app)

    my_login_manager = LoginManager()
    my_login_manager.init_app(app)

    #we will be creating the databases and creating the tables
    #craeting of the admin id

    return app

app=create_app()
from routes import *  # noqa: E402, F401

if __name__ == '__main__':
    app.run(debug=True)


