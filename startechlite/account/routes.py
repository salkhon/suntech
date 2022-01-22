import random
import flask
from werkzeug import Response
import startechlite
from startechlite.account.model import User
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
    if flask_login.current_user.is_authenticated:  # type: ignore
        flask.flash("You are already logged in!", "info")
        return flask.redirect("main.home")

    if flask.request.method == "POST":
        firstname = flask.request.form.get("firstname")
        lastname = flask.request.form.get("lastname")
        email = flask.request.form.get("email")
        hashed_password = startechlite.bcrypt.generate_password_hash(
            flask.request.form.get("password")).decode("utf-8")
        telephone = flask.request.form.get("telephone")

        if firstname and lastname and email and hashed_password and telephone:
            id = random.randint(100000, 999999)
            user = User(id, firstname, lastname, email, hashed_password,
                        [telephone], "#")
            dbmanager.insert_user(user)

            flask.flash(
                "Your account has been successfully created! You are now able to login!", "success")
        else:
            # TODO: validate later
            flask.flash("Fields cannot be empty")
            flask.redirect(flask.url_for("account.register"))

        return flask.redirect(flask.url_for("account.login"))

    return flask.render_template("register.html")


def _auth_login() -> bool:
    email = flask.request.form.get("email")
    print(email)
    print(flask.request.form.get("password"))
    if email:
        queried_user = dbmanager.get_user_by_email(email)
        if queried_user and startechlite.bcrypt.check_password_hash(queried_user.password, flask.request.form.get("password")):
            # flask_login.login_user(queried_user)
            print(f"***************User login successful {email}")
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
        return flask.redirect("main.home")

    if flask.request.method == "POST" and _auth_login():
        next_page = flask.request.args.get("next")
        return flask.redirect(next_page) if next_page else flask.redirect(flask.url_for("main.home"))

    return flask.render_template("login.html")
