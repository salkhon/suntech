import flask
import flask_login
import json
from startechlite.constants import BRANDS, CAT_SUBCAT_BRAND_DICT, CATEGORIES, SUBCATEGORIES
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.admin.utils import _make_new_basic_product_from_form, _make_updated_product_from_form, _make_updated_user_from_form, _get_deleted_product_basic_info_from_form

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
def edit_or_ban_user(userid):
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        flask.redirect(flask.url_for("main.home"))

    if flask.request.method == "POST":
        if flask.request.form.get("action") == "Update":
            updated_user = _make_updated_user_from_form()
            dbman.update_user(updated_user)
        elif flask.request.form.get("action") == "Ban":
            id, email = flask.request.form.get("id"), flask.request.form.get("email")
            assert id and email
            ban_successful = dbman.ban_user(int(id), email)
            if ban_successful:
                flask.flash("Banned user", "success")
            else:
                flask.flash("Could not ban", "error")

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

            uploaded_images = []
            if flask.request.files.get("image"):
                uploaded_images = flask.request.files.getlist("image")

            dbman.update_product_by_id(
                product_id, updated_product, uploaded_images)

            return flask.redirect(flask.url_for(
                "admin.edit_product",
                product_id=product_id
            ))
        elif flask.request.form.get("action") == "Delete":
            _, del_cat, del_subcat, del_brand = _get_deleted_product_basic_info_from_form()

            dbman.delete_product(product_id)

            return flask.redirect(flask.url_for(
                "productslist.get_category_subcategory_brand",
                category=del_cat,
                subcategory=del_subcat,
                brand=del_brand
            ))
        elif flask.request.form.get("action") == "Add New Specification":
            spec_attr_name, spec_attr_val = flask.request.form.get(
                "attr_name"), flask.request.form.get("attr_value")
            assert spec_attr_name and spec_attr_val

            existing_attr_val = dbman.get_product_spec_attr_val_by_id_and_attr_name(
                product_id, spec_attr_name)

            if existing_attr_val:
                flask.flash(
                    f"Attribute named by {spec_attr_name} already exists")
            else:
                dbman.add_new_spec_for_product_by_id(
                    product_id, spec_attr_name, spec_attr_val)

            return flask.redirect(flask.url_for(
                "admin.edit_product",
                product_id=product_id
            ))
    else:
        product = dbman.get_product_by_id(product_id)
        return flask.render_template("admin_edit_product.html", product=product)


@admin.route("/createproduct", methods=["GET", "POST"])
@flask_login.login_required
def create_product():
    if flask.request.method == "POST":
        new_basic_product = _make_new_basic_product_from_form()
        dbman.create_new_product(new_basic_product)
    return flask.render_template(
        "admin_create_product.html",
        CAT_SUBCAT_BRAND_DICT=json.dumps(CAT_SUBCAT_BRAND_DICT)
    )


@admin.route("/purchases")
@flask_login.login_required
def get_purchases():
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        return flask.redirect(flask.url_for("main.home"))

    purchases = dbman.get_all_purchases()
    return flask.render_template("admin_purchases.html", purchases=purchases)


@admin.route("/purchases/approve/<int:purchase_id>", methods=["POST"])
@flask_login.login_required
def approve_purchase(purchase_id: int):
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        return flask.redirect(flask.url_for("main.home"))

    dbman.approve_purchase(purchase_id)
    return flask.redirect(flask.url_for("admin.get_purchases"))
