# Functional Test Guide: Coin mechanism and listening connection

## 1. Basic Information

* **Test Subject:** Qiyin Huang
* **Test Date:** 2026-04-02
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: First Correct Answer Rewards 1 Coin**

* **Test content:** Complete a listening exercise and answer a question correctly for the first time.
* **Execution result:** The system grants +1 coin to the user’s total coins; The coin display in the top right corner of the homepage will update in real time.
* **Status:** [Passed]

---

### **Scene 2: No Additional Coin for Repeated Correct Answers on Same Question**

* **Test content:** Answer the same question correctly again by resetting the exercise.
* **Execution result:** No additional coin is awarded for subsequent correct answers to the same question. Ordinary correct information correctly displayed.
* **Status:** [Passed]

---

### **Scene 3: Incorrect Answer Allows Retry (Bug Fix Verification)**

* **Test content:** Answer a question incorrectly; then attempt to answer it again.
* **Execution result:** The system does not lock the question; the user can select a different option and submit again. After a correct retry, the coin reward is granted as per Scene 1.
* **Status:** [Passed]


---

## 3. Test Conclusion

1. The listening module correctly integrates the coin reward system: each first-time correct answer grants 1 coin, and repeated correct answers do not yield extra coins.

2.  The bug that previously locked incorrectly answered questions has been fixed – users can now retry wrong answers freely.

3. These improvements enhance user engagement and fairness in the listening practice workflow. All core functionalities are stable and ready for release.

