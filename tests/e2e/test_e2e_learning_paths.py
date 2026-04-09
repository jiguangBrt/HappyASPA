import re

import pytest
from playwright.sync_api import expect


def _login(page, base_url, username, password):
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')


@pytest.mark.e2e
def test_listening_notes_flow(page, e2e_server):
    _login(page, e2e_server, "e2euser", "password123")

    page.goto(f"{e2e_server}/listening")
    page.wait_for_function("document.querySelectorAll('.btn-start').length > 0")
    page.locator(".btn-start").first.click()
    expect(page).to_have_url(re.compile(r".*/listening/practice/\d+(\?.*)?$"))
    page.wait_for_function("typeof window.saveNotesToServer === 'function'")
    page.fill("#notesTextarea", "E2E note: key idea")
    with page.expect_response(
        lambda r: "/listening/api/notes" in r.url and r.request.method == "POST" and r.status == 200
    ):
        page.click("#saveNotesBtn")


@pytest.mark.e2e
def test_vocabulary_learning_flow(page, e2e_server):
    _login(page, e2e_server, "e2euser", "password123")

    page.goto(f"{e2e_server}/vocabulary")
    page.wait_for_selector(".category-card[data-cat-id='academic']", timeout=10000)
    page.click(".category-card[data-cat-id='academic']")

    expect(page.locator("#learningSection")).to_be_visible()
    page.wait_for_function(
        "document.getElementById('wordDisplay').innerText.trim() !== '--'"
    )

    page.click("#knownBtn")
    expect(page.locator("#meaningContainer")).to_be_visible()

    page.click("#nextBtn")
    expect(page.locator("#knownBtn")).to_be_visible()
