import random
import flask
from werkzeug import Response
import startechlite
from startechlite.account.model import User
from startechlite.constants import *
import flask_breadcrumbs
import flask_login
from startechlite.dbmanager.dbmanager import DBManager

dbmanager = DBManager()

sales = flask.Blueprint("sales", __name__, url_prefix="/sale")

"""
Cart will be manager only at the frontend until the sale is confirmed and the 
data needs to be sent to the server. 
"""

@sales.route("/checkout", methods=["GET", "POST"])  # POST will send the cart data 
@flask_login.login_required
def checkout() -> str | Response:
    return flask.render_template("checkout.html")

@sales.route("/cart")
def cart() -> str | Response:
    print("to be done cart")
    return ""
