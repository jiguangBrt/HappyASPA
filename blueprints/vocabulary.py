import json
import os
import random
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, UserVocabularyProgress

vocabulary_bp = Blueprint("vocabulary", __name__, url_prefix="/vocabulary")

# 加载单词 JSON 文件（新格式：每个单词包含 category 字段）
WORDS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "words.json")
with open(WORDS_JSON_PATH, "r", encoding="utf-8") as f:
    WORDS = json.load(f)

# 分类显示名称映射
CATEGORY_NAMES = {
    "cs": "计算机科学",
    "civil": "土木工程",
    "mech": "机械工程",
    "math": "应用数学",
    "traffic": "交通控制",
    "academic": "学术英语",
}

# 建立 id -> word 映射
WORDS_BY_ID = {word["id"]: word for word in WORDS}

# 按分类组织单词
WORDS_BY_CATEGORY = {}
for word in WORDS:
    cat = word["category"]
    if cat not in WORDS_BY_CATEGORY:
        WORDS_BY_CATEGORY[cat] = []
    WORDS_BY_CATEGORY[cat].append(word)


@vocabulary_bp.route("/")
@login_required
def index():
    return render_template("vocabulary/index.html")


@vocabulary_bp.route("/api/categories")
@login_required
def get_categories():
    categories = []
    for cat_id, words in WORDS_BY_CATEGORY.items():
        categories.append(
            {
                "id": cat_id,
                "name": CATEGORY_NAMES.get(cat_id, cat_id),
                "count": len(words),
            }
        )
    return jsonify(categories)


@vocabulary_bp.route("/api/next")
@login_required
def next_word():
    category = request.args.get("category")
    if not category:
        return jsonify({"error": "Missing category parameter"}), 400

    word_list = WORDS_BY_CATEGORY.get(category)
    if not word_list:
        return jsonify({"error": "Category not found"}), 404

    word = random.choice(word_list)
    progress = UserVocabularyProgress.query.filter_by(
        user_id=current_user.id, word_id=word["id"]
    ).first()

    return jsonify(
        {
            "id": word["id"],
            "word": word["word"],
            "meaning": word.get(
                "meaning", "暂无释义"
            ),  # 增加这一行，若没有 meaning 字段则返回默认值
            "status": progress.status if progress else "new",
        }
    )


@vocabulary_bp.route("/api/record", methods=["POST"])
@login_required
def record_choice():
    data = request.get_json()
    word_id = data.get("word_id")
    known = data.get("known")

    if word_id is None or known is None:
        return jsonify({"error": "Missing word_id or known"}), 400

    # 验证 word_id 是否存在于 JSON 中
    if word_id not in WORDS_BY_ID:
        return jsonify({"error": "Invalid word_id"}), 400

    progress = UserVocabularyProgress.query.filter_by(
        user_id=current_user.id, word_id=word_id
    ).first()

    if not progress:
        progress = UserVocabularyProgress(
            user_id=current_user.id,
            word_id=word_id,
            status="new",
            attempts=0,
            correct_count=0,
        )
        db.session.add(progress)

    progress.attempts += 1
    if known:
        progress.correct_count += 1

    # 简单状态更新规则（可自定义）
    if progress.correct_count >= 5:
        progress.status = "mastered"
    elif progress.attempts >= 3:
        progress.status = "learning"
    else:
        progress.status = "new"

    progress.last_reviewed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"success": True, "new_status": progress.status})
