# Functional Test Report: Dashboard Schedule Calendar (Fixed Size, Month Navigation & Modal Save Flow)

## 1. Basic Information 
* **Test Subject:** Sihan Wang
* **Test Date:** 2026-03-20 
* **Test Environment:** Localhost 

## 2. Test Cases and Execution Results 

**Scene 1: Calendar Container Stability (Layout / Regression Test)** * **Test content:** Click multiple dates, open/close the schedule modal, add/remove pending items, and switch between months with different week counts while observing the calendar container size and surrounding elements.
* **Execution result:** Calendar width/height remains constant. The grid does not “jump” when switching months. Interactions do not shift surrounding page elements.
* **Status:** [Passed] 

**Scene 2: Month Navigation Buttons (Functional Test)** * **Test content:** Click “Previous Month” (<) and “Next Month” (>) repeatedly, including cross-year transitions (e.g., Dec 2025 → Jan 2026 and Jan 2026 → Dec 2025). 
* **Execution result:** Both buttons are clickable and responsive. Calendar view updates to the correct month/year, including cross-year changes. 
* **Status:** [Passed] 

**Scene 3: Month/Year Header Label Update (UI Consistency Test)** * **Test content:** After each month navigation click, verify the header label updates immediately to the currently viewed month and year. 
* **Execution result:** Month/year label updates instantly and consistently reflects the active view. 
* **Status:** [Passed]

**Scene 4: Date Selection Behavior on Month Change (Business Logic Test)** * **Test content:** Select a date, then change month forward/backward and verify whether selection persists or clears according to visibility logic. 
* **Execution result:** Selection persists only when the selected date remains visible in the new 6-week grid; otherwise it clears automatically. 
* **Status:** [Passed]

**Scene 5: Modal Add Flow — Pending Draft + Confirm Save (Functional Test)** * **Test content:** Open a date, add one or more items using the in-modal “Add” button (pending), verify they appear as pending, then click “Save changes”. 
* **Execution result:** “Add” only stages items as pending and does not immediately write to the database. “Save changes” commits all pending additions/deletions in one action and closes the modal upon success. 
* **Status:** [Passed]

**Scene 6: Modal Cancel/Close — Discard Pending Changes (Negative / Safety Test)** * **Test content:** Create pending additions and/or mark deletions, then click “Cancel” or close the modal via the top-right close button. Reopen the same date. 
* **Execution result:** Pending changes are discarded on close. Reopening shows only the persisted server data (no leftover drafts or delete marks). 
* **Status:** [Passed]

**Scene 7: English UI Labels Verification (UI Text Test)** * **Test content:** Verify dropdown options and key modal action labels are in English (e.g., Listening/Speaking/Vocabulary/Custom, “Add”, “Save changes”, “Remove/Undo”). 
* **Execution result:** All updated options and action labels display in English as intended. 
* **Status:** [Passed]

## 3. Test Conclusion
✅ The Dashboard Schedule Calendar has been successfully verified for layout stability, month navigation correctness, immediate header updates, and the revised modal workflow. The module is stable and ready for merging.