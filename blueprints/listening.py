from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, ListeningExercise, UserListeningProgress
from datetime import datetime

listening_bp = Blueprint('listening', __name__, url_prefix='/listening')

@listening_bp.route('/')
@login_required
def index():
    exercises = ListeningExercise.query.order_by(ListeningExercise.difficulty).all()
    return render_template('listening/index.html', exercises=exercises)

@listening_bp.route('/progress', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    exercise_id = data.get('exercise_id')
    last_position = data.get('last_position')
    answers = data.get('answers')
    two_thirds_reached = data.get('two_thirds_reached', False)
    completed = data.get('completed', False)
    score = data.get('score')
    reset = data.get('reset', False)  # 获取重置标志

    if not exercise_id:
        return jsonify({'error': 'exercise_id required'}), 400

    exercise = ListeningExercise.query.get(exercise_id)
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id
    ).first()
    if not progress:
        progress = UserListeningProgress(
            user_id=current_user.id,
            exercise_id=exercise_id
        )
        db.session.add(progress)

    if reset:
        # 重置：强制设置 last_position = 0 并清空 answers
        progress.last_position = 0
        progress.answers = {}
    else:
        # 正常更新
        if last_position is not None:
            if progress.last_position is None or last_position > progress.last_position:
                progress.last_position = last_position

        if answers is not None:
            if not answers:  # 空字典表示清空答案（如重置时）
                progress.answers = {}
            else:
                if progress.answers is None:
                    progress.answers = answers
                else:
                    # 合并新旧答案（新答案覆盖同题号旧答案）
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
    return jsonify({'success': True})

# Use to test for visibility
@listening_bp.route('/progress/<int:exercise_id>', methods=['GET'])
@login_required
def get_progress(exercise_id):
    progress = UserListeningProgress.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id
    ).first()
    if not progress:
        return jsonify({'exists': False})
    return jsonify({
        'exists': True,
        'last_position': progress.last_position,
        'two_thirds_count': progress.two_thirds_count,
        'answers': progress.answers,
        'completed': progress.completed,
        'score': progress.score,
        'last_attempt_at': progress.last_attempt_at.isoformat() if progress.last_attempt_at else None
    })