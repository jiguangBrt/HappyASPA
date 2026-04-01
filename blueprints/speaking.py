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
DAILY_AUDIO_COIN_LIMIT = 10

# 工具函数：验证文件扩展名
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def can_reward_audio_coin_today(user_id):
    """检查用户今日是否还能通过提交音频获得金币（按发放日志计数，删除录音不影响）。"""
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    rewarded_count_today = UserActivityLog.query.filter(
        UserActivityLog.user_id == user_id,
        UserActivityLog.module == 'speaking',
        UserActivityLog.action == 'audio_coin_reward',
        UserActivityLog.timestamp >= today_start
    ).count()
    return rewarded_count_today < DAILY_AUDIO_COIN_LIMIT


def reward_audio_coin_if_eligible(user):
    """尝试发放 1 枚音频奖励金币，并记录日志用于每日上限控制。"""
    coin_reward = 0
    coin_message = "You have reached today's coin reward limit and cannot earn more."

    if can_reward_audio_coin_today(user.id):
        if user.coins is None:
            user.coins = 0
        user.coins += 1
        db.session.add(
            UserActivityLog(
                user_id=user.id,
                module='speaking',
                action='audio_coin_reward'
            )
        )
        coin_reward = 1
        coin_message = 'Coin +1'

    return coin_reward, coin_message

# 工具函数：上传文件到TOS并返回URL（独立纯函数）
def upload_audio_to_tos(file_storage, filename,file_path):
    """
    独立纯函数：只上传文件到TOS，返回公网URL
    不依赖任何业务，不修改任何数据
    """
    AK = os.environ.get("VOLC_TOS_AK", "")
    SK = os.environ.get("VOLC_TOS_SK", "")
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


def build_topic_context_text(topic_context):
    """将题目上下文规范化为可读文本，供 LLM 结合录音进行点评。"""
    if not topic_context:
        return ""

    lines = []
    if topic_context.get("type"):
        lines.append(f"Practice type: {topic_context.get('type')}")
    if topic_context.get("title"):
        lines.append(f"Title: {topic_context.get('title')}")
    if topic_context.get("category"):
        lines.append(f"Category: {topic_context.get('category')}")
    if topic_context.get("difficulty") is not None:
        lines.append(f"Difficulty: {topic_context.get('difficulty')}")
    if topic_context.get("prompt"):
        lines.append(f"Prompt: {topic_context.get('prompt')}")
    if topic_context.get("background"):
        lines.append(f"Background: {topic_context.get('background')}")
    if topic_context.get("role"):
        lines.append(f"Role: {topic_context.get('role')}")

    tasks = topic_context.get("tasks")
    if tasks:
        if isinstance(tasks, list):
            task_text = "; ".join(str(t) for t in tasks if t)
        else:
            task_text = str(tasks)
        if task_text:
            lines.append(f"Required tasks: {task_text}")

    if topic_context.get("reference_material"):
        lines.append(f"Reference material: {topic_context.get('reference_material')}")

    return "\n".join(lines)

def audio_to_text(tos_public_url):
    print(f"Audio URL for ASR: {tos_public_url}")
    import json
    import time
    import uuid
    import requests

    # 从环境变量读取，避免密钥硬编码在源码中
    appid = os.environ.get("VOLC_ASR_APPID", "")
    token = os.environ.get("VOLC_ASR_TOKEN", "")
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
            "show_additions": True,
            "enable_emotion_detection": True,
            "enable_gender_detection": True,
            "enable_smooth": True
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

            full_text = " ".join(
                u.get('text', '').strip() for u in utterances if u.get('text')
            ).strip()

            # 兼容不同返回结构：优先取汇总特征，其次取最后一个分段特征
            result_additions = result_json.get('result', {}).get('additions', {})
            last_additions = utterances[-1].get('additions', {}) if utterances else {}
            additions = result_additions or last_additions

            return {
                "text": full_text,
                "gender": additions.get('gender', 'unknown'),
                "emotion": additions.get('emotion', 'neutral'),
                "smooth": additions.get('smooth_score', 0.0)
            }

        elif code not in ['20000001', '20000002']:
            return {"text": f"识别失败：{code}", "gender": "", "emotion": "", "smooth": 0}

        time.sleep(1)

def text_evaluation(text, topic_context_text=""):
    print("Evaluating text with AI, input length:", len(text))
    api_key = os.environ.get("VOLC_ARK_API_KEY", "")
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
                        {"type": "input_text", "text": '''  You are a friendly, supportive, and encouraging English speaking coach.
                                                            Your goal is to make students feel motivated, confident, and excited to improve.

                                                            Give them specific feedback on their speaking performance, covering these aspects:
                                                            Evaluate their speaking based on:
                                                            - Mark the overall performance with a score out of 100, and give a brief reason for the score.
                                                            - Clarity & pronunciation
                                                            - Fluency & natural rhythm
                                                            - Grammar & vocabulary choice
                                                            - Confidence & emotional delivery
                                                            - How well they express their ideas
                                                            - How well they stay on topic and address the speaking task

                                                            IMPORTANT:
                                                            1) If topic context is provided, use it to judge relevance and task completion.
                                                            2) Mention whether the learner answered the prompt or scenario tasks clearly.
                                                            3) Keep a warm and encouraging tone.

                                                            Please respond:
                                                            1.  What they did really well (positive, specific, warm)
                                                            2.  One or two small, gentle suggestions to improve (include topic relevance if needed)
                                                            3.  A short, encouraging message to keep them practicing

                                                            Use simple, positive, friendly English. Keep it short and supportive.
                                                            Give feedback in plain text only — NO asterisks, NO bullet points, NO hashtags, NO bold, NO markdown symbols of any kind.'''},
                        {"type": "input_text", "text": f"Topic Context:\n{topic_context_text or 'N/A'}"},
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

def ai_evaluate_audio(tos_public_url, topic_context=None):
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
    topic_context_text = build_topic_context_text(topic_context)
    print(f"Built topic context text:\n{topic_context_text}")

    # 把题目上下文+音频分析+转写文本拼接，让 AI 同时判断语言表现与切题度
    input_for_llm = (
        f"[Topic Context]\n"
        f"{topic_context_text or 'N/A'}\n\n"
        f"[Audio Analysis]\n"
        f"Gender: {gender}\n"
        f"Emotion: {emotion}\n"
        f"Smoothness score: {smooth:.2f}\n\n"
        f"Transcript: {text}"
    )

    feedback = text_evaluation(input_for_llm, topic_context_text)

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

# 4. 上传录音接口
@speaking_bp.route('/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    filepath = None
    submission_committed = False
    try:
        if 'audio_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['audio_file']
        exercise_id_raw = request.form.get('exercise_id')

        try:
            exercise_id = int(exercise_id_raw)
        except (TypeError, ValueError):
            return jsonify({'status': 'error', 'message': 'Invalid exercise'}), 400
        
        exercise = db.session.get(SpeakingExercise, exercise_id)
        
        if not exercise:
            return jsonify({'status': 'error', 'message': 'Invalid exercise'}), 400
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400
        
        MAX_FILE_SIZE = 50 * 1024 * 1024
        if file.content_length and file.content_length > MAX_FILE_SIZE:
            return jsonify({'status': 'error', 'message': 'File too large (max 50MB)'}), 413
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"user_{current_user.id}_ex_{exercise_id}_{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            duration = request.form.get('duration', 0)
            can_reward_coin = can_reward_audio_coin_today(current_user.id)

            submission = UserSpeakingSubmission(
                user_id=current_user.id,
                exercise_id=exercise_id,
                audio_filename=filename,
                duration_seconds=float(duration) if duration else 0.0
            )
            db.session.add(submission)

            coin_reward = 0
            coin_message = "You have reached today's coin reward limit and cannot earn more."
            if can_reward_coin:
                coin_reward, coin_message = reward_audio_coin_if_eligible(current_user)
            db.session.commit()
            submission_committed = True

            utc_time = submission.submitted_at
            local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))

            return jsonify({
                'status': 'success',
                'message': 'Audio saved successfully!',
                'submission_id': submission.id,
                'filename': filename,
                'submitted_at': local_time.strftime('%Y-%m-%d %H:%M'),
                'duration': round(submission.duration_seconds or 0, 1),
                'coin_reward': coin_reward,
                'coins': current_user.coins or 0,
                'coin_message': coin_message
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400
    except Exception as e:
        db.session.rollback()
        if filepath and not submission_committed and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                current_app.logger.warning(f"Failed to remove orphaned upload file: {filepath}")
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

    exercise = db.session.get(SpeakingExercise, submission.exercise_id)
    if not exercise:
        return jsonify({'status': 'error', 'message': 'Exercise not found'}), 404

    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.audio_filename)
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'Audio file not found'}), 404

        tos_url = upload_audio_to_tos(None, submission.audio_filename, filepath)
        if not tos_url:
            return jsonify({'status': 'error', 'message': 'Audio upload failed'}), 500

        topic_context = {
            "type": "English Corner",
            "title": exercise.title,
            "category": exercise.category,
            "difficulty": exercise.difficulty,
            "prompt": exercise.prompt
        }

        ai_result = ai_evaluate_audio(tos_url, topic_context=topic_context)
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
    exercise = db.session.get(SpeakingExercise, submission.exercise_id)
    
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
    filepath = None
    submission_committed = False
    try:
        if 'audio_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['audio_file']
        scenario_id_raw = request.form.get('scenario_id')
        duration = request.form.get('duration', 0)

        try:
            scenario_id = int(scenario_id_raw)
        except (TypeError, ValueError):
            return jsonify({'status': 'error', 'message': 'Invalid scenario ID'}), 400
        
        scenario = db.session.get(AcademicScenario, scenario_id)
        if not scenario:
            return jsonify({'status': 'error', 'message': 'Scenario not found'}), 404
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"user_{current_user.id}_scenario_{scenario_id}_{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)
            
            can_reward_coin = can_reward_audio_coin_today(current_user.id)

            new_sub = UserScenarioSubmission(
                user_id=current_user.id,
                scenario_id=scenario_id,
                audio_filename=filename,
                duration_seconds=float(duration) if duration else 0.0
            )
            db.session.add(new_sub)

            coin_reward = 0
            coin_message = "You have reached today's coin reward limit and cannot earn more."
            if can_reward_coin:
                coin_reward, coin_message = reward_audio_coin_if_eligible(current_user)
            db.session.commit()
            submission_committed = True

            utc_time = new_sub.submitted_at
            local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))

            return jsonify({
                'status': 'success',
                'message': 'Scenario recording uploaded successfully!',
                'submission_id': new_sub.id,
                'filename': filename,
                'submitted_at': local_time.strftime('%Y-%m-%d %H:%M'),
                'duration': round(new_sub.duration_seconds or 0, 1),
                'coin_reward': coin_reward,
                'coins': current_user.coins or 0,
                'coin_message': coin_message
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400
            
    except Exception as e:
        db.session.rollback()
        if filepath and not submission_committed and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                current_app.logger.warning(f"Failed to remove orphaned scenario upload: {filepath}")
        current_app.logger.error(f"Upload scenario audio error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error, please try again'}), 500

# 10.1 按需触发学术情景 AI 分析
@speaking_bp.route('/analyze-scenario-audio/<int:sub_id>', methods=['POST'])
@login_required
def analyze_scenario_audio(sub_id):
    submission = UserScenarioSubmission.query.get_or_404(sub_id)

    if submission.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    if submission.overall_feedback:
        return jsonify({'status': 'success', 'message': 'Already analyzed'})

    scenario = db.session.get(AcademicScenario, submission.scenario_id)
    if not scenario:
        return jsonify({'status': 'error', 'message': 'Scenario not found'}), 404

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.audio_filename)
    if not os.path.exists(filepath):
        return jsonify({'status': 'error', 'message': 'Audio file not found'}), 404

    try:
        tos_url = upload_audio_to_tos(None, submission.audio_filename, filepath)
        if not tos_url:
            return jsonify({'status': 'error', 'message': 'Audio upload failed'}), 500

        topic_context = {
            "type": "Academic Scenario",
            "title": scenario.title,
            "category": scenario.category,
            "difficulty": scenario.difficulty,
            "background": scenario.background,
            "role": scenario.role,
            "tasks": scenario.tasks,
            "reference_material": scenario.reference_material
        }

        ai_result = ai_evaluate_audio(tos_url, topic_context=topic_context)
        submission.overall_feedback = ai_result.get('feedback', 'No feedback generated.')

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'AI analysis complete!'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scenario AI analysis error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'AI Analysis failed. Please try again.'}), 500

# 10.2 学术情景 AI 点评详情页
@speaking_bp.route('/scenario-analysis-detail/<int:sub_id>')
@login_required
def scenario_analysis_detail(sub_id):
    submission = UserScenarioSubmission.query.get_or_404(sub_id)

    if submission.user_id != current_user.id:
        return "Access denied", 403

    scenario = AcademicScenario.query.get_or_404(submission.scenario_id)

    utc_time = submission.submitted_at
    local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
    formatted_time = local_time.strftime('%Y-%m-%d %H:%M')

    return render_template(
        'speaking/academic_analysis_detail.html',
        submission=submission,
        scenario=scenario,
        formatted_time=formatted_time
    )

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
            can_reward_coin = can_reward_audio_coin_today(current_user.id)

            new_record = UserShadowingRecord(
                user_id=current_user.id,
                exercise_id=practice_id,
                audio_path=filename,
                attempt_number=next_attempt
            )
            db.session.add(new_record)

            coin_reward = 0
            coin_message = "You have reached today's coin reward limit and cannot earn more."
            if can_reward_coin:
                coin_reward, coin_message = reward_audio_coin_if_eligible(current_user)
            db.session.commit()
            
            # 5. 返回给前端渲染
            local_time = new_record.created_at.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
            
            return jsonify({
                'success': True,
                'message': '录音保存成功！',
                'audio_url': url_for('speaking.get_audio', filename=filename),
                'attempt': next_attempt,
                'created_at': local_time.strftime("%H:%M:%S"),
                'record_id': new_record.id,
                'coin_reward': coin_reward,
                'coins': current_user.coins or 0,
                'coin_message': coin_message
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
