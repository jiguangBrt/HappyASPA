# Sprint cycle: 2026/4/6 - 2026/4/12

**Team PO**: Ge Hang

**Team SM**: Xingzhuo Bao

**Developers**: Qiyin Huang, Jing Lu, Xingzhuo Bao, Hang Ge, Jiachi Zhu, Sihan Wang, Yihan Wang, Yukun Wang

**Working Hours**: Sun–Fri, 10:00 AM – 2:00 AM (Saturdays off)

## Working Increment:
This sprint completed the transition from feature expansion to **stabilization and experience refinement**: we finalized DIICSU forum customization and invitation-based community flow, polished cross-module UI consistency, and improved data correctness and reliability in Listening and Orchard interactions.

## Specific Incremental Details
| Module | This Sprint Increment | Demo Evidence | Person in charge |
| :--- | :--- | :--- | :--- |
| **Forum & Personal Center** | DIICSU branding overhaul, invitation-code team lifecycle, and end-to-end functional hardening. | 1. Discussion/Guide boards are isolated; Guide posting permission is correctly restricted.<br>2. Hot/New sorting and category filtering work correctly with weighted recommendation logic.<br>3. Team invitation code flow (valid/invalid/expired), leave/dismiss permissions, and personal center team state updates are stable.<br>4. DIICSU visual system (blue palette, banner, mascot, shield watermark) is rendered consistently; pointer blocking issue resolved (`pointer-events: none`). | Jiachi Zhu |
| **Listening** | UI refinement, reference support, note sharing integration, and progress/coin logic stabilization. | 1. Semi-fullscreen/fullscreen layouts are stable, with persistent note-taking and difficult-word sections.<br>2. Source information modal correctly shows platform/author/license/URL; 1-2 star videos and subtitles are displayed and synchronized.<br>3. "Share to Forum" pre-fills title/content correctly, supports multiline/special characters, and disables sharing when notes are empty.<br>4. Correct-answer timestamp now updates immediately and preserves historical dates; only one daily progress record is kept.<br>5. Coin mechanism remains fair: first correct answer grants coin, repeated answers do not. | Qiyin Huang / Jing Lu |
| **Dashboard & Cross-page UI** | Visual consistency upgrade and regression-safe rendering updates. | 1. Overall Guidance overlay updated to uniform light-blue style.<br>2. Dashboard background now includes subtle DIICSU shield watermark, consistent with forum styling.<br>3. Integration checks pass (`23 passed`) with no template/render regressions. | Sihan Wang |
| **Orchard & Profile UI** | Orchard interaction polish and growth-transition stability improvements. | 1. Plant/Harvest buttons are centered per land tile and shown on hover only, with improved visual style and clarity.<br>2. Growth progress display follows `elapsed / total (percent)` and updates in real time.<br>3. Water/fertilizer boosts increase elapsed progress without altering total duration.<br>4. Near-maturity transition is stable: instant 100% lock, delayed refresh, and no timer rollback artifacts. | Xingzhuo Bao |
| **Speaking & Infrastructure** | Speaking interface consistency and deployment-readiness support. | 1. Speaking-related page visuals align better with the unified DIICSU style language in this sprint's UI pass.<br>2. Forum and profile ecosystem verified on production-equivalent environment (`dii.csuu.asia`) and marked deployment-ready for release integration. | Hang Ge / Yihan Wang |
| **QA / DevOps** | Comprehensive cross-module verification and release confidence uplift. | 1. Functional tests executed across forum, listening, dashboard, orchard, and timing/data boundary scenarios.<br>2. All documented sprint test scenes passed, with no critical blocking defects reported.<br>3. Regression-sensitive behaviors (sorting, timestamp logic, rendering consistency) were specifically re-verified. | Jing Lu / Sihan Wang / Yihan Wang |

## Deferred / Dropped Items
| Item | Decision | Reason |
| :--- | :--- | :--- |
| **No major feature drop in Sprint 4** | Deferred only at polish granularity | Sprint 4 focused on stabilization and UI consistency. Remaining items are mostly copy/content polish and further visual tuning rather than architectural changes. |

## Feedback Captured
### Client Positive Feedback
| Area | Positive Feedback |
| :--- | :--- |
| **Forum Structure** | The client is very satisfied with the clear separation between `Discussion` and `Guide`, and believes this structure improves learning-focused community quality. |
| **Product Identity** | The client recognizes the site-wide visual consistency and can clearly perceive this as an English-learning platform. |
| **Mascot Design** | The client especially likes the mascot visuals and finds them memorable and welcoming for users. |
| **Orchard Experience** | The client finds the Orchard/farming gameplay interesting and engaging, with clear value for learner motivation. |

### Potential Improvement Opportunities
| Area | Improvement Opportunity |
| :--- | :--- |
| **Listening Content Quality** | Continue proofreading difficult-word content and provide richer in-context guidance for key vocabulary. |
| **Forum & Community Safety** | Consider stronger anti-abuse constraints (e.g., invitation-code usage limits and optional moderation queue) as community traffic grows. |
| **UI/UX Governance** | Maintain a shared visual checklist for border radius, mascot scale, overlay opacity, and watermark strength to avoid style drift across pages. |
| **Data & Reliability** | Extend automated checks for timestamp/coin boundary logic and multi-day progress integrity to reduce future regression risk. |
