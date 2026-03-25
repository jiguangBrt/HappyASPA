from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm',  '')

        # Basic validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-username', methods=['POST'])
@login_required
def change_username():
    new_username = request.form.get('new_username', '').strip()
    if not new_username:
        flash('Username cannot be empty.', 'danger')
    elif len(new_username) < 2 or len(new_username) > 80:
        flash('Username must be between 2 and 80 characters.', 'danger')
    elif User.query.filter_by(username=new_username).first():
        flash('That username is already taken.', 'danger')
    else:
        current_user.username = new_username
        db.session.commit()
        flash('Username updated successfully!', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password', '')
    new_password     = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
    elif not new_password:
        flash('New password cannot be empty.', 'danger')
    elif len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'danger')
    elif new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))

# ==========================================
# 💰 NEW: 每日签到 API
# ==========================================
@auth_bp.route('/checkin', methods=['POST'])
@login_required
def daily_checkin():
    today = date.today()
    
    # 判断今天是否已经签到过
    if current_user.last_checkin_date == today:
        return jsonify({
            "status": "error",
            "message": "You have already checked in today!",
            "coins": current_user.coins
        }), 400
        
    # 执行签到逻辑：更新日期，金币 +1
    if current_user.coins is None:
        current_user.coins = 0  # 👈 新增这句兜底代码，防止旧账号报错
        
    current_user.last_checkin_date = today
    current_user.coins += 1
    
    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Sign-in successful! Gold coins +1",
            "coins": current_user.coins
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database save failed"}), 500


# ==========================================
# 🎓 NEW: 英语成绩认证与权限判定 API
# ==========================================
@auth_bp.route('/proficiency', methods=['POST'])
@login_required
def update_english_proficiency():
    # 兼容 JSON 提交或普通表单提交
    data = request.get_json() or request.form
    
    gaokao = data.get('gaokao_score')
    ielts = data.get('ielts_score')
    toefl = data.get('toefl_score')
    gre = data.get('gre_score')
    
    # 更新数据库字段 (如果有传值的话)
    if gaokao: current_user.gaokao_score = float(gaokao)
    if ielts: current_user.ielts_score = float(ielts)
    if toefl: current_user.toefl_score = int(toefl)
    if gre: current_user.gre_score = int(gre)
    
    # 核心判定逻辑 (Guard Thresholds)
    is_qualified = False
    if current_user.gaokao_score and current_user.gaokao_score > 135:
        is_qualified = True
    elif current_user.ielts_score and current_user.ielts_score > 7.0:
        is_qualified = True
    elif current_user.toefl_score and current_user.toefl_score >= 100:
        is_qualified = True
    elif current_user.gre_score and current_user.gre_score >= 320:
        is_qualified = True
        
    # 更新认证状态
    current_user.is_guide_qualified = is_qualified
    
    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "成绩认证更新成功！",
            "is_guide_qualified": current_user.is_guide_qualified
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "数据库保存失败"}), 500
    
    # ==========================================
# 🏠 NEW: 个人中心页面路由
# ==========================================
@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')