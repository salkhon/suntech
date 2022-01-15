import flask
from startechlite.product.model import Item
from startechlite.constants import *
import flask_breadcrumbs

product = flask.Blueprint("product", __name__, url_prefix="/product")
flask_breadcrumbs.default_breadcrumb_root(product, ".")


def dynamic_breadcrumb_name() -> list[dict]:
    assert flask.request.view_args
    prod_name =  flask.request.view_args.get("product_name")
    path = flask.request.path
    return [{"text": prod_name, "url": path}]


@product.route("/<string:product_name>")
@flask_breadcrumbs.register_breadcrumb(product, ".item", "", dynamic_list_constructor=dynamic_breadcrumb_name)
def product_view(product_name) -> str:
    item = Item("sample product", product_name, "BMW", "#", [
                "prop1: nice", "prop2: real nice", "prop3: great"])
    return flask.render_template("product_page.html", item=item)
