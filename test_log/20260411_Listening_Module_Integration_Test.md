# Functional Test Report: Listening Module(Progress Tracking, Layout Features, Coin Mechanism)

## 1. Basic Information
* **Test Subject:** Qiyin Huang
* **Test date:** 2026-04-11
* **Test environment:** https://dii.csuu.asia

## 2. Test Cases and Execution Results

**Scene 1: Listening Practice Progress – Detailed Tracking & Resume Functionality**
* **Test content:** 
- Verify that the system records each question’s history (display previous correct answers)
- Re-asks wrong questions until correct, allows manual reset to fresh state
- Saves overall practice progress (including which question the user is on)
- Reports daily practice counts (total exercises / correct questions) in the personal growth module.
* **Execution result:**

| Sub‑case | Verification point | Status |
|----------|--------------------|--------|
| 1.1 **Show previous correct answers** | When a user answers a question correctly, the system stores the answer record. Upon revisiting the same question (e.g., via later practice), the UI displays “Correct!(Previous Answer)” as a reference. The user is not forced to re‑answer unless they choose reset. | Passed |
| 1.2 **Wrong‑question re‑prompt** | If the user answers incorrectly, the system does **not** mark the question as complete. It keeps presenting the same question (or re-present the questions via later practice) until the user provides the correct answer.  | Passed |
| 1.3 **Manual reset – fresh state** | A “Reset Listening Practice” button is available. After confirmation, all progress for that listening material is cleared: video playback position resets to 0, and all questions become unanswered. The user can then practice again from the beginning as if it were the first time. Reset does **not** affect already earned coins or forum posts. | Passed |
| 1.4 **Resume from last exit** | When the user leaves the listening module (closes browser, navigates away) and later returns, the system restores the exact same state: current question index, video timestamp, answer history for completed questions, and pending wrong‑question state. No data loss occurs even after a full page refresh. | Passed |
| 1.5 **Daily stats in personal growth** | A dedicated section in “Personal Growth” (or similar dashboard) shows for each day: total number of listening exercises completed, number of correct answers. Data updates in real time after each answer. Stats are grouped by calendar day (server time). Resetting a practice does **not** erase historical stats – only new attempts contribute to the current day’s counts. | Passed |
* **Status:** [Passed]

**Scene 2: Listening Layout – Fun Question & Note Sharing to Forum & Key Vocabulary**
* **Test content:** Validate fun quiz appears correctly within the listening layout; ensure users can share notes to the forum and verify the shared content appears in the forum module; Test that key vocabulary items are extracted/displayed during listening, including word and definition.

* **Execution result:**
- Fun quiz renders with proper UI and timing (e.g., after video or between segments); user selections are captured and feedback is displayed without breaking player state.  
- “Share notes to forum” button triggers a compose window; submitted notes (title + content) are successfully posted to the designated forum board with correct author and timestamp.  
- Shared posts link back to the listening section (optional) and do not interfere with existing forum data.
- Key vocabulary list can be displayed correctly and can be scrolled if necessary.
* **Status:** [Passed]

**Scene 3: Listening Coin Mechanism – Reward Rules & Inventory Sync (Economic Integration)**
* **Test content:** Verify that coins are awarded based on the first correct answer to a question. Check that coin changes reflect correctly in the user’s coin balance and that no duplicate/invalid rewards occur.
* **Execution result:**
- Coin rewards are granted only when predefined conditions are met (e.g., first-time correct answer this question). Repeated actions do not give extra coins(including reset).
- After each eligible action, the coin balance updates immediately in the listening module and is consistent with the global coin inventory(on dashboard).
* **Status:** [Passed]

**Scene 4: Cross-Scene Consistency – Progress, Layout, and Coins Working Together (End-to-End Integration)**
* **Test content:** Simulate a complete user journey including reset, daily stats, and resume. Validate all modules update without conflict.
* **Execution result:**
- All actions in sequence produce correct final state: video progress at 100%, answer status completed, daily practice marked done, coin balance increased by expected total, notes forum post appears.
- No data corruption or UI freeze observed.
- Reset clears progress but not coins; daily stats correctly reflect only new attempts after reset(The daily records only store the newest daily practice time record); resume after reset starts from fresh state.
* **Status:** [Passed]

## 3. Test Conclusion
✅ **READY FOR DEPLOYMENT**  
The Listening module, including detailed progress tracking (showing previous correct answers, re‑asking wrong questions, manual reset, resume from last exit, daily statistics in personal growth), layout features (fun quiz, note sharing to forum, key vocabulary), and the coin reward mechanism, has been fully tested in a production-equivalent environment (dii.csuu.asia). All core business rules, data persistence, cross-module integration, and UI behavior meet release expectations. No critical or blocking defects remain.
