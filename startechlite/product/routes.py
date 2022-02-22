import flask
from werkzeug import Response
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.constants import *
import flask_breadcrumbs

product = flask.Blueprint("product", __name__, url_prefix="/product")
dbman = DBManager()


def product_id_dlc():
    view_args = flask.request.view_args
    assert view_args
    return f"{view_args.get('product_id')}"


@product.route("/<string:product_id>", methods=['GET', 'POST'])
@flask_breadcrumbs.register_breadcrumb(product, ".productid", "", dynamic_list_constructor=product_id_dlc)
def product_view(product_id) -> str:
    if flask.request.method == "POST":
        p_id = flask.request.form.getlist('product_id')
        comments = flask.request.form.getlist('comment')
        comment_on = flask.request.form.getlist('comment_on')
        ratings = flask.request.form.getlist('rating')
        review_texts = flask.request.form.getlist('review_text')

        if len(comments) != 0:
            dbman.add_comment([p_id, comments, comment_on])

        if len(review_texts) != 0:
            dbman.add_review([p_id, ratings, review_texts])

    product = dbman.get_product_by_id(product_id, True)
    reviews = dbman.get_reviews(product_id)
    main_comments, sub_comments = dbman.get_comments(
        product_id)  # type: ignore
    return flask.render_template("product_page.html", product=product, main_comments=main_comments, sub_comments=sub_comments, reviews=reviews)


@product.route("/compare")
@flask_breadcrumbs.register_breadcrumb(product, ".compare", "Product Comparison")
def compare() -> str | Response:
    prod1_id = flask.request.args.get("prod1")
    prod2_id = flask.request.args.get("prod2")

    assert prod1_id and prod2_id

    product1 = dbman.get_product_by_id(int(prod1_id))
    product2 = dbman.get_product_by_id(int(prod2_id))

    assert product1 and product2

    return flask.render_template("compare.html", product1=product1, product2=product2)
