import flask
from werkzeug import Response
import startechlite
from startechlite.account.model import User
from startechlite.constants import *
import flask_breadcrumbs
import flask_login
from startechlite.dbmanager.dbmanager import DBManager
from startechlite.sales.model import Purchase

dbman = DBManager()

account = flask.Blueprint("account", __name__, url_prefix="/account")


@account.route("/account")
@flask_breadcrumbs.register_breadcrumb(account, ".account", "Account")
@flask_login.login_required
def user_account():
    return flask.render_template("account.html")


@account.route("/order")
@flask_breadcrumbs.register_breadcrumb(account, ".order", "Order History")
@flask_login.login_required
def order_history():
    purchases: list[Purchase] = dbman.get_user_purhcases()
    # TODO: fill purchases with product info. So have to query products to fill purchase.
    return flask.render_template("account_order_history.html", purchases=purchases)


@account.route("/edit", methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(account, ".edit", "Edit Information")
@flask_login.login_required
def edit_info():
    # TODO: might POST edit, that needs to be updated. Email and phone can't be changed.
    return flask.render_template("account_edit_info.html")


def get_validated_registered_user() -> User | None:
    firstname = flask.request.form.get("firstname")
    lastname = flask.request.form.get("lastname")
    email = flask.request.form.get("email")
    password = flask.request.form.get("password")
    telephone = flask.request.form.get("telephone")
    address = flask.request.form.get("address", "")
    PLACEHOLDER_ID = -1

    if (
        not (firstname and lastname and email and telephone and password) or
        not dbman.is_user_email_registrable(email)
    ):
        return None

    return User(PLACEHOLDER_ID, firstname, lastname, email, startechlite.bcrypt.generate_password_hash(password).decode("utf-8"), telephone, address)


@account.route("/register", methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(account, ".register", "Register")
def register() -> str | Response:
    if flask_login.current_user.is_authenticated:  # type: ignore
        flask.flash("You are already logged in!", "info")
        return flask.redirect(flask.url_for("main.home"))

    if flask.request.method == "POST":
        validated_user = get_validated_registered_user()

        if not validated_user:
            flask.flash("Registration failed", "danger")
            return flask.render_template("register.html")

        dbman.insert_user(validated_user)

        flask.flash(
            "Your account has been successfully created! You are now able to login!", "success")

        return flask.redirect(flask.url_for("account.login"))

    return flask.render_template("register.html")


def _auth_login() -> bool:
    email = flask.request.form.get("email")
    if email:
        queried_user = dbman.get_user_by_email(email)
        if queried_user and startechlite.bcrypt.check_password_hash(queried_user.password, flask.request.form.get("password")):
            flask.flash(f"Welcome {queried_user.first_name}!")
            if queried_user.is_admin:
                flask.flash("You have admin access!")

            flask_login.login_user(queried_user)
            return True
        else:
            flask.flash("Login Failed", "danger")
    else:
        # TODO: Validate input
        flask.flash("Field cannot be empty login", "info")
    return False


@account.route("/login", methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(account, ".login", "Login")
def login() -> str | Response:
    if flask_login.current_user.is_authenticated:  # type: ignore
        flask.flash("You are already logged in!", "info")
        return flask.redirect(flask.url_for("main.home"))

    if flask.request.method == "POST" and _auth_login():
        next_page = flask.request.args.get("next")

        if next_page and not flask_login.current_user.is_admin:  # type: ignore
            return flask.redirect(next_page)
        else:
            return flask.redirect(flask.url_for("main.home"))

    return flask.render_template("login.html")


@account.route("/logout")
def logout() -> str | Response:
    flask_login.logout_user()
    return flask.redirect(flask.url_for("main.home"))
