import flask
import flask_login
from startechlite.account.model import User
from startechlite.dbmanager.dbmanager import DBManager

dbman = DBManager()

admin = flask.Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/users")
def get_users():
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        flask.redirect(flask.url_for("main.home"))

    page = int(flask.request.args.get("page", default=1))

    users, pagination = dbman.get_user_list(page)

    return flask.render_template("admin_users.html", users=users, pagination=pagination)


@admin.route("/edituser/<int:userid>", methods=["GET", "POST"])
def edit_user(userid):
    if not flask_login.current_user.is_admin:  # type: ignore
        flask.flash("You don't have sufficient privileges", "warning")
        flask.redirect(flask.url_for("main.home"))

    if flask.request.method == "POST":
        if flask.request.form.get("action") == "Update":
            id, first_name, last_name, email, phone_number, address, _ = flask.request.form.values()
            dbman.update_user(
                User(int(id), first_name, last_name, email, "", phone_number, address))
        elif flask.request.form.get("action") == "Delete":
            id = flask.request.form.get("id")
            assert id
            dbman.delete_user(int(id))

        return flask.redirect(flask.url_for("admin.get_users"))

    user = dbman.get_user_by_id(userid)
    return flask.render_template("admin_edit_user.html", user=user)
