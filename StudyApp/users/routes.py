from flask import render_template, redirect, url_for, flash, request, Blueprint
from StudyApp import db, bcrypt, mail
from StudyApp.users.forms import *
from StudyApp.models import *
from StudyApp.users.utils import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        stat = Stats(owner=user)
        db.session.add(stat)
        db.session.add(user)
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"Account created for {form.username.data}!"}, "success")
        return redirect(url_for("users.login"))
    return render_template("account/register.html", title="Register", form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash({"title": "Congratulations!", "message": "You have been logged in!"}, "success")
            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        else:
            flash({"title": "Login Unsuccssful...", "message": "Please check email and password"}, "error")
    return render_template("account/login.html", title="Login", form=form)

@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("main.index"))
    form = ResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            reset_link = url_for("users.reset_token", token=token, _external=True)
            reset_link = reset_link.encode('utf-8').decode('utf-8')

            msg = Message(
                subject="Reset Password",
                sender="mateusggvega@gmail.com",
                recipients=[user.email]
            )

            msg.body = f"Click the link to reset your password: {reset_link}"
            msg.body = msg.body.encode('utf-8').decode('utf-8')

            msg.charset = "utf-8"

            mail.send(msg)

            flash({"title": "Almost there!", "message": "Check your email for a password reset link."}, "info")
            return redirect(url_for("users.login"))
        else:
            flash({"title": "Unsuccssful...", "message": "Email not found."}, "error")

    return render_template("account/reset_request.html", title="Reset Password", form=form)

@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    email = verify_reset_token(token)
    if email is None:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("users.reset_request"))

    user = User.query.filter_by(email=email).first()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash({"title": "Congratulations!", "message": "Your password has been updated!"}, "success")
        return redirect(url_for("users.login"))

    return render_template("account/reset_password.html", title="Reset Password", form=form)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    flash({"title": "Success", "message": "You have logout successfully!"}, "success")
    return redirect(url_for("main.index"))

@users.route("/account")
@login_required
def account():
    stats = Stats.query.get(current_user.id)
    return render_template("account/account.html", title="Account", stats=stats)

@users.route("/account/update", methods=["GET", "POST"])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.current_password.data and form.new_password.data:
            if bcrypt.check_password_hash(current_user.password, form.current_password.data):
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
                current_user.password = hashed_password
            else:
                flash({"title": "Error!", "message": "The current password is not right!"}, "error")
                return redirect(url_for("users.update_account"))
        current_user.email = form.email.data
        current_user.username = form.username.data
        db.session.commit()
        flash({"title": "Congratulations!", "message": "The account is updated!"}, "success")
        return redirect(url_for("users.account"))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    return render_template("account/update_account.html", title="Update Account", form=form)