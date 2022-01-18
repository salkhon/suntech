import random
import flask
from werkzeug import Response
from startechlite.account.model import User
from startechlite.product.model import Product
from startechlite.constants import *
import flask_breadcrumbs
import flask_login
from startechlite.dbmanager.dbmanager import DBManager

dbmanager = DBManager()

account = flask.Blueprint("account", __name__, url_prefix="/account")
flask_breadcrumbs.default_breadcrumb_root(account, ".")

@account.route("/account")
@flask_breadcrumbs.register_breadcrumb(account, ".account", "Account")
def user_account():
    # have to check if logged in, otherwise redirects to login page
    return flask.redirect(flask.url_for("account.login"))

@account.route("/register", methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(account, ".register", "Register")
def register() -> str | Response:
    print(flask_breadcrumbs.current_breadcrumbs[0].url)

    if flask_login.current_user.is_authenticated:  # type: ignore
        flask.flash("You are already logged in!", "info")
        return flask.redirect("main.home")

    if flask.request.method == "POST":
        firstname = flask.request.args.get("firstname")
        lastname = flask.request.args.get("lastname")
        email = flask.request.args.get("email")
        password = flask.request.args.get("password")
        telephone = flask.request.args.get("telephone")

        if firstname and lastname and email and password and telephone:
            id = random.randint(100000, 999999)
            user = User(id, firstname, lastname, email, password,
                        telephone, "#")
            dbmanager.insert_user(user)

        flask.flash(
            f"Your account has been successfully created! You are now able to login!", "success")

        return flask.redirect(flask.url_for("account.login"))

    return flask.render_template("register.html")


@account.route("/login", methods=["GET", "POST"])
@flask_breadcrumbs.register_breadcrumb(account, ".login", "Login")
def login() -> str | Response:
    if flask_login.current_user.is_authenticated:  # type: ignore
        flask.flash("You are already logged in!", "info")
        return flask.redirect("main.home")

    if flask.request.method == "POST":
        print(flask.request.args.get("password"))

    return flask.render_template("login.html")
