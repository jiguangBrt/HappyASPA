# Functional Test Guide: Listening Question Correct Timestamp

## 1. Basic Information

* **Test Subject:** Qiyin Huang
* **Test Date:** 2026-04-09
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: Question answered correctly → timestamp updates immediately**

* **Test content:** Start a brand‑new listening exercise, answer the question correctly. Check question_correct_times in database.
* **Execution result:** Timestamp for question 0 is written in real time after submission. No delay until second question. Date key uses current date (YYYY‑MM‑DD).
* **Status:** [Passed]

---

### **Scene 2: Multiple days practice → historical timestamps are preserved**

* **Test content:** Answer a question correctly on day 1, then answer the same question again on day 2.
* **Execution result:** Both dates are kept in question_correct_times. Only current date is overwritten; old dates are not deleted.
* **Status:** [Passed]

---

### **Scene 3: New exercise creates only ONE progress record**

* **Test content:** Enter a new exercise(or reset it) and answer one question. Check UserListeningProgress table.
* **Execution result:** The most recent record of the day will overwrite the old time record of the day, keeping only one.
* **Status:** [Passed]

---


## 3. Test Conclusion

1. The question correct timestamp now updates immediately when each question is answered correctly, no longer delayed until the next question.

2. The system correctly preserves all historical date records and only overwrites the current day’s timestamp, complying with the design logic.

3. Data migration logic ensures backward compatibility for empty or old‑format data, with no errors for new users or teammates pulling the code.

