import random
import string
from datetime import datetime, timezone
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
    word = db.session.get(VocabularyWord, word_id)
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

    progress.last_reviewed_at = datetime.now(timezone.utc)

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


# 辅助函数：生成拼图矩阵
def generate_puzzle(words, size=15):
    grid = [['' for _ in range(size)] for _ in range(size)]
    actual_placed = []

    for word_obj in words:
        word = word_obj.word.upper().replace(" ", "")  # 转大写并去空格
        placed = False
        for _ in range(50):  # 尝试50次放置
            direction = random.choice(['H', 'V'])  # H: 水平, V: 垂直
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)

            # 检查是否越界
            if direction == 'H' and col + len(word) > size: continue
            if direction == 'V' and row + len(word) > size: continue

            # 检查冲突
            can_place = True
            for i in range(len(word)):
                r, c = (row, col + i) if direction == 'H' else (row + i, col)
                if grid[r][c] != '' and grid[r][c] != word[i]:
                    can_place = False
                    break

            if can_place:
                for i in range(len(word)):
                    r, c = (row, col + i) if direction == 'H' else (row + i, col)
                    grid[r][c] = word[i]
                actual_placed.append(word)
                placed = True
                break

    # 填充随机字母
    for r in range(size):
        for c in range(size):
            if grid[r][c] == '':
                grid[r][c] = random.choice(string.ascii_uppercase)
    return grid, actual_placed


@vocabulary_bp.route('/api/puzzle')
@login_required
def get_puzzle():
    # 随机获取5个单词
    words = VocabularyWord.query.order_by(func.random()).limit(5).all()
    grid, placed_words = generate_puzzle(words)

    return jsonify({
        'grid': grid,
        'target_words': placed_words
    })