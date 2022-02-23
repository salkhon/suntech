import flask
import flask_breadcrumbs
from startechlite.dbmanager.dbmanager import DBManager

main = flask.Blueprint("main", __name__)
flask_breadcrumbs.default_breadcrumb_root(main, ".")
dbman = DBManager()


@main.route("/")
def home() -> str:
    return flask.render_template("home.html")


@main.route("/search")
@flask_breadcrumbs.register_breadcrumb(main, ".search", "Search")
def search():
    search_string = flask.request.args.get("search_string")

    products, pagination = dbman.get_by_search(search_string)  # type: ignore
    return flask.render_template("productslist.html", products=products, pagination=pagination)
    