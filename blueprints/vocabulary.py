from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, VocabularyWord, UserActivityLog

vocabulary_bp = Blueprint('vocabulary', __name__, url_prefix='/vocabulary')


@vocabulary_bp.route('/')
@login_required
def index():
    words = VocabularyWord.query.order_by(VocabularyWord.difficulty).all()

    # Log activity
    log = UserActivityLog(user_id=current_user.id, module='vocabulary', action='viewed')
    db.session.add(log)
    db.session.commit()

    return render_template('vocabulary/index.html', words=words)
