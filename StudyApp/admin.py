from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort

admin = Admin()

def is_admin():
    return current_user.is_authenticated and getattr(current_user, "is_admin", False)

class AdminOnlyView(ModelView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class UserView(AdminOnlyView):
    can_delete = False
    can_create = False
    can_edit = True
    column_list = ['id', 'username', 'email', 'date_created', 'is_admin']

class CategoryView(AdminOnlyView):
    can_delete = False
    can_create = True
    can_edit = True
    column_list = ['id', 'name', 'color']

class BlogPostView(AdminOnlyView):
    can_delete = True
    can_create = True
    can_edit = True
    column_list = ['id', 'title', 'subtitle', 'author', 'paragraph', 'category_id', 'image_file']
    form_columns = ['title', 'subtitle', 'author', 'paragraphs', 'category_id', 'image_file']

class BlogPostParagraphView(AdminOnlyView):
    can_delete = True
    can_create = True
    can_edit = True
    column_list = ['id', 'title', 'content', 'blog_post_id']
    form_columns = ['title', 'content', 'blog_post_id']

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        abort(403)

def init_admin(app):
    from StudyApp import db
    from StudyApp.models import User, Category, BlogPost, BlogPostParagraph

    admin.init_app(app, index_view=MyAdminIndexView()) 
    admin.add_view(UserView(User, db.session))
    admin.add_view(CategoryView(Category, db.session))
    admin.add_view(BlogPostView(BlogPost, db.session))
    admin.add_view(BlogPostParagraphView(BlogPostParagraph, db.session))
