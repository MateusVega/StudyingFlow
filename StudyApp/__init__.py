from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from StudyApp.config import Config

admin = Admin()
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = {"title": "You need a account!", "message": "Please log in to your account"}
login_manager.login_message_category = "info"

class UserView(ModelView):
    can_delete = False
    can_create = False
    can_edit = True
    column_list = ['id', 'username', 'email', 'date_created']

class CategoryView(ModelView):
    can_delete = False
    can_create = True
    can_edit = True
    column_list = ['id', 'name', 'color']

class BlogPostView(ModelView):
    can_delete = False
    can_create = True
    can_edit = True
    column_list = ['id', 'title', 'category_id', 'image_file']
    form_columns = ['title', 'content', 'category_id', 'image_file']

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    admin.init_app(app)
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

    from StudyApp.models import User, Category, BlogPost
    
    admin.add_view(UserView(User, db.session))
    admin.add_view(CategoryView(Category, db.session))
    admin.add_view(BlogPostView(BlogPost, db.session))

    return app