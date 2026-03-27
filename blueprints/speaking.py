from flask import Blueprint, render_template, request, jsonify, current_app, url_for, redirect, flash
from flask_login import login_required, current_user
from models import db, UserActivityLog, SpeakingExercise, UserSpeakingSubmission, User, AcademicScenario, UserScenarioSubmission, ShadowingExercise, ShadowingAudio, UserShadowingRecord
from werkzeug.utils import secure_filename 
from flask import send_from_directory
from datetime import datetime, timezone, timedelta
import os
import uuid
# === AI 语音识别与点评依赖 ===
import requests
import base64
from volcenginesdkarkruntime import Ark

speaking_bp = Blueprint('speaking', __name__, url_prefix='/speaking')

# 工具函数：验证文件扩展名
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# ====================== AI 工具函数 ======================
def file_to_base64(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ 文件不存在：{file_path}")
    with open(file_path, 'rb') as file:
        file_data = file.read()
        base64_data = base64.b64encode(file_data).decode('utf-8')
    return base64_data

def audio_to_text(file_path):
    recognize_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
    appid = "2401097724"  # TODO: 建议改为配置项
    token = "FRVUrCiYhwku-7ZX66HvB248g8pxkITr"  # TODO: 建议改为配置项
    print('appid:', appid)
    print('token:', token)
    headers = {
        "X-Api-App-Key": appid,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": "volc.bigasr.auc_turbo",
        "X-Api-Request-Id": str(uuid.uuid4()),
        "X-Api-Sequence": "-1",
    }
    try:
        base64_data = file_to_base64(file_path)
        request_data = {
            "user": {"uid": appid},
            "audio": {"data": base64_data},
            "request": {"model_name": "bigmodel"}
        }
        response = requests.post(
            recognize_url,
            json=request_data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        code = response.headers.get('X-Api-Status-Code', '')
        if code != '20000000':
            raise Exception(f"❌ 识别失败：{response.headers.get('X-Api-Message', '未知错误')}")
        result_json = response.json()
        if 'text' in result_json.get('result', {}):
            pure_text = result_json['result']['text']
        elif 'utterances' in result_json.get('result', {}):
            pure_text = ' '.join([utt.get('text', '') for utt in result_json['result']['utterances']])
        else:
            pure_text = "⚠️ 未识别到文本内容"
        return pure_text
    except Exception as e:
        return f"❌ 语音识别出错：{str(e)}"

def text_evaluation(text):
    api_key = "31720b1b-57b7-467d-9517-eab3ab9c1ec1"  # TODO: 建议改为配置项
    print('api_key:', api_key)
    if Ark is None:
        return "❌ 未安装volcenginesdkarkruntime"
    client = Ark(
        base_url='https://ark.cn-beijing.volces.com/api/v3',
        api_key=api_key,
    )
    try:
        response = client.responses.create(
            model="doubao-seed-2-0-lite-260215",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": '''请作为专业的口语练习教练，从以下维度点评这段口语文本（{话题名称}话题）：
                                                        1. 基础表达：包含发音感知（从词汇适配性判断）、流畅度、语法准确性；
                                                        2. 内容表达：包含词汇丰富度、逻辑连贯性、话题贴合度；
                                                        3. 沟通效果：包含易懂性、互动性（如有）。

                                                        要求：
                                                        - 每个维度分别说明「优点」和「不足」，语言简洁易懂；
                                                        - 针对不足给出具体的「改进建议」（如替换词汇、补充逻辑词）；
                                                        - 最后给出1句整体总结和核心提升方向；
                                                        - 用英语回答。'''},
                        {"type": "input_text", "text": text}
                    ]
                }
            ]
        )
        if response.output and len(response.output) > 1:
            answer = response.output[1].content[0].text
            return answer
        else:
            return "⚠️ 未获取到有效点评内容"
    except Exception as e:
        return f"❌ 点评出错：{str(e)}"

def ai_evaluate_audio(audio_path):
    """
    综合调用：音频转文字+AI点评
    返回 {'transcript':..., 'feedback':...}
    """
    transcript = audio_to_text(audio_path)
    if transcript.startswith("❌"):
        return {'transcript': transcript, 'feedback': transcript}
    feedback = text_evaluation(transcript)
    return {'transcript': transcript, 'feedback': feedback}

# 1. 口语练习首页
@speaking_bp.route('/')
@login_required
def index():
    # 记录访问日志
    log = UserActivityLog(user_id=current_user.id, module='speaking', action='viewed')
    db.session.add(log)
    db.session.commit()
    
    # 查出 English Corner 的数据
    exercises = SpeakingExercise.query.all()
    raw_submissions = UserSpeakingSubmission.query.filter_by(user_id=current_user.id).all()
    user_submissions_dict = {sub.exercise_id: sub for sub in raw_submissions}
    
    # 查出 Academic Scenarios 的数据
    scenarios = AcademicScenario.query.order_by(AcademicScenario.created_at.desc()).all()
    
    # 查出所有跟读练习的数据
    shadowing_practices = ShadowingExercise.query.order_by(ShadowingExercise.id.asc()).all()
    
    return render_template('speaking/index.html', 
                           exercises=exercises, 
                           user_submissions=user_submissions_dict,
                           scenarios=scenarios,
                           shadowing_practices=shadowing_practices)

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
                creator_id=current_user.id
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
        submission = UserScenarioSubmission.query.filter_by(audio_filename=filename).first()
    if not submission:
        submission = UserShadowingRecord.query.filter_by(audio_path=filename).first()
    if not submission:
        return "Access denied", 403
        
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# 4. 上传录音接口 (修改：仅保存录音，不再自动调用 AI)
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
            # 直接提交数据库，不再等待 AI 分析
            db.session.commit() 
            
            return jsonify({
                'status': 'success',
                'message': 'Audio saved successfully!',
                'submission_id': submission.id,
                'filename': filename
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload audio error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error, please try again'}), 500

# 4.1 🌟 NEW: 专门用于触发 AI 分析的接口
@speaking_bp.route('/analyze-audio/<int:sub_id>', methods=['POST'])
@login_required
def analyze_audio(sub_id):
    submission = UserSpeakingSubmission.query.get_or_404(sub_id)
    
    # 权限校验：只能分析自己的录音
    if submission.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    # 如果已经分析过了，直接返回成功
    if submission.feedback:
        return jsonify({'status': 'success', 'message': 'Already analyzed'})

    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.audio_filename)
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'Audio file not found'}), 404
            
        # 调用火山引擎 AI 自动点评
        ai_result = ai_evaluate_audio(filepath)
        submission.feedback = ai_result.get('feedback', 'No feedback generated.')
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'AI analysis complete!'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"AI analysis error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'AI Analysis failed. Please try again.'}), 500

# 4.2 🌟 NEW: AI 点评详情页路由
@speaking_bp.route('/analysis-detail/<int:sub_id>')
@login_required
def analysis_detail(sub_id):
    submission = UserSpeakingSubmission.query.get_or_404(sub_id)
    exercise = SpeakingExercise.query.get(submission.exercise_id)
    
    # 格式化时间
    utc_time = submission.submitted_at       
    local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
    formatted_time = local_time.strftime('%Y-%m-%d %H:%M')
    
    return render_template('speaking/analysis_detail.html', 
                           submission=submission, 
                           exercise=exercise,
                           formatted_time=formatted_time)

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

# ==========================================
# 🎓 学术情景模拟 (Academic Scenarios) 专属路由
# ==========================================

# 8. 学术情景库（列表页）
@speaking_bp.route('/academic-scenarios')
@login_required
def academic_index():
    scenarios = AcademicScenario.query.order_by(AcademicScenario.created_at.desc()).all()
    return render_template('speaking/academic_index.html', scenarios=scenarios)

# 9. 学术情景模拟室（动态读取数据库）
@speaking_bp.route('/academic-scenarios/<int:scenario_id>')
@login_required
def academic_detail(scenario_id):
    scenario = AcademicScenario.query.get_or_404(scenario_id)
    
    submissions = UserScenarioSubmission.query.filter_by(
        user_id=current_user.id, 
        scenario_id=scenario_id
    ).order_by(UserScenarioSubmission.submitted_at.desc()).all()
    
    submission_list = []
    for sub in submissions:
        utc_time = sub.submitted_at       
        local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
        submission_list.append({
            'id': sub.id,
            'audio_filename': sub.audio_filename,
            'duration': round(sub.duration_seconds or 0, 1),
            'submitted_at': local_time.strftime('%Y-%m-%d %H:%M'),
            'score_vocabulary': sub.score_vocabulary,
            'score_logic': sub.score_logic,
            'score_politeness': sub.score_politeness,
            'overall_feedback': sub.overall_feedback
        })
        
    return render_template('speaking/academic_detail.html', scenario=scenario, submissions=submission_list)

# 10. 上传学术情景录音接口
@speaking_bp.route('/upload-scenario-audio', methods=['POST'])
@login_required
def upload_scenario_audio():
    try:
        if 'audio_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['audio_file']
        scenario_id = request.form.get('scenario_id')
        duration = request.form.get('duration', 0)
        
        if not scenario_id:
            return jsonify({'status': 'error', 'message': 'Invalid scenario ID'}), 400
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"user_{current_user.id}_scenario_{scenario_id}_{timestamp}.{ext}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)
            
            new_sub = UserScenarioSubmission(
                user_id=current_user.id,
                scenario_id=scenario_id,
                audio_filename=filename,
                duration_seconds=float(duration)
            )
            db.session.add(new_sub)
            db.session.flush()
            # === AI 自动点评 ===
            ai_result = ai_evaluate_audio(filepath)
            new_sub.overall_feedback = ai_result.get('feedback', '')
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Scenario Audio uploaded & evaluated!',
                'filename': filename,
                'feedback': new_sub.overall_feedback
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload scenario audio error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error, please try again'}), 500

# 11. 删除学术情景录音记录
@speaking_bp.route('/delete-scenario-submission/<int:sub_id>', methods=['POST'])
@login_required
def delete_scenario_submission(sub_id):
    submission = UserScenarioSubmission.query.filter_by(id=sub_id, user_id=current_user.id).first()
    
    if not submission:
        return jsonify({'status': 'error', 'message': 'Submission not found or unauthorized'}), 404
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.audio_filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            current_app.logger.error(f"Error deleting file {filepath}: {str(e)}")
    
    db.session.delete(submission)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Scenario submission deleted'}), 200

# ==========================================
# 🎙️ NEW: 沉浸式跟读练习 (Shadowing Practice)
# ==========================================

# 12. 沉浸式跟读练习舱 (Practice Detail) - 包含历史记录
@speaking_bp.route('/practice/<int:practice_id>')
@login_required
def practice_detail(practice_id):
    practice = ShadowingExercise.query.get_or_404(practice_id)
    audio_dict = {audio.accent_code: audio.audio_url for audio in practice.audios}
    
    practice_data = {
        'id': practice.id,
        'title': practice.title,
        'focus': practice.focus,
        'text': practice.text,
        'audio': audio_dict
    }
    
    # 查询该用户在此题目的录音历史
    records = UserShadowingRecord.query.filter_by(
        user_id=current_user.id, 
        exercise_id=practice_id
    ).order_by(UserShadowingRecord.attempt_number.desc()).all()
    
    # 格式化给前端渲染
    history_list = []
    for r in records:
        local_time = r.created_at.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
        history_list.append({
            'id': r.id,
            'attempt': r.attempt_number,
            'audio_url': url_for('speaking.get_audio', filename=r.audio_path),
            'created_at': local_time.strftime("%H:%M:%S")
        })
    
    return render_template('speaking/practice_detail.html', practice=practice_data, history=history_list)

# 13. 上传跟读录音接口
@speaking_bp.route('/practice/<int:practice_id>/upload_record', methods=['POST'])
@login_required
def upload_shadowing_record(practice_id):
    try:
        # 1. 检查文件是否存在
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': '没有找到音频文件'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
            
        if file and allowed_file(file.filename):
            # 2. 生成安全文件名并保存
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"user_{current_user.id}_shadow_{practice_id}_{timestamp}.{ext}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            # 3. 计算这次是第几次尝试
            last_record = UserShadowingRecord.query.filter_by(
                user_id=current_user.id, 
                exercise_id=practice_id
            ).order_by(UserShadowingRecord.attempt_number.desc()).first()
            
            next_attempt = (last_record.attempt_number + 1) if last_record else 1
            
            # 4. 写入数据库
            new_record = UserShadowingRecord(
                user_id=current_user.id,
                exercise_id=practice_id,
                audio_path=filename,
                attempt_number=next_attempt
            )
            db.session.add(new_record)
            db.session.commit()
            
            # 5. 返回给前端渲染
            local_time = new_record.created_at.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
            
            return jsonify({
                'success': True,
                'message': '录音保存成功！',
                'audio_url': url_for('speaking.get_audio', filename=filename),
                'attempt': next_attempt,
                'created_at': local_time.strftime("%H:%M:%S"),
                'record_id': new_record.id
            })
        else:
            return jsonify({'success': False, 'message': '文件类型不被允许'}), 400
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload shadowing record error: {str(e)}")
        return jsonify({'success': False, 'message': '服务器处理失败'}), 500

# 14. 删除某条跟读录音记录接口
@speaking_bp.route('/delete-shadowing-record/<int:record_id>', methods=['POST'])
@login_required
def delete_shadowing_record(record_id):
    record = UserShadowingRecord.query.filter_by(id=record_id, user_id=current_user.id).first()
    if not record:
        return jsonify({'success': False, 'message': '未找到记录或无权限删除'}), 404
        
    # 删除物理文件
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], record.audio_path)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            current_app.logger.error(f"Error deleting shadowing file {filepath}: {str(e)}")
            
    # 删除数据库记录
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '记录已删除'})