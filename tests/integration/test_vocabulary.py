from datetime import datetime, timezone

from models import db, VocabularyWord, UserVocabularyProgress
from tests.conftest import login


def create_word(app, word, category="cs"):
    with app.app_context():
        vw = VocabularyWord(
            word=word,
            definition="meaning",
            category=category,
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(vw)
        db.session.commit()
        word_id = vw.id
        db.session.expunge(vw)
        return word_id


def test_get_categories(client, user, app):
    """Category endpoint should return counts."""
    create_word(app, "alpha", category="cs")
    create_word(app, "beta", category="cs")
    create_word(app, "gamma", category="math")

    login(client, user.username, "password123")
    response = client.get("/vocabulary/api/categories")
    assert response.status_code == 200
    data = response.get_json()
    counts = {item["id"]: item["count"] for item in data}
    assert counts["cs"] == 2
    assert counts["math"] == 1


def test_next_word_validation(client, user):
    """Missing or unknown category should error."""
    login(client, user.username, "password123")

    response = client.get("/vocabulary/api/next")
    assert response.status_code == 400

    response = client.get("/vocabulary/api/next?category=unknown")
    assert response.status_code == 404


def test_next_word_returns_status(client, user, app):
    """Next word returns status new when no progress exists."""
    word_id = create_word(app, "delta", category="cs")

    login(client, user.username, "password123")
    response = client.get("/vocabulary/api/next?category=cs")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == word_id
    assert data["status"] == "new"


def test_record_choice_updates_progress_and_coins(client, user, app):
    """Recording a choice updates progress and optionally coins."""
    word_id = create_word(app, "epsilon", category="cs")

    login(client, user.username, "password123")
    response = client.post(
        "/vocabulary/api/record",
        json={"word_id": word_id, "known": True, "completed_set": True},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["coins"] == 1

    with app.app_context():
        progress = UserVocabularyProgress.query.filter_by(
            user_id=user.id, word_id=word_id
        ).first()
        assert progress is not None
        assert progress.attempts == 1
        assert progress.correct_count == 1


def test_record_choice_validation_errors(client, user):
    """Missing fields or invalid word should fail."""
    login(client, user.username, "password123")

    response = client.post("/vocabulary/api/record", json={"known": True})
    assert response.status_code == 400

    response = client.post(
        "/vocabulary/api/record",
        json={"word_id": 99999, "known": True},
    )
    assert response.status_code == 400
