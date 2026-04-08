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
| Clear Attribution | Partially met | Listening has source fields and UI attribution modal; speaking/vocabulary lack source metadata fields |
| Optimization Plans | Completed | Section 5 provides remediation actions with owners and deadlines |

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
- Fail (citation completeness):
  - Models do not include source/citation/license fields for speaking content objects.
  - Seed data has no source attribution fields for speaking/scenario/shadowing items.
  - UI shows reference scripts and reference audio but not source provenance.

#### Vocabulary books
- Fail (citation completeness):
  - Vocabulary model only stores lexical content fields; no source/citation/license fields.
  - `words.json` entries include id/word/meaning/category only; no source provenance.
  - UI markets categories as "Word Books" but does not display book/source info.

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

### 4.3 Explicit Missing Attribution Items

Missing/insufficiently documented items:
1. All 2 English Corner prompts: no source/citation metadata.
2. All 6 Academic Scenarios: no source/citation metadata.
3. All 4 Shadowing scripts and 12 reference audios: no source/citation metadata.
4. All 6 vocabulary books (205 words): no source/citation metadata.
5. No centralized material registry (`material_id`, `source`, `license`, `authorization`, `owner`, `verification_date`) in repository.

## 5) Remediation Plan (Owners + Deadlines)

| Priority | Action | Owner | Deadline | Deliverable |
| --- | --- | --- | --- | --- |
| P0 | Add source metadata fields for speaking/scenario/shadowing/vocabulary tables (URL/author/license/platform/authorization_note) | Backend Owner | 2026-04-12 | Migration + model update + API serialization |
| P0 | Add attribution display in Speaking and Vocabulary pages (similar to listening attribution modal) | Frontend Owner | 2026-04-14 | UI attribution panel for every script/book |
| P0 | Build a material source registry file (`doc/material_source_registry.csv`) for all current assets | Content Owner | 2026-04-14 | Complete inventory with source links and authorization status |
| P1 | Verify each listening source license claim and capture evidence (screenshot/export + checked date) | Content Owner + PM | 2026-04-16 | Evidence pack linked from registry |
| P1 | Content QA round for listening transcripts/questions (two-reviewer signoff) | Listening Lead | 2026-04-18 | QA checklist with corrections log |
| P1 | Content QA round for speaking scripts and vocabulary definitions | Speaking Lead + Vocabulary Lead | 2026-04-18 | Accuracy review log + replacement proposals |
| P2 | Add CI guard: fail build if new material is added without required attribution fields | DevOps Owner | 2026-04-20 | CI job + validation script |
| P2 | Add repository-level legal docs (`LICENSE`, `NOTICE`/third-party attributions) | PM + Tech Lead | 2026-04-20 | Compliance docs in repo root |

## 6) Final Audit Verdict

- Listening module: mostly compliant on attribution structure and display, pending external license evidence archiving.
- Speaking module: not compliant for source/citation completeness.
- Vocabulary module: not compliant for source/citation completeness.
- Code/compliance documentation: partially compliant (AI attribution exists, but no centralized material registry and no repo-level license/notice artifacts).

Overall status: **Partially Pass** (high-priority remediation required before claiming full citation/compliance readiness).
