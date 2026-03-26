from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ListeningExercise, UserListeningProgress
from datetime import datetime

listening_bp = Blueprint("listening", __name__, url_prefix="/listening")


@listening_bp.route("/")
@login_required
def index():
    # 获取URL参数
    difficulty = request.args.get("difficulty", type=int)
    category = request.args.get("category", type=str)  
    accent = request.args.get("accent", type=str)  # 新增：获取accent参数

    # 构建查询
    query = ListeningExercise.query

    # 如果选择了难度 → 过滤
    if difficulty is not None:
        query = query.filter(ListeningExercise.difficulty == difficulty)
    # 分类过滤
    if category:
        query = query.filter(ListeningExercise.category == category)
    # 口音过滤
    if accent:
        query = query.filter(ListeningExercise.accent == accent)  # 新增：根据accent过滤

    # 排序 + 查询
    exercises = query.order_by(ListeningExercise.difficulty).all()

    # 传递给前端（包含当前用户ID + 当前accent）
    return render_template(
        "listening/index.html",
        exercises=exercises,
        current_difficulty=difficulty,
        current_category=category,
        current_accent=accent,  # 新增：传递当前accent
        user_id=current_user.id
    )


@listening_bp.route("/progress", methods=["POST"])
@login_required
def save_progress():
    data = request.get_json()
    exercise_id = data.get("exercise_id")
    last_position = data.get("last_position")
    answers = data.get("answers")
    two_thirds_reached = data.get("two_thirds_reached", False)
    completed = data.get("completed", False)
    score = data.get("score")
    reset = data.get("reset", False)

    if not exercise_id:
        return jsonify({"error": "exercise_id required"}), 400

    exercise = ListeningExercise.query.get(exercise_id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    if not progress:
        progress = UserListeningProgress(
            user_id=current_user.id, exercise_id=exercise_id
        )
        db.session.add(progress)

    if reset:
        progress.last_position = 0
        progress.answers = {}
    else:
        if last_position is not None:
            if progress.last_position is None or last_position > progress.last_position:
                progress.last_position = last_position

        if answers is not None:
            if not answers:
                progress.answers = {}
            else:
                if progress.answers is None:
                    progress.answers = answers
                else:
                    merged = {**progress.answers, **answers}
                    progress.answers = merged

        if two_thirds_reached:
            progress.two_thirds_count = (progress.two_thirds_count or 0) + 1

        if completed:
            progress.completed = True
            if score is not None:
                progress.score = score

    progress.last_attempt_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"success": True})


@listening_bp.route("/progress/<int:exercise_id>", methods=["GET"])
@login_required
def get_progress(exercise_id):
    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    if not progress:
        return jsonify({"exists": False})
    return jsonify(
        {
            "exists": True,
            "last_position": progress.last_position,
            "two_thirds_count": progress.two_thirds_count,
            "answers": progress.answers,
            "completed": progress.completed,
            "score": progress.score,
            "last_attempt_at": (
                progress.last_attempt_at.isoformat()
                if progress.last_attempt_at
                else None
            ),
        }
    )