from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Flashcard, UserActivityLog

flashcards_bp = Blueprint('flashcards', __name__, url_prefix='/flashcards')


@flashcards_bp.route('/')
@login_required
def index():
    # Show public cards + cards created by the current user
    cards = (
        Flashcard.query
        .filter(
            Flashcard.is_public.is_(True) |
            (Flashcard.created_by == current_user.id)
        )
        .order_by(Flashcard.created_at.desc())
        .all()
    )

    # Log activity
    log = UserActivityLog(user_id=current_user.id, module='flashcard', action='viewed')
    db.session.add(log)
    db.session.commit()

    return render_template('flashcards/index.html', cards=cards)
