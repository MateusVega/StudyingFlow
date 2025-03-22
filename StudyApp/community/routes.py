from flask import render_template, Blueprint
from StudyApp.models import *

community = Blueprint("community", __name__)

@community.route("/blog", methods=["GET", "POST"])
def blog():
    categories = Category.query.all()
    blogs = BlogPost.query.all()
    return render_template("community/blog.html", title="Blog", categories=categories, blogs=blogs)

@community.route("/blog/<string:category>", methods=["GET", "POST"])
def blog_category(category):
    categories = Category.query.all()
    category_id = Category.query.filter_by(name=category).first().id
    blogs = BlogPost.query.filter_by(category_id=category_id).all()
    return render_template("community/blog.html", title="Blog", categories=categories, blogs=blogs)

@community.route("/forum", methods=["GET", "POST"])
def forum():
    return render_template("community/forum.html", title="Forum")
