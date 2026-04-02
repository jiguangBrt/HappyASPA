import os
import sys
import tempfile

import pytest

# Add project root to Python path for imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, User


def _get_test_database_uri():
    """
    Resolve a safe test database URI.
    Priority:
    1) TEST_DATABASE_URL (explicit test DB)
    2) Temporary sqlite file (auto-generated)
    """
    test_db = os.environ.get("TEST_DATABASE_URL")
    if test_db:
        return test_db, None

    os.makedirs("instance", exist_ok=True)
    db_fd, db_path = tempfile.mkstemp(prefix="happyaspa_test_", suffix=".db")
    os.close(db_fd)
    return f"sqlite:///{db_path}", db_path


def _assert_safe_test_db(uri, temp_path):
    # Never allow tests to run against production DATABASE_URL by accident.
    prod_db = os.environ.get("DATABASE_URL")
    if prod_db and uri == prod_db:
        raise RuntimeError("Refusing to run tests against DATABASE_URL. Set TEST_DATABASE_URL.")

    # If not using a temp DB, require explicit TEST_DATABASE_URL to be set.
    if temp_path is None and not os.environ.get("TEST_DATABASE_URL"):
        raise RuntimeError("Non-temp test DB requires TEST_DATABASE_URL to be set explicitly.")


@pytest.fixture
def app():
    """Create a Flask app configured for testing with a safe test database."""
    app = create_app()

    os.makedirs(app.instance_path, exist_ok=True)
    db_uri, temp_path = _get_test_database_uri()
    _assert_safe_test_db(db_uri, temp_path)

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_EXPIRE_ON_COMMIT=False,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)


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
