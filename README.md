## 🛠️ Tech Stack

This project utilizes a lightweight, modular architecture designed for rapid Agile development and easy deployment.

| Category | Technology | Description |
| --- | --- | --- |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python) ![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask) | **Python Flask**: A micro-framework chosen for its simplicity and flexibility, allowing our team to implement features quickly without complex boilerplate. |
| **Frontend** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5) ![JS](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) | **Bootstrap 5 (CDN)**: Used for responsive design and consistent UI components without writing extensive custom CSS. **Jinja2**: Templating engine for dynamic HTML rendering. |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite) | **SQLite**: Serverless and zero-configuration database, ensuring a consistent development environment across all team members' local machines. |
| **Tools** | ![Git](https://img.shields.io/badge/Git-F05032?logo=git) ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visual-studio-code) | **Git/GitHub**: For version control. |

---
## 📂 Project Structure

The project follows a **Flask Blueprint** architecture to ensure modularity and scalability for the agile team.

```text
HappyASPA/
├── app.py                      # Application Entry Point (App Factory, DB Init, Blueprint Registration)
├── models.py                   # SQLAlchemy ORM Models
├── requirements.txt            # Project dependencies and packages
├── add_default_data.py         # CLI command script to add default data
├── blueprints/                 # Backend Logic (Modularized by feature)
│   ├── __init__.py
│   ├── auth.py                 # Authentication routes (/login, /register, /logout)
│   ├── dashboard.py            # Main Dashboard & Learning Progress Tracking
│   ├── forum.py                # Forum logic (List, View Post, Create Post)
│   ├── listening.py            # Listening practice logic
│   ├── speaking.py             # Speaking practice logic (with audio/video upload)
│   └── vocabulary.py           # Vocabulary module logic
├── migrations/                 # Database migrations (Flask-Migrate / Alembic)
├── static/                     # Static assets (subtitles, videos, etc.)
├── templates/                  # Frontend Views (Jinja2 Templates)
│   ├── base.html               # Base Template (Navbar, Footer, Flash Messages)
│   ├── auth/                   # Login and Register pages
│   ├── dashboard.html          # Dashboard view
│   ├── forum/                  # Forum pages
│   ├── listening/              # Listening exercise pages
│   ├── speaking/               # Speaking exercise pages
│   └── vocabulary/             # Vocabulary pages
└── uploads/                    # User uploaded files (e.g., speaking recordings)
```

---
## 🚀 Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HappyASPA
   ```

2. **Create a virtual environment** (Recommended)
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   The project uses Flask-Migrate. Apply the migrations to set up your database:
   ```bash
   flask db upgrade
   ```

5. **Add default data** (Optional but recommended)
   ```bash
   flask add-default-data
   ```

---
## 🏃 Run

To start the development server, simply run:

```bash
python app.py
```


The application will be available at `http://127.0.0.1:5000/`.

---
## 🧪 Test

Currently, you can run tests using `pytest` or Python's built-in `unittest` framework if test files are added. 
To run existing tests (if any are added in the future):

```bash
# Install pytest if not already installed
pip install pytest

# Run tests
pytest
```

---
## 🤝 How to Contribute

We welcome contributions! Please follow these steps to contribute to the project:

1. **Fork the repository** and clone it locally.
2. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and ensure they follow the project's coding standards.
4. **Test your changes** locally to ensure nothing is broken.
5. **Commit your changes** with clear and descriptive commit messages:
   ```bash
   git commit -m "Add: your feature description"
   ```
6. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Submit a Pull Request** to the `main` branch of the original repository. Please provide a detailed description of your changes in the PR.

---
## 👥 Team member
Jiachi Zhu
Yihan Wang
Sihan Wang
Xingzhuo Bao
Jing Lu
Qiyin Huang 
Hang Ge
