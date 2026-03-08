from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, ListeningExercise, UserActivityLog

listening_bp = Blueprint('listening', __name__, url_prefix='/listening')


@listening_bp.route('/')
@login_required
def index():
    exercises = ListeningExercise.query.order_by(ListeningExercise.difficulty).all()

    log = UserActivityLog(user_id=current_user.id, module='listening', action='viewed')
    db.session.add(log)
    db.session.commit()

    return render_template('listening/index.html', exercises=exercises)
