from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ListeningExercise, UserListeningProgress
from datetime import datetime, timezone
from sqlalchemy.orm.attributes import flag_modified  # 新增导入

listening_bp = Blueprint("listening", __name__, url_prefix="/listening")


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
    reset_mode = data.get("reset_mode", False)   # 重置模式标志

    if not exercise_id:
        return jsonify({"error": "exercise_id required"}), 400

    exercise = db.session.get(ListeningExercise, exercise_id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    # 重置请求即使没有其他数据也需要处理
    if (not answers and last_position is None and duration_spent <= 0) and not reset:
        return jsonify({"success": True})

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
        db.session.add(progress)

    if reset:
        # 重置：清空所有临时进度，但保留永久记录
        progress.last_position = 0
        progress.answers = {}
        progress.completed = False
        flag_modified(progress, "answers")
        progress.last_attempt_at = datetime.utcnow()
        db.session.add(progress)
        db.session.commit()
        return jsonify({"success": True})
    else:
        # 正常保存进度
        if last_position is not None:
            progress.last_position = last_position
            db.session.add(progress)

        # 确保永久记录字段是列表
        if progress.permanent_answered is None:
            progress.permanent_answered = []
            flag_modified(progress, "permanent_answered")
        if progress.permanent_correct is None:
            progress.permanent_correct = []
            flag_modified(progress, "permanent_correct")

        questions = exercise.questions or []

        # 处理答案
        if answers:
            for q_idx_str, selected_opt in answers.items():
                q_idx = int(q_idx_str)
                if q_idx >= len(questions) or q_idx < 0:
                    continue

                # 记录到永久已答（第一次答）
                if q_idx not in progress.permanent_answered:
                    progress.permanent_answered.append(q_idx)
                    flag_modified(progress, "permanent_answered")

                # 判断正确性
                correct_answer = questions[q_idx].get("answer")
                correct_answer_int = None
                if correct_answer is not None:
                    try:
                        correct_answer_int = int(correct_answer)
                    except (ValueError, TypeError):
                        pass

                if correct_answer_int is not None and selected_opt == correct_answer_int:
                    # 只有非重置模式且首次正确时，才更新永久正确
                    if not reset_mode and q_idx not in progress.permanent_correct:
                        progress.permanent_correct.append(q_idx)
                        flag_modified(progress, "permanent_correct")
                        if current_user.total_correct_questions is None:
                            current_user.total_correct_questions = 0
                        current_user.total_correct_questions += 1
                        db.session.add(current_user)

            # 合并临时答案
            if progress.answers is None:
                progress.answers = answers
            else:
                merged = {**progress.answers, **answers}
                progress.answers = merged
            flag_modified(progress, "answers")
            db.session.add(progress)

        if completed:
            progress.completed = True
            db.session.add(progress)

    # 累计学习时长
    if duration_spent > 0:
        if current_user.total_listening_duration is None:
            current_user.total_listening_duration = 0
        current_user.total_listening_duration += duration_spent
        db.session.add(current_user)

    progress.last_attempt_at = datetime.now(timezone.utc)
    db.session.add(progress)

    # 标记 JSON 字段
    flag_modified(progress, "permanent_answered")
    flag_modified(progress, "permanent_correct")
    flag_modified(progress, "answers")

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
    return jsonify({
        "exists": True,
        "last_position": progress.last_position,
        "answers": progress.answers,
        "completed": progress.completed,
        "last_attempt_at": progress.last_attempt_at.isoformat() if progress.last_attempt_at else None,
        "permanent_answered": progress.permanent_answered or [],
        "permanent_correct": progress.permanent_correct or [],
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
        db.session.add(progress)
        db.session.flush()

    # 如果笔记内容变化，追加历史
    if progress.notes != new_notes:
        history_entry = {
            "content": new_notes,
            "created_at": datetime.utcnow().isoformat()
        }
        if progress.notes_history is None:
            progress.notes_history = []
        progress.notes_history.append(history_entry)
        progress.notes = new_notes
        flag_modified(progress, "notes_history")
        db.session.add(progress)

    db.session.commit()
    return jsonify({"success": True})


@listening_bp.route("/api/notes/history/<int:exercise_id>")
@login_required
def get_notes_history(exercise_id):
    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    if not progress or not progress.notes_history:
        return jsonify({"history": []})
    return jsonify({"history": progress.notes_history})
