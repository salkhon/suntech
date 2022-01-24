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


@account.route("/account")
@flask_breadcrumbs.register_breadcrumb(account, ".account", "Account")
def user_account():
    # have to check if logged in, otherwise redirects to login page
    if flask_login.current_user.is_authenticated:  # type: ignore
        # TODO: render user profile page
        pass
    return flask.redirect(flask.url_for("account.login"))


def get_validated_registered_user() -> User | None:
    firstname = flask.request.form.get("firstname")
    lastname = flask.request.form.get("lastname")
    email = flask.request.form.get("email")
    password = flask.request.form.get("password")
    telephone = flask.request.form.get("telephone")
    id = random.randint(100000, 999999)

    if not (firstname and lastname and email and telephone and password):
        return None

    if dbmanager.get_user_by_email(email):
        return None

    return User(id, firstname, lastname, email, startechlite.bcrypt.generate_password_hash(password).decode("utf-8"), telephone, "")


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

        dbmanager.insert_user(validated_user)

        flask.flash(
            "Your account has been successfully created! You are now able to login!", "success")

        return flask.redirect(flask.url_for("account.login"))

    return flask.render_template("register.html")


def _auth_login() -> bool:
    email = flask.request.form.get("email")
    if email:
        queried_user = dbmanager.get_user_by_email(email)
        print(queried_user)
        if queried_user and startechlite.bcrypt.check_password_hash(queried_user.password, flask.request.form.get("password")):
            flask.flash(f"Welcome {queried_user.first_name}!")
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
        return flask.redirect(next_page) if next_page else flask.redirect(flask.url_for("main.home"))

    return flask.render_template("login.html")


@account.route("/logout")
def logout() -> str | Response:
    flask_login.logout_user()
    return flask.redirect(flask.url_for("main.home"))
