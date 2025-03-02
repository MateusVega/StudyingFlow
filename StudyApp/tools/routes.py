from flask import render_template, request, jsonify, Blueprint
from StudyApp import db
from StudyApp.models import *
from flask_login import current_user, login_required

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

@tools.route("/kanban", methods=["GET"])
@login_required
def kanban_home():
    boards = KanbanBoard.query.filter_by(user_id=current_user.id).all()
    return render_template("tools/kanban_home.html", boards=boards)

@tools.route("/kanban/new", methods=["POST"])
@login_required
def new_board():
    print("FOI!")
    data = request.get_json()
    board = KanbanBoard(title=data['name'], user_id=current_user.id)
    db.session.add(board)
    db.session.commit()
    return jsonify({"id": board.id, "name": board.title}), 201

@tools.route("/kanban/<string:board_id>/delete", methods=["POST", "DELETE"])
@login_required
def delete_board(board_id):
    board = KanbanBoard.query.filter_by(id=board_id, user_id=current_user.id).first()
    if not board:
        return jsonify({"error": "Board not found"}), 404
    
    db.session.delete(board)
    db.session.commit()
    return jsonify({"message": "Board deleted"}), 200

@tools.route("/kanban/<string:board_id>", methods=["GET"])
@login_required
def board_detail(board_id):
    board = KanbanBoard.query.filter_by(id=board_id, user_id=current_user.id).first()
    if not board:
        return "Not found", 404
    return render_template("tools/kanban_board.html", board=board)


@tools.route("/studyingcicle", methods=["GET", "POST"])
def studyingcicle():
    return render_template("tools/studyingcicle.html", title="Studying Cicle")


@tools.route("/routine", methods=["GET", "POST"])
def routine():
    return render_template("tools/routine.html", title="Routine")