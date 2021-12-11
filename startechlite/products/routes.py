import flask

products  = flask.Blueprint("products", __name__)

@products.route("/products/keyboards")
def get_keyboards() -> str:
    items = ["a", "b", "c"]
    return flask.render_template("products.html", items=items)