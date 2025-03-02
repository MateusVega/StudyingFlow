from flask import render_template, redirect, url_for, flash, request, jsonify
from StudyApp import app, db, bcrypt, mail
from StudyApp.forms import *
from StudyApp.models import *
from StudyApp.utils import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
def index():
    return render_template("index.html")

# Contas

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        stat = Stats(owner=user)
        db.session.add(stat)
        db.session.add(user)
        db.session.commit()
        flash({"title": "Congratulations!", "message": f"Account created for {form.username.data}!"}, "success")
        return redirect(url_for("login"))
    return render_template("account/register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash({"title": "Congratulations!", "message": "You have been logged in!"}, "success")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash({"title": "Login Unsuccssful...", "message": "Please check email and password"}, "error")
    return render_template("account/login.html", title="Login", form=form)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("index"))
    form = ResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            reset_link = url_for("reset_token", token=token, _external=True)
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
            return redirect(url_for("login"))
        else:
            flash({"title": "Unsuccssful...", "message": "Email not found."}, "error")

    return render_template("account/reset_request.html", title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        flash({"title": "Authenticated!", "message": "You are already logged in!"}, "info")
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    email = verify_reset_token(token)
    if email is None:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("reset_request"))

    user = User.query.filter_by(email=email).first()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash({"title": "Congratulations!", "message": "Your password has been updated!"}, "success")
        return redirect(url_for("login"))

    return render_template("account/reset_password.html", title="Reset Password", form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash({"title": "Success", "message": "You have logout successfully!"}, "success")
    return redirect(url_for("index"))

@app.route("/account")
@login_required
def account():
    stats = Stats.query.get(current_user.id)
    return render_template("account/account.html", title="Account", stats=stats)

@app.route("/account/update", methods=["GET", "POST"])
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
                return redirect(url_for("update_account"))
        current_user.email = form.email.data
        current_user.username = form.username.data
        db.session.commit()
        flash({"title": "Congratulations!", "message": "The account is updated!"}, "success")
        return redirect(url_for("account"))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    return render_template("account/update_account.html", title="Update Account", form=form)

# Community

@app.route("/blog", methods=["GET", "POST"])
def blog():
    return render_template("community/blog.html", title="Blog")

@app.route("/forum", methods=["GET", "POST"])
def forum():
    return render_template("community/forum.html", title="Forum")

# Tools

@app.route("/pomodoro", methods=["GET", "POST"])
def pomodoro():
    if request.method == "POST":
        response = request.get_json()
        time = response.get("time")
        mode = response.get("mode")

        stats = Stats.query.get(current_user.id)
        if mode: # is break time
            stats.pomodoro_breaks += time
        else: # is focus time
            stats.pomodoro_focus += time
        db.session.commit()
        return jsonify({"status": "success", "time": time})
    else:
        return render_template("tools/pomodoro.html", title="Pomodoro")

@app.route("/kanban", methods=["GET", "POST"])
def kanban():
    return render_template("tools/kanban.html", title="Kanban")


@app.route("/studyingcicle", methods=["GET", "POST"])
def studyingcicle():
    return render_template("tools/studyingcicle.html", title="Studying Cicle")


@app.route("/routine", methods=["GET", "POST"])
def routine():
    return render_template("tools/routine.html", title="Routine")

# Errors

@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500