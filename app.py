import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User
from dotenv import load_dotenv
from time_utils import is_system_tz_beijing

load_dotenv()


def create_app():
    app = Flask(__name__)

    # ── Configuration ────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///happyaspa.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['VOLC_TOS_BUCKET'] = os.environ.get('VOLC_TOS_BUCKET', 'english-practice-audio')
    app.config['VOLC_TOS_ENDPOINT'] = os.environ.get('VOLC_TOS_ENDPOINT', 'tos-cn-beijing.volces.com')
    app.config['VOLC_TOS_REGION'] = os.environ.get('VOLC_TOS_REGION', 'cn-beijing')

    # 新增：文件上传配置
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads/speaking')  # 音频存储路径
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 最大50MB
    app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg', 'm4a','webm'}  # 允许的音频格式

    # 创建上传目录（如果不存在）
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)
    migrate = Migrate(app, db)

    if not is_system_tz_beijing():
        app.logger.warning("System timezone is not UTC+8 (Asia/Shanghai). Datetimes are stored as naive UTC; display should be converted explicitly.")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Blueprints ───────────────────────────────────────────────────────────
    from blueprints.auth       import auth_bp
    from blueprints.dashboard  import dashboard_bp
    from blueprints.vocabulary import vocabulary_bp
    from blueprints.forum      import forum_bp
    from blueprints.listening  import listening_bp
    from blueprints.speaking   import speaking_bp
    from blueprints.orchard    import orchard_bp
    
    # 👇 1. 导入你刚刚写的 team 蓝图
    from blueprints.team       import team_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vocabulary_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(listening_bp)
    app.register_blueprint(speaking_bp)
    app.register_blueprint(orchard_bp)

    # ── CLI Commands ─────────────────────────────────────────────────────────
    from add_default_data import add_default_data
    app.cli.add_command(add_default_data)
    
    # 👇 2. 注册 team 蓝图
    app.register_blueprint(team_bp)

    # ── Database initialisation ───────────────────────────────────────────────
    # db.create_all() 已由 Flask-Migrate 的 flask db upgrade 负责管理，此处保留注释
    # with app.app_context():
    #     db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    # 设置服务器最大接收体积：16MB (留1MB给文本，5MB图片+10MB语音)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.run(debug=True)
