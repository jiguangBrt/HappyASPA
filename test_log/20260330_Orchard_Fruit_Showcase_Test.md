# Functional Test Report: Orchard Fruit Showcase Bug Fix

## 1. Basic Information

* **Test Subject:** Orchard Fruit Showcase
* **Test Date:** 2026-03-30
* **Test Environment:** Localhost

---

## 2. Test Cases and Execution Results

### **Scene 1: Displaying Fruits in the Showcase**

* **Test content:** Access the Orchard page and verify that fruits in the showcase are displayed correctly without Jinja2 template errors.
* **Execution result:** The page loads successfully. The `UserShowcaseFruit` object correctly accesses the `fruit_type` through the `harvested_fruit` relationship.
* **Status:** [Passed]

---

### **Scene 2: Displaying Fruit Rarity and Stars**

* **Test content:** Verify that fruits of different rarities (Normal, Rare, Legendary) are displayed with the correct border colors and star ratings (1-3 stars).
* **Execution result:** Normal fruits have a blue border and 1 star. Rare fruits have a purple border and 2 stars. Legendary fruits have a gold border and 3 stars.
* **Status:** [Passed]

---

### **Scene 3: Planting and Harvesting Random Fruits**

* **Test content:** Plant a "Magic Seed" and harvest it to verify that it can produce fruits of different rarities based on their drop rates.
* **Execution result:** The seed grows and can be harvested into Normal, Rare, or Legendary fruits of the respective type (Apple, Strawberry, Pineapple).
* **Status:** [Passed]

---

## 3. Test Conclusion

✅ The Jinja2 `UndefinedError` caused by incorrect relationship access in the template has been resolved.

✅ The fruit showcase now correctly displays fruits with their respective rarity borders and star ratings.

✅ The seed system has been updated to use a unified "Magic Seed" that can yield fruits of varying rarities, enhancing the gamification aspect of the Orchard module.

---