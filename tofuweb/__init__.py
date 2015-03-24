from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.restful import Api


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/app.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'changesometimesoon'

api = Api(app)
db = SQLAlchemy(app)
admin = Admin(app)


import tofuweb.views
import tofuweb.rest
