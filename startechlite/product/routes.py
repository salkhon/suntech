import flask
import flask_login
from werkzeug import Response
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.product.model import Product
from startechlite.constants import *
import flask_breadcrumbs

product = flask.Blueprint("product", __name__, url_prefix="/product")
dbman = DBManager()


def product_id_dlc():
    view_args = flask.request.view_args
    assert view_args
    return f"{view_args.get('product_id')}"


@product.route("/<string:product_id>")
@flask_breadcrumbs.register_breadcrumb(product, ".productid", "", dynamic_list_constructor=product_id_dlc)
def product_view(product_id) -> str | Response:
    product = dbman.get_product_by_id(
        product_id, bought_togethers_included=True)
    return flask.render_template("product_page.html", product=product)


@product.route("/compare")
@flask_breadcrumbs.register_breadcrumb(product, ".compare", "Product Comparison")
def compare() -> str | Response:
    prod1_id = flask.request.args.get("prod1")
    prod2_id = flask.request.args.get("prod2")

    assert prod1_id and prod2_id

    product1 = dbman.get_product_by_id(int(prod1_id))
    product2 = dbman.get_product_by_id(int(prod2_id))

    assert product1 and product2

    return flask.render_template("compare.html", product1=product1, product2=product2)
