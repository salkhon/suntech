import flask
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.product.model import Product
from startechlite.productslist.routes import view_arg_dlc
from startechlite.constants import *
import flask_breadcrumbs

product = flask.Blueprint("product", __name__, url_prefix="/product")
dbman = DBManager()


def product_name_dlc():
    return view_arg_dlc("product_handle")

@product.route("/<string:product_handle>")
@flask_breadcrumbs.register_breadcrumb(product, ".producthandle", "", dynamic_list_constructor=product_name_dlc)
def product_view(product_handle) -> str:
    product = dbman.get_product_by_handle(product_handle)
    return flask.render_template("product_page.html", product=product)
