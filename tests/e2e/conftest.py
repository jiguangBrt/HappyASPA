import os
import socket
import tempfile
import threading
import time

import pytest
from werkzeug.serving import make_server

from app import create_app
from models import db, User


def _get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def e2e_server():
    app = create_app()

    os.makedirs(app.instance_path, exist_ok=True)
    db_fd, db_path = tempfile.mkstemp(prefix="happyaspa_e2e_", suffix=".db")
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
        user = User(username="e2euser", email="e2e@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    port = _get_free_port()
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    server.shutdown()
    thread.join(timeout=5)

    with app.app_context():
        db.session.remove()
        db.drop_all()

    if os.path.exists(db_path):
        os.remove(db_path)
