import os
import sys
import tempfile

import pytest

# Add project root to Python path for imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, User


@pytest.fixture
def app():
    """Create a Flask app configured for testing with a temp SQLite database."""
    app = create_app()

    os.makedirs(app.instance_path, exist_ok=True)
    db_fd, db_path = tempfile.mkstemp(prefix="happyaspa_test_", suffix=".db")
    os.close(db_fd)

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_EXPIRE_ON_COMMIT=False,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(app):
    """Flask test client for HTTP requests."""
    return app.test_client()


@pytest.fixture
def user(app):
    """Create a test user for login flows."""
    with app.app_context():
        user = User(username="tester", email="tester@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)
        return user


def login(client, username, password, follow_redirects=False):
    """Login helper to reduce duplication in tests."""
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=follow_redirects,
    )


@pytest.fixture
def make_user(app):
    """Factory for creating users with custom attributes in tests."""
    def _make_user(
        username,
        email,
        password="password123",
        coins=0,
        is_guide_qualified=False,
    ):
        with app.app_context():
            user = User(username=username, email=email, coins=coins)
            user.set_password(password)
            user.is_guide_qualified = is_guide_qualified
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            db.session.expunge(user)
            return user
    return _make_user
