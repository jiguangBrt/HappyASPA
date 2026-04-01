import re

import pytest
from playwright.sync_api import expect


def _login(page, base_url, username, password):
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')


@pytest.mark.e2e
def test_login_success(page, e2e_server):
    _login(page, e2e_server, "e2euser", "password123")
    expect(page).to_have_url(re.compile(r".*/$"))
    expect(page.get_by_role("link", name="Dashboard")).to_be_visible()


@pytest.mark.e2e
def test_login_failure_shows_message(page, e2e_server):
    _login(page, e2e_server, "e2euser", "wrongpass")
    expect(page.get_by_text("Invalid username or password.")).to_be_visible()


@pytest.mark.e2e
def test_create_forum_post(page, e2e_server):
    _login(page, e2e_server, "e2euser", "password123")

    page.goto(f"{e2e_server}/forum/new")
    page.fill('input[name="title"]', "E2E Post Title")
    page.select_option('select[name="board"]', "discussion")
    page.select_option('select[name="category"]', "General")
    page.fill('textarea[name="content"]', "This is an E2E test post.")
    page.click('button[type="submit"]')

    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="E2E Post Title")).to_be_visible()
