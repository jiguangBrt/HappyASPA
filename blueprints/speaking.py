
from flask import Blueprint, render_template, request, jsonify, current_app, url_for, redirect, flash
from flask_login import login_required, current_user
from models import db, UserActivityLog, SpeakingExercise, UserSpeakingSubmission, User, AcademicScenario, UserScenarioSubmission
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
# 工具函数：验证文件扩展名
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# 工具函数：上传文件到TOS并返回URL（独立纯函数）
def upload_audio_to_tos(file_storage, filename,file_path):
    """
    独立纯函数：只上传文件到TOS，返回公网URL
    不依赖任何业务，不修改任何数据
    """
    AK = "AKLTNDZmNzZjNWY0NDY3NGMxYjgyN2FiYzA5NjA4OGMxOTM"
    SK = "WkRjeU5USmtOR1JsTmpjNU5ESmxZVGszTVdRd1l6VXdaRGRsWkROak5tTQ=="
    BUCKET = "english-practice-audio"
    ENDPOINT = "tos-cn-beijing.volces.com"
    REGION = "cn-beijing"

    try:
        import tos
        client = tos.TosClientV2(AK, SK, ENDPOINT, REGION)
        client.put_object_from_file(BUCKET,filename, file_path)
        return f"https://{BUCKET}.{ENDPOINT}/{filename}"
    except Exception as e:
        current_app.logger.error(f"TOS上传失败: {str(e)}")
        return None

# ====================== AI 工具函数 ======================
def file_to_base64(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ 文件不存在：{file_path}")
    with open(file_path, 'rb') as file:
        file_data = file.read()
        base64_data = base64.b64encode(file_data).decode('utf-8')
    return base64_data

def audio_to_text(tos_public_url):
    print(f"Audio URL for ASR: {tos_public_url}")
    import json
    import time
    import uuid
    import requests

    # 直接用官方的配置
    appid = "2401097724"
    token = "FRVUrCiYhwku-7ZX66HvB248g8pxkITr"
    submit_url = "https://openspeech-direct.zijieapi.com/api/v3/auc/bigmodel/submit"
    query_url = "https://openspeech-direct.zijieapi.com/api/v3/auc/bigmodel/query"

    # ====================== 提交任务 ======================
    task_id = str(uuid.uuid4())
    headers = {
        "X-Api-App-Key": appid,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": "volc.bigasr.auc",
        "X-Api-Request-Id": task_id,
        "X-Api-Sequence": "-1"
    }

    request_data = {
        "user": {"uid": "fake_uid"},
        "audio": {"url": tos_public_url},  # 你的TOS链接
        "request": {
            "model_name": "bigmodel",
            "enable_channel_split": True,
            "enable_ddc": True,
            "enable_speaker_info": True,
            "enable_punc": True,
            "enable_itn": True,
            # 你要的核心功能全部开启
            "show_utterances": True,
            # "show_additions": True,
            "enable_emotion_detection": True,
             "enable_gender_detection": True,
            # "enable_smooth": True
        }
    }

    # 提交
    resp = requests.post(submit_url, data=json.dumps(request_data), headers=headers)
    if resp.headers.get("X-Api-Status-Code") != "20000000":
        return {"text": f"提交失败：{resp.headers}", "gender": "", "emotion": "", "smooth": 0}

    x_tt_logid = resp.headers.get("X-Tt-Logid", "")

    # ====================== 轮询查询 ======================
    while True:
        query_headers = {
            "X-Api-App-Key": appid,
            "X-Api-Access-Key": token,
            "X-Api-Resource-Id": "volc.bigasr.auc",
            "X-Api-Request-Id": task_id,
            "X-Tt-Logid": x_tt_logid
        }
        query_resp = requests.post(query_url, json.dumps({}), headers=query_headers)
        code = query_resp.headers.get('X-Api-Status-Code', "")

        if code == '20000000':
            # 任务完成 → 解析结果
            result_json = query_resp.json()
            utterances = result_json.get('result', {}).get('utterances', [])
            if not utterances:
                print("⚠️ 识别结果中没有utterances字段或为空")
                return {"text": "无识别结果", "gender": "", "emotion": "", "smooth": 0}

            utt = utterances[0]
            additions = utt.get('additions', {})
            return {
                "text": utt.get('text', ''),
                "gender": additions.get('gender', 'unknown'),
                "emotion": additions.get('emotion', 'neutral'),
                "smooth": additions.get('smooth_score', 0.0)
            }

        elif code not in ['20000001', '20000002']:
            return {"text": f"识别失败：{code}", "gender": "", "emotion": "", "smooth": 0}

        time.sleep(1)

def text_evaluation(text):
    print("Evaluating text with AI, input length:", len(text))
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
                        {"type": "input_text", "text": '''You are a professional speaking coach.
                                                            Please evaluate the speaker’s performance based on:
                                                            1. EXPLAIN: Explain what the speaker said in the text, to show you understand it.
                                                            2. BASIC DELIVERY: pronunciation, fluency, grammar
                                                            3. CONTENT: vocabulary, logic, relevance
                                                            4. DELIVERY & EXPRESSIVENESS: emotion, confidence, smoothness, naturalness

                                                            Please return:
                                                            - Strengths
                                                            - Weaknesses
                                                            - Improvement suggestions
                                                            - 1-sentence summary

                                                            Use clear, simple English.'''},
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

def ai_evaluate_audio(tos_public_url):
    """
    综合调用：音频转文字+AI点评
    现在接收 TOS 公网链接，并把音频特征一起送给豆包点评
    """
    asr_result = audio_to_text(tos_public_url)
    print(f"ASR Result: {asr_result}")

    text = asr_result.get("text", "")
    gender = asr_result.get("gender", "unknown")
    emotion = asr_result.get("emotion", "neutral")
    smooth = asr_result.get("smooth", 0.0)

    # 把音频信息拼到文本前面，让AI一起点评
    input_for_llm = (
        f"[Audio Analysis]\n"
        f"Gender: {gender}\n"
        f"Emotion: {emotion}\n"
        f"Smoothness score: {smooth:.2f}\n\n"
        f"Transcript: {text}"
    )

    feedback = text_evaluation(input_for_llm)

    return {
        "transcript": text,
        "feedback": feedback,
        "gender": gender,
        "emotion": emotion,
        "smooth": smooth
    }

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
    
    # 🌟 NEW: 查出 Academic Scenarios 的数据！
    scenarios = AcademicScenario.query.order_by(AcademicScenario.created_at.desc()).all()
    
    return render_template('speaking/index.html', 
                           exercises=exercises, 
                           user_submissions=user_submissions_dict,
                           scenarios=scenarios) # 🌟 别忘了把 scenarios 传给前端

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

# 3. 提供音频文件访问 (升级版：支持普通口语和学术情景两张表)
@speaking_bp.route('/audio/<filename>')
@login_required
def get_audio(filename):
    # 先在普通口语表里找
    submission = UserSpeakingSubmission.query.filter_by(audio_filename=filename).first()
    
    # 如果没找到，再去新的学术情景表里找
    if not submission:
        submission = UserScenarioSubmission.query.filter_by(audio_filename=filename).first()
        
    # 如果两张表里都没有，说明有人在乱猜文件名，拒绝访问
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
            # 解耦上传 TOS（不影响原有逻辑）
            file.seek(0)
            tos_url = upload_audio_to_tos(file, filename,filepath)
            
            duration = request.form.get('duration', 0)
            submission = UserSpeakingSubmission(
                user_id=current_user.id,
                exercise_id=exercise_id,
                audio_filename=filename,
                duration_seconds=float(duration) if duration else 0.0
            )
            db.session.add(submission)
            db.session.flush()  # 获取ID
            # === AI 自动点评 ===
            exercise = SpeakingExercise.query.get(exercise_id)
            ai_result = ai_evaluate_audio(tos_url)
            submission.feedback = ai_result.get('feedback', '')
            # 可选：如需评分，可在 text_evaluation 返回结构中解析分数
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Audio uploaded & evaluated!',
                'submission_id': submission.id,
                'filename': filename,
                'feedback': submission.feedback
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

# ==========================================
# 🎓 NEW: 学术情景模拟 (Academic Scenarios) 专属路由
# ==========================================

# 8. 学术情景库（列表页）
@speaking_bp.route('/academic-scenarios')
@login_required
def academic_index():
    # 从数据库获取所有情景，按创建时间倒序排列
    scenarios = AcademicScenario.query.order_by(AcademicScenario.created_at.desc()).all()
    
    # 把查出来的数据传给前端模板
    return render_template('speaking/academic_index.html', scenarios=scenarios)

# 9. 学术情景模拟室（动态读取数据库）
@speaking_bp.route('/academic-scenarios/<int:scenario_id>')
@login_required
def academic_detail(scenario_id):
    # 1. 查询真实的情景题目数据
    scenario = AcademicScenario.query.get_or_404(scenario_id)
    
    # 2. 查询当前用户在这个题目下的所有历史录音
    submissions = UserScenarioSubmission.query.filter_by(
        user_id=current_user.id, 
        scenario_id=scenario_id
    ).order_by(UserScenarioSubmission.submitted_at.desc()).all()
    
    # 3. 格式化提交记录的时间
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

# 10. 上传学术情景录音接口 (真实写入数据库版)
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
            
            # 1. 保存物理文件
            file.save(filepath)
            # 解耦上传 TOS（不影响原有逻辑）
            file.seek(0)
            tos_url = upload_audio_to_tos(file, filename,filepath)
            
            # 2. 🌟 写入数据库！
            new_sub = UserScenarioSubmission(
                user_id=current_user.id,
                scenario_id=scenario_id,
                audio_filename=filename,
                duration_seconds=float(duration)
            )
            db.session.add(new_sub)
            db.session.flush()
            # === AI 自动点评 ===
            ai_result = ai_evaluate_audio(tos_url)
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
    # 确保只能删除当前登录用户自己的录音
    submission = UserScenarioSubmission.query.filter_by(id=sub_id, user_id=current_user.id).first()
    
    if not submission:
        return jsonify({'status': 'error', 'message': 'Submission not found or unauthorized'}), 404
    
    # 1. 从硬盘上删除物理音频文件
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.audio_filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            current_app.logger.error(f"Error deleting file {filepath}: {str(e)}")
    
    # 2. 从数据库中删除记录
    db.session.delete(submission)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Scenario submission deleted'}), 200