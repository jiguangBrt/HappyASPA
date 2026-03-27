from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func  # <--- 新增：用于统计点赞数
from datetime import datetime
from models import db, ForumPost, ForumComment, ForumLike, ForumFavorite, CommentLike, CommentFavorite

import os
import uuid

# 允许上传的文件后缀白名单
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename, allowed_set):
    """检查文件后缀是否在白名单内"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

# ==========================================
# 💰 NEW: 每日首次互动金币奖励小助手
# ==========================================
# 🔍 检查用户今天是否已经完成互动的工具函数
def has_user_interacted_today():
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    
    # 只要发帖数 + 评论数 > 0，就说明今天任务已完成
    posts_count = ForumPost.query.filter(ForumPost.user_id == current_user.id, ForumPost.created_at >= today_start).count()
    comments_count = ForumComment.query.filter(ForumComment.user_id == current_user.id, ForumComment.created_at >= today_start).count()
    
    return (posts_count + comments_count) > 0

def reward_daily_forum_coin():
    """
    检查用户今天是否是第一次发帖或评论。
    因为这个函数会在刚才的帖子/评论保存到数据库 *之后* 调用，
    所以如果今天的总数刚好等于 1，就说明刚刚那条是今天的首发！
    """
    now = datetime.utcnow()
    # 获取今天 UTC 时间的零点
    today_start = datetime(now.year, now.month, now.day)
    
    # 统计今天该用户发了多少帖
    posts_today = ForumPost.query.filter(
        ForumPost.user_id == current_user.id,
        ForumPost.created_at >= today_start
    ).count()
    
    # 统计今天该用户发了多少评论
    comments_today = ForumComment.query.filter(
        ForumComment.user_id == current_user.id,
        ForumComment.created_at >= today_start
    ).count()
    
    # 如果两者加起来刚好等于 1，说明触发了“今日首发”成就！
    if (posts_today + comments_today) == 1:
        if current_user.coins is None:
            current_user.coins = 0  # 兜底旧账号
        current_user.coins += 1
        db.session.commit()
        return True
        
    return False

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')
@forum_bp.context_processor
def inject_category_colors():
    return dict(category_colors={
        'Vocabulary': 'success',   # 绿色
        'Grammar': 'primary',      # 蓝色
        'Listening': 'info',       # 青色
        'Speaking': 'warning',     # 黄色
        'Writing': 'danger',       # 红色
        'Reading': 'dark',         # 黑色
        'General': 'secondary'     # 灰色
    })

def calculate_hot_score(post):
    # 基础互动分 (维持不变)
    base_score = (post.views * 1) + \
                 (len(post.comments) * 3) + \
                 (post.like_count * 5) + \
                 (post.favorite_count * 10)

    now = datetime.utcnow()
    age_timedelta = now - post.created_at
    age_hours = age_timedelta.total_seconds() / 3600

    # ==========================================
    # 👇 算法参数微调区 👇
    # ==========================================
    gravity = 1.2  # 调小重力：老帖衰减变慢，优质内容存活更久 (原为1.5)
    buffer = 10    # 调大缓冲值：新帖不再自带巨大得分倍率 (原为2)
    
    # 最终热度分
    hot_score = base_score / ((age_hours + buffer) ** gravity)
    return hot_score


@forum_bp.route('/')
@login_required
def index():
    tab = request.args.get('tab', 'all')
    category_filter = request.args.get('category')
    sort_by = request.args.get('sort_by', 'hot') 
    board = request.args.get('board', 'discussion') 
    
    saved_comments = []

    # 初始化基础查询
    post_query = db.session.query(ForumPost)

    if tab == 'saved':
        # 👇 NEW: 在查询收藏帖子时，加上 .filter(ForumPost.board == board) 强隔离！
        post_query = post_query.join(ForumFavorite, ForumPost.id == ForumFavorite.post_id)\
            .filter(ForumFavorite.user_id == current_user.id)\
            .filter(ForumPost.board == board)\
            .order_by(ForumFavorite.created_at.desc())
            
        # 👇 NEW: 收藏的评论同样要 join 帖子表，并根据帖子所在的 board 进行强隔离！
        comment_query = db.session.query(ForumComment)\
            .join(CommentFavorite, ForumComment.id == CommentFavorite.comment_id)\
            .join(ForumPost, ForumComment.post_id == ForumPost.id)\
            .filter(CommentFavorite.user_id == current_user.id)\
            .filter(ForumPost.board == board)
            
        if category_filter:
            comment_query = comment_query.filter(ForumPost.category == category_filter)
                
        saved_comments = comment_query.order_by(CommentFavorite.created_at.desc()).all()
        
    else:
        # 常规列表下的分区过滤
        post_query = post_query.filter(ForumPost.board == board)

    # 无论哪个 tab，处理小标签分类过滤 (Vocabulary/Grammar等)
    if category_filter:
        post_query = post_query.filter(ForumPost.category == category_filter)

    posts = post_query.all()

    # 根据 sort_by 进行排序
    if tab != 'saved' and posts:
        if sort_by == 'new':
            posts.sort(key=lambda p: p.created_at, reverse=True)
        else:
            posts.sort(key=calculate_hot_score, reverse=True)

    daily_done = has_user_interacted_today()  # 调用刚才写的检查函数

    return render_template('forum/index.html', 
                           posts=posts, 
                           tab=tab, 
                           saved_comments=saved_comments,
                           current_category=category_filter,
                           sort_by=sort_by,
                           daily_done=daily_done,
                           board=board)

@forum_bp.route('/post/<int:post_id>')
@login_required
def post_detail(post_id):
    post = ForumPost.query.get_or_404(post_id)
    post.views += 1
    db.session.commit()
    return render_template('forum/post.html', post=post)


@forum_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    # 接收前端传来的 board 参数，用于告诉发帖页面“默认选中哪个区”
    current_board = request.args.get('board', 'discussion')
    
    if request.method == 'POST':
        title    = request.form.get('title',    '').strip()
        content  = request.form.get('content',  '').strip()
        category = request.form.get('category', '').strip()
        
        # 👇 NEW: 抓取用户想发到的板块
        board    = request.form.get('board', 'discussion').strip() 

        # ==========================================
        # 🛡️ THE GUARD (发帖守卫核心逻辑)
        # ==========================================
        if board == 'guide' and not current_user.is_guide_qualified:
            flash('Post submission failed: Your English score has not yet reached the guideline standard. Please go to your personal center to complete the verification first!', 'danger')
            # 拦截后，强行把他踢回交流区
            return redirect(url_for('forum.index', board='discussion'))

        if not title or not content:
            flash('Title and content are required.', 'danger')
        else:
            post = ForumPost(
                user_id=current_user.id,
                title=title,
                content=content,
                category=category,
                board=board  # 👇 NEW: 将板块信息正式存入数据库
            )
            db.session.add(post)
            db.session.commit()

            # 👇 检查并发放奖励
            if reward_daily_forum_coin():
                flash('Post published! 🎉 [Daily First] You earned 1 Coin!', 'success')
            else:
                flash('Post created!', 'success')
            return redirect(url_for('forum.post_detail', post_id=post.id))

    return render_template('forum/new_post.html', current_board=current_board)


@forum_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = ForumPost.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    
    # 👇 新增 1：获取前端表单可能传过来的 parent_id
    parent_id = request.form.get('parent_id')
    
    # 如果传了 parent_id 且是数字，就转成整数；否则设为 None（代表这是一条独立评论，不是回复）
    if parent_id and parent_id.isdigit():
        parent_id = int(parent_id)
    else:
        parent_id = None

    if content:
        # 👇 新增 2：在创建评论实例时，把 parent_id 也存进去
        comment = ForumComment(
            post_id=post.id, 
            user_id=current_user.id, 
            content=content,
            parent_id=parent_id  # <--- 加了这一行
        )
        db.session.add(comment)
        db.session.commit()
        
        # 👇 检查并发放奖励
        if reward_daily_forum_coin():
            flash('Post published! 🎉 [Daily First] You earned 1 Coin!', 'success')
        else:
            flash('Comment added!', 'success')
    else:
        flash('Comment cannot be empty.', 'danger')

    return redirect(url_for('forum.post_detail', post_id=post_id))

# ─────────────────────────────────────────────
# 👇 点赞 和 收藏
# ─────────────────────────────────────────────

@forum_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    
    # 检查当前用户是否已经点赞过这篇帖子
    like = ForumLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if like:
        # 如果已经点赞，再次点击就是取消点赞
        db.session.delete(like)
        flash('Unliked the post.', 'info')
    else:
        # 如果没点赞，则添加点赞记录
        new_like = ForumLike(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        
        # 可选：记录用户点赞的行为到日志
        
        flash('Liked the post!', 'success')
        
    db.session.commit()
    
    # 刷新页面，返回原本所在的页面（帖子详情页或首页）
    return redirect(request.referrer or url_for('forum.post_detail', post_id=post.id))


@forum_bp.route('/post/<int:post_id>/favorite', methods=['POST'])
@login_required
def favorite_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    
    # 检查当前用户是否已经收藏
    favorite = ForumFavorite.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if favorite:
        # 取消收藏
        db.session.delete(favorite)
        flash('Removed from favorites.', 'info')
    else:
        # 添加收藏
        new_favorite = ForumFavorite(user_id=current_user.id, post_id=post.id)
        db.session.add(new_favorite)
        flash('Saved to favorites!', 'success')
        
    db.session.commit()
    
    return redirect(request.referrer or url_for('forum.post_detail', post_id=post.id))

# ─────────────────────────────────────────────
# 👇 评论的点赞 和 收藏
# ─────────────────────────────────────────────

@forum_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = ForumComment.query.get_or_404(comment_id)
    like = CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment.id).first()
    
    if like:
        db.session.delete(like)
    else:
        new_like = CommentLike(user_id=current_user.id, comment_id=comment.id)
        db.session.add(new_like)
        
    db.session.commit()
    # 👇 改成这样：直接返回原页面，浏览器会自动保持在当前滚动位置
    return redirect(url_for('forum.post_detail', post_id=comment.post_id) + f'#comment-{comment.id}')


@forum_bp.route('/comment/<int:comment_id>/favorite', methods=['POST'])
@login_required
def favorite_comment(comment_id):
    comment = ForumComment.query.get_or_404(comment_id)
    fav = CommentFavorite.query.filter_by(user_id=current_user.id, comment_id=comment.id).first()
    
    if fav:
        db.session.delete(fav)
    else:
        new_fav = CommentFavorite(user_id=current_user.id, comment_id=comment.id)
        db.session.add(new_fav)
        
    db.session.commit()
    # 👇 改成这样：去掉讨厌的锚点
    return redirect(url_for('forum.post_detail', post_id=comment.post_id) + f'#comment-{comment.id}')

# ─────────────────────────────────────────────
# 👇 帖子的删除
# ─────────────────────────────────────────────

@forum_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    
    # 安全拦截：只有作者本人才能删除
    if post.user_id != current_user.id:
        flash('You can only delete your own posts.', 'danger')
        return redirect(url_for('forum.post_detail', post_id=post.id))
    
    # 因为 models 里设置了 cascade='all, delete-orphan'
    # 这里直接删 post 就能自动清空该帖子的所有评论、点赞和收藏！
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('forum.index'))