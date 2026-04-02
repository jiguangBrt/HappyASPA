# Functional Test Guide: Orchard Plant Button and Growth Flow

## 1. Basic Information

* **Test Subject:** Jiachi Zhu
* **Test Date:** 2026-04-02
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: Plant Button Positioning and Hover Visibility**

* **Test content:** Verify that `Plant` and `Harvest` buttons are no longer fixed below the land image, but centered on the land and only visible on hover.
* **Execution result:** Buttons appear at the center of each corresponding land tile; default state is hidden; hover interaction reveals buttons correctly without overlap or misalignment.
* **Status:** [Passed]

---

### **Scene 2: Plant Button Visual Styling**

* **Test content:** Check updated `Plant` button UI (gradient color, rounded style, icon, hover animation, transparency behavior).
* **Execution result:** The button style is consistent with the orchard theme, hover feedback is smooth, and visual clarity remains acceptable under transparent overlay settings.
* **Status:** [Passed]

---

### **Scene 3: Planting Flow and Progress Display Logic**

* **Test content:** Plant seeds and validate growth progress display format as `elapsed / total (percent)`.
* **Execution result:** Progress bar advances according to elapsed ratio; text updates in real time using elapsed time against total growth duration; percentage reflects current growth state.
* **Status:** [Passed]

---

### **Scene 4: Item Effect Rule (Water/Fertilizer)**

* **Test content:** Use water/fertilizer during growth and verify that item usage increases elapsed growth progress without reducing total required growth duration.
* **Execution result:** Total growth duration remains unchanged; elapsed progress increases after item use; remaining time decreases accordingly; behavior matches updated design.
* **Status:** [Passed]

---

### **Scene 5: Theoretical Maturity Transition**

* **Test content:** Trigger item usage when current progress + item boost reaches/exceeds full maturity, then observe transition behavior.
* **Execution result:** The accelerate modal closes immediately; progress bar reaches 100%; text is locked to `total / total (100%)`; page waits 3 seconds before refreshing into mature state.
* **Status:** [Passed]

---

### **Scene 6: Timer Override and Refresh Stability**

* **Test content:** Confirm that the periodic timer does not overwrite forced 100% text during the maturity transition window.
* **Execution result:** No regression observed. The timer lock prevents temporary rollback to pre-boost elapsed text; transition remains stable until refresh.
* **Status:** [Passed]

---

## 3. Test Conclusion

1. The orchard interaction update successfully improves UX by centering action buttons and using hover-based visibility, preventing layout breakage after UI rearrangement.

2. Growth display logic is now clearer (`elapsed / total`) and consistent with user perception of planting progress.

3. Item-boost maturity transition behavior is stable: instant modal exit, deterministic 100% progress display, and delayed refresh produce a smoother visual handoff into harvest-ready state.

