from flask import render_template, Blueprint

community = Blueprint("community", __name__)

@community.route("/blog", methods=["GET", "POST"])
def blog():
    return render_template("community/blog.html", title="Blog")

@community.route("/forum", methods=["GET", "POST"])
def forum():
    return render_template("community/forum.html", title="Forum")
