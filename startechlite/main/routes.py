import flask
import flask_breadcrumbs

main = flask.Blueprint("main", __name__)
flask_breadcrumbs.default_breadcrumb_root(main, ".")

@main.route("/")
def home() -> str:
    return flask.render_template("home.html")
