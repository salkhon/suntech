import flask

main = flask.Blueprint("main", __name__)

@main.route("/")
def home() -> str:
    return flask.render_template("index.html")
