from flask import Blueprint, render_template
from flask_login import login_required
from models import ListeningExercise

listening_bp = Blueprint('listening', __name__, url_prefix='/listening')


@listening_bp.route('/')
@login_required
def index():
    exercises = ListeningExercise.query.order_by(ListeningExercise.difficulty).all()

    return render_template('listening/index.html', exercises=exercises)
