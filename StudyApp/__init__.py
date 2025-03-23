from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from StudyApp.config import Config
from StudyApp.admin import init_admin

db = SQLAlchemy()
bcrypt = Bcrypt()
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

    init_admin(app)

    register_commands(app)

    return app

def register_commands(app):
    import click
    from flask.cli import with_appcontext
    from StudyApp.models import User

    @click.command("add-admin")
    @click.argument("email")
    @click.argument("id")
    @with_appcontext
    def add_admin(email, id):
        user = User.query.filter_by(email=email, id=id).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"{email} is now an admin.")
        else:
            print("User not found.")

    app.cli.add_command(add_admin)