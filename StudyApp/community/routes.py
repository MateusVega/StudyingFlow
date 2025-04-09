from flask import render_template, Blueprint, abort, redirect, url_for, flash, request
from flask_login import login_required, current_user
from StudyApp.forms import *
from StudyApp.models import *
from StudyApp.utils import save_blog_picture

community = Blueprint("community", __name__)

@community.route("/blog/", methods=["GET", "POST"])
def blog():
    categories = Category.query.all()
    blogs = BlogPost.query.all()
    return render_template("community/blog.html", title="Blog", categories=categories, blogs=blogs)

@community.route("/blog/<string:category>/", methods=["GET", "POST"])
def blog_category(category):
    categories = Category.query.all()
    category_id = Category.query.filter_by(name=category).first_or_404().id
    blogs = BlogPost.query.filter_by(category_id=category_id).all()
    return render_template("community/blog.html", title="Blog", categories=categories, blogs=blogs)

@community.route("/blog/post/<string:blog_title>/", methods=["GET", "POST"])
def blog_post(blog_title):
    blog = BlogPost.query.filter_by(title=blog_title).first_or_404()
    paragraphs = BlogPostParagraph.query.filter_by(blog_post_id=blog.id)
    return render_template("community/blog_post.html", title=f"{blog.title}", blog=blog, paragraphs=paragraphs)

@login_required
@community.route("/blog/create_post/", methods=["GET", "POST"])
def create_blog():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)
    form = NewBlogPostForm()
    categories = Category.query.all()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_blog_picture(form.picture.data)
        category = Category.query.filter_by(name=form.category.data).first_or_404().id
        print(category)
        author = current_user.username
        blog_post = BlogPost(title=form.title.data, subtitle=form.subtitle.data, author=author, image_file=picture_file, category_id=category)
        db.session.add(blog_post)
        db.session.commit()
        
        first_paragraph = BlogPostParagraph(title=form.title_paragraph.data, content=form.paragraph.data, blog_post_id=blog_post.id)
        db.session.add(first_paragraph)

        titles = request.form.getlist('title[]')
        paragraphs = request.form.getlist('paragraph[]')
        
        for t, p in zip(titles, paragraphs):
            db.session.add(BlogPostParagraph(title=t, content=p, blog_post_id=blog_post.id))
        
        db.session.commit()

        flash({"title": "Congratulations!", "message": f"Blog Post Created!"}, "success")
        return redirect(url_for('main.index'))
    return render_template("community/create_blog.html", title="Blog Creator", form=form, categories=categories)

@community.route("/forum/", methods=["GET", "POST"])
def forum():
    return render_template("community/forum.html", title="Forum")
