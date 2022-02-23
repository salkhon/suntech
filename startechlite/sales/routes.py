import flask
from werkzeug import Response
from startechlite.constants import *
import flask_breadcrumbs
import flask_login
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.sales.model import Purchase

dbman = DBManager()

sales = flask.Blueprint("sales", __name__, url_prefix="/sale")

"""
Cart will be manager only at the frontend until the sale is confirmed and the 
data needs to be sent to the server. 
"""


def _make_purchase_from_form_and_json() -> Purchase:
    purchase_json = flask.request.get_json()
    assert purchase_json

    product_counts: list[dict[str, int]] = purchase_json["products"]
    formdata: dict[str, str] = purchase_json["formdata"]

    productid_count = {}
    for product_count in product_counts:
        productid_count[product_count["id"]] = product_count["count"]

    purchase = Purchase(info=formdata.get(
        "payment_method"), address=formdata.get("address_1"), bought_by=flask_login.current_user.id, productid_count=productid_count)  # type: ignore

    return purchase


@sales.route("/checkout", methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(sales, ".checkout", "Checkout")
@flask_login.login_required
def checkout() -> str | Response:
    if flask_login.current_user.is_admin:  # type: ignore
        return flask.redirect(flask.url_for("admin.get_purchases"))

    if flask.request.method == "POST":
        purchase = _make_purchase_from_form_and_json()
        dbman.insert_purchase(purchase)
        return flask.redirect(flask.url_for("sales.order_confirmed"))

    return flask.render_template("checkout.html")


@sales.route("/confirm")
def order_confirmed() -> str | flask.Response:
    flask.flash("Success", "success")
    return flask.render_template("order_confirmed.html")


@sales.route("/info/<int:purchase_id>", methods=["GET", "POST"])
@flask_login.login_required
def info(purchase_id: int):
    if flask.request.method == "POST":
        if flask.request.form.get("action") == "Change Address":
            new_address = flask.request.form.get("address")
            dbman.update_purchase_address_by_id(purchase_id, new_address)
            return flask.redirect(flask.url_for("sales.info", purchase_id=purchase_id))
        elif flask.request.form.get("action") == "Delete Purchase":
            purchase_to_be_deleted = dbman.get_purchase_by_id(purchase_id)

            if not purchase_to_be_deleted or (purchase_to_be_deleted and purchase_to_be_deleted.approval_date):
                flask.flash("Purchase cannot be deleted")
                return flask.redirect(flask.url_for("sales.info", purchase_id=purchase_id))

            dbman.delete_purchase_by_id(purchase_id)
            flask.flash("Purchase deleted")
            return flask.redirect(flask.url_for("main.home"))
        print("here")

    purchase = dbman.get_purchase_by_id(purchase_id)

    if not purchase:
        flask.abort(404)

    if purchase.bought_by != flask_login.current_user.id and not flask_login.current_user.is_admin:  # type: ignore
        flask.abort(404)

    return flask.render_template("sale_info.html", purchase=purchase)
