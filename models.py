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
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
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
    created_at       = db.Column(db.DateTime,    default=datetime.utcnow)

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
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CommentFavorite(db.Model):
    __tablename__ = 'comment_favorites'

    id         = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('forum_comments.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ForumLike(db.Model):
    __tablename__ = 'forum_likes'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ForumFavorite(db.Model):
    __tablename__ = 'forum_favorites'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at       = db.Column(db.DateTime,     default=datetime.utcnow)
    subtitle_url     = db.Column(db.String(256),  nullable=True)
    accent = db.Column(db.String(50), nullable=True)
    questions = db.Column(db.JSON, nullable=True)  

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
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 建立和提交记录的关系
    submissions = db.relationship('UserScenarioSubmission', backref='scenario', lazy=True)

class UserScenarioSubmission(db.Model):
    __tablename__ = 'user_scenario_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('academic_scenarios.id'), nullable=False)
    
    audio_filename = db.Column(db.String(256), nullable=False)  
    duration_seconds = db.Column(db.Float, nullable=True)  
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    
    # 录音时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    timestamp = db.Column(db.DateTime,   default=datetime.utcnow)

# Dashboard schedule items
class UserScheduleItem(db.Model):
    __tablename__ = 'user_schedule_items'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    kind           = db.Column(db.String(30), nullable=False)  
    title          = db.Column(db.String(200), nullable=False)
    notes          = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)