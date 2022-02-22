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


def read_filters():

    price = []
    price.append( flask.request.form.getlist("price_from")[0][3:] )
    price.append(flask.request.form.getlist("price_to")[0][3:])
   
    subcat = flask.request.form.getlist("Subcategory")
    brands = flask.request.form.getlist("Brand")
    

    processor = flask.request.form.getlist("Processor")
    ram = flask.request.form.getlist("Ram")
    display = flask.request.form.getlist("Display")
    storage = flask.request.form.getlist("Storage")
    graphics = flask.request.form.getlist("Graphics")



    return [price, subcat, brands, processor, ram, display, storage, graphics]
   


@productslist.route("/<string:category>",  methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(productslist, ".category", "", dynamic_list_constructor=category_dlc)
def get_category(category: str) -> str:
    category = category.lower()

    if flask.request.method == "POST":

        filters = read_filters()
        page = int(flask.request.args.get("page", default=1))
        products, pagination, side_filters = dbman.get_by_filters(
            filters, category, page)
        return flask.render_template("productslist_filters.html", products=products, pagination=pagination, side_filters=side_filters)

    page = int(flask.request.args.get("page", default=1))
    products, pagination, side_filters = dbman.get_category(category, page)
    print(side_filters, flush=True)

    return flask.render_template("productslist_filters.html", products=products, pagination=pagination, side_filters=side_filters)


@productslist.route("/<string:category>/<string:subcategory>")
@flask_breadcrumbs.register_breadcrumb(productslist, ".category.subcategory", "", dynamic_list_constructor=subcategory_dlc)
def get_category_subcategory(category: str, subcategory: str) -> str:
    category, subcategory = category.lower(), subcategory.lower()

    page = int(flask.request.args.get("page", default=1))
    products, pagination, _ = dbman.get_category_subcategory(
        category, subcategory, page)
    return flask.render_template("productslist.html", products=products, pagination=pagination)


@productslist.route("/<string:category>/<string:subcategory>/<string:brand>")
@flask_breadcrumbs.register_breadcrumb(productslist, ".category.subcategory.brand", "", dynamic_list_constructor=brand_dlc)
def get_category_subcategory_brand(category: str, subcategory: str, brand: str) -> str:
    category, subcategory, brand = category.lower(), subcategory.lower(), brand.lower()

    page = int(flask.request.args.get("page", default=1))
    products, pagination, _ = dbman.get_category_subcategory_brand(
        category, subcategory, brand, page)
    return flask.render_template("productslist.html", products=products, pagination=pagination)


@productslist.route("/bundles")
@flask_breadcrumbs.register_breadcrumb(productslist, ".bundles", "")
def get_bundles() -> str:
    page = int(flask.request.args.get("page", default=1))
    bundles, pagination = dbman.get_bundles(page=page)
    return flask.render_template("bundle_list.html", bundles=bundles, pagination=pagination)
