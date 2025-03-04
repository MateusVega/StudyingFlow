from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from StudyApp.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = {"title": "You need a account!", "message": "Please log in to your account"}
login_manager.login_message_category = "info"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    migrate = Migrate(app, db)

    from StudyApp.users.routes import users
    from StudyApp.main.routes import main
    from StudyApp.errors.routes import errors
    from StudyApp.tools.routes import tools
    from StudyApp.community.routes import community
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(tools)
    app.register_blueprint(community)

    return app