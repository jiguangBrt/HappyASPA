## 🛠️ Tech Stack

This project utilizes a lightweight, modular architecture designed for rapid Agile development and easy deployment.

| Category | Technology | Description |
| --- | --- | --- |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python) ![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?logo=flask) | **Python Flask**: A micro-framework chosen for its simplicity and flexibility, allowing our team to implement features quickly without complex boilerplate. |
| **Frontend** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5) ![JS](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) | **Bootstrap 5 (CDN)**: Used for responsive design and consistent UI components without writing extensive custom CSS. **Jinja2**: Templating engine for dynamic HTML rendering. |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite) | **SQLite**: Serverless and zero-configuration database, ensuring a consistent development environment across all team members' local machines. |
| **Tools** | ![Git](https://img.shields.io/badge/Git-F05032?logo=git) ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visual-studio-code) | **Git/GitHub**: For version control. |

---
## 📂 Project Structure

The project follows a **Flask Blueprint** architecture to ensure modularity and scalability for the agile team.

```text
HappyASPA/
├── app.py                      # Application Entry Point (App Factory, DB Init, Blueprint Registration)
├── models.py                   # SQLAlchemy ORM Models (Defines all 13 database tables)
├── requirements.txt            # Project dependencies and packages
├── blueprints/                 # Backend Logic (Modularized by feature)
│   ├── __init__.py
│   ├── auth.py                 # Authentication routes (/login, /register, /logout)
│   ├── dashboard.py            # Main Dashboard & Learning Progress Tracking
│   ├── vocabulary.py           # Vocabulary module logic
│   ├── flashcards.py           # Flashcards module logic
│   ├── forum.py                # Forum logic (List, View Post, Create Post)
│   ├── listening.py            # Listening practice logic
│   └── writing.py              # Writing exercise logic
└── templates/                  # Frontend Views (Jinja2 Templates)
    ├── base.html               # Base Template (Navbar, Footer, Flash Messages) - Extended by all pages
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── dashboard.html          # Dashboard (Stats cards + Navigation to 5 core modules)
    ├── vocabulary/
    │   └── index.html          # Vocabulary List (With search & difficulty filtering)
    ├── flashcards/
    │   └── index.html          # Flashcard Interface (Pure CSS 3D flip animation)
    ├── forum/
    │   ├── index.html          # Forum Thread List
    │   ├── post.html           # Post Detail View (Content + Comments section)
    │   └── new_post.html       # New Post Creation Form
    ├── listening/
    │   └── index.html          # Listening Exercises (Embedded <audio> + Collapsible transcripts)
    └── writing/
        ├── index.html          # Writing Prompts List
        └── exercise.html       # Writing Workspace (Real-time word count + Submission)
```
---
Team member:
Jiachi Zhu
Yihan Wang
Sihan Wang
Xingzhuo Bao
Jing Lu
Qiyin Huang 

