# Functional test report: Forum category filtering, dynamic badges, and weighted hotness recommendation algorithm.

## 1. Basic Information
* **Test Subject:** Zhu Jiachi
* **Test date:** 2026-03-22
* **Test environment:** Localhost

## 2. Test Cases and Execution Results

**Scene 1: Dynamic Category Badges and Global Filtering (Positive test)**
* **Test content:** Click on different category filter buttons (e.g., Vocabulary, Writing) on the forum index across both "All Posts" and "My Saved" tabs. Verify badge colors.
* **Execution result:** Posts are correctly filtered by the selected category. In the "My Saved" tab, saved comments are also strictly filtered based on their parent post's category. All category badges correctly render their dynamically mapped Bootstrap colors (e.g., green for Vocabulary, red for Writing).
* **Status:** [Passed]

**Scene 2: Weighted Hotness Algorithm Sorting (Logic/Integration Testing)**
* **Test content:** View the default post list in the "All Posts" tab. Evaluate the sorting order of posts with varying ages and interaction metrics (views, likes, comments, favorites).
* **Execution result:** Posts are successfully sorted in memory using the calculate_hot_score function instead of simple chronological order. The time decay formula correctly balances new content visibility with high-quality old content retention (using parameters Gravity = 1.2, Buffer = 10).
* **Status:** [Passed]

**Scene 3: New Post Category Dropdown Rendering (UI/UX Testing)**
* **Test content:** Navigate to the "New Post" creation page and expand the Category dropdown menu.
* **Execution result:** The `<select>` element renders perfectly without rendering empty or broken top rows. The default placeholder "— Select category —" is correctly pre-selected and passes an empty string if no specific category is chosen.
* **Status:** [Passed]

## 3. Test Conclusion
✅ The UI color mapping, global tag filtering system, and the core hotness recommendation algorithm have been successfully verified and passed. The forum's content discovery and visual hierarchy are significantly improved. Ready for merge.