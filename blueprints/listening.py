from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ListeningExercise, UserListeningProgress
from datetime import datetime
from time_utils import utcnow_naive
from sqlalchemy.orm.attributes import flag_modified

listening_bp = Blueprint("listening", __name__, url_prefix="/listening")


def _migrate_question_correct_times(progress):
    """
    数据迁移：确保 question_correct_times 是
    { 题目序号: { 日期: 时间戳 }, ... }
    永远保留所有日期，不删除历史！
    """
    if not isinstance(progress.question_correct_times, dict):
        progress.question_correct_times = {}
        flag_modified(progress, "question_correct_times")
        return

    new_qct = {}
    for q_idx, data in progress.question_correct_times.items():
        # 题目序号转字符串（统一格式）
        key = str(q_idx)
        if key not in new_qct:
            new_qct[key] = {}

        if isinstance(data, dict):
            # 直接合并，保留所有旧日期
            for date_str, ts in data.items():
                new_qct[key][date_str] = ts

        elif isinstance(data, list):
            # 旧数组格式 → 转字典
            for ts in data:
                date_str = ts[:10]
                new_qct[key][date_str] = ts

    progress.question_correct_times = new_qct
    flag_modified(progress, "question_correct_times")


@listening_bp.route("/")
@login_required
def index():
    difficulty = request.args.get("difficulty", type=int)
    category = request.args.get("category", type=str)
    accent = request.args.get("accent", type=str)

    query = ListeningExercise.query
    if difficulty is not None:
        query = query.filter(ListeningExercise.difficulty == difficulty)
    if category:
        query = query.filter(ListeningExercise.category == category)
    if accent:
        query = query.filter(ListeningExercise.accent == accent)

    exercises = query.order_by(ListeningExercise.difficulty).all()
    return render_template(
        "listening/index.html",
        exercises=exercises,
        current_difficulty=difficulty,
        current_category=category,
        current_accent=accent,
        user_id=current_user.id
    )


@listening_bp.route("/practice/<int:exercise_id>")
@login_required
def practice(exercise_id):
    exercise = ListeningExercise.query.get_or_404(exercise_id)
    return render_template("listening/practice.html", exercise=exercise)


@listening_bp.route("/api/practice/<int:exercise_id>")
@login_required
def get_practice_data(exercise_id):
    exercise = ListeningExercise.query.get_or_404(exercise_id)
    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()

    if progress:
        _migrate_question_correct_times(progress)
        db.session.commit()

    return jsonify({
        "exercise": {
            "id": exercise.id,
            "title": exercise.title,
            "audio_url": exercise.audio_url,
            "subtitle_url": exercise.subtitle_url,
            "questions": exercise.questions or [],
            "key_vocab": exercise.key_vocab or [],
            "duration_seconds": exercise.duration_seconds,
            "transcript": exercise.transcript,
        },
        "progress": {
            "exists": progress is not None,
            "last_position": progress.last_position if progress else 0,
            "answers": progress.answers if progress else {},
            "completed": progress.completed if progress else False,
            "permanent_answered": progress.permanent_answered or [] if progress else [],
            "permanent_correct": progress.permanent_correct or [] if progress else [],
            "exercise_completion_times": progress.exercise_completion_times or [] if progress else [],
            "notes": progress.notes if progress else "",
        },
    })


@listening_bp.route("/progress", methods=["POST"])
@login_required
def save_progress():
    data = request.get_json()
    exercise_id = data.get("exercise_id")
    last_position = data.get("last_position")
    answers = data.get("answers")
    completed = data.get("completed", False)
    reset = data.get("reset", False)
    duration_spent = data.get("duration_spent", 0)
    reset_mode = data.get("reset_mode", False)

    if not exercise_id:
        return jsonify({"error": "exercise_id required"}), 400

    exercise = db.session.get(ListeningExercise, exercise_id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    # 先查询当前用户 + 当前练习的进度
    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()

    # 🔥 修复：自动删除重复的空记录（只保留第一条）
    if progress:
        duplicates = UserListeningProgress.query.filter_by(
            user_id=current_user.id, exercise_id=exercise_id
        ).offset(1).all()
    
        for dup in duplicates:
            db.session.delete(dup)

    first_correct_questions = []
    if not progress:
        progress = UserListeningProgress(
            user_id=current_user.id, exercise_id=exercise_id
        )
        progress.permanent_answered = []
        progress.permanent_correct = []
        progress.answers = {}
        progress.notes_history = []
        progress.question_correct_times = {}
        db.session.add(progress)

    # 自动迁移旧数据（保证多日期共存）
    _migrate_question_correct_times(progress)

    if reset:
        progress.last_position = 0
        progress.answers = {}
        progress.completed = False
        flag_modified(progress, "answers")
        progress.last_attempt_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True})

    # 正常保存进度
    if last_position is not None:
        progress.last_position = last_position

    questions = exercise.questions or []
    current_time = datetime.utcnow().isoformat()
    current_date = current_time[:10]

    # ==============================
    # 🔥 核心修复 1：立即保存时间戳
    # ==============================
    if answers:
        for q_idx_str, selected_opt in answers.items():
            q_idx = int(q_idx_str)
            if q_idx >= len(questions) or q_idx < 0:
                continue

            # 记录已答题
            if q_idx not in progress.permanent_answered:
                progress.permanent_answered.append(q_idx)
                flag_modified(progress, "permanent_answered")

            correct_answer = questions[q_idx].get("answer")
            try:
                correct_int = int(correct_answer)
            except:
                continue

            if selected_opt == correct_int:
                q_key = str(q_idx)

                # 🔥 关键：保留所有历史日期，只更新当天
                if q_key not in progress.question_correct_times:
                    progress.question_correct_times[q_key] = {}

                # 覆盖今天，但保留昨天/前天
                progress.question_correct_times[q_key][current_date] = current_time
                flag_modified(progress, "question_correct_times")

                # 首次正确奖励
                if not reset_mode and q_idx not in progress.permanent_correct:
                    progress.permanent_correct.append(q_idx)
                    flag_modified(progress, "permanent_correct")
                    current_user.total_correct_questions = (current_user.total_correct_questions or 0) + 1
                    current_user.coins = (current_user.coins or 0) + 1
                    db.session.add(current_user)
                    first_correct_questions.append(q_idx)

        # 保存答案
        progress.answers = {**(progress.answers or {}), **answers}
        flag_modified(progress, "answers")

    # 完成练习
    if completed:
        progress.completed = True
        t = datetime.utcnow().isoformat()
        d = t[:10]
        progress.exercise_completion_times = [
            ts for ts in (progress.exercise_completion_times or [])
            if not ts.startswith(d)
        ]
        progress.exercise_completion_times.append(t)
        flag_modified(progress, "exercise_completion_times")

    # 时长统计
    if duration_spent > 0:
        current_user.total_listening_duration = (current_user.total_listening_duration or 0) + duration_spent
        db.session.add(current_user)

    progress.last_attempt_at = utcnow_naive()
    flag_modified(progress, "permanent_answered")
    flag_modified(progress, "permanent_correct")

    db.session.commit()
    return jsonify({
        "success": True,
        "coin_reward": len(first_correct_questions),
        "coins": current_user.coins
    })


@listening_bp.route("/progress/<int:exercise_id>", methods=["GET"])
@login_required
def get_progress(exercise_id):
    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    if progress:
        _migrate_question_correct_times(progress)
        db.session.commit()
    if not progress:
        return jsonify({"exists": False})
    return jsonify({
        "exists": True,
        "last_position": progress.last_position,
        "answers": progress.answers,
        "completed": progress.completed,
        "last_attempt_at": progress.last_attempt_at.isoformat() if progress.last_attempt_at else None,
        "permanent_answered": progress.permanent_answered or [],
        "permanent_correct": progress.permanent_correct or [],
        "exercise_completion_times": progress.exercise_completion_times or [],
        "notes": progress.notes or "",
    })


@listening_bp.route("/api/notes", methods=["POST"])
@login_required
def save_notes():
    data = request.get_json()
    exercise_id = data.get("exercise_id")
    new_notes = data.get("notes", "")

    if not exercise_id:
        return jsonify({"error": "exercise_id required"}), 400

    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    if not progress:
        progress = UserListeningProgress(
            user_id=current_user.id, exercise_id=exercise_id
        )
        progress.permanent_answered = []
        progress.permanent_correct = []
        progress.answers = {}
        progress.notes_history = []
        progress.question_correct_times = {}
        db.session.add(progress)

    if progress.notes != new_notes:
        progress.notes_history.append({
            "content": new_notes,
            "created_at": datetime.utcnow().isoformat()
        })
        progress.notes = new_notes
        flag_modified(progress, "notes_history")
        db.session.commit()

    return jsonify({"success": True})


@listening_bp.route("/api/notes/history/<int:exercise_id>")
@login_required
def get_notes_history(exercise_id):
    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    return jsonify({"history": progress.notes_history or []})