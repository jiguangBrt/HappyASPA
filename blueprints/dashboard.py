from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import UserActivityLog

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    # Fetch the last 20 activity log entries for the learning trajectory
    recent_activity = (
        UserActivityLog.query
        .filter_by(user_id=current_user.id)
        .order_by(UserActivityLog.timestamp.desc())
        .limit(20)
        .all()
    )

    # Summary stats per module
    from sqlalchemy import func
    from models import db
    stats = (
        db.session.query(
            UserActivityLog.module,
            func.count(UserActivityLog.id).label('count')
        )
        .filter_by(user_id=current_user.id)
        .group_by(UserActivityLog.module)
        .all()
    )
    stats_dict = {row.module: row.count for row in stats}

    return render_template(
        'dashboard.html',
        recent_activity=recent_activity,
        stats=stats_dict
    )
