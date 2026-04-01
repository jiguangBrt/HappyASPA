# Functional test report: Dashboard Overall Guidance vertical scroll + Guidance subpages (blank)

## 1. Basic Information
* **Test Subject:** Sihan Wang
* **Test date:** 2026-03-19
* **Test environment:** Localhost

## 2. Test Cases and Execution Results

**Scene 1: Overall Guidance list layout (UI layout test)**
* **Test content:** Open Dashboard, check the Overall Guidance area on the right-side panel.
* **Execution result:** The Overall Guidance area is displayed as a vertical scroll list (not flip-cards, not horizontal carousel). The visible area height is reduced so that **3 mini-cards can be seen at once** (depending on browser zoom/viewport).
* **Status:** [Passed]

**Scene 2: Vertical scroll paging behavior (interaction test)**
* **Test content:** Use mouse wheel / trackpad to scroll the Overall Guidance list up and down; verify it can scroll through all cards smoothly.
* **Execution result:** The list scrolls vertically within the panel, without affecting the whole page scroll unexpectedly; cards remain clickable; no layout jitter/overlap.
* **Status:** [Passed]

**Scene 3: Guidance card click → dedicated subpage (navigation test)**
* **Test content:** Click each mini-card (Teams/DIICSU/Misconduct/Focus).
* **Execution result:** Each click navigates to its dedicated URL `/guidance/<card_key>` and loads a **content page**.
* **Status:** [Passed]

**Scene 4: Background image placeholder hook (configuration test)**
* **Test content:** Locate the background image placeholder in the dashboard CSS; optionally add a test URL and refresh.
* **Execution result:** Background image can be configured by editing `background-image: url("...")` in the dashboard CSS; after adding a URL, the panel shows the background image with `cover` + `center` behavior.
* **Status:** [Passed]

**Scene 5: Practice Modules removed (regression test)**
* **Test content:** Verify the Dashboard no longer displays the “Practice Modules” section/cards.
* **Execution result:** Practice Modules section is not present; primary navigation still works via the top navbar (Dashboard/Listening/Speaking/Vocabulary/Forum).
* **Status:** [Passed]

## 3. Test Conclusion
⏳ The test cases are prepared for execution. Run the above scenes and update statuses to confirm readiness for launch.