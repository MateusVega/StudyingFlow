from flask import render_template, Blueprint, abort, redirect, url_for, flash
from StudyApp import bcrypt
from StudyApp.models import *
from StudyApp.admin.forms import *

admin = Blueprint("admin", __name__)

@admin.route("/admin/")
def admin_panel():
    Stats.query.filter_by(user_id=2).delete()
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)
    return render_template("admin/index.html", title="Admin")

@admin.route("/admin/users/")
def users():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template("admin/users.html", title="Admin", users=users)

@admin.route("/admin/users/delete/<int:user_id>", methods=["GET", "POST"])
def users_delete(user_id):
    username = User.query.filter_by(id=user_id).first().username
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    flash({"title": "Congratulations!", "message": f"{username} deleted!"}, "success")
    return redirect(url_for("admin.users"))

@admin.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
def users_edit(user_id):
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
    return render_template("admin/users_edit.html", title="Admin", form=form)

@admin.route("/admin/users/add/", methods=["GET", "POST"])
def users_add():
    form = NewUserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=form.is_admin.data)
        stat = Stats(owner=user)
        db.session.add(stat)
        db.session.commit()
        print(user.id)
        flash({"title": "Congratulations!", "message": f"Account created for {form.username.data}!"}, "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/users_add.html", title="Admin", form=form)