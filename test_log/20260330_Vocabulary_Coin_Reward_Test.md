# Functional Test Report: Vocabulary Coin Reward System

## 1. Basic Information

* **Test Subject:** Jing Lu
* **Test Date:** 2026-03-30
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: Basic Vocabulary Learning Flow**

* **Test content:** Complete vocabulary tasks by marking words as "Known" or "Unknown".
* **Execution result:** The system correctly records user progress (attempts, correct_count, status).
* **Status:** [Passed]

---

### **Scene 2: Coin Reward Trigger (5 Words per Set)**

* **Test content:** Mark 5 words as "Known".
* **Execution result:** After every 5 correctly recognized words, the system rewards +1 coin.
* **Status:** [Passed]

---

### **Scene 3: No Reward for Incorrect or Incomplete Sets**

* **Test content:** Mix "Known" and "Unknown" selections within 5 words.
* **Execution result:** Coins are not rewarded unless 5 "Known" words are completed.
* **Status:** [Passed]

---

### **Scene 4: Frontend Feedback (Encouragement Modal)**

* **Test content:** Complete a set of 5 known words.
* **Execution result:** Encouragement modal appears immediately after completing the set.
* **Status:** [Passed]

---

### **Scene 5: Database Persistence (Coins Storage)**

* **Test content:** Complete multiple sets of 5 words and refresh the page.
* **Execution result:** Coin count is correctly stored and persists in the database.
* **Status:** [Passed]


---

## 3. Test Conclusion

✅ The vocabulary coin reward system correctly implements gamification by rewarding users after completing each set of 5 known words.

✅ The system ensures accurate progress tracking, proper database persistence, and stable API responses.

✅ The feature enhances user motivation while maintaining consistency and reliability in both frontend and backend operations.

---
