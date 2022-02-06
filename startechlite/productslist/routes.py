import flask
import flask_breadcrumbs
from startechlite.constants import *

from startechlite.dbmanager.dbmanager import DBManager

productslist = flask.Blueprint(
    "productslist", __name__, url_prefix="/productlist")
dbman = DBManager()


def view_arg_dlc(view_arg: str) -> list[dict[str, str]]:
    # level meaning category, subcategory or brand
    assert flask.request.view_args
    name: str = flask.request.view_args.get(
        view_arg)  # type: ignore
    name = name.replace("-", " ").replace("_", " ").capitalize()
    return [{"text": name, "url": flask.request.path}]


def category_dlc():
    return view_arg_dlc("category")


def subcategory_dlc():
    return view_arg_dlc("subcategory")


def brand_dlc():
    return view_arg_dlc("brand")


@productslist.route("/<string:category>")
@flask_breadcrumbs.register_breadcrumb(productslist, ".category", "", dynamic_list_constructor=category_dlc)
def get_category(category: str) -> str:
    category = category.lower()

    if category not in CATEGORIES:
        flask.abort(404)

    page = int(flask.request.args.get("page", default=1))
    products, pagination = dbman.get_category(category, page)
    return flask.render_template("productslist.html", products=products, pagination=pagination)


@productslist.route("/<string:category>/<string:subcategory>")
@flask_breadcrumbs.register_breadcrumb(productslist, ".category.subcategory", "", dynamic_list_constructor=subcategory_dlc)
def get_category_subcategory(category: str, subcategory: str) -> str:
    category, subcategory = category.lower(), subcategory.lower()

    if category not in CATEGORIES or subcategory not in SUBCATEGORIES:
        flask.abort(404)

    page = int(flask.request.args.get("page", default=1))
    products, pagination = dbman.get_category_subcategory(
        category, subcategory, page)
    return flask.render_template("productslist.html", products=products, pagination=pagination)


@productslist.route("/<string:category>/<string:subcategory>/<string:brand>")
@flask_breadcrumbs.register_breadcrumb(productslist, ".category.subcategory.brand", "", dynamic_list_constructor=brand_dlc)
def get_category_subcategory_brand(category: str, subcategory: str, brand: str) -> str:
    category, subcategory, brand = category.lower(), subcategory.lower(), brand.lower()

    if category not in CATEGORIES or subcategory not in SUBCATEGORIES or brand not in BRANDS:
        flask.abort(404)

    page = int(flask.request.args.get("page", default=1))
    products, pagination = dbman.get_category_subcategory_brand(
        category, subcategory, brand, page)
    return flask.render_template("productslist.html", products=products, pagination=pagination)
