from flask import render_template, Blueprint, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from StudyApp.forms import *
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

@community.route("/blog/post/<string:blog_title>", methods=["GET", "POST"])
def blog_post(blog_title):
    blog = BlogPost.query.filter_by(title=blog_title).first()
    paragraphs = BlogPostParagraph.query.filter_by(blog_post_id=blog.id)
    return render_template("community/blog_post.html", title=f"{blog.title}", blog=blog, paragraphs=paragraphs)

@login_required
@community.route("/blog/create_post", methods=["GET", "POST"])
def create_blog():
    if not current_user.is_authenticated or not User.query.filter_by(id=current_user.id).first().is_admin:
        abort(403)
    form = NewBlogPostForm()
    categories = Category.query.all()
    if form.validate_on_submit():
        flash({"title": "Congratulations!", "message": f"Blog Post Created!"}, "success")
        return redirect(url_for('main.index'))
    return render_template("community/create_blog.html", title="Blog Creator", form=form, categories=categories)

@community.route("/forum", methods=["GET", "POST"])
def forum():
    return render_template("community/forum.html", title="Forum")
