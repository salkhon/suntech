from flask import Flask
import flask_bcrypt
import flask_login
from startechlite.config import Config
import flask_breadcrumbs

bcrypt = flask_bcrypt.Bcrypt()

login_manager = flask_login.LoginManager()
login_manager.login_view = "account.login"  # type: ignore
login_manager.login_message_category = "info"

breadcrumbs = flask_breadcrumbs.Breadcrumbs()


def create_app(config_cls=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_cls)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    breadcrumbs.init_app(app)

    from startechlite.main.routes import main
    from startechlite.productslist.routes import productslist
    from startechlite.product.routes import product
    from startechlite.account.routes import account
    from startechlite.sales.routes import sales
    from startechlite.admin.routes import admin

    app.register_blueprint(main)
    app.register_blueprint(productslist)
    app.register_blueprint(product)
    app.register_blueprint(account)
    app.register_blueprint(sales)
    app.register_blueprint(admin)

    return app
