import flask
from startechlite.component.model import Item
from startechlite.constants import *
import flask_breadcrumbs
import flask_paginate

component = flask.Blueprint("component", __name__)

flask_breadcrumbs.default_breadcrumb_root(component, ".")


@component.route(f"/{Component.COMPONENT}")
@flask_breadcrumbs.register_breadcrumb(component, ".", "Component")
def get_components() -> str:
    # return components
    page = flask.request.args.get("page", type=int, default=1)
    items = [Item("item", "#", ["prop1: prop"])] * 43
    # TODO:
    # pagination needs to be done inside datamanager, that returns the sliced query
    # along with the pagination object. 
    pagination = flask_paginate.Pagination(page=page, total=len(items), per_page=10)
    print(pagination.alignment)
    print(pagination.info)
    return flask.render_template("products.html", items=items, pagination=pagination, topbar_title="Component")


@component.route(f"/component/processor/")
@flask_breadcrumbs.register_breadcrumb(component, f".processor", "Processors")
def processors() -> str:
    return flask.render_template("products.html", items=[])


def brand_dyn_li_ctor(*args, **kwargs) -> list[dict]:
    url = flask.request.path
    brand = flask.request.view_args["brand"]  # type: ignore
    return [{"text": brand, "url": url}]


@component.route("/component/processor/<string:brand>")
@flask_breadcrumbs.register_breadcrumb(component, ".processor.brand", "", dynamic_list_constructor=brand_dyn_li_ctor)
def specific_processors(brand) -> str:
    if not brand:
        flask.redirect(flask.url_for("processors"))
    elif brand == Component.Processor.AMD:
        pass
    elif brand == Component.Processor.INTEL:
        pass
    return flask.render_template("products.html", items=[])


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
