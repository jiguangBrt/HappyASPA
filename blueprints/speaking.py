from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, UserActivityLog

speaking_bp = Blueprint('speaking', __name__, url_prefix='/speaking')


@speaking_bp.route('/')
@login_required
def index():
    log = UserActivityLog(user_id=current_user.id, module='speaking', action='viewed')
    db.session.add(log)
    db.session.commit()

    return render_template('speaking/index.html')
