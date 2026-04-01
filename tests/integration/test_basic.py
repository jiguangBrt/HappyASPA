from tests.conftest import login


def test_app_is_created(app):
    """Ensure the Flask app instance is created."""
    assert app.name == "app"


def test_home_requires_login(client):
    """Home route is protected and should redirect to login when unauthenticated."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers.get("Location", "")


def test_login_success_redirects_to_dashboard(client, user):
    """Valid credentials should redirect to the dashboard."""
    response = login(client, user.username, "password123")
    assert response.status_code == 302
    assert response.headers.get("Location", "").endswith("/")