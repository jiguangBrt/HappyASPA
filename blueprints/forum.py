from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func  # <--- 新增：用于统计点赞数

from models import db, ForumPost, ForumComment, ForumLike, ForumFavorite, CommentLike, CommentFavorite

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')


@forum_bp.route('/')
@login_required
def index():
    tab = request.args.get('tab', 'all')
    saved_comments = [] # 预设为空列表

    if tab == 'saved':
        # 查收藏的帖子
        posts = db.session.query(ForumPost)\
            .join(ForumFavorite, ForumPost.id == ForumFavorite.post_id)\
            .filter(ForumFavorite.user_id == current_user.id)\
            .order_by(ForumFavorite.created_at.desc())\
            .all()
        # 查收藏的评论
        saved_comments = db.session.query(ForumComment)\
            .join(CommentFavorite, ForumComment.id == CommentFavorite.comment_id)\
            .filter(CommentFavorite.user_id == current_user.id)\
            .order_by(CommentFavorite.created_at.desc())\
            .all()
    else:
        # 默认查所有帖子
        posts = db.session.query(ForumPost)\
            .outerjoin(ForumLike, ForumPost.id == ForumLike.post_id)\
            .group_by(ForumPost.id)\
            .order_by(func.count(ForumLike.id).desc(), ForumPost.created_at.desc())\
            .all()

    # 把 saved_comments 也传给前端
    return render_template('forum/index.html', posts=posts, tab=tab, saved_comments=saved_comments)


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
    if request.method == 'POST':
        title    = request.form.get('title',    '').strip()
        content  = request.form.get('content',  '').strip()
        category = request.form.get('category', '').strip()

        if not title or not content:
            flash('Title and content are required.', 'danger')
        else:
            post = ForumPost(
                user_id=current_user.id,
                title=title,
                content=content,
                category=category
            )
            db.session.add(post)
            db.session.commit()

            flash('Post created!', 'success')
            return redirect(url_for('forum.post_detail', post_id=post.id))

    return render_template('forum/new_post.html')


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