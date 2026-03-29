from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ListeningExercise, UserListeningProgress
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified  # 新增导入

listening_bp = Blueprint("listening", __name__, url_prefix="/listening")


@listening_bp.route("/")
@login_required
def index():
    difficulty = request.args.get("difficulty", type=int)
    category = request.args.get("category", type=str)  
    accent = request.args.get("accent", type=str)  # 新增：获取accent参数

    # 构建查询
    query = ListeningExercise.query
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
    completed = data.get("completed", False)
    reset = data.get("reset", False)
    duration_spent = data.get("duration_spent", 0)

    if not exercise_id:
        return jsonify({"error": "exercise_id required"}), 400

    exercise = ListeningExercise.query.get(exercise_id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    # 只有当有实际数据时才创建记录
    if not answers and last_position is None and duration_spent <= 0:
        return jsonify({"success": True})

    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id, exercise_id=exercise_id
    ).first()
    if not progress:
        progress = UserListeningProgress(
            user_id=current_user.id, exercise_id=exercise_id
        )
        # 确保初始化
        progress.permanent_answered = []
        progress.permanent_correct = []
        progress.answers = {}
        db.session.add(progress)

    if reset:
        progress.last_position = 0
        progress.answers = {}
        # 如需清空永久记录，取消注释
        # progress.permanent_answered = []
        # progress.permanent_correct = []
        # 标记修改
        flag_modified(progress, "permanent_answered")
        flag_modified(progress, "permanent_correct")
        db.session.add(progress)
    else:
        if last_position is not None:
            progress.last_position = last_position
            db.session.add(progress)

        # 确保永久记录字段是列表类型（避免 None）
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
                    print(f"  Skipping, invalid index")
                    continue

                # 确保列表存在
                if progress.permanent_answered is None:
                    progress.permanent_answered = []
                if progress.permanent_correct is None:
                    progress.permanent_correct = []

                # ========== 1. 记录到 permanent_answered（第一次答题） ==========
                if q_idx not in progress.permanent_answered:
                    # 修改列表（直接在原列表上操作，然后标记为修改）
                    progress.permanent_answered.append(q_idx)
                    flag_modified(progress, "permanent_answered")
                    # 可选刷新，但不是必须
                    # db.session.flush()

                # ========== 2. 判断正确性，更新 permanent_correct ==========
                correct_answer = questions[q_idx].get("answer")
                correct_answer_int = None
                if correct_answer is not None:
                    try:
                        correct_answer_int = int(correct_answer)
                    except (ValueError, TypeError):
                        pass

                if correct_answer_int is not None and selected_opt == correct_answer_int:
                    if q_idx not in progress.permanent_correct:
                        progress.permanent_correct.append(q_idx)
                        flag_modified(progress, "permanent_correct")
                        if current_user.total_correct_questions is None:
                            current_user.total_correct_questions = 0
                        current_user.total_correct_questions += 1
                        db.session.add(current_user)

            # 合并 answers 字段
            if progress.answers is None:
                progress.answers = answers
            else:
                merged = {**progress.answers, **answers}
                progress.answers = merged
            # 标记 answers 字段修改（可选，因为 answers 是 JSON，也需要 flag_modified）
            flag_modified(progress, "answers")
            db.session.add(progress)

        if completed:
            progress.completed = True
            db.session.add(progress)

    if duration_spent > 0:
        if current_user.total_listening_duration is None:
            current_user.total_listening_duration = 0
        current_user.total_listening_duration += duration_spent
        db.session.add(current_user)

    progress.last_attempt_at = datetime.utcnow()
    db.session.add(progress)

    # 提交前再次确保字段被标记
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
    return jsonify(
        {
            "exists": True,
            "last_position": progress.last_position,
            "answers": progress.answers,
            "completed": progress.completed,
            "last_attempt_at": progress.last_attempt_at.isoformat() if progress.last_attempt_at else None,
            "permanent_answered": progress.permanent_answered or [],
            "permanent_correct": progress.permanent_correct or [],
        }
    )