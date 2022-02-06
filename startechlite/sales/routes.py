import random
import flask
from werkzeug import Response
import startechlite
from startechlite.account.model import User
from startechlite.constants import *
import flask_breadcrumbs
import flask_login
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.sales.model import Purchase

dbmanager = DBManager()

sales = flask.Blueprint("sales", __name__, url_prefix="/sale")

"""
Cart will be manager only at the frontend until the sale is confirmed and the 
data needs to be sent to the server. 
"""

def _get_purchase() -> Purchase:
    purchase_json = flask.request.get_json()
    assert purchase_json

    product_counts: list[dict[str, int]] = purchase_json["products"]
    formdata: dict[str, str] = purchase_json["formdata"]
    
    productid_count = {}
    for product_count in product_counts:
        productid_count[product_count["id"]] = product_count["count"]

    purchase = Purchase(info=formdata.get(
        "payment_method"), bought_by=flask_login.current_user.id, productid_count=productid_count)  # type: ignore
    
    return purchase


# POST will send the cart data
@sales.route("/checkout", methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(sales, ".checkout", "Checkout")
@flask_login.login_required
def checkout() -> str | Response:
    if flask.request.method == "POST":
        purchase = _get_purchase()
        dbmanager.insert_purchase(purchase)
        return flask.redirect(flask.url_for("sales.order_confirmed"))

    return flask.render_template("checkout.html")


@sales.route("/confirm")
def order_confirmed() -> str | flask.Response:
    flask.flash("Success", "success")
    return flask.render_template("order_confirmed.html")


@sales.route("/cart")
def cart() -> str | Response:
    print("to be done cart")
    return ""
