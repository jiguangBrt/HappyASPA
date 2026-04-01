from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ─────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(80),  unique=True, nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password_hash  = db.Column(db.String(256), nullable=False)
    avatar_url     = db.Column(db.String(256), nullable=True)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login_at  = db.Column(db.DateTime, nullable=True)

    # ==========================================
    # 💰 NEW: 经济系统与每日任务字段
    # ==========================================
    coins                 = db.Column(db.Integer, default=0)
    last_checkin_date     = db.Column(db.Date, nullable=True)
    last_post_reward_date = db.Column(db.Date, nullable=True)

    # ==========================================
    # 🎓 NEW: 英语成绩认证与权限字段
    # ==========================================
    gaokao_score       = db.Column(db.Float, nullable=True)   # 高考英语
    ielts_score        = db.Column(db.Float, nullable=True)   # 雅思
    toefl_score        = db.Column(db.Integer, nullable=True) # 托福
    gre_score          = db.Column(db.Integer, nullable=True) # GRE
    is_guide_qualified = db.Column(db.Boolean, default=False) # 指导区发帖资格标签

    # relationships
    vocab_progress      = db.relationship('UserVocabularyProgress', backref='user', lazy=True)
    flashcard_progress  = db.relationship('UserFlashcardProgress',  backref='user', lazy=True)
    forum_posts         = db.relationship('ForumPost',              backref='author', lazy=True)
    forum_comments      = db.relationship('ForumComment',           backref='author', lazy=True)
    forum_likes         = db.relationship('ForumLike',              backref='user',   lazy=True)
    forum_favorites     = db.relationship('ForumFavorite',          backref='user',   lazy=True) 
    listening_progress  = db.relationship('UserListeningProgress',  backref='user',   lazy=True)
    writing_submissions = db.relationship('UserWritingSubmission',  backref='user',   lazy=True)
    activity_logs       = db.relationship('UserActivityLog',        backref='user',   lazy=True)
    created_flashcards  = db.relationship('Flashcard', backref='creator', lazy=True)
    schedule_items      = db.relationship('UserScheduleItem',       backref='user',   lazy=True)
    journal_markers     = db.relationship('UserJournalMarker',      backref='user',   lazy=True)
    
    # 关联用户的学术情景录音提交
    scenario_submissions = db.relationship('UserScenarioSubmission', backref='user', lazy=True)
    
    # 🌟 NEW: 关联用户的跟读练习录音记录
    shadowing_records    = db.relationship('UserShadowingRecord',    backref='user', lazy=True)

    # 累计正确题目数（首次做对计数的题目总数）
    total_correct_questions = db.Column(db.Integer, default=0, nullable=False)
    
    # 累计学习时长（秒）
    total_listening_duration = db.Column(db.Integer, default=0, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    
# ─────────────────────────────────────────────
# Vocabulary
# ─────────────────────────────────────────────
class VocabularyWord(db.Model):
    __tablename__ = 'vocabulary_words'

    id               = db.Column(db.Integer, primary_key=True)
    word             = db.Column(db.String(100), nullable=False)
    phonetic         = db.Column(db.String(100), nullable=True)
    definition       = db.Column(db.Text,        nullable=False)
    example_sentence = db.Column(db.Text,        nullable=True)
    difficulty       = db.Column(db.Integer,     default=1)   # 1–5
    category         = db.Column(db.String(50),  nullable=True)
    created_at       = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))

    progress = db.relationship('UserVocabularyProgress', backref='word', lazy=True)

class UserVocabularyProgress(db.Model):
    __tablename__ = 'user_vocabulary_progress'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id         = db.Column(db.Integer, db.ForeignKey('vocabulary_words.id'), nullable=False)
    status          = db.Column(db.String(20), default='new')  # new / learning / mastered
    attempts        = db.Column(db.Integer,  default=0)
    correct_count   = db.Column(db.Integer,  default=0)
    last_reviewed_at = db.Column(db.DateTime, nullable=True)

# ─────────────────────────────────────────────
# Flashcards
# ─────────────────────────────────────────────
class Flashcard(db.Model):
    __tablename__ = 'flashcards'

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    front_content = db.Column(db.Text,        nullable=False)
    back_content  = db.Column(db.Text,        nullable=False)
    category      = db.Column(db.String(50),  nullable=True)
    created_by    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    progress = db.relationship('UserFlashcardProgress', backref='flashcard', lazy=True)

class UserFlashcardProgress(db.Model):
    __tablename__ = 'user_flashcard_progress'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'),      nullable=False)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.id'), nullable=False)
    is_bookmarked = db.Column(db.Boolean, default=False)
    times_viewed  = db.Column(db.Integer, default=0)
    last_viewed_at = db.Column(db.DateTime, nullable=True)

# ─────────────────────────────────────────────
# Forum
# ─────────────────────────────────────────────
class ForumPost(db.Model):
    __tablename__ = 'forum_posts'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    content    = db.Column(db.Text,        nullable=False)
    category   = db.Column(db.String(50),  nullable=True)
    # 👇 NEW: 新增一个字段专门管大分区（默认发到交流区 discussion）
    board      = db.Column(db.String(50),  default='discussion')
    views      = db.Column(db.Integer,     default=0)
    created_at = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    image_url = db.Column(db.String(256), nullable=True) # 👈 存图片路径
    audio_url = db.Column(db.String(256), nullable=True) # 👈 存语音路径
    
    comments  = db.relationship('ForumComment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes     = db.relationship('ForumLike',    backref='post', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('ForumFavorite', backref='post', lazy=True, cascade='all, delete-orphan') 

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        from models import ForumLike
        return ForumLike.query.filter_by(post_id=self.id, user_id=user.id).first() is not None

    def is_favorited_by(self, user):
        if not user or not user.is_authenticated:
            return False
        from models import ForumFavorite
        return ForumFavorite.query.filter_by(post_id=self.id, user_id=user.id).first() is not None

    @property
    def like_count(self):
        from models import ForumLike
        return ForumLike.query.filter_by(post_id=self.id).count()

    @property
    def favorite_count(self):
        from models import ForumFavorite
        return ForumFavorite.query.filter_by(post_id=self.id).count()


class ForumComment(db.Model):
    __tablename__ = 'forum_comments'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    content    = db.Column(db.Text,     nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    parent_id  = db.Column(db.Integer, db.ForeignKey('forum_comments.id'), nullable=True)

    replies    = db.relationship(
        'ForumComment', 
        backref=db.backref('parent', remote_side=[id]), 
        lazy=True, 
        cascade='all, delete-orphan'
    )

    likes      = db.relationship('CommentLike', backref='comment', lazy=True, cascade='all, delete-orphan')
    favorites  = db.relationship('CommentFavorite', backref='comment', lazy=True, cascade='all, delete-orphan')

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        from models import CommentLike
        return CommentLike.query.filter_by(comment_id=self.id, user_id=user.id).first() is not None

    def is_favorited_by(self, user):
        if not user or not user.is_authenticated:
            return False
        from models import CommentFavorite
        return CommentFavorite.query.filter_by(comment_id=self.id, user_id=user.id).first() is not None

    @property
    def like_count(self):
        from models import CommentLike
        return CommentLike.query.filter_by(comment_id=self.id).count()

    @property
    def favorite_count(self):
        from models import CommentFavorite
        return CommentFavorite.query.filter_by(comment_id=self.id).count()

class CommentLike(db.Model):
    __tablename__ = 'comment_likes'

    id         = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('forum_comments.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class CommentFavorite(db.Model):
    __tablename__ = 'comment_favorites'

    id         = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('forum_comments.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ForumLike(db.Model):
    __tablename__ = 'forum_likes'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class ForumFavorite(db.Model):
    __tablename__ = 'forum_favorites'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ─────────────────────────────────────────────
# Listening
# ─────────────────────────────────────────────
class ListeningExercise(db.Model):
    __tablename__ = 'listening_exercises'

    id               = db.Column(db.Integer, primary_key=True)
    title            = db.Column(db.String(200), nullable=False)
    description      = db.Column(db.Text,        nullable=True)
    audio_url        = db.Column(db.String(256),  nullable=True)
    transcript       = db.Column(db.Text,         nullable=True)
    difficulty       = db.Column(db.Integer,      default=1)   # 1–5
    category         = db.Column(db.String(50),   nullable=True)
    duration_seconds = db.Column(db.Integer,      nullable=True)
    created_at       = db.Column(db.DateTime,     default=lambda: datetime.now(timezone.utc))
    subtitle_url     = db.Column(db.String(256),  nullable=True)
    accent = db.Column(db.String(50), nullable=True)
    questions = db.Column(db.JSON, nullable=True)  
    key_vocab = db.Column(db.JSON, nullable=True)

    progress = db.relationship('UserListeningProgress', backref='exercise', lazy=True)


class UserListeningProgress(db.Model):
    __tablename__ = 'user_listening_progress'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'),                nullable=False)
    exercise_id     = db.Column(db.Integer, db.ForeignKey('listening_exercises.id'),  nullable=False)
    completed       = db.Column(db.Boolean, default=False)
    # score           = db.Column(db.Float,   nullable=True)
    attempts        = db.Column(db.Integer, default=0)
    last_attempt_at = db.Column(db.DateTime, nullable=True)

    last_position   = db.Column(db.Float, nullable=True)           # current play position
    # two_thirds_count = db.Column(db.Integer, default=0)           # count of finishing exercises
    answers         = db.Column(db.JSON, nullable=True)           # record of answer result
    notes = db.Column(db.Text, nullable=True)  # 用户笔记区域
    notes_history = db.Column(db.JSON, default=list)   # 历史笔记列表

    # 永久记录：已做过的题目索引列表（无论对错，永不重置）
    permanent_answered = db.Column(db.JSON, default=lambda: list())

    # 永久记录：已正确答对的题目索引列表（首次正确才记录）
    permanent_correct = db.Column(db.JSON, default=lambda: list())
    
# ─────────────────────────────────────────────
# Writing
# ─────────────────────────────────────────────
class WritingExercise(db.Model):
    __tablename__ = 'writing_exercises'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    prompt       = db.Column(db.Text,        nullable=False)
    type         = db.Column(db.String(50),  default='essay')  # essay/paragraph/email/report
    difficulty   = db.Column(db.Integer,     default=1)        # 1–5
    word_limit   = db.Column(db.Integer,     nullable=True)
    model_answer = db.Column(db.Text,        nullable=True)
    created_at   = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))

    submissions = db.relationship('UserWritingSubmission', backref='exercise', lazy=True)


class UserWritingSubmission(db.Model):
    __tablename__ = 'user_writing_submissions'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'),                nullable=False)
    exercise_id  = db.Column(db.Integer, db.ForeignKey('writing_exercises.id'),  nullable=False)
    content      = db.Column(db.Text,    nullable=False)
    word_count   = db.Column(db.Integer, nullable=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    feedback     = db.Column(db.Text,    nullable=True)   # 预留 AI 反馈字段
    score        = db.Column(db.Float,   nullable=True)

# ─────────────────────────────────────────────
# Speaking (English Corner)
# ─────────────────────────────────────────────
class SpeakingExercise(db.Model):
    __tablename__ = 'speaking_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=False)  
    difficulty = db.Column(db.Integer, default=1)  
    category = db.Column(db.String(50), nullable=True)  
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    creator = db.relationship('User', backref='created_exercises')

    submissions = db.relationship('UserSpeakingSubmission', backref='exercise', lazy=True)

class UserSpeakingSubmission(db.Model):
    __tablename__ = 'user_speaking_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('speaking_exercises.id'), nullable=False)
    audio_filename = db.Column(db.String(256), nullable=False)  
    duration_seconds = db.Column(db.Float, nullable=True)  
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    feedback = db.Column(db.Text, nullable=True)  
    score = db.Column(db.Float, nullable=True)  


# ==========================================
# 🎓 Academic Scenarios (学术情景模拟)
# ==========================================
class AcademicScenario(db.Model):
    __tablename__ = 'academic_scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=True)      # e.g., "Office Hours", "Negotiation"
    difficulty = db.Column(db.Integer, default=1)           # 1-5
    
    background = db.Column(db.Text, nullable=False)         # 情景背景
    role = db.Column(db.Text, nullable=False)               # 你的角色
    tasks = db.Column(db.JSON, nullable=True)               # 需要完成的任务清单
    reference_material = db.Column(db.Text, nullable=True)  # 参考资料/线索
    prep_time_seconds = db.Column(db.Integer, default=120)  # 建议准备时间
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 建立和提交记录的关系
    submissions = db.relationship('UserScenarioSubmission', backref='scenario', lazy=True)

class UserScenarioSubmission(db.Model):
    __tablename__ = 'user_scenario_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('academic_scenarios.id'), nullable=False)
    
    audio_filename = db.Column(db.String(256), nullable=False)  
    duration_seconds = db.Column(db.Float, nullable=True)  
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # AI 评估专属字段
    score_vocabulary = db.Column(db.Float, nullable=True)
    score_logic = db.Column(db.Float, nullable=True)
    score_politeness = db.Column(db.Float, nullable=True)
    overall_feedback = db.Column(db.Text, nullable=True)


# ==========================================
# 🎙️ NEW: 跟读练习模型 (Shadowing Practice)
# ==========================================
class ShadowingExercise(db.Model):
    __tablename__ = 'shadowing_exercises'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    focus = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    duration_str = db.Column(db.String(20)) # e.g., "~0:30"
    word_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    audios = db.relationship('ShadowingAudio', backref='exercise', lazy=True, cascade='all, delete-orphan')
    
    # 🌟 NEW: 关联用户的录音记录
    records = db.relationship('UserShadowingRecord', backref='exercise', lazy=True, cascade='all, delete-orphan')

class ShadowingAudio(db.Model):
    __tablename__ = 'shadowing_audios'
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('shadowing_exercises.id'), nullable=False)
    accent_code = db.Column(db.String(10), nullable=False) # 'us', 'gb', 'au'
    audio_url = db.Column(db.String(255), nullable=False)  # '/static/audio/shadowing/...'

# 🌟 NEW: 用户跟读录音表
class UserShadowingRecord(db.Model):
    __tablename__ = 'user_shadowing_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('shadowing_exercises.id'), nullable=False)
    
    # 录音文件存放路径
    audio_path = db.Column(db.String(255), nullable=False)
    
    # 记录这是用户的第几次尝试，方便前端排序展示
    attempt_number = db.Column(db.Integer, default=1)

    # AI 跟读反馈
    ai_feedback = db.Column(db.Text, nullable=True)
    
    # 录音时间
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ─────────────────────────────────────────────
# Activity Log（学习轨迹核心）
# ─────────────────────────────────────────────
class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_log'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module    = db.Column(db.String(50), nullable=False)
    action    = db.Column(db.String(50), nullable=False)
    ref_id    = db.Column(db.Integer,    nullable=True)   
    timestamp = db.Column(db.DateTime,   default=lambda: datetime.now(timezone.utc))

# Dashboard schedule items
class UserScheduleItem(db.Model):
    __tablename__ = 'user_schedule_items'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    kind           = db.Column(db.String(30), nullable=False)  
    title          = db.Column(db.String(200), nullable=False)
    notes          = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Dashboard journal markers (custom log)
class UserJournalMarker(db.Model):
    __tablename__ = 'user_journal_markers'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    kind       = db.Column(db.String(30), default='custom')
    value      = db.Column(db.Float, nullable=True)
    unit       = db.Column(db.String(20), nullable=True)
    notes      = db.Column(db.Text, nullable=True)
    color      = db.Column(db.String(20), nullable=True)
    event_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ─────────────────────────────────────────────
# 🌳 Academic Orchard (我的家园)
# ─────────────────────────────────────────────

# 种子定义表（管理员预设的种子类型）
class SeedType(db.Model):
    __tablename__ = 'orchard_seed_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)              # 种子名称
    name_en = db.Column(db.String(100), nullable=False)           # 英文名
    description = db.Column(db.Text, nullable=True)               # 描述
    icon = db.Column(db.String(100), default='🌱')                # 图标/emoji
    price = db.Column(db.Integer, default=10)                     # 购买价格（金币）
    growth_hours = db.Column(db.Integer, default=4)               # 生长时间（小时）
    is_mystery = db.Column(db.Boolean, default=False)             # 是否为盲盒种子
    available = db.Column(db.Boolean, default=True)               # 是否可购买
    plant_image_url = db.Column(db.String(256), nullable=True)    # 成熟时的植物图片
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关联可能产出的果实
    possible_fruits = db.relationship('FruitType', backref='seed_type', lazy=True)


# 果实定义表（管理员预设的果实类型）
class FruitType(db.Model):
    __tablename__ = 'orchard_fruit_types'
    
    id = db.Column(db.Integer, primary_key=True)
    seed_type_id = db.Column(db.Integer, db.ForeignKey('orchard_seed_types.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)              # 果实名称
    name_en = db.Column(db.String(100), nullable=False)           # 英文名
    description = db.Column(db.Text, nullable=True)               # 描述/专属文案
    icon = db.Column(db.String(100), default='🍎')                # 图标/emoji
    rarity = db.Column(db.String(20), default='N')                # 稀有度: N/R/SR/SSR
    points = db.Column(db.Integer, default=10)                    # 转化积分
    drop_rate = db.Column(db.Float, default=0.5)                  # 掉落概率（0-1）
    is_showcase_worthy = db.Column(db.Boolean, default=False)     # 是否值得展示（SR/SSR自动true）
    academic_element = db.Column(db.String(100), nullable=True)   # 学术元素（如"戴学士帽的苹果"）
    image_url = db.Column(db.String(256), nullable=True)          # 果实图片路径
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# 土地等级定义表
class LandType(db.Model):
    __tablename__ = 'orchard_land_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)              # 土地名称（如：普通泥土、红壤、黑土）
    name_en = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)                      # 土地等级 1-5
    icon = db.Column(db.String(100), default='🟫')                # 图标
    upgrade_cost = db.Column(db.Integer, default=0)               # 升级到此等级的金币成本
    rare_boost = db.Column(db.Float, default=0.0)                 # 稀有果实概率加成（百分比）
    growth_reduction = db.Column(db.Float, default=0.0)           # 生长时间缩短比例（0-1）
    description = db.Column(db.Text, nullable=True)


# 道具定义表
class OrchardItem(db.Model):
    __tablename__ = 'orchard_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)              # 道具名称
    name_en = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)          # 道具类型: fertilizer/water/etc
    icon = db.Column(db.String(100), default='💧')
    price = db.Column(db.Integer, default=5)                      # 购买价格
    effect_value = db.Column(db.Float, default=1.0)               # 效果数值（如加速1小时）
    description = db.Column(db.Text, nullable=True)
    available = db.Column(db.Boolean, default=True)


# 用户农场数据表（用户的农场整体信息）
class UserOrchard(db.Model):
    __tablename__ = 'user_orchards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_harvests = db.Column(db.Integer, default=0)             # 总收获次数
    total_points = db.Column(db.Integer, default=0)               # 总积分
    weekly_points = db.Column(db.Integer, default=0)              # 本周积分
    last_weekly_reset = db.Column(db.Date, nullable=True)         # 上次周榜重置日期
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    user = db.relationship('User', backref=db.backref('orchard', uselist=False, lazy=True))
    lands = db.relationship('UserLand', backref='orchard', lazy=True, cascade='all, delete-orphan')
    showcase_fruits = db.relationship('UserShowcaseFruit', backref='orchard', lazy=True, cascade='all, delete-orphan')


# 用户土地表（每个用户拥有的土地）
class UserLand(db.Model):
    __tablename__ = 'user_lands'
    
    id = db.Column(db.Integer, primary_key=True)
    orchard_id = db.Column(db.Integer, db.ForeignKey('user_orchards.id'), nullable=False)
    land_type_id = db.Column(db.Integer, db.ForeignKey('orchard_land_types.id'), nullable=False)
    position = db.Column(db.Integer, default=0)                   # 土地位置索引
    
    # 当前种植状态
    current_seed_id = db.Column(db.Integer, db.ForeignKey('orchard_seed_types.id'), nullable=True)
    plant_status = db.Column(db.String(20), default='idle')       # idle/planted/growing/mature
    planted_at = db.Column(db.DateTime, nullable=True)            # 播种时间
    matures_at = db.Column(db.DateTime, nullable=True)            # 成熟时间
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    land_type = db.relationship('LandType')
    current_seed = db.relationship('SeedType')


# 用户背包（存放种子和道具）
class UserOrchardInventory(db.Model):
    __tablename__ = 'user_orchard_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)          # 'seed' 或 'item'
    item_id = db.Column(db.Integer, nullable=False)               # SeedType.id 或 OrchardItem.id
    quantity = db.Column(db.Integer, default=1)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_type', 'item_id', name='unique_user_item'),
    )


# 用户收获的果实（历史记录）
class UserHarvestedFruit(db.Model):
    __tablename__ = 'user_harvested_fruits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fruit_type_id = db.Column(db.Integer, db.ForeignKey('orchard_fruit_types.id'), nullable=False)
    land_id = db.Column(db.Integer, db.ForeignKey('user_lands.id'), nullable=True)
    harvested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    points_earned = db.Column(db.Integer, default=0)              # 获得的积分
    
    # 关系
    fruit_type = db.relationship('FruitType')
    user = db.relationship('User', backref='harvested_fruits')


# 用户展示柜中的果实
class UserShowcaseFruit(db.Model):
    __tablename__ = 'user_showcase_fruits'
    
    id = db.Column(db.Integer, primary_key=True)
    orchard_id = db.Column(db.Integer, db.ForeignKey('user_orchards.id'), nullable=False)
    harvested_fruit_id = db.Column(db.Integer, db.ForeignKey('user_harvested_fruits.id'), nullable=False)
    position = db.Column(db.Integer, default=0)                   # 展示位置
    display_message = db.Column(db.Text, nullable=True)           # 自定义展示文案
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    harvested_fruit = db.relationship('UserHarvestedFruit')
