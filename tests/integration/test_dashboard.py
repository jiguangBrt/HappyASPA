from datetime import date, timedelta

import pytest

from models import db, UserJournalMarker, UserScheduleItem
from blueprints.dashboard import calculate_streak, normalize_schedule_title
from tests.conftest import login


def test_normalize_schedule_title_translates_legacy_title():
    """Legacy Chinese schedule titles should be translated for display."""
    translated = normalize_schedule_title("listening", "听听力1篇")
    assert translated == "Listening practice"


def test_calculate_streak_counts_consecutive_days():
    """Streak counts consecutive days up to today."""
    today = date.today()
    dates = [today, today - timedelta(days=1), today - timedelta(days=2)]
    assert calculate_streak(dates) == 3


def test_dashboard_requires_login(client):
    """Dashboard is protected by login_required."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers.get("Location", "")


def test_create_schedule_item_success(client, user, app):
    """Create schedule item returns normalized title for built-in kind."""
    login(client, user.username, "password123")

    payload = {
        "scheduled_date": date.today().isoformat(),
        "kind": "listening",
        "title": "ignored",
        "notes": "focus on lecture 1",
    }
    response = client.post("/schedule", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["kind"] == "listening"
    assert data["title"] == "Listening practice"

    with app.app_context():
        assert UserScheduleItem.query.filter_by(id=data["id"]).first() is not None


def test_create_schedule_item_validation_errors(client, user):
    """Missing fields or invalid kinds return 400."""
    login(client, user.username, "password123")

    response = client.post("/schedule", json={"kind": "listening"})
    assert response.status_code == 400

    response = client.post(
        "/schedule",
        json={
            "scheduled_date": date.today().isoformat(),
            "kind": "invalid",
            "title": "x",
        },
    )
    assert response.status_code == 400


def test_delete_schedule_item(client, user, app):
    """Deleting an existing schedule item returns ok."""
    with app.app_context():
        item = UserScheduleItem(
            user_id=user.id,
            scheduled_date=date.today(),
            kind="custom",
            title="Test",
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    login(client, user.username, "password123")
    response = client.delete(f"/schedule/{item_id}")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

    with app.app_context():
        assert UserScheduleItem.query.filter_by(id=item_id).first() is None


def test_growth_log_create_and_update(client, user, app):
    """Create and update growth logs via API."""
    login(client, user.username, "password123")

    create_payload = {
        "title": "Weekly report",
        "event_date": date.today().isoformat(),
        "kind": "custom",
        "value": 2,
        "unit": "sessions",
    }
    response = client.post("/growth/logs", json=create_payload)
    assert response.status_code == 201
    data = response.get_json()

    update_payload = {
        "title": "Weekly report updated",
        "event_date": date.today().isoformat(),
        "value": 3,
        "unit": "sessions",
        "notes": "extra practice",
    }
    response = client.put(f"/growth/logs/{data['id']}", json=update_payload)
    assert response.status_code == 200
    updated = response.get_json()
    assert updated["title"] == "Weekly report updated"
    assert updated["value"] == 3

    with app.app_context():
        assert UserJournalMarker.query.filter_by(id=data["id"]).first() is not None