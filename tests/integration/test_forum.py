from datetime import datetime

from models import db, ForumPost, ForumComment, ForumLike, ForumFavorite, User
from tests.conftest import login


def create_post(app, user_id, title="Hello", content="World", board="discussion"):
    with app.app_context():
        post = ForumPost(
            user_id=user_id,
            title=title,
            content=content,
            category="General",
            board=board,
            created_at=datetime.utcnow(),
        )
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        db.session.expunge(post)
        return post_id


def test_forum_requires_login(client):
    """Forum index should redirect to login when unauthenticated."""
    response = client.get("/forum/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers.get("Location", "")


def test_create_post_rewards_daily_coin(client, make_user, app):
    """First post of the day should grant one coin."""
    user = make_user("forumuser", "forum@example.com", coins=0)
    login(client, user.username, "password123")

    response = client.post(
        "/forum/new",
        data={
            "title": "My post",
            "content": "Content",
            "category": "General",
            "board": "discussion",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    with app.app_context():
        post = ForumPost.query.filter_by(user_id=user.id).first()
        assert post is not None
        assert post.title == "My post"
        refreshed = db.session.get(User, user.id)
        assert refreshed.coins == 1


def test_create_post_guard_for_guide_board(client, make_user):
    """Unqualified users cannot post to guide board."""
    user = make_user("noguide", "noguide@example.com", coins=0, is_guide_qualified=False)
    login(client, user.username, "password123")

    response = client.post(
        "/forum/new?board=guide",
        data={
            "title": "Guide post",
            "content": "Content",
            "category": "General",
            "board": "guide",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_add_comment_creates_record(client, user, app):
    """Posting a comment should create a ForumComment."""
    post_id = create_post(app, user.id)
    login(client, user.username, "password123")

    response = client.post(
        f"/forum/post/{post_id}/comment",
        data={"content": "Nice post"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    with app.app_context():
        comment = ForumComment.query.filter_by(post_id=post_id, user_id=user.id).first()
        assert comment is not None


def test_like_toggle(client, user, app):
    """Liking twice should toggle like on/off."""
    post_id = create_post(app, user.id)
    login(client, user.username, "password123")

    response = client.post(f"/forum/post/{post_id}/like")
    assert response.status_code == 302

    with app.app_context():
        assert ForumLike.query.filter_by(post_id=post_id, user_id=user.id).count() == 1

    response = client.post(f"/forum/post/{post_id}/like")
    assert response.status_code == 302

    with app.app_context():
        assert ForumLike.query.filter_by(post_id=post_id, user_id=user.id).count() == 0


def test_favorite_toggle(client, user, app):
    """Favoriting twice should toggle favorite on/off."""
    post_id = create_post(app, user.id)
    login(client, user.username, "password123")

    response = client.post(f"/forum/post/{post_id}/favorite")
    assert response.status_code == 302

    with app.app_context():
        assert ForumFavorite.query.filter_by(post_id=post_id, user_id=user.id).count() == 1

    response = client.post(f"/forum/post/{post_id}/favorite")
    assert response.status_code == 302

    with app.app_context():
        assert ForumFavorite.query.filter_by(post_id=post_id, user_id=user.id).count() == 0


def test_delete_post_only_author(client, make_user, app):
    """Only the author can delete a post."""
    author = make_user("author", "author@example.com")
    other = make_user("other", "other@example.com")
    post_id = create_post(app, author.id)

    login(client, other.username, "password123")
    response = client.post(f"/forum/post/{post_id}/delete", follow_redirects=False)
    assert response.status_code == 302

    with app.app_context():
        assert ForumPost.query.get(post_id) is not None
