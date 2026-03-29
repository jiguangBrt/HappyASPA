# Functional Test Report: Listening Performance Display (Resolved the Conflict)

## 1. Basic Information 
* **Test Subject:** Qiyin Huang
* **Test Date:** 2026-03-27
* **Test Environment:** Localhost 

## 2. Test Cases and Execution Results 

**Scene 1: Dashboard Field** 
* **Test content:** Do an exercise during the listening process correctly. 
* **Execution result:** The listening growth track on the homepage will increase by 1. (The prompt has not been changed yet)
* **Status:** [Passed] 

**Scene 2: Preparing to rank for fun** 
* **Test content:** Do a fun question in a listening exercise.
* **Execution result:** Regardless of whether the choice is correct or not, the database records that you have done this question, which can serve as a basis for the 'number of questions completed'. 
* **Status:** [Passed] 

**Scene 3: Fix some details of practice operations** 
* **Test content:** Create a new account
* **Execution result:** This account will not have any listening progress from other accounts.
* **Status:** [Passed] 

**Scene 3: Improve the storage of database** 
* **Test content:** Do a listening exercise.
* **Execution result:** The database only creates records for the current exercise questions, and the storage logic of last_position has been corrected, optimizing database storage space.
* **Status:** [Passed]

## 3. Test Conclusion
✅ Accurately reflect the user's listening practice situation through their performance on exercises, optimize user experience and database storage logic.