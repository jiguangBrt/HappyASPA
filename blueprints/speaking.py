from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from models import db, UserActivityLog, SpeakingExercise, UserSpeakingSubmission
from flask import send_from_directory
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
    if 'audio_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['audio_file']
    exercise_id = request.form.get('exercise_id')
    
    # 验证练习ID和文件
    if not exercise_id or not SpeakingExercise.query.get(exercise_id):
        return jsonify({'status': 'error', 'message': 'Invalid exercise'}), 400
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        # 生成唯一文件名（避免重复）
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{current_user.id}_{uuid.uuid4()}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # 保存文件
        file.save(filepath)
        
        # 记录到数据库
        duration = request.form.get('duration', 0)  # 前端传的录音时长
        submission = UserSpeakingSubmission(
            user_id=current_user.id,
            exercise_id=exercise_id,
            audio_filename=filename,
            duration_seconds=float(duration)
        )
        db.session.add(submission)
        # 记录活动日志
        activity_log = UserActivityLog(
            user_id=current_user.id,
            module='speaking',
            action='submitted_audio',
            ref_id=exercise_id
        )
        db.session.add(activity_log)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Audio uploaded successfully!',
            'submission_id': submission.id
        }), 200
    else:
        return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400

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