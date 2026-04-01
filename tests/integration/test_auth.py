from models import User
from tests.conftest import login


def test_login_failure(client, user):
    """Invalid credentials should keep user on login page."""
    response = login(client, user.username, "wrongpass", follow_redirects=True)
    assert response.status_code == 200


def test_login_success(client, user):
    """Valid credentials should redirect to dashboard."""
    response = login(client, user.username, "password123")
    assert response.status_code == 302
    assert response.headers.get("Location", "").endswith("/")


def test_register_success(client, app):
    """New user should be created on register."""
    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "secret123",
            "confirm": "secret123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    with app.app_context():
        assert User.query.filter_by(username="newuser").first() is not None


def test_register_duplicate_username(client, user):
    """Duplicate usernames should be rejected."""
    response = client.post(
        "/auth/register",
        data={
            "username": user.username,
            "email": "dup@example.com",
            "password": "secret123",
            "confirm": "secret123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_register_duplicate_email(client, user):
    """Duplicate emails should be rejected."""
    response = client.post(
        "/auth/register",
        data={
            "username": "another",
            "email": user.email,
            "password": "secret123",
            "confirm": "secret123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200