from flask import Blueprint, render_template, request, jsonify, current_app
from models import db, SpeakingExercise, UserSpeakingProgress  # 导入你的模型
import os
from datetime import datetime

# 创建蓝图（保持你的原有配置）
speaking_bp = Blueprint('speaking', __name__, 
                        template_folder='templates/speaking',
                        static_folder='static')

# 录音保存路径（确保文件夹存在）
RECORDINGS_DIR = os.path.join(os.path.dirname(__file__), 'static/uploads/speaking')
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# 1. 口语首页：从数据库读取题目和用户记录
@speaking_bp.route('/')
def index():
    # 读取所有口语题目
    exercises = SpeakingExercise.query.all()
    # 读取用户ID=1的练习记录（后续替换为真实用户ID，比如current_user.id）
    records = UserSpeakingProgress.query.filter_by(user_id=1).order_by(UserSpeakingProgress.submitted_at.desc()).all()
    # 传递给前端
    return render_template('index.html', topics=exercises, records=records)

# 2. 题目详情页
@speaking_bp.route('/exercise/<int:exercise_id>')
def exercise_detail(exercise_id):
    exercise = SpeakingExercise.query.get_or_404(exercise_id)
    return render_template('exercise.html', exercise=exercise)

# 3. 上传录音+保存到数据库（核心接口）
@speaking_bp.route('/upload', methods=['POST'])
def upload_recording():
    try:
        # 获取前端数据
        audio_file = request.files.get('audio')
        exercise_id = request.form.get('exercise_id')
        if not audio_file or not exercise_id:
            return jsonify({"error": "缺少音频文件或题目ID"}), 400
        
        # 1. 保存音频文件
        filename = f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}.webm"
        file_path = os.path.join(RECORDINGS_DIR, filename)
        audio_file.save(file_path)
        audio_url = f"/speaking/static/recordings/{filename}"  # 前端可访问的路径

        # 2. 模拟AI评分（后续替换为真实接口）
        score = round(80 + (datetime.now().second % 20), 1)  # 随机80-99.9分
        feedback = f"AI Feedback: Your pronunciation is clear! Score: {score}/100"

        # 3. 保存到数据库
        new_record = UserSpeakingProgress(
            user_id=1,  # 后续替换为真实用户ID
            exercise_id=int(exercise_id),
            audio_url=audio_url,
            score=score,
            feedback=feedback,
            submitted_at=datetime.utcnow()
        )
        db.session.add(new_record)
        db.session.commit()

        # 4. 返回结果给前端
        return jsonify({
            "success": True,
            "score": score,
            "feedback": feedback,
            "audio_url": audio_url
        })

    except Exception as e:
        db.session.rollback()  # 出错回滚
        return jsonify({"error": str(e)}), 500

# 4. 提交评分（备用接口）
@speaking_bp.route('/submit/<int:exercise_id>', methods=['POST'])
def submit_exercise(exercise_id):
    data = request.get_json()
    score = data.get('score')
    feedback = data.get('feedback')
    
    # 更新数据库记录
    record = UserSpeakingProgress.query.filter_by(user_id=1, exercise_id=exercise_id).first()
    if record:
        record.score = score
        record.feedback = feedback
        db.session.commit()
    
    return jsonify({
        "success": True,
        "message": f"题目 {exercise_id} 提交成功！",
        "score": score,
        "feedback": feedback
    })
