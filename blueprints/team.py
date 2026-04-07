import random
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Team, User, team_members

team_bp = Blueprint('team', __name__, url_prefix='/team')

# 🎯 生成6位不重复的大写邀请码 (剔除易混淆的 0, O, 1, I)
def generate_invite_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = ''.join(random.choices(chars, k=6))
        # 确保数据库里没有撞车的码
        if not Team.query.filter_by(invite_code=code).first():
            return code

@team_bp.route('/create', methods=['POST'])
@login_required
def create_team():
    data = request.get_json()
    team_name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not team_name:
        return jsonify({'success': False, 'message': 'Team name cannot be empty.'}), 400

    if Team.query.filter_by(name=team_name).first():
        return jsonify({'success': False, 'message': 'Team name already exists.'}), 400

    # 👇 创建队伍时，自动生成专属邀请码 👇
    new_code = generate_invite_code()
    new_team = Team(name=team_name, description=description, leader_id=current_user.id, invite_code=new_code)
    new_team.members.append(current_user)
    
    try:
        db.session.add(new_team)
        db.session.flush() # 先拿到 id
        
        stmt = team_members.update().\
            where(team_members.c.user_id == current_user.id).\
            where(team_members.c.team_id == new_team.id).\
            values(role='leader')
        db.session.execute(stmt)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Team created successfully!', 'invite_code': new_code})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Server error.'}), 500

# 🎯 废弃强拉人，改为凭借邀请码主动 Join
@team_bp.route('/join', methods=['POST'])
@login_required
def join_team():
    data = request.get_json()
    code = data.get('invite_code', '').strip().upper() # 自动转大写防呆

    if not code:
        return jsonify({'success': False, 'message': 'Please enter an invite code.'}), 400

    # 通过邀请码查找队伍
    target_team = Team.query.filter_by(invite_code=code).first()
    
    if not target_team:
        return jsonify({'success': False, 'message': 'Invalid invite code.'}), 404

    if current_user in target_team.members:
        return jsonify({'success': False, 'message': 'You are already in this team.'}), 400

    if current_user.teams:
         return jsonify({'success': False, 'message': 'You are already in another team. Please leave first.'}), 400

    try:
        # 核销成功，加入队伍！
        target_team.members.append(current_user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Welcome to {target_team.name}!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Server error.'}), 500
    
    # ==========================================
# 🛑 退队与解散逻辑 (Leave & Dismiss)
# ==========================================

@team_bp.route('/leave', methods=['POST'])
@login_required
def leave_team():
    # 1. 检查是否在队伍里
    if not current_user.teams:
        return jsonify({'success': False, 'message': 'You are not in any team.'}), 400
    
    my_team = current_user.teams[0]
    
    # 2. 队长拦截：队长不能用普通的“退队”，必须“解散”
    if my_team.leader_id == current_user.id:
        return jsonify({'success': False, 'message': 'As the leader, you must dismiss the team instead of leaving.'}), 400

    try:
        # 3. 核心逻辑：把当前用户从队伍成员名单里踢掉
        my_team.members.remove(current_user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'You have left the team successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Server error.'}), 500


@team_bp.route('/dismiss', methods=['POST'])
@login_required
def dismiss_team():
    # 1. 检查是否在队伍里
    if not current_user.teams:
        return jsonify({'success': False, 'message': 'You are not in any team.'}), 400
    
    my_team = current_user.teams[0]
    
    # 2. 权限拦截：只有队长能解散
    if my_team.leader_id != current_user.id:
        return jsonify({'success': False, 'message': 'Only the leader can dismiss the team.'}), 403

    try:
        # 3. 核心逻辑：直接删除该队伍！
        # (SQLAlchemy 的 relationship 会自动清理 team_members 中间表里的关联)
        db.session.delete(my_team)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Team has been dismissed.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Server error.'}), 500