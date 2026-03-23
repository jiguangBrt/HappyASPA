# Functional Test Report: Listening Progress Records (Resolved the Conflict)

## 1. Basic Information 
* **Test Subject:** Qiyin Huang
* **Test Date:** 2026-03-22 
* **Test Environment:** Localhost 

## 2. Test Cases and Execution Results 

**Scene 1: Video Display Function (Positive Test)** * **Test content:** Create different accounts to perform various listening exercises and check progress synchronization. 
* **Execution result:** The listening practice progress is correctly isolated and updated for different accounts, accurately reflecting each user's individual practice status. 
* **Status:** [Passed] 

**Scene 2: Fun Question Progress Records** * **Test content:** Choose to "Continue from last progress" and verify the persistence of previous answer results. 
* **Execution result:** Choosing to continue successfully retains previously correct answer records; questions that were skipped or answered incorrectly are prompted again as intended. 
* **Status:** [Passed] 

## 3. Test Conclusion
✅ The listening exercise progress is recorded correctly, including both video playback progress and question-level data. The module is functioning as expected.