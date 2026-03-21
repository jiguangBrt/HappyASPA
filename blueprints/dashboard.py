from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

from models import (
    db,
    ForumPost,
    ForumFavorite,
    ForumLike,
    UserListeningProgress,
    UserScheduleItem,
    UserSpeakingSubmission,
    UserVocabularyProgress,
    UserScenarioSubmission,  # 🌟 新增导入这行
)

dashboard_bp = Blueprint('dashboard', __name__)

RECOMMENDED_SCHEDULES = {
    "listening": "\u542c\u542c\u529b1\u7bc7",
    "speaking": "\u4f7f\u7528\u53e3\u8bed\u677f\u5757",
    "vocabulary": "\u5b66\u8bcd\u6c4710\u4e2a",
}


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()
    calendar_start = today - timedelta(days=today.weekday())  # Monday
    calendar_end = calendar_start + timedelta(days=27)

    schedule_table_ready = True
    try:
        schedule_items = (
            UserScheduleItem.query.filter(UserScheduleItem.user_id == current_user.id)
            .filter(UserScheduleItem.scheduled_date >= calendar_start)
            .filter(UserScheduleItem.scheduled_date <= calendar_end)
            .order_by(
                UserScheduleItem.scheduled_date.asc(), UserScheduleItem.created_at.asc()
            )
            .all()
        )
    except OperationalError:
        db.session.rollback()
        schedule_table_ready = False
        schedule_items = []

    schedule_items_payload = [
        {
            "id": item.id,
            "scheduled_date": item.scheduled_date.isoformat(),
            "kind": item.kind,
            "title": item.title,
            "notes": item.notes or "",
        }
        for item in schedule_items
    ]

    today_schedule_payload = [
        payload
        for payload in schedule_items_payload
        if payload["scheduled_date"] == today.isoformat()
    ]

    favorite_posts = (
        db.session.query(ForumPost)
        .join(ForumFavorite, ForumPost.id == ForumFavorite.post_id)
        .filter(ForumFavorite.user_id == current_user.id)
        .order_by(ForumFavorite.created_at.desc())
        .all()
    )

    liked_posts = (
        db.session.query(ForumPost)
        .join(ForumLike, ForumPost.id == ForumLike.post_id)
        .filter(ForumLike.user_id == current_user.id)
        .order_by(ForumLike.created_at.desc())
        .all()
    )

    vocab_mastered = (
        db.session.query(func.count(UserVocabularyProgress.id))
        .filter(UserVocabularyProgress.user_id == current_user.id)
        .filter(UserVocabularyProgress.status == "mastered")
        .scalar()
        or 0
    )
    vocab_learning = (
        db.session.query(func.count(UserVocabularyProgress.id))
        .filter(UserVocabularyProgress.user_id == current_user.id)
        .filter(UserVocabularyProgress.status == "learning")
        .scalar()
        or 0
    )
    listening_completed = (
        db.session.query(func.count(UserListeningProgress.id))
        .filter(UserListeningProgress.user_id == current_user.id)
        .filter(UserListeningProgress.completed.is_(True))
        .scalar()
        or 0
    )
    # 1. 统计 English Corner 的录音数量
    english_corner_count = (
        db.session.query(func.count(UserSpeakingSubmission.id))
        .filter(UserSpeakingSubmission.user_id == current_user.id)
        .scalar()
        or 0
    )
    
    # 2. 统计 Academic Scenarios 的录音数量
    academic_scenario_count = (
        db.session.query(func.count(UserScenarioSubmission.id))
        .filter(UserScenarioSubmission.user_id == current_user.id)
        .scalar()
        or 0
    )
    
    # 3. 两者相加得出总数
    speaking_submissions = english_corner_count + academic_scenario_count

    return render_template(
        "dashboard.html",
        calendar_start=calendar_start.isoformat(),
        schedule_items=schedule_items_payload,
        today_schedule=today_schedule_payload,
        schedule_table_ready=schedule_table_ready,
        growth_stats={
            "vocab_mastered": vocab_mastered,
            "vocab_learning": vocab_learning,
            "listening_completed": listening_completed,
            "speaking_submissions": speaking_submissions,
        },
        favorite_posts=favorite_posts,
        liked_posts=liked_posts,
    )


@dashboard_bp.route("/schedule", methods=["POST"])
@login_required
def create_schedule_item():
    payload = request.get_json(silent=True) or {}

    scheduled_date_raw = (payload.get("scheduled_date") or "").strip()
    kind = (payload.get("kind") or "").strip()
    title = (payload.get("title") or "").strip()
    notes = (payload.get("notes") or "").strip() or None

    if not scheduled_date_raw:
        return jsonify({"error": "scheduled_date is required"}), 400

    try:
        scheduled_date = datetime.strptime(scheduled_date_raw, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "scheduled_date must be YYYY-MM-DD"}), 400

    allowed_kinds = set(RECOMMENDED_SCHEDULES.keys()) | {"custom"}
    if kind not in allowed_kinds:
        return jsonify({"error": "Invalid kind"}), 400

    if kind != "custom":
        title = RECOMMENDED_SCHEDULES.get(kind, title) or title

    if not title:
        return jsonify({"error": "title is required"}), 400

    try:
        item = UserScheduleItem(
            user_id=current_user.id,
            scheduled_date=scheduled_date,
            kind=kind,
            title=title[:200],
            notes=notes,
        )
        db.session.add(item)
        db.session.commit()
    except OperationalError:
        db.session.rollback()
        return jsonify({"error": "Schedule table not ready. Please run: flask db upgrade"}), 503

    return (
        jsonify(
            {
                "id": item.id,
                "scheduled_date": item.scheduled_date.isoformat(),
                "kind": item.kind,
                "title": item.title,
                "notes": item.notes or "",
            }
        ),
        201,
    )


@dashboard_bp.route("/schedule/<int:item_id>", methods=["DELETE"])
@login_required
def delete_schedule_item(item_id: int):
    try:
        item = UserScheduleItem.query.filter_by(
            id=item_id, user_id=current_user.id
        ).first()
    except OperationalError:
        db.session.rollback()
        return jsonify({"error": "Schedule table not ready. Please run: flask db upgrade"}), 503
    if not item:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"status": "ok"})
