import flask
import flask_breadcrumbs
from startechlite.constants import Desktop

from startechlite.dbmanager.dbmanager import DBManager

desktop = flask.Blueprint("desktop", __name__, url_prefix="/desktop")
flask_breadcrumbs.default_breadcrumb_root(desktop, ".")

dbmanager = DBManager()


@desktop.route("/")
@flask_breadcrumbs.register_breadcrumb(desktop, ".", "Desktop")
def desktops() -> str:
    print("on root")
    page = flask.request.args.get("page", type=int, default=1)
    items, pagination = dbmanager.get_desktops(page=page)
    return flask.render_template("products.html", items=items, pagination=pagination)

# all categories > sub categories > brand (if exists)


def desktop_subcategory_dlc():
    assert flask.request.view_args
    subcategory: str = flask.request.view_args.get(
        "subcategory")  # type: ignore
    subcategory = subcategory.replace("-", " ").replace("_", " ").capitalize()
    return [{"text": subcategory, "url": flask.request.path}]


def desktop_sucategory_brand_dlc():
    assert flask.request.view_args
    brand: str = flask.request.view_args.get("brand")  # type: ignore
    brand = brand.replace("-", " ").capitalize()
    return [{"text": brand, "url": flask.request.path}]


@desktop.route("/<string:subcategory>/")
@flask_breadcrumbs.register_breadcrumb(desktop, ".subcat", "", dynamic_list_constructor=desktop_subcategory_dlc)
def get_subcategory(subcategory: str) -> str:
    if subcategory not in Desktop.SUBCATEGORIES:
        pass  # return error page

    page = flask.request.args.get("page", type=int, default=1)
    items, pagination = dbmanager.get_desktop_subcategory(
        subcategory, page=page)
    return flask.render_template("products.html", items=items, pagination=pagination)


@desktop.route("/<string:subcategory>/<string:brand>/")
@flask_breadcrumbs.register_breadcrumb(desktop, ".subcat.brand", "", dynamic_list_constructor=desktop_sucategory_brand_dlc)
def get_subcategory_brand(subcategory: str, brand: str) -> str:
    if subcategory not in Desktop.SUBCATEGORIES or brand not in Desktop.BRANDS:
        pass  # return error page

    page = flask.request.args.get("page", type=int, default=1)
    items, pagination = dbmanager.get_desktop_subcategory_brand(
        subcategory, brand, page=page)
    return flask.render_template("products.html", items=items, pagination=pagination)
