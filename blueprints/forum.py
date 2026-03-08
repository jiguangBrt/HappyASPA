from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, ForumPost, ForumComment, UserActivityLog

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')


@forum_bp.route('/')
@login_required
def index():
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()

    log = UserActivityLog(user_id=current_user.id, module='forum', action='viewed')
    db.session.add(log)
    db.session.commit()

    return render_template('forum/index.html', posts=posts)


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

            log = UserActivityLog(user_id=current_user.id, module='forum', action='posted')
            db.session.add(log)
            db.session.commit()

            flash('Post created!', 'success')
            return redirect(url_for('forum.post_detail', post_id=post.id))

    return render_template('forum/new_post.html')


@forum_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = ForumPost.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()

    if content:
        comment = ForumComment(post_id=post.id, user_id=current_user.id, content=content)
        db.session.add(comment)

        log = UserActivityLog(user_id=current_user.id, module='forum', action='commented', ref_id=post_id)
        db.session.add(log)
        db.session.commit()
        flash('Comment added!', 'success')
    else:
        flash('Comment cannot be empty.', 'danger')

    return redirect(url_for('forum.post_detail', post_id=post_id))
