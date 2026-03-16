from flask import Blueprint, render_template
from flask_login import login_required
from models import VocabularyWord

vocabulary_bp = Blueprint('vocabulary', __name__, url_prefix='/vocabulary')


@vocabulary_bp.route('/')
@login_required
def index():
    words = VocabularyWord.query.order_by(VocabularyWord.difficulty).all()

    return render_template('vocabulary/index.html', words=words)
