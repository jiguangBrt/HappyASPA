# Functional Test Guide: Coin mechanism and listening connection

## 1. Basic Information

* **Test Subject:** Qiyin Huang
* **Test Date:** 2026-04-06
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: Share Notes Button Opens Forum New Post Page**

* **Test content:** In listening practice page, enter some notes, click “Share to Forum” button.
* **Execution result:** The system opens the forum’s new post page with the note content pre-filled in the content area, and a default title (e.g., “Listening Notes: [exercise title]”). The user can edit all fields (title, board, category, content, add images/audio) before publishing.
* **Status:** [Passed]

---

### **Scene 2: Pre-filled Content Matches Current Notes**

* **Test content:** Write a multi‑line note containing special characters (e.g., line breaks, quotes, emojis). Share to forum.
* **Execution result:** The new post page’s content textarea accurately displays the exact note content (preserving line breaks and special characters). Title is pre-filled as described.
* **Status:** [Passed]

---

### **Scene 3: User Can Modify Pre-filled Content Freely**

* **Test content:** On the forum new post page, change the title, select a different board/category, edit the note content, add an image or audio, then publish.
* **Execution result:** The post is successfully created with the user’s custom modifications. No data loss or corruption occurs.
* **Status:** [Passed]

---

### **Scene 4: Empty Notes Disables Share Button**

* **Test content:** Leave the notes textarea empty (or only whitespace). Observe the “Share to Forum” button.
* **Execution result:** The button remains disabled (greyed out) and cannot be clicked. After entering text, the button becomes enabled.
* **Status:** [Passed]

---

### **Scene 5: Cancel or Return from New Post Page**

* **Test content:** Click “Share to Forum”, then on the forum new post page click “Cancel” or navigate back without publishing.
* **Execution result:** The user returns to the listening practice page without creating a post. No error occurs, and the listening progress remains unchanged.
* **Status:** [Passed]

---

### **Scene 6: Share After Page Refresh**

* **Test content:** Save some notes, refresh the listening page, then share the already loaded notes
* **Execution result:** The pre-filled content on the forum new post page still shows the saved notes (not empty). The share button works correctly.
* **Status:** [Passed]

---

## 3. Test Conclusion

1. The note sharing feature successfully redirects users from listening practice to the forum’s new post page with pre‑filled content, while preserving full user editability.

2.  All pre‑filled data (title, content) is accurately transferred, and users can freely modify any field before publishing.

3. The share button is properly disabled when no notes exist, and works reliably after page reloads.

4. This integration enhances the user experience by allowing seamless sharing of listening notes to the forum, encouraging discussion and collaboration.

