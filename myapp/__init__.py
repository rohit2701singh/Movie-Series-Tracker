from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from myapp.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.login"    # blueprint prefix!
login_manager.login_message = "You must be logged in to continue."
login_manager.login_message_category = "warning"


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # register blueprint
    from .routes import main
    app.register_blueprint(main)

    # Create tables within app context
    with app.app_context():
        db.create_all()

    return app