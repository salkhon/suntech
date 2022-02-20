import flask
import flask_login
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.admin.util import _make_updated_product_from_form, _make_updated_user_from_form, _get_deleted_product_basic_info_from_form

dbman = DBManager()

admin = flask.Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/users")
@flask_login.login_required
def get_users():
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        flask.redirect(flask.url_for("main.home"))

    page = int(flask.request.args.get("page", default=1))

    users, pagination = dbman.get_user_list(page)

    return flask.render_template("admin_users.html", users=users, pagination=pagination)


@admin.route("/edituser/<int:userid>", methods=["GET", "POST"])
@flask_login.login_required
def edit_user(userid):
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        flask.redirect(flask.url_for("main.home"))

    if flask.request.method == "POST":
        if flask.request.form.get("action") == "Update":
            updated_user = _make_updated_user_from_form()
            dbman.update_user(updated_user)
        elif flask.request.form.get("action") == "Delete":
            id = flask.request.form.get("id")
            assert id
            dbman.delete_user(int(id))

        return flask.redirect(flask.url_for("admin.get_users"))
    else:
        user = dbman.get_user_by_id(userid)
        return flask.render_template("admin_edit_user.html", user=user)


@admin.route("/editproduct/<int:product_id>", methods=["GET", "POST"])
@flask_login.login_required
def edit_product(product_id):
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        flask.redirect(flask.url_for("main.home"))

    if flask.request.method == "POST":
        if flask.request.form.get("action") == "Update":
            updated_product = _make_updated_product_from_form()
            print(updated_product)
            return flask.redirect(flask.url_for(
                "admin.edit_product",
                product_id=updated_product.id
            ))
        elif flask.request.form.get("action") == "Delete":
            del_id, del_cat, del_subcat, del_brand = _get_deleted_product_basic_info_from_form()

            dbman.delete_product(product_id)

            return flask.redirect(flask.url_for(
                "productslist.get_category_subcategory_brand",
                category=del_cat,
                subcategory=del_subcat,
                brand=del_brand
            ))
    else:
        product = dbman.get_product_by_id(product_id)
        return flask.render_template("admin_edit_product.html", product=product)

@admin.route("/purchases")
@flask_login.login_required
def get_purchases():
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        return flask.redirect(flask.url_for("main.home"))
    
    purchases = dbman.get_all_purchases()
    return flask.render_template("admin_purchases.html", purchases=purchases)

@admin.route("/purchases/approve/<int:purchase_id>")
@flask_login.login_required
def approve_purchase(purchase_id: int):
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        return flask.redirect(flask.url_for("main.home"))

    dbman.approve_purchase(purchase_id)
    return flask.redirect(flask.url_for("admin.get_purchases"))
