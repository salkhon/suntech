import flask
from startechlite.constants import *
from startechlite.dbmanager.dbmanager import DBManager
import flask_breadcrumbs

component = flask.Blueprint("component", __name__, url_prefix="/component")
dbmanager = DBManager()
flask_breadcrumbs.default_breadcrumb_root(component, ".")


@component.route("")
@flask_breadcrumbs.register_breadcrumb(component, ".", "Component")
def get_components() -> str:
    # return components
    page = flask.request.args.get("page", type=int, default=1)
    items, pagination = dbmanager.get_components(page=page)
    return flask.render_template("products.html", items=items, pagination=pagination)


@component.route("/processor")
@flask_breadcrumbs.register_breadcrumb(component, ".processor", "Processors")
def processors() -> str:
    page = flask.request.args.get("page", type=int, default=1)
    items, pagination = dbmanager.get_components(
        page=page)  # should be processors
    return flask.render_template("products.html", items=items, pagination=pagination)


def brand_dyn_li_ctor(*args, **kwargs) -> list[dict]:
    url = flask.request.path
    brand: str = flask.request.view_args["brand"]  # type: ignore
    brand = brand.replace("-", " ").capitalize()
    return [{"text": brand, "url": url}]


@component.route("/processor/<string:brand>")
@flask_breadcrumbs.register_breadcrumb(component, ".processor.brand", "", dynamic_list_constructor=brand_dyn_li_ctor)
def specific_processors(brand) -> str | None:
    items = []
    page = flask.request.args.get("page", type=int, default=1)
    pagination = None

    if not brand:
        flask.redirect(flask.url_for("component.processors"))
    elif brand == Component.Processor.AMD:
        items, pagination = dbmanager.get_components(
            page=page)  # should get AMD processors
        return flask.render_template("products.html", items=items, pagination=pagination)
    elif brand == Component.Processor.INTEL:
        items, pagination = dbmanager.get_components(
            page=page)  # should get INTEL processors
        return flask.render_template("products.html", items=items, pagination=pagination)
    else:
        flask.abort(404)


@component.route("/products/keyboards")
def keyboards() -> str:
    items = ["a", "b", "c"]
    """
    TODO:
    item = {
        title: "", 
        img_url: "", 
        short_description: list[str]
    }
    """
    return flask.render_template("products.html", items=items)
