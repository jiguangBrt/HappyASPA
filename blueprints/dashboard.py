from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, abort, redirect
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

from models import (
    db,
    ForumPost,
    ForumFavorite,
    ForumLike,
    UserJournalMarker,
    UserListeningProgress,
    UserScheduleItem,
    UserSpeakingSubmission,
    UserShadowingRecord,
    UserVocabularyProgress,
    UserScenarioSubmission,
)

dashboard_bp = Blueprint('dashboard', __name__)

OVERALL_GUIDANCE_CARDS = [
    {
        "key": "teams",
        "title": "How to Use Microsoft Teams",
        "front": "For group communication and meetings.",
        "back": "Open Teams every day to check announcements, files, and channels. Keep questions and decisions in the channel/chat so you can find them later.",
        "icon": "bi-people",
        "color": "primary",
    },
    {
        "key": "diicsu",
        "title": "DIICSU Before You Start",
        "front": "The DIICSU website.",
        "back": "Learn the core tools and expectations in DIICSU before Week 1. This app guides your weekly routine so you arrive prepared and confident.",
        "icon": "bi-building",
        "color": "secondary",
        "url": "https://dii.csu.edu.cn/EN/ABOUT/Why_DIICSU/Introduction.htm",
    },
    {
        "key": "misconduct",
        "title": "Academic Integrity",
        "front": "Avoid mistakes with sources and collaboration.",
        "back": "Write in your own words, cite sources, and don’t reuse others’ writing without permission. If you’re unsure what’s allowed, ask before you submit.",
        "icon": "bi-shield-check",
        "color": "danger",
        "url": "https://www.dundee.ac.uk/corporate-information/code-practice-academic-misconduct-students",
    },
    {
        "key": "focus",
        "title": "Academic Skills",
        "front": "DIICSU focus on skills.",
        "back": "Prioritize listening + speaking every week. Use the forum when you’re stuck, and keep vocabulary practice steady to support both skills.",
        "icon": "bi-bullseye",
        "color": "success",
        "url": "https://www.dundee.ac.uk/academic-skills",
    },
]

RECOMMENDED_SCHEDULES = {
    "listening": "Listening practice",
    "speaking": "Speaking practice",
    "vocabulary": "Learn 10 words",
}

LEGACY_RECOMMENDED_SCHEDULES_ZH = {
    "listening": "\u542c\u542c\u529b1\u7bc7",
    "speaking": "\u4f7f\u7528\u53e3\u8bed\u677f\u5757",
    "vocabulary": "\u5b66\u8bcd\u6c4710\u4e2a",
}


def normalize_schedule_title(kind: str, title: str) -> str:
    """Translate legacy built-in schedule titles to English for display."""
    if not kind or not title:
        return title
    legacy = LEGACY_RECOMMENDED_SCHEDULES_ZH.get(kind)
    if legacy and title.strip() == legacy:
        return RECOMMENDED_SCHEDULES.get(kind, title)
    return title


def calculate_streak(dates):
    if not dates:
        return 0
    date_set = set(dates)
    today = date.today()
    streak = 0
    cursor = today
    while cursor in date_set:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


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
            "title": normalize_schedule_title(item.kind, item.title),
            "notes": item.notes or "",
        }
        for item in schedule_items
    ]

    today_schedule_payload = [
        payload
        for payload in schedule_items_payload
        if payload["scheduled_date"] == today.isoformat()
    ]

    journal_markers = (
        UserJournalMarker.query.filter(UserJournalMarker.user_id == current_user.id)
        .order_by(UserJournalMarker.event_date.asc(), UserJournalMarker.created_at.asc())
        .all()
    )

    journal_markers_payload = [
        {
            "id": marker.id,
            "title": marker.title,
            "kind": marker.kind,
            "value": marker.value,
            "unit": marker.unit or "",
            "notes": marker.notes or "",
            "color": marker.color or "",
            "event_date": marker.event_date.isoformat(),
            "created_at": marker.created_at.isoformat(),
        }
        for marker in journal_markers
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
    listening_lecture_count = (
        db.session.query(
            func.coalesce(
                func.sum(func.coalesce(UserListeningProgress.two_thirds_count, 0)), 0
            )
        )
        .filter(UserListeningProgress.user_id == current_user.id)
        .scalar()
        or 0
    )

    listening_attempts = (
        db.session.query(
            func.coalesce(func.sum(func.coalesce(UserListeningProgress.attempts, 0)), 0)
        )
        .filter(UserListeningProgress.user_id == current_user.id)
        .scalar()
        or 0
    )

    listening_progress_rows = (
        UserListeningProgress.query.filter(
            UserListeningProgress.user_id == current_user.id
        ).all()
    )
    listening_question_count = 0
    for row in listening_progress_rows:
        answers = row.answers
        if isinstance(answers, list):
            listening_question_count += len(answers)
        elif isinstance(answers, dict):
            listening_question_count += len(answers.keys())
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

    shadowing_count = (
        db.session.query(func.count(UserShadowingRecord.id))
        .filter(UserShadowingRecord.user_id == current_user.id)
        .scalar()
        or 0
    )
    
    # 3. 两者相加得出总数
    speaking_submissions = english_corner_count + academic_scenario_count + shadowing_count

    latest_vocab_ts = (
        db.session.query(func.max(UserVocabularyProgress.last_reviewed_at))
        .filter(UserVocabularyProgress.user_id == current_user.id)
        .scalar()
    )
    latest_listening_ts = (
        db.session.query(func.max(UserListeningProgress.last_attempt_at))
        .filter(UserListeningProgress.user_id == current_user.id)
        .scalar()
    )
    latest_speaking_ts = (
        db.session.query(func.max(UserSpeakingSubmission.submitted_at))
        .filter(UserSpeakingSubmission.user_id == current_user.id)
        .scalar()
    )
    latest_scenario_ts = (
        db.session.query(func.max(UserScenarioSubmission.submitted_at))
        .filter(UserScenarioSubmission.user_id == current_user.id)
        .scalar()
    )
    latest_shadowing_ts = (
        db.session.query(func.max(UserShadowingRecord.created_at))
        .filter(UserShadowingRecord.user_id == current_user.id)
        .scalar()
    )

    def to_date_or_today(dt):
        return (dt.date() if dt else today)

    growth_milestones = [
        {
            "key": "vocab_mastered",
            "title": "Words Mastered",
            "value": vocab_mastered,
            "unit": "words",
            "event_date": to_date_or_today(latest_vocab_ts).isoformat(),
        },
        {
            "key": "vocab_learning",
            "title": "Words Learning",
            "value": vocab_learning,
            "unit": "words",
            "event_date": to_date_or_today(latest_vocab_ts).isoformat(),
        },
        {
            "key": "listening_questions",
            "title": "Listening Questions",
            "value": listening_question_count,
            "unit": "items",
            "event_date": to_date_or_today(latest_listening_ts).isoformat(),
        },
        {
            "key": "listening_attempts",
            "title": "Listening Attempts",
            "value": listening_attempts,
            "unit": "times",
            "event_date": to_date_or_today(latest_listening_ts).isoformat(),
        },
        {
            "key": "scenario_participations",
            "title": "Scenario Participations",
            "value": academic_scenario_count,
            "unit": "times",
            "event_date": to_date_or_today(latest_scenario_ts).isoformat(),
        },
        {
            "key": "english_corner_recordings",
            "title": "English Corner Recordings",
            "value": english_corner_count,
            "unit": "times",
            "event_date": to_date_or_today(latest_speaking_ts).isoformat(),
        },
        {
            "key": "shadowing_records",
            "title": "Shadowing Records",
            "value": shadowing_count,
            "unit": "times",
            "event_date": to_date_or_today(latest_shadowing_ts).isoformat(),
        },
    ]

    streak_count = calculate_streak([m.event_date for m in journal_markers])

    return render_template(
        "dashboard.html",
        calendar_start=calendar_start.isoformat(),
        schedule_items=schedule_items_payload,
        today_schedule=today_schedule_payload,
        today_iso=today.isoformat(),
        schedule_table_ready=schedule_table_ready,
        overall_guidance_cards=OVERALL_GUIDANCE_CARDS,
        growth_milestones=growth_milestones,
        growth_custom_logs=journal_markers_payload,
        streak_count=streak_count,
        growth_stats={
            "vocab_mastered": vocab_mastered,
            "vocab_learning": vocab_learning,
            "listening_lecture_count": listening_lecture_count,
            "listening_attempts": listening_attempts,
            "listening_question_count": listening_question_count,
            "speaking_submissions": speaking_submissions,
            "english_corner_recordings": english_corner_count,
            "scenario_participations": academic_scenario_count,
            "shadowing_records": shadowing_count,
        },
        favorite_posts=favorite_posts,
        liked_posts=liked_posts,
    )


@dashboard_bp.route("/guidance/<card_key>")
@login_required
def guidance_page(card_key: str):
    card = next(
        (item for item in OVERALL_GUIDANCE_CARDS if item["key"] == card_key), None
    )
    if not card:
        abort(404)
    if card.get("url"):
        return redirect(card["url"])
    return render_template(f"guidance/{card_key}.html", card=card)


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


@dashboard_bp.route("/growth/logs", methods=["POST"])
@login_required
def create_growth_log():
    payload = request.get_json(silent=True) or {}

    title = (payload.get("title") or "").strip()
    event_date_raw = (payload.get("event_date") or "").strip()
    kind = (payload.get("kind") or "custom").strip() or "custom"
    notes = (payload.get("notes") or "").strip() or None
    color = (payload.get("color") or "").strip() or None
    unit = (payload.get("unit") or "").strip() or None
    value_raw = payload.get("value")

    if not title:
        return jsonify({"error": "title is required"}), 400

    try:
        event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "event_date must be YYYY-MM-DD"}), 400

    value = None
    if value_raw not in (None, ""):
        try:
            value = float(value_raw)
        except (TypeError, ValueError):
            return jsonify({"error": "value must be a number"}), 400

    marker = UserJournalMarker(
        user_id=current_user.id,
        title=title[:200],
        kind=kind[:30],
        value=value,
        unit=(unit[:20] if unit else None),
        notes=notes,
        color=(color[:20] if color else None),
        event_date=event_date,
    )
    db.session.add(marker)
    db.session.commit()

    return (
        jsonify(
            {
                "id": marker.id,
                "title": marker.title,
                "kind": marker.kind,
                "value": marker.value,
                "unit": marker.unit or "",
                "notes": marker.notes or "",
                "color": marker.color or "",
                "event_date": marker.event_date.isoformat(),
                "created_at": marker.created_at.isoformat(),
            }
        ),
        201,
    )


@dashboard_bp.route("/growth/logs/<int:log_id>", methods=["PUT"])
@login_required
def update_growth_log(log_id: int):
    payload = request.get_json(silent=True) or {}

    marker = UserJournalMarker.query.filter_by(id=log_id, user_id=current_user.id).first()
    if not marker:
        return jsonify({"error": "Not found"}), 404

    title = (payload.get("title") or "").strip()
    event_date_raw = (payload.get("event_date") or "").strip()
    notes = (payload.get("notes") or "").strip() or None
    color = (payload.get("color") or "").strip() or None
    unit = (payload.get("unit") or "").strip() or None
    value_raw = payload.get("value")

    if title:
        marker.title = title[:200]

    if event_date_raw:
        try:
            marker.event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "event_date must be YYYY-MM-DD"}), 400

    value = None
    if value_raw not in (None, ""):
        try:
            value = float(value_raw)
        except (TypeError, ValueError):
            return jsonify({"error": "value must be a number"}), 400
    marker.value = value
    marker.unit = unit[:20] if unit else None
    marker.notes = notes
    marker.color = color[:20] if color else None

    db.session.commit()

    return jsonify(
        {
            "id": marker.id,
            "title": marker.title,
            "kind": marker.kind,
            "value": marker.value,
            "unit": marker.unit or "",
            "notes": marker.notes or "",
            "color": marker.color or "",
            "event_date": marker.event_date.isoformat(),
            "created_at": marker.created_at.isoformat(),
        }
    )
