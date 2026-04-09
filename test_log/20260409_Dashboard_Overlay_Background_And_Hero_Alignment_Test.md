# Functional Test Guide: Dashboard Overlay Background and Hero Alignment

## 1. Basic Information

* **Test Subject:** Qiyin Huang
* **Test Date:** 2026-04-09
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: Dashboard Overall Guidance Overlay**

* **Test content:** Open dashboard and inspect the Overall Guidance panel overlay style.
* **Execution result:** The previous gradient mask is removed; the panel now uses a uniform light-blue overlay as expected.
* **Status:** [Passed]

---

### **Scene 2: Dashboard Page Background Watermark**

* **Test content:** Check dashboard page background style against forum page style.
* **Execution result:** Dashboard now shows a subtle centered DIICSU shield watermark at page level, matching the forum-style background approach.
* **Status:** [Passed]

---

### **Scene 3: Listening Hero and Filter Placement**

* **Test content:** Open listening page and verify hero/filter layout and mascot rendering.
* **Execution result:** Filter controls are moved into a separate section below hero; mascot keeps natural proportion without compression or stretch.
* **Status:** [Passed]

---

### **Scene 4: Orchard Hero Rounded Corner Alignment**

* **Test content:** Open orchard page and compare hero corner radius with speaking-style rounded header.
* **Execution result:** Orchard hero corner radius is aligned with the target rounded style.
* **Status:** [Passed]

---

### **Scene 5: Regression and Render Validation**

* **Test content:** Run template compile checks and integration tests; generate before/after screenshots.
* **Execution result:** Templates compile successfully; integration tests pass (`23 passed`); before/after and comparison images are generated correctly.
* **Status:** [Passed]

---

## 3. Test Conclusion

1. Dashboard visual update is correctly applied: overall guidance overlay is now uniform light blue, and page background includes the subtle shield watermark.

2. Cross-page consistency is improved: listening hero/filter structure and orchard header corner radius now better match the intended speaking-style UI language.

3. No functional regression was detected through template checks and integration test verification.
