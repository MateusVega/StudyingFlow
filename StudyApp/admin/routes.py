from flask import render_template, Blueprint, abort, redirect, url_for, flash, request
from StudyApp import bcrypt
from StudyApp.models import *
from StudyApp.admin.forms import *
from StudyApp.utils import save_blog_picture
import os
import json

admin = Blueprint("admin", __name__)

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static/data', 'exercises.json')

def verify_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)
    else:
        return True

@admin.route("/static/data/<string:filename>")
def protect_static_files(filename):
    if filename in ["exercises.json"]:
        verify_admin()
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return data
    else:
        abort(403)

@admin.route("/admin/")
def admin_panel():
    verify_admin()
    return render_template("admin/index.html")

@admin.route("/admin/users/")
def users():
    verify_admin()
    users = User.query.all()
    stats = Stats.query.all()
    users_stats = zip(users, stats)
    return render_template("admin/users/users.html", users_stats=users_stats)

@admin.route("/admin/users/delete/<int:user_id>", methods=["GET"])
def users_delete(user_id):
    verify_admin()
    username = User.query.filter_by(id=user_id).first_or_404().username
    User.query.filter_by(id=user_id).delete()
    Stats.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    flash({"title": "Congratulations!", "message": f"{username} deleted!"}, "success")
    return redirect(url_for("admin.users"))

@admin.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
def users_edit(user_id):
    verify_admin()
    user = User.query.filter_by(id=user_id).first_or_404()
    form = UpdateUserForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"{form.username.data} edited!"}, "success")
        return redirect(url_for("admin.users"))
    else:
        form.id.data = user.id
        form.email.data = user.email
        form.username.data = user.username
        form.is_admin.data = user.is_admin
    return render_template("admin/users/users_edit.html", form=form)

@admin.route("/admin/users/add/", methods=["GET", "POST"])
def users_add():
    verify_admin()
    form = NewUserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit() 
        
        stat = Stats(owner=user)
        db.session.add(stat)
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"Account created for {form.username.data}!"}, "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/users/users_add.html", form=form)

# CATEGORIES

@admin.route("/admin/category/")
def categories():
    verify_admin()
    categories = Category.query.all()
    return render_template("admin/categories/categories.html", categories=categories)

@admin.route("/admin/categories/delete/<int:category_id>", methods=["GET"])
def categories_delete(category_id):
    verify_admin()
    name = Category.query.filter_by(id=category_id).first_or_404().name
    Category.query.filter_by(id=category_id).delete()
    db.session.commit()
    flash({"title": "Congratulations!", "message": f"{name} deleted!"}, "success")
    return redirect(url_for("admin.categories"))

@admin.route("/admin/categories/edit/<int:category_id>", methods=["GET", "POST"])
def categories_edit(category_id):
    verify_admin()

    category = Category.query.get_or_404(category_id)
    form = UpdateCategoryForm(category=category)

    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"{form.name.data} edited!"}, "success")
        return redirect(url_for("admin.categories"))
    else:
        form.name.data = category.name

    return render_template("admin/categories/categories_edit.html", form=form)

@admin.route("/admin/categories/add/", methods=["GET", "POST"])
def categories_add():
    verify_admin()
    form = NewCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"{form.name.data} created!"}, "success")
        return redirect(url_for("admin.categories"))
    return render_template("admin/categories/categories_add.html", form=form)

# BLOG POSTS

@admin.route("/admin/blog_post/")
def blog_post():
    verify_admin()
    blog_post = BlogPost.query.all()
    paragraphs = BlogPostParagraph.query.all()
    return render_template("admin/blog_post/blog_post.html", blog_post=blog_post, Category=Category, paragraphs=paragraphs)

@admin.route("/admin/blog_post/delete/<int:blog_post_id>", methods=["GET"])
def blog_post_delete(blog_post_id):
    verify_admin()
    blog =  BlogPost.query.filter_by(id=blog_post_id).first_or_404()
    title = blog.title
    id = blog.id
    for p in BlogPostParagraph.query.filter_by(blog_post_id=id).all():
        db.session.delete(p)

    with open(file_path, 'r') as json_file:
        exercise = json.load(json_file)

    for e in exercise:
        if e["blog_post_id"] == id:
            exercise.remove(e)

    with open(file_path, 'w') as json_file:
        json.dump(exercise, json_file, indent=4)

    BlogPost.query.filter_by(id=blog_post_id).delete()
    db.session.commit()
    flash({"title": "Congratulations!", "message": f"{title} deleted!"}, "success")
    return redirect(url_for("admin.blog_post"))

@admin.route("/admin/blog_post/edit/<int:blog_post_id>", methods=["GET", "POST"])
def blog_post_edit(blog_post_id):
    verify_admin()
    post = BlogPost.query.filter_by(id=blog_post_id).first_or_404()
    form = UpdateBlogPostForm(blog_post=post)

    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.category_id = form.category.data
        if form.picture.data:
            post.image_file = save_blog_picture(form.picture.data)
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"{form.title.data} edited!"}, "success")
        return redirect(url_for("admin.blog_post"))
    else:
        form.id.data = post.id
        form.title.data = post.title
        form.subtitle.data = post.subtitle
        form.category.data = post.category_id

    return render_template("admin/blog_post/blog_post_edit.html", form=form)

# PARAGRAPHS

@admin.route("/admin/paragraphs/delete/<int:paragraph_id>", methods=["GET"])
def paragraphs_delete(paragraph_id):
    verify_admin()
    BlogPostParagraph.query.filter_by(id=paragraph_id).delete()
    db.session.commit()
    return redirect(url_for('admin.blog_post'))

@admin.route("/admin/paragraph/edit/<int:paragraph_id>", methods=["GET", "POST"])
def paragraphs_edit(paragraph_id):
    verify_admin()
    paragraph = BlogPostParagraph.query.filter_by(id=paragraph_id).first_or_404()
    form = UpdateParagraphForm()
    if form.validate_on_submit():
        paragraph.title = form.title.data
        paragraph.content = form.content.data
        db.session.commit()
        return redirect(url_for("admin.blog_post"))
    else:
        form.id.data = paragraph_id
        form.title.data = paragraph.title
        form.content.data = paragraph.content
    return render_template("admin/paragraph/paragraph_edit.html", form=form)

@admin.route("/admin/paragraph/add/<int:blog_post_id>", methods=["GET", "POST"])
def paragraphs_add(blog_post_id):
    verify_admin()
    form = NewParagraphForm()

    if form.validate_on_submit():
        paragraph = BlogPostParagraph(title=form.title.data, content=form.content.data, blog_post_id=blog_post_id)
        db.session.add(paragraph)
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"{form.title.data} added!"}, "success")
        return redirect(url_for("admin.blog_post"))

    return render_template("admin/paragraph/paragraph_add.html", form=form)

@admin.route("/admin/exercises/", methods=["GET", "POST"])
def exercises():
    verify_admin()
    if request.method == "POST":
        modified_exercises = request.form["exercises"]
        with open(file_path, 'w') as json_file:
            json.dump(json.loads(modified_exercises), json_file, indent=4)
        return redirect(url_for('admin.exercises'))
    else:
        with open(file_path, 'r') as json_file:
            exercises = json.load(json_file)
        formatted_exercises = json.dumps(exercises, indent=4)
        return render_template("admin/exercises/exercises.html", exercises=formatted_exercises)
