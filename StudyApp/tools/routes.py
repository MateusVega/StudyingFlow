from flask import render_template, request, jsonify, Blueprint, flash, session
from StudyApp import db
from StudyApp.models import *
from flask_login import current_user, login_required
import time

tools = Blueprint("tools", __name__)

@tools.route("/pomodoro/", methods=["GET", "POST"])
def pomodoro():
    if request.method == "POST":
        if current_user.is_authenticated:
            session["pomodoro_started_at"] = int(time.time())
            return jsonify({"status": "started"})
        else:
            return jsonify({"status": "unauthenticated"}), 401
    else:
        if not current_user.is_authenticated:
            flash({"title": "Attention", "message": "Sign In to save your stats!"}, "info")
        return render_template("tools/pomodoro.html", title="Pomodoro")

@login_required
@tools.route("/pomodoro_finished/", methods=["POST"])
def pomodoro_finished():
    data = request.get_json()
    mode = data.get("mode")

    server_start_time = session.get("pomodoro_started_at")
    current_time = int(time.time())

    if server_start_time is None:
        return jsonify({"status": "no_session_start"}), 400

    elapsed_time = current_time - server_start_time

    if mode == "focus":
        expected_time = 25 * 60
    elif mode == "breakS":
        expected_time = 5 * 60
    elif mode == "breakL":
        expected_time = 15 * 60
    else:
        return jsonify({"status": "no_valid_mode"}), 400

    if abs(elapsed_time - expected_time) <= 10:
        stats = Stats.query.get(current_user.id)
        if mode == "breakS" or mode == "breakL":
            stats.pomodoro_breaks += expected_time / 60
        elif mode == "focus":
            stats.pomodoro_focus += expected_time / 60
        db.session.commit()
        return jsonify({"status": "success"})
    else:
        return jsonify({
            "status": "rejected",
            "reason": "Time mismatch",
            "elapsed": elapsed_time,
            "expected": expected_time
        }), 400

@tools.route("/kanban/", methods=["GET"])
def kanban_home():
    if current_user.is_authenticated:
        boards = KanbanBoard.query.filter_by(user_id=current_user.id).all()
        return render_template("tools/kanban_home.html", boards=boards, title="Kanban")
    else:
        flash({"title": "Attention", "message": "Sign In to save your Kanban!"}, "info")
        return render_template("tools/kanban_board.html", title="Kanban")

@tools.route("/kanban/new/", methods=["POST"])
@login_required
def new_board():
    data = request.get_json()
    board = KanbanBoard(title=data['name'], user_id=current_user.id)
    db.session.add(board)
    db.session.commit()
    return jsonify({"id": board.id, "name": board.title}), 201

@tools.route("/kanban/<string:board_id>/delete/", methods=["DELETE"])
@login_required
def delete_board(board_id):
    board = KanbanBoard.query.filter_by(id=board_id, user_id=current_user.id).first_or_404()
    if not board:
        return jsonify({"error": "Board not found"}), 404
    
    db.session.delete(board)
    db.session.commit()
    return jsonify({"message": "Board deleted"}), 200

@tools.route("/kanban/<string:board_id>/", methods=["GET"])
@login_required
def board_detail(board_id):
    board = KanbanBoard.query.filter_by(id=board_id, user_id=current_user.id).first_or_404()

    todo_tasks = KanbanTask.query.filter_by(board_id=board_id, status="todo").all()
    doing_tasks = KanbanTask.query.filter_by(board_id=board_id, status="doing").all()
    done_tasks = KanbanTask.query.filter_by(board_id=board_id, status="done").all()

    if not board:
        return "Not found", 404
    return render_template("tools/kanban_board.html", board=board, board_id=board_id, todo_tasks=todo_tasks, doing_tasks=doing_tasks, done_tasks=done_tasks)

@tools.route("/kanban/<string:board_id>/clear_tasks/", methods=["POST"])
@login_required
def clear_tasks(board_id):
    tasks = KanbanTask.query.filter_by(board_id=board_id).all()
    if tasks:
        for task in tasks:
            db.session.delete(task)
        db.session.commit()
        return jsonify({"status": "success", "message": "Tasks cleared."})
    else:
        return jsonify({"status": "error", "message": "No tasks to clean."})

@tools.route("/kanban/<string:board_id>/add_tasks/", methods=["POST"])
@login_required
def add_tasks(board_id):
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

@tools.route("/studyingcicle/", methods=["GET"])
def studyingcicle():
    return render_template("tools/studyingcicle.html", title="Studying Cicle")

@tools.route("/schedule/", methods=["GET"])
def schedule():
    return render_template("tools/schedule.html", title="Schedule")

@tools.route("/gpacalculator/", methods=["GET"])
def gpacalculator():
    return render_template("tools/gpacalculator.html", title="GPA Calculator")

@tools.route("/whiteboard/", methods=["GET"])
def whiteboard():
    return render_template("tools/whiteboard.html", title="Whiteboard - Excalidraw")