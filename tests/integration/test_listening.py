from datetime import datetime, timezone

from models import db, ListeningExercise, UserListeningProgress, User
from tests.conftest import login


def create_exercise(app, questions=None):
    with app.app_context():
        ex = ListeningExercise(
            title="Test",
            description="desc",
            questions=questions or [{"answer": 1}, {"answer": 0}],
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(ex)
        db.session.commit()
        exercise_id = ex.id
        db.session.expunge(ex)
        return exercise_id


def test_save_progress_requires_exercise_id(client, user):
    """Missing exercise_id should return 400."""
    login(client, user.username, "password123")
    response = client.post("/listening/progress", json={})
    assert response.status_code == 400


def test_save_progress_exercise_not_found(client, user):
    """Unknown exercise should return 404."""
    login(client, user.username, "password123")
    response = client.post("/listening/progress", json={"exercise_id": 999})
    assert response.status_code == 404


def test_save_progress_updates_stats(client, user, app):
    """Saving progress should update answers and user counters."""
    exercise_id = create_exercise(app)
    login(client, user.username, "password123")

    response = client.post(
        "/listening/progress",
        json={
            "exercise_id": exercise_id,
            "last_position": 12.5,
            "answers": {"0": 1, "1": 1},
            "completed": True,
            "duration_spent": 30,
        },
    )
    assert response.status_code == 200

    with app.app_context():
        progress = UserListeningProgress.query.filter_by(
            user_id=user.id, exercise_id=exercise_id
        ).first()
        assert progress is not None
        assert progress.completed is True
        assert 0 in (progress.permanent_correct or [])
        assert progress.last_position == 12.5

        refreshed = db.session.get(User, user.id)
        assert refreshed.total_correct_questions >= 1
        assert refreshed.total_listening_duration >= 30


def test_get_progress_exists_flag(client, user, app):
    """Progress endpoint should indicate existence."""
    exercise_id = create_exercise(app)
    login(client, user.username, "password123")

    response = client.get(f"/listening/progress/{exercise_id}")
    assert response.status_code == 200
    assert response.get_json()["exists"] is False

    client.post(
        "/listening/progress",
        json={"exercise_id": exercise_id, "answers": {"0": 1}},
    )

    response = client.get(f"/listening/progress/{exercise_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["exists"] is True
    assert 0 in data["permanent_answered"]
