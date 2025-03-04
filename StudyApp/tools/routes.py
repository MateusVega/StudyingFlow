from flask import render_template, request, jsonify, Blueprint, abort
from StudyApp import db
from StudyApp.models import *
from flask_login import current_user, login_required

tools = Blueprint("tools", __name__)

@tools.route("/pomodoro", methods=["GET", "POST"])
def pomodoro():
    if request.method == "POST":
        referer = request.headers.get("Referer")
        if not referer or "studyingflow.com" not in referer:
            abort(403, "Invalid request source")

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
    referer = request.headers.get("Referer")
    if not referer or "studyingflow.com" not in referer:
        abort(403, "Invalid request source")
    data = request.get_json()
    board = KanbanBoard(title=data['name'], user_id=current_user.id)
    db.session.add(board)
    db.session.commit()
    return jsonify({"id": board.id, "name": board.title}), 201

@tools.route("/kanban/<string:board_id>/delete", methods=["POST", "DELETE"])
@login_required
def delete_board(board_id):
    referer = request.headers.get("Referer")
    if not referer or "studyingflow.com" not in referer:
        abort(403, "Invalid request source")
    
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

    todo_tasks = KanbanTask.query.filter_by(board_id=board_id, status="todo").all()
    doing_tasks = KanbanTask.query.filter_by(board_id=board_id, status="doing").all()
    done_tasks = KanbanTask.query.filter_by(board_id=board_id, status="done").all()

    if not board:
        return "Not found", 404
    return render_template("tools/kanban_board.html", board=board, board_id=board_id, todo_tasks=todo_tasks, doing_tasks=doing_tasks, done_tasks=done_tasks)

@tools.route("/kanban/<string:board_id>/clear_tasks", methods=["POST"])
@login_required
def clear_tasks(board_id):
    referer = request.headers.get("Referer")
    if not referer or "studyingflow.com" not in referer:
        abort(403, "Invalid request source")

    tasks = KanbanTask.query.filter_by(board_id=board_id).all()
    if tasks:
        for task in tasks:
            db.session.delete(task)
        db.session.commit()
        return jsonify({"status": "success", "message": "Tasks cleared."})
    else:
        return jsonify({"status": "error", "message": "No tasks to clean."})

@tools.route("/kanban/<string:board_id>/add_tasks", methods=["POST"])
@login_required
def add_tasks(board_id):
    referer = request.headers.get("Referer")
    if not referer or "studyingflow.com" not in referer:
        abort(403, "Invalid request source")

    try:
        data = request.get_json()

        status = data.get('status')
        title = data.get('title')

        task = KanbanTask(board_id=board_id, title=title, status=status)
        db.session.add(task)
        db.session.commit()
        return jsonify({"status": "success", "message": "Task added with success"})
    except Exception as Error:
        return jsonify({"status": "error", "message": f"{Error}"})

@tools.route("/studyingcicle", methods=["GET", "POST"])
def studyingcicle():
    return render_template("tools/studyingcicle.html", title="Studying Cicle")


@tools.route("/routine", methods=["GET", "POST"])
def routine():
    return render_template("tools/routine.html", title="Routine")