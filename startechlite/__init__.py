from flask import Flask
import flask_bcrypt
import flask_login
import flask_mail
from startechlite.config import Config

bcrypt = flask_bcrypt.Bcrypt()

# login_manager = flask_login.LoginManager()
# has to implement user_loader method, UserMixin methods

mail = flask_mail.Mail()

def create_app(config_cls=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_cls)

    bcrypt.init_app(app)
    # login_manager.init_app(app)
    mail.init_app(app)

    from startechlite.main.routes import main

    app.register_blueprint(main)

    return app
