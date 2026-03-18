# Sprint cycle: 2026/3/17 - 2026/3/22

**Team PO**: Jing Lu

**Team SM**: Qiyin Huang

**Developers**: Qiyin Huang, Jing Lu, Xingzhuo Bao, Hang Ge, Jiachi Zhu, Sihan Wang, Yihan Wang, Yukun Wang

**Working Hours**: Sun–Fri, 10:00 AM – 12:00 AM (Saturdays off)


## Sprint Goal: 
Complete the basic setup of core functional modules and database iterations, optimize some advanced features.

## Selected User Story & Task Plan
<table>
  <thead>
    <tr>
      <th>module</th>
      <th>user story</th>
      <th>task description</th>
      <th>person in charge</th>
    </tr>
  </thead>
  <tbody>
    <!-- Listening -->
    <tr>
      <td rowspan="3">Listening</td>
      <td>As a user, I want to be able to check the listening exercise progress and records so that I can plan my learning on my performance.</td>
      <td>Implement listening progress records. </td>
      <td>Qiyin Huang</td>
    </tr>
    <tr>
      <td>As a user, I can filter exercises by difficulty so that I can match my skill level.</td>
      <td>Find more audios or videos, and implement the classification of listening exercises. </td>
      <td>Jing Lu</td>
    </tr>
    <tr>
      <td>As a user, I can access a larger collection of listening exercises so that I can improve my listening skills with more diverse materials.</td>
      <td>Expand listening exercises repository. </td>
      <td>Jing Lu</td>
    </tr>
    <!-- Speaking -->
    <tr>
      <td rowspan="2">Speaking</td>
      <td>As a language learner, I want to access scenario-based simulation exercises within my speaking practice, so that I can simulate real-life conversations and improve the effectiveness of my training.</td>
      <td>Implement a scenario simulation module with text-based system interaction. </td>
      <td>Hang Ge, Xingzhuo Bao</td>
    </tr>
    <tr>
     <td>As a student, I want the system to track and display the total number of audio recordings I have submitted，so that I can visually monitor my speaking practice progress and learning performance over time.</td>
     <td>Count the number of audios uploaded by users. </td>
     <td>Xingzhuo Bao</td>
    <!-- Forum -->
    <tr>
      <td rowspan="3">Forum</td>
      <td>As a user browsing the forum, I want to see the most popular posts and comments surfaced to the top based on community engagement, so that I can quickly discover the highest-quality and most discussed content.</td>
      <td>Design the popular recommendation algorithm for posts and their comments (based on the current data of likes, collections, and views). </td>
      <td>Jiachi Zhu</td>
    </tr>
    <tr>
      <td>As an authenticated user reading the discussion, I want to be able to "like" and "collect" (save) specific comments, so that I can show my appreciation for valuable insights and easily find them later in my personal profile.</td>
      <td>Add corresponding like and collection buttons for the comments. </td>
      <td>Jiachi Zhu</td>
    </tr>
    <tr>
      <td>As a user engaging in a discussion, I want to be able to reply directly to a specific comment under a post, so that I can have focused, threaded conversations without losing the context of who I am talking to.<br>As a user participating in a thread, I want my reply to clearly indicate which specific comment I am responding to, so that other readers can understand the relationship between our messages.</td>
      <td>Reply to the comments of the corresponding post and comment. </td>
      <td>Jiachi Zhu</td>
    </tr>
    <!-- Vocabulary -->
    <tr>
      <td rowspan="1">Vocabulary</td>
      <td>As a language learner who is memorizing vocabulary, I want an intuitive, clear, and aesthetically pleasing vocabulary learning interface so that I can efficiently browse flashcards, view definitions, and perform memorization tasks.</td>
      <td>Design and implement the vocabulary learning interface prototype. </td>
      <td>Yukun Wang</td>
    </tr>
    <!-- Standardize the testing process -->
    <tr>
      <td rowspan="1">Standardize the testing process</td>
      <td>As a developer, I want to be able to automate the testing of my code, so that I can quickly iterate on new versions.</td>
      <td>Design and implement CI automatic test. </td>
      <td>Yihan Wang</td>
    </tr>
    <!-- Dashboard -->
    <tr>
      <td rowspan="2">Dashboard</td>
      <td>1. As a user navigating the site, I want to be taken to a dedicated subpage after a redirect occurs, so that I have the correct context and can seamlessly find the specific information or next steps I need.<br>2. As a user viewing the interface, I want the information cards to be displayed in an adjusted and optimized layout, so that I can more easily scan, read, and understand the key details presented on them.<br>3. As a user reading the content, I want the references section to be clearly organized and structured, so that I can easily locate, verify, or explore the source materials without confusion.</td>
      <td>Change the homepage introduction card to a clickable link card. </td>
      <td>Sihan Wang</td>
    </tr>
    <tr>
      <td>1. As a user, I want the calendar to maintain a consistent and fixed size after I interact with it, so that the page layout remains stable and my workflow is not disrupted by unexpected visual shifts.<br>2. As a user, I want to be able to navigate between different months on the calendar (e.g., using "next" and "previous" buttons), so that I can easily view and select dates in the past or future.</td>
      <td>1. Fixed a bug where the calendar size would change after use.<br>2. Fixed a bug where the calendar month could not be changed. </td>
      <td>Sihan Wang</td>
    </tr>
  </tbody>
</table>