from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, WritingExercise, UserWritingSubmission, UserActivityLog

writing_bp = Blueprint('writing', __name__, url_prefix='/writing')


@writing_bp.route('/')
@login_required
def index():
    exercises = WritingExercise.query.order_by(WritingExercise.difficulty).all()

    log = UserActivityLog(user_id=current_user.id, module='writing', action='viewed')
    db.session.add(log)
    db.session.commit()

    return render_template('writing/index.html', exercises=exercises)


@writing_bp.route('/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def exercise_detail(exercise_id):
    exercise = WritingExercise.query.get_or_404(exercise_id)

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            word_count = len(content.split())
            submission = UserWritingSubmission(
                user_id=current_user.id,
                exercise_id=exercise.id,
                content=content,
                word_count=word_count
            )
            db.session.add(submission)

            log = UserActivityLog(
                user_id=current_user.id,
                module='writing',
                action='submitted',
                ref_id=exercise_id
            )
            db.session.add(log)
            db.session.commit()
            flash('Submission saved!', 'success')
            return redirect(url_for('writing.index'))
        else:
            flash('Please write something before submitting.', 'danger')

    return render_template('writing/exercise.html', exercise=exercise)
