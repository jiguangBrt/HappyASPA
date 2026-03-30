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

    # 定义一个内部辅助函数，安全地处理日期转换
    def safe_iso(d):
        if d is None:
            return today.isoformat()
        # 如果 d 已经是字符串（SQLite 常见情况），直接返回
        if isinstance(d, str):
            return d
        # 如果 d 是日期对象，调用 isoformat()
        if hasattr(d, 'isoformat'):
            return d.isoformat()
        return str(d)

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
            "scheduled_date": safe_iso(item.scheduled_date),
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
            "event_date": safe_iso(marker.event_date),
            "created_at": safe_iso(marker.created_at),
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

    # --- 1. 计算总量统计 (用于卡片显示) ---
    vocab_mastered = (
        db.session.query(func.count(UserVocabularyProgress.id))
        .filter(UserVocabularyProgress.user_id == current_user.id)
        .filter(UserVocabularyProgress.status == "mastered")
        .scalar() or 0
    )
    vocab_learning = (
        db.session.query(func.count(UserVocabularyProgress.id))
        .filter(UserVocabularyProgress.user_id == current_user.id)
        .filter(UserVocabularyProgress.status == "learning")
        .scalar() or 0
    )

    listening_lecture_count = 0
    listening_question_count = 0
    listening_attempts = (
        db.session.query(func.coalesce(func.sum(func.coalesce(UserListeningProgress.attempts, 0)), 0))
        .filter(UserListeningProgress.user_id == current_user.id)
        .scalar() or 0
    )

    progresses = UserListeningProgress.query.filter_by(user_id=current_user.id).all()
    for prog in progresses:
        try:
            if prog.permanent_correct and isinstance(prog.permanent_correct, list):
                listening_lecture_count += len(prog.permanent_correct)
        except (UnicodeDecodeError, ValueError, TypeError):
            prog.permanent_correct = []
            db.session.commit()
        
        answers = prog.answers
        if isinstance(answers, list):
            listening_question_count += len(answers)
        elif isinstance(answers, dict):
            listening_question_count += len(answers.keys())

    english_corner_count = db.session.query(func.count(UserSpeakingSubmission.id)).filter(UserSpeakingSubmission.user_id == current_user.id).scalar() or 0
    academic_scenario_count = db.session.query(func.count(UserScenarioSubmission.id)).filter(UserScenarioSubmission.user_id == current_user.id).scalar() or 0
    shadowing_count = db.session.query(func.count(UserShadowingRecord.id)).filter(UserShadowingRecord.user_id == current_user.id).scalar() or 0
    speaking_submissions = english_corner_count + academic_scenario_count + shadowing_count


    # --- 2. 每日增量统计 (用于时间轴) ---
    daily_vocab = db.session.query(
        func.date(UserVocabularyProgress.last_reviewed_at).label('date'),
        func.count(UserVocabularyProgress.id).label('count')
    ).filter(UserVocabularyProgress.user_id == current_user.id, UserVocabularyProgress.status == "mastered") \
     .group_by(func.date(UserVocabularyProgress.last_reviewed_at)).all()

    daily_listening = db.session.query(
        func.date(UserListeningProgress.last_attempt_at).label('date'),
        func.count(UserListeningProgress.id).label('count')
    ).filter(UserListeningProgress.user_id == current_user.id) \
     .group_by(func.date(UserListeningProgress.last_attempt_at)).all()

    daily_speaking = db.session.query(
        func.date(UserSpeakingSubmission.submitted_at).label('date'),
        func.count(UserSpeakingSubmission.id).label('count')
    ).filter(UserSpeakingSubmission.user_id == current_user.id) \
     .group_by(func.date(UserSpeakingSubmission.submitted_at)).all()

    daily_scenarios = db.session.query(
        func.date(UserScenarioSubmission.submitted_at).label('date'),
        func.count(UserScenarioSubmission.id).label('count')
    ).filter(UserScenarioSubmission.user_id == current_user.id) \
     .group_by(func.date(UserScenarioSubmission.submitted_at)).all()

    daily_shadowing = db.session.query(
        func.date(UserShadowingRecord.created_at).label('date'),
        func.count(UserShadowingRecord.id).label('count')
    ).filter(UserShadowingRecord.user_id == current_user.id) \
     .group_by(func.date(UserShadowingRecord.created_at)).all()


    # --- 3. 构造里程碑 (使用 safe_iso 修复报错) ---
    growth_milestones = []
    
    for d, c in daily_vocab:
        if d and c > 0: 
            growth_milestones.append({"kind": "vocabulary", "title": "Words Mastered", "value": c, "unit": "words", "event_date": safe_iso(d)})
    
    for d, c in daily_listening:
        if d and c > 0: 
            growth_milestones.append({"kind": "listening", "title": "Listening Practice", "value": c, "unit": "sessions", "event_date": safe_iso(d)})

    for d, c in daily_speaking:
        if d and c > 0: 
            growth_milestones.append({"kind": "speaking", "title": "English Corner", "value": c, "unit": "exercises", "event_date": safe_iso(d)})

    for d, c in daily_scenarios:
        if d and c > 0: 
            growth_milestones.append({"kind": "scenario", "title": "Academic Scenario", "value": c, "unit": "sessions", "event_date": safe_iso(d)})

    for d, c in daily_shadowing:
        if d and c > 0: 
            growth_milestones.append({"kind": "shadowing", "title": "Shadowing Practice", "value": c, "unit": "exercises", "event_date": safe_iso(d)})

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
