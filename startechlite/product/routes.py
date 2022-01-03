import flask
from startechlite.product.model import Item
from startechlite.constants import *
import flask_breadcrumbs
import flask_paginate

product = flask.Blueprint("product", __name__, url_prefix="/product")

flask_breadcrumbs.default_breadcrumb_root(product, ".")


def dynamic_breadcrumb_name() -> str | None:
    return flask.request.args.get("product_name")


@product.route("/<string:product_name>")
@flask_breadcrumbs.register_breadcrumb(product, ".item", "", dynamic_list_constructor=dynamic_breadcrumb_name)
def product_view(product_name) -> str:
    item = Item("sample product", product_name, "BMW", "#", [
                "prop1: nice", "prop2: real nice", "prop3: great"])
    return flask.render_template("product_page.html", item=item)
