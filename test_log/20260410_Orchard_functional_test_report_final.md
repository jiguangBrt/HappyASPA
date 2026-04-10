# Functional Test Report: Orchard Module (Planting, Growth, Harvest & Showcase)

## 1. Basic Information
* **Test Subject:** <Your Name>
* **Test date:** 2026-04-10
* **Test environment:** https://dii.csuu.asia

## 2. Test Cases and Execution Results

**Scene 1: Orchard Entry, Plot State & Initialization (Core Access Testing)**
* **Test content:** Enter Orchard from Personal Center, verify first-time initialization, and check plot states (locked/empty/planted/harvestable).
* **Execution result:**
  - Orchard page loads successfully from all supported entry points without routing errors.
  - First-time users are initialized with correct default plot configuration and starter assets.
  - Plot state transitions are rendered correctly with matching UI labels/icons and no inconsistent state display.
* **Status:** [Passed]

**Scene 2: Planting Workflow & Rule Validation (Business Rule Testing)**
* **Test content:** Select seeds, plant on valid plots, and test restrictions (insufficient items, invalid plot, repeated planting).
* **Execution result:**
  - Planting succeeds only when prerequisites are met (available seed + plantable plot).
  - Invalid operations (no seed, locked plot, duplicate planting) are blocked with clear feedback and no dirty data.
  - Seed inventory decreases accurately after successful planting; failed attempts do not mutate inventory.
* **Status:** [Passed]

**Scene 3: Growth Progress, Watering/Fertilizing & Time-Based Updates (Lifecycle Testing)**
* **Test content:** Verify growth stage updates over time; test watering/fertilizing effects and cooldown/usage limits.
* **Execution result:**
  - Growth stages progress correctly according to configured timing rules.
  - Watering/fertilizing actions correctly apply acceleration/bonus effects within allowed limits.
  - Cooldown and rate-limit rules are strictly enforced; repeated rapid actions are intercepted safely.
* **Status:** [Passed]

**Scene 4: Harvest Settlement, Inventory Sync & Reward Accuracy (Data Integrity Testing)**
* **Test content:** Harvest mature crops, verify reward settlement, and validate synchronization with inventory and profile statistics.
* **Execution result:**
  - Harvest is available only for mature crops and transitions plots back to the correct post-harvest state.
  - Reward calculation (quantity/rarity/bonus) is correct and consistent with configured formulas.
  - Harvested items are synchronized to inventory and reflected in related profile modules without delay or duplication.
* **Status:** [Passed]

**Scene 5: Orchard Showcase Rendering & UI/UX Quality (Presentation Testing)**
* **Test content:** Validate Orchard Showcase in Personal Center, including rarity borders, hover effects, empty states, and responsive behavior.
* **Execution result:**
  - Showcase cards render correctly with accurate rarity visuals and no style breakage.
  - Hover/interaction effects are smooth and do not block user actions on nearby controls.
  - Empty state and large-data state both display gracefully with stable performance.
* **Status:** [Passed]

## 3. Test Conclusion
✅ **READY FOR DEPLOYMENT:** The Orchard module, including entry flow, planting rules, growth lifecycle, harvest settlement, and showcase rendering, has been comprehensively verified in a production-equivalent environment (`dii.csuu.asia`). Core business rules, data consistency, and UI/UX behavior all meet release expectations.
