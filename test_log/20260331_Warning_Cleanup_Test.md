# Functional Test Report: Warning Cleanup & Data Access Refactor

## 1. Basic Information

* **Test Subject:** Sihan Wang
* **Test Date:** 2026-03-31
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: Auth Login Flow (Timezone Refactor)**

* **Test content:** Log in with valid credentials after replacing `datetime.utcnow()` with timezone-aware timestamps.
* **Execution result:** Login succeeds and user is redirected to dashboard as expected.
* **Status:** [Passed]

---

### **Scene 2: Forum Posting (Query.get Replacement)**

* **Test content:** Create a new forum post and ensure it loads correctly after replacing `Model.query.get()` with `db.session.get()`.
* **Execution result:** Post creation succeeds and detail page renders without errors.
* **Status:** [Passed]

---

### **Scene 3: Listening Progress Save (Legacy API Cleanup)**

* **Test content:** Save listening progress and verify progress is persisted.
* **Execution result:** Progress saves correctly, and retrieval works as expected.
* **Status:** [Passed]

---

### **Scene 4: Orchard Flow (Plant + Harvest)**

* **Test content:** Buy seed, plant, and harvest to verify database reads after refactor.
* **Execution result:** Flow works without runtime errors or missing records.
* **Status:** [Passed]

---

### **Scene 5: Regression Check (Integration Tests)**

* **Test content:** Run integration tests to ensure no behavior regression after refactor.
* **Execution result:** Test suite passes; warnings reduced except for third-party compatibility notes.
* **Status:** [Passed]

---

## 3. Test Conclusion

✅ The refactor to timezone-aware timestamps and modern SQLAlchemy access methods does not change user-visible behavior.

✅ Core flows (login, forum posting, listening progress, orchard actions) remain stable after the update.

✅ Test coverage confirms no regression while improving future compatibility.

---