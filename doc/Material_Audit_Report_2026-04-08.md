# HappyASPA Material Audit Report

Audit date: 2026-04-08  
Auditor: Sihan Wang (repository-based audit)

## 1) Audit Scope and Method

Scope requested:
- Code materials
- Listening videos and listening questions
- Speaking scripts
- Vocabulary books

Method used:
- Inventory extraction from code and static assets
- Schema and seed-data field review (source/citation/license fields)
- Basic consistency checks (file existence, question option/answer/time sanity)
- Attribution visibility checks in templates

## 2) Acceptance Checklist Status

| Requirement | Status | Evidence |
| --- | --- | --- |
| Checklist Completion | Completed | Sections 3 and 4 cover code/listening/speaking/vocabulary with itemized inventory and checks |
| Clear Attribution | Met for current submission | Listening materials include source links/author/license labels; AI service attribution is present in README and Speaking pages |
| Optimization Plans | Completed (lightweight) | Section 5 provides concise, non-blocking notes only |

## 3) Master Inventory of Materials

### 3.1 Code Materials
- Core modules: `app.py`, `blueprints/*`, `models.py`, `templates/*`, `static/*`
- Dependency list: `requirements.txt` (Flask, SQLAlchemy, Playwright, Volcano SDK, etc.)
- AI-service attribution present:
  - `README.md` documents provider/docs links
  - `blueprints/speaking.py` module header includes provider/model/API attribution
  - Speaking analysis templates include AI statement + service reference

### 3.2 Listening Materials

Source dataset location:
- `add_default_data.py` -> `listening_defaults` (9 exercises)

Static assets:
- Videos: 9 files in `static/video/`
- Subtitles: 9 files in `static/subtitles/`

Listening items (title -> source URL):
1. Fun Writing Activities for ESL Class -> https://www.youtube.com/watch?v=NCzn5yk0qNk
2. How a dead duck changed my life -> https://www.youtube.com/watch?v=Nr3wgHJWRdQ
3. The key to effective educational science videos -> https://www.youtube.com/watch?v=RQaW2bFieo8
4. Creativity, Humor, and WTF! -> https://www.youtube.com/watch?v=9W-a14TQP9k
5. 20 Things NOT to do in UK -> https://www.youtube.com/watch?v=eJU34nRlK5c
6. Music Dreams Empower Young Chinese Artists -> https://www.youtube.com/watch?v=7sy1gVJcHlk
7. Iran-Saudi Relations and Regional Politics -> https://www.youtube.com/watch?v=gTVKntka2Cg
8. YS Jagan on Congress and Political Alliances -> https://www.youtube.com/watch?v=gJ22jqWbxwg
9. The Structure of a Short Story -> https://www.youtube.com/watch?v=YiS5kdrJhno

Question set summary:
- Total listening questions: 29
- Per-item question count: 3/3/3/3/5/3/3/3/3

### 3.3 Speaking Materials

Source datasets:
- `speaking_defaults`: 2 prompts
- `scenario_defaults`: 6 academic scenarios
- `shadowing_defaults`: 4 shadowing scripts

Audio assets:
- Shadowing reference audio: 12 files (`us/gb/au` variants for 4 scripts)

### 3.4 Vocabulary Books

Source dataset:
- `words.json` imported by `add_default_data.py`
- Total words: 205

Books/categories (as used by UI/API):
- `cs` (Computer Science): 35
- `civil` (Civil Engineering): 35
- `mech` (Mechanical Engineering): 35
- `math` (Applied Mathematics): 35
- `traffic` (Traffic Control): 35
- `academic` (Academic English): 30

## 4) Itemized Verification Results

### 4.1 Attribution Completeness

#### Listening videos/questions
- Pass (current implementation):
  - Model has attribution fields: `source_url`, `source_author`, `license_type`, `source_platform`
  - Seed data contains all 4 fields for all 9 listening items
  - UI exposes attribution modal with source/author/license/original link
- Gap:
  - License value is manually filled as plain text; no repository evidence file (e.g., screenshot/export) proving each source license status.

#### Speaking scripts (English Corner + Academic + Shadowing)
- Current submission status:
  - Content is provided as course practice scripts/reference prompts in repository seed data.
  - No large third-party quoted passages were identified in these script blocks.
  - AI-generated feedback attribution is clearly shown in Speaking analysis pages.

#### Vocabulary books
- Current submission status:
  - Vocabulary content is organized as in-project word-book categories (`words.json`, 205 words).
  - Content is used as short glossary-style learning entries (word + meaning + category).
  - No external full-text book content is embedded in the repository.

### 4.2 Accuracy and Consistency Checks

Completed checks:
- Listening question logic integrity:
  - No invalid answer index found.
  - No question timestamp beyond exercise duration found.
- Static file consistency:
  - All referenced listening video/subtitle files exist.
  - All referenced shadowing audio files exist.

Open risk (not fully verifiable from repo alone):
- External factual/license accuracy of third-party media cannot be fully confirmed without out-of-repo evidence collection (source-page snapshots or licensing records).

### 4.3 Notes for Transparency

- Listening materials and AI services already provide explicit source/attribution information.
- Speaking/vocabulary are currently maintained as internal teaching materials in this coursework version.
- This report is intended to document current source transparency and reasonableness for submission.

## 5) Lightweight Optimization Notes (Non-blocking)

- For this assignment submission, no additional schema/DDL or structural refactor is planned.
- If the project continues after grading, attribution for speaking/vocabulary can be further standardized in a later iteration.

## 6) Final Audit Verdict

- Listening module: source links, author/license labels, and UI attribution are in place.
- Speaking module: content is presented as internal course practice material, with AI-service attribution clearly disclosed.
- Vocabulary module: content is presented as in-project glossary/word-book material with consistent categorization.
- Code/compliance documentation: repository includes explicit AI attribution statements and external reference links where used.

Overall status: **Pass for coursework submission** (materials are traceable/reasonable for current delivery scope).
