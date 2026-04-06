from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Team, User, team_members

team_bp = Blueprint('team', __name__, url_prefix='/team')

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

    new_team = Team(name=team_name, description=description, leader_id=current_user.id)
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
        return jsonify({'success': True, 'message': 'Team created successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Server error.'}), 500

@team_bp.route('/invite', methods=['POST'])
@login_required
def invite_to_team():
    data = request.get_json()
    team_id = data.get('team_id')
    target_user_id = data.get('target_user_id')

    team = Team.query.get(team_id)
    target_user = User.query.get(target_user_id)

    if not team or not target_user:
        return jsonify({'success': False, 'message': 'Team or User not found.'}), 404

    if team.leader_id != current_user.id:
        return jsonify({'success': False, 'message': 'Only the team leader can invite members.'}), 403

    if target_user in team.members:
        return jsonify({'success': False, 'message': 'User is already in this team.'}), 400

    try:
        # 👇 只有这一行才是唯一正确的方式！中间表会自动处理一切 👇
        team.members.append(target_user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Successfully added {target_user.username} to {team.name}!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Server error.'}), 500