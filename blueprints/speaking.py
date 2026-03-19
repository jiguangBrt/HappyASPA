from flask import Blueprint, render_template, request, jsonify, current_app, url_for, redirect, flash
from flask_login import login_required, current_user
from models import db, UserActivityLog, SpeakingExercise, UserSpeakingSubmission, User
from flask import send_from_directory
from datetime import datetime, timezone, timedelta
import os
import uuid

speaking_bp = Blueprint('speaking', __name__, url_prefix='/speaking')

# 工具函数：验证文件扩展名
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# 1. 口语练习首页
@speaking_bp.route('/')
@login_required
def index():
    # 记录访问日志
    log = UserActivityLog(user_id=current_user.id, module='speaking', action='viewed')
    db.session.add(log)
    db.session.commit()
    
    exercises = SpeakingExercise.query.all()
    
    # 获取用户的所有原始提交记录
    raw_submissions = UserSpeakingSubmission.query.filter_by(user_id=current_user.id).all()
    
    # 【核心修改点】将列表转换为字典：{ exercise_id: submission对象 }
    user_submissions_dict = {sub.exercise_id: sub for sub in raw_submissions}
    
    return render_template('speaking/index.html', 
                           exercises=exercises, 
                           # 把字典传给前端
                           user_submissions=user_submissions_dict)

# 2. 新建口语练习（GET 展示表单 / POST 创建）
@speaking_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_exercise():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        prompt = request.form.get('prompt', '').strip()
        category = request.form.get('category', '').strip()
        try:
            difficulty = int(request.form.get('difficulty', 1))
            if difficulty < 1 or difficulty > 5:
                difficulty = 1
        except (TypeError, ValueError):
            difficulty = 1
            
        if not title or not prompt:
            flash('Title and prompt are required.', 'danger')
        else:
            exercise = SpeakingExercise(
                title=title,
                prompt=prompt,
                difficulty=difficulty,
                category=category or None,
                creator_id=current_user.id  # 绑定创建者
            )
            db.session.add(exercise)
            db.session.flush()
            log = UserActivityLog(user_id=current_user.id, module='speaking', action='created_exercise', ref_id=exercise.id)
            db.session.add(log)
            db.session.commit()
            
            flash('Speaking exercise created!', 'success')
            return redirect(url_for('speaking.exercise_detail', exercise_id=exercise.id))
            
    return render_template('speaking/new_exercise.html')

# 3. 提供音频文件访问
@speaking_bp.route('/audio/<filename>')
@login_required
def get_audio(filename):
    submission = UserSpeakingSubmission.query.filter_by(audio_filename=filename).first()
    if not submission:
        return "Access denied", 403
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# 4. 上传录音接口
@speaking_bp.route('/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    try:
        if 'audio_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['audio_file']
        exercise_id = request.form.get('exercise_id')
        
        if not exercise_id or not SpeakingExercise.query.get(exercise_id):
            return jsonify({'status': 'error', 'message': 'Invalid exercise'}), 400
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400
        
        # 文件大小限制（50MB）
        MAX_FILE_SIZE = 50 * 1024 * 1024
        if file.content_length and file.content_length > MAX_FILE_SIZE:
            return jsonify({'status': 'error', 'message': 'File too large (max 50MB)'}), 413
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"user_{current_user.id}_ex_{exercise_id}_{timestamp}.{ext}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            duration = request.form.get('duration', 0)
            submission = UserSpeakingSubmission(
                user_id=current_user.id,
                exercise_id=exercise_id,
                audio_filename=filename,
                duration_seconds=float(duration) if duration else 0.0
            )
            db.session.add(submission)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Audio uploaded successfully!',
                'submission_id': submission.id,
                'filename': filename
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'File type not allowed (only mp3/wav/ogg/webm)'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload audio error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error, please try again'}), 500

# 5. 删除录音记录
@speaking_bp.route('/delete-submission/<int:sub_id>', methods=['POST'])
@login_required
def delete_submission(sub_id):
    submission = UserSpeakingSubmission.query.filter_by(id=sub_id, user_id=current_user.id).first()
    if not submission:
        return jsonify({'status': 'error', 'message': 'Submission not found'}), 404
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.audio_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    db.session.delete(submission)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Submission deleted'}), 200

# 6. 查看练习详情页面
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

# 7. 删除口语练习题 (仅限创建者)
@speaking_bp.route('/delete-exercise/<int:exercise_id>', methods=['POST'])
@login_required
def delete_exercise(exercise_id):
    exercise = SpeakingExercise.query.get_or_404(exercise_id)
    
    if exercise.creator_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'You do not have permission to delete this exercise.'}), 403
    
    try:
        submissions = UserSpeakingSubmission.query.filter_by(exercise_id=exercise.id).all()
        for sub in submissions:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], sub.audio_filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        UserSpeakingSubmission.query.filter_by(exercise_id=exercise.id).delete() 
        db.session.delete(exercise)
        db.session.commit()
        
        flash('Speaking exercise deleted successfully.', 'success')
        return redirect(url_for('speaking.index'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting exercise: {str(e)}")
        flash('An error occurred while deleting the exercise.', 'danger')
        return redirect(url_for('speaking.index'))