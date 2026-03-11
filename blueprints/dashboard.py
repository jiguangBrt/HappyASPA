from flask import Blueprint, render_template
from flask_login import login_required, current_user
# 👇 修改：多引入了 db, ForumPost, ForumFavorite, ForumLike
from models import db, UserActivityLog, ForumPost, ForumFavorite, ForumLike
from sqlalchemy import func

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

    # 👇 新增：查询当前用户收藏的帖子，按收藏时间倒序
    favorite_posts = db.session.query(ForumPost)\
        .join(ForumFavorite, ForumPost.id == ForumFavorite.post_id)\
        .filter(ForumFavorite.user_id == current_user.id)\
        .order_by(ForumFavorite.created_at.desc())\
        .all()

    # 👇 新增：查询当前用户点赞的帖子，按点赞时间倒序
    liked_posts = db.session.query(ForumPost)\
        .join(ForumLike, ForumPost.id == ForumLike.post_id)\
        .filter(ForumLike.user_id == current_user.id)\
        .order_by(ForumLike.created_at.desc())\
        .all()

    # 👇 修改：把查出来的 favorite_posts 和 liked_posts 传给前端模板
    return render_template(
        'dashboard.html',
        recent_activity=recent_activity,
        stats=stats_dict,
        favorite_posts=favorite_posts,
        liked_posts=liked_posts
    )