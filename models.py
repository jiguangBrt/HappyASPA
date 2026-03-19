from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

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

    # relationships
    vocab_progress      = db.relationship('UserVocabularyProgress', backref='user', lazy=True)
    flashcard_progress  = db.relationship('UserFlashcardProgress',  backref='user', lazy=True)
    forum_posts         = db.relationship('ForumPost',              backref='author', lazy=True)
    forum_comments      = db.relationship('ForumComment',           backref='author', lazy=True)
    forum_likes         = db.relationship('ForumLike',              backref='user',   lazy=True)
    forum_favorites     = db.relationship('ForumFavorite',          backref='user',   lazy=True) # <--- 新增：收藏关联
    listening_progress  = db.relationship('UserListeningProgress',  backref='user',   lazy=True)
    writing_submissions = db.relationship('UserWritingSubmission',  backref='user',   lazy=True)
    activity_logs       = db.relationship('UserActivityLog',        backref='user',   lazy=True)
    created_flashcards  = db.relationship('Flashcard', backref='creator', lazy=True)
    schedule_items      = db.relationship('UserScheduleItem',       backref='user',   lazy=True)

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
    views      = db.Column(db.Integer,     default=0)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    comments  = db.relationship('ForumComment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes     = db.relationship('ForumLike',    backref='post', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('ForumFavorite', backref='post', lazy=True, cascade='all, delete-orphan') # <--- 新增：收藏关联

    # 👇 新增：判断点赞、收藏状态的辅助方法
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


class ForumComment(db.Model):
    __tablename__ = 'forum_comments'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    content    = db.Column(db.Text,     nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ForumLike(db.Model):
    __tablename__ = 'forum_likes'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 👇 新增：收藏表
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
    questions = db.Column(db.JSON, nullable=True)  #添加了新字段 存储题目列表

    progress = db.relationship('UserListeningProgress', backref='exercise', lazy=True)


class UserListeningProgress(db.Model):
    __tablename__ = 'user_listening_progress'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'),                nullable=False)
    exercise_id     = db.Column(db.Integer, db.ForeignKey('listening_exercises.id'),  nullable=False)
    completed       = db.Column(db.Boolean, default=False)
    score           = db.Column(db.Float,   nullable=True)
    attempts        = db.Column(db.Integer, default=0)
    last_attempt_at = db.Column(db.DateTime, nullable=True)
    # new colomn：to store user listening practise progress
    last_position   = db.Column(db.Float, nullable=True)           # current play position
    two_thirds_count = db.Column(db.Integer, default=0)           # count of finishing exercises (Which reachs 2/3 progress of the whole exercise)
    answers         = db.Column(db.JSON, nullable=True)           # record of answer result

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
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'),              nullable=False)
    exercise_id  = db.Column(db.Integer, db.ForeignKey('writing_exercises.id'),  nullable=False)
    content      = db.Column(db.Text,    nullable=False)
    word_count   = db.Column(db.Integer, nullable=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    feedback     = db.Column(db.Text,    nullable=True)   # 预留 AI 反馈字段
    score        = db.Column(db.Float,   nullable=True)

# ─────────────────────────────────────────────
# Speaking (新增)
# ─────────────────────────────────────────────
class SpeakingExercise(db.Model):
    __tablename__ = 'speaking_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=False)  # 口语练习题目/提示
    difficulty = db.Column(db.Integer, default=1)  # 1-5
    category = db.Column(db.String(50), nullable=True)  # 如：interview/lecture/discussion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 👇 新增 1：在数据库表里加一列，用来存创建这个话题的用户的 ID
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    
    # 👇 新增 2：建立模型层面的关联，这样前端就能直接用 ex.creator.username 拿到名字了
    creator = db.relationship('User', backref='created_exercises')

    # 关联用户的录音提交（保留你原来的这行代码）
    submissions = db.relationship('UserSpeakingSubmission', backref='exercise', lazy=True)

class UserSpeakingSubmission(db.Model):
    __tablename__ = 'user_speaking_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('speaking_exercises.id'), nullable=False)
    audio_filename = db.Column(db.String(256), nullable=False)  # 音频文件名（存储路径）
    duration_seconds = db.Column(db.Float, nullable=True)  # 录音时长
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text, nullable=True)  # 预留反馈字段
    score = db.Column(db.Float, nullable=True)  # 预留评分字段

# ─────────────────────────────────────────────
# Activity Log（学习轨迹核心）
# ─────────────────────────────────────────────
class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_log'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # module: vocabulary / flashcard / listening / writing / forum
    module    = db.Column(db.String(50), nullable=False)
    # action:  viewed / completed / submitted / posted / commented
    action    = db.Column(db.String(50), nullable=False)
    ref_id    = db.Column(db.Integer,    nullable=True)   # 关联资源 ID
    timestamp = db.Column(db.DateTime,   default=datetime.utcnow)


# Dashboard schedule items
class UserScheduleItem(db.Model):
    __tablename__ = 'user_schedule_items'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    kind           = db.Column(db.String(30), nullable=False)  # listening / speaking / vocabulary / custom
    title          = db.Column(db.String(200), nullable=False)
    notes          = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
