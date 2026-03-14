from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from models import db, UserActivityLog, SpeakingExercise, UserSpeakingSubmission, User
from flask import send_from_directory
from datetime import datetime, timezone,timedelta
import os
import uuid

speaking_bp = Blueprint('speaking', __name__, url_prefix='/speaking')

# 工具函数：验证文件扩展名
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# 1. 口语练习首页（正确绑定根路由 /）
@speaking_bp.route('/')  # 根路由绑定给 index 函数
@login_required
def index():  # ✅ 函数名与端点名一致（speaking.index）
    # 记录访问日志
    log = UserActivityLog(user_id=current_user.id, module='speaking', action='viewed')
    db.session.add(log)
    db.session.commit()
    
    # 获取所有口语练习
    exercises = SpeakingExercise.query.all()
    # 获取当前用户的录音记录
    user_submissions = UserSpeakingSubmission.query.filter_by(user_id=current_user.id).all()
    
    return render_template('speaking/index.html', 
                           exercises=exercises, 
                           user_submissions=user_submissions)

# 2. 提供音频文件访问（绑定带 filename 参数的路由）
@speaking_bp.route('/audio/<filename>')  # ✅ 路由参数与函数参数匹配
@login_required
def get_audio(filename):
    # 安全校验：确保当前用户只能访问自己的音频
    submission = UserSpeakingSubmission.query.filter_by(audio_filename=filename).first()
    if not submission or submission.user_id != current_user.id:
        return "Access denied", 403
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# 3. 上传录音接口（原有逻辑不变）
@speaking_bp.route('/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    try:
        if 'audio_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['audio_file']
        exercise_id = request.form.get('exercise_id')
        
        # 验证练习ID
        if not exercise_id or not SpeakingExercise.query.get(exercise_id):
            return jsonify({'status': 'error', 'message': 'Invalid exercise'}), 400
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400
        
        # 新增：文件大小限制（50MB）
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        if file.content_length and file.content_length > MAX_FILE_SIZE:
            return jsonify({'status': 'error', 'message': 'File too large (max 50MB)'}), 413
        
        if file and allowed_file(file.filename):
            # ✅ 核心修改：生成规整的文件名
            # 1. 获取文件扩展名（webm/mp3/wav）
            ext = file.filename.rsplit('.', 1)[1].lower()
            # 2. 生成时间戳（格式：年月日_时分秒，比如 20260314_155030）
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 3. 规整文件名：user_用户ID_ex_练习ID_时间戳.扩展名
            filename = f"user_{current_user.id}_ex_{exercise_id}_{timestamp}.{ext}"
            
            # 保存文件（确保目录存在）
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            # 写入数据库
            duration = request.form.get('duration', 0)
            submission = UserSpeakingSubmission(
                user_id=current_user.id,
                exercise_id=exercise_id,
                audio_filename=filename,  # 存规整后的文件名
                duration_seconds=float(duration) if duration else 0.0
            )
            db.session.add(submission)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Audio uploaded successfully!',
                'submission_id': submission.id,
                'filename': filename  # 可选：返回文件名给前端
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'File type not allowed (only mp3/wav/ogg/webm)'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload audio error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error, please try again'}), 500
    
# 4. 删除录音记录（原有逻辑不变）
@speaking_bp.route('/delete-submission/<int:sub_id>', methods=['POST'])
@login_required
def delete_submission(sub_id):
    submission = UserSpeakingSubmission.query.filter_by(id=sub_id, user_id=current_user.id).first()
    if not submission:
        return jsonify({'status': 'error', 'message': 'Submission not found'}), 404
    
    # 删除文件
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.audio_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # 删除数据库记录
    db.session.delete(submission)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Submission deleted'}), 200

#5 查看练习详情页面
@speaking_bp.route('/exercise/<int:exercise_id>')
@login_required
def exercise_detail(exercise_id):
    exercise = SpeakingExercise.query.get_or_404(exercise_id)
    submissions = db.session.query(UserSpeakingSubmission, User).join(
        User, UserSpeakingSubmission.user_id == User.id
    ).filter(
        UserSpeakingSubmission.exercise_id == exercise_id
    ).order_by(
        UserSpeakingSubmission.submitted_at.desc()
    ).all()
    
    submission_list = []
    for sub, user in submissions:
        audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sub.audio_filename)
        if not os.path.exists(audio_path):
            continue
        utc_time = sub.submitted_at       
        local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
       
        
        submission_list.append({
            'id': sub.id,
            'username': user.username,
            'audio_filename': sub.audio_filename,
            'duration': round(sub.duration_seconds, 1),
            'submitted_at': local_time.strftime('%Y-%m-%d %H:%M'),
            'feedback': sub.feedback or 'No feedback yet',
            'score': sub.score or 'Not scored'
        })
    
    return render_template(
        'speaking/detail.html',
        exercise=exercise,
        submissions=submission_list
    )