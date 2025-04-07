from datetime import datetime
from StudyApp import db, login_manager
from flask_login import UserMixin
import uuid

def generate_uuid():
    return str(uuid.uuid4())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    stats = db.relationship('Stats', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class Stats(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    pomodoro_focus = db.Column(db.Integer, default=0)
    pomodoro_breaks = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class KanbanBoard(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    tasks = db.relationship('KanbanTask', backref='board', lazy=True, cascade='all, delete-orphan')

class KanbanTask(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(10), nullable=False, default="todo")
    board_id = db.Column(db.String(36), db.ForeignKey('kanban_board.id'), nullable=False)

    def __repr__(self):
        return f"KanbanTask('{self.title}', Status: '{self.status}', Board: '{self.board_id}')"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    posts = db.relationship("BlogPost", backref="category", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Category('{self.name}')"

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    subtitle = db.Column(db.String(300), nullable=True)
    author = db.Column(db.String(40), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    image_file = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    paragraphs = db.relationship("BlogPostParagraph", backref="blog_post", lazy=True, cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"BlogPost('{self.title}', ID: {self.id})"
    
class BlogPostParagraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    blog_post_id = db.Column(db.Integer, db.ForeignKey("blog_post.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"Paragraph('{self.content[:30]}...', ID: {self.id})"
