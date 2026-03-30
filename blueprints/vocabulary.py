import random
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, UserVocabularyProgress, VocabularyWord

vocabulary_bp = Blueprint('vocabulary', __name__, url_prefix='/vocabulary')

# 分类显示名称映射（可选，用于前端英文显示）
CATEGORY_NAMES = {
    'cs': 'Computer Science',
    'civil': 'Civil Engineering',
    'mech': 'Mechanical Engineering',
    'math': 'Applied Mathematics',
    'traffic': 'Traffic Control',
    'academic': 'Academic English'
}

@vocabulary_bp.route('/')
@login_required
def index():
    return render_template('vocabulary/index.html')

@vocabulary_bp.route('/api/categories')
@login_required
def get_categories():
    # 从数据库获取所有分类及其单词数量
    categories = db.session.query(
        VocabularyWord.category,
        func.count(VocabularyWord.id).label('count')
    ).group_by(VocabularyWord.category).all()

    result = []
    for cat, count in categories:
        result.append({
            'id': cat,
            'name': CATEGORY_NAMES.get(cat, cat),  # 优先使用英文映射
            'count': count
        })
    return jsonify(result)

@vocabulary_bp.route('/api/next')
@login_required
def next_word():
    category = request.args.get('category')
    if not category:
        return jsonify({'error': 'Missing category parameter'}), 400

    # 从数据库查询该分类的所有单词
    words = VocabularyWord.query.filter_by(category=category).all()
    if not words:
        return jsonify({'error': 'Category not found'}), 404

    # 随机选择一个单词
    word = random.choice(words)
    
    progress = UserVocabularyProgress.query.filter_by(
        user_id=current_user.id, word_id=word.id
    ).first()

    return jsonify({
        'id': word.id,
        'word': word.word,
        'meaning': word.definition,   # 注意：我们将 meaning 存入了 definition 字段
        'status': progress.status if progress else 'new'
    })

@vocabulary_bp.route('/api/record', methods=['POST'])
@login_required
def record_choice():
    data = request.get_json()
    word_id = data.get('word_id')
    known = data.get('known')
    completed_set = data.get('completed_set', False)

    if word_id is None or known is None:
        return jsonify({'error': 'Missing word_id or known'}), 400

    # 验证单词是否存在
    word = VocabularyWord.query.get(word_id)
    if not word:
        return jsonify({'error': 'Invalid word_id'}), 400

    progress = UserVocabularyProgress.query.filter_by(
        user_id=current_user.id, word_id=word_id
    ).first()

    if not progress:
        progress = UserVocabularyProgress(
            user_id=current_user.id,
            word_id=word_id,
            status='new',
            attempts=0,
            correct_count=0
        )
        db.session.add(progress)

    progress.attempts += 1
    if known:
        progress.correct_count += 1

    # 状态更新规则（可自定义）
    if progress.correct_count >= 5:
        progress.status = 'mastered'
    elif progress.attempts >= 3:
        progress.status = 'learning'
    else:
        progress.status = 'new'

    progress.last_reviewed_at = datetime.utcnow()

# ⭐ 每5个词奖励1 coin
    if completed_set:
        if current_user.coins is None:
            current_user.coins = 0
        current_user.coins += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'new_status': progress.status,
        'coins': current_user.coins
    })