from flask import render_template, request, jsonify, Blueprint
from StudyApp import db
from StudyApp.models import *
from flask_login import current_user

tools = Blueprint("tools", __name__)

@tools.route("/pomodoro", methods=["GET", "POST"])
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

@tools.route("/kanban", methods=["GET", "POST"])
def kanban():
    return render_template("tools/kanban.html", title="Kanban")


@tools.route("/studyingcicle", methods=["GET", "POST"])
def studyingcicle():
    return render_template("tools/studyingcicle.html", title="Studying Cicle")


@tools.route("/routine", methods=["GET", "POST"])
def routine():
    return render_template("tools/routine.html", title="Routine")