"""
🌳 Academic Orchard Blueprint (我的家园)
功能模块：荣誉果实陈列室、学识农田核心区、丰收排行榜
"""
from datetime import datetime, date, timedelta, timezone
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, desc
import random

from models import (
    db, User,
    SeedType, FruitType, LandType, OrchardItem,
    UserOrchard, UserLand, UserOrchardInventory,
    UserHarvestedFruit, UserShowcaseFruit
)

orchard_bp = Blueprint('orchard', __name__, url_prefix='/orchard')


# ─────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────

def get_or_create_user_orchard(user_id):
    """获取或创建用户的农场数据"""
    orchard = UserOrchard.query.filter_by(user_id=user_id).first()
    if not orchard:
        orchard = UserOrchard(user_id=user_id)
        db.session.add(orchard)
        db.session.commit()
        
        # 为新用户创建初始土地（3块普通土地）
        basic_land_type = LandType.query.filter_by(level=1).first()
        if basic_land_type:
            for i in range(3):
                land = UserLand(
                    orchard_id=orchard.id,
                    land_type_id=basic_land_type.id,
                    position=i
                )
                db.session.add(land)
            db.session.commit()
    
    return orchard


def check_weekly_reset(orchard):
    """检查并重置周榜积分"""
    today = date.today()
    # 每周一重置
    monday = today - timedelta(days=today.weekday())
    
    if orchard.last_weekly_reset is None or orchard.last_weekly_reset < monday:
        orchard.weekly_points = 0
        orchard.last_weekly_reset = monday
        db.session.commit()


def calculate_mature_time(seed_type, land):
    """计算种子成熟时间，考虑土地加成"""
    base_hours = seed_type.growth_hours
    land_type = land.land_type
    
    # 土地等级减少生长时间
    reduction = land_type.growth_reduction if land_type else 0
    actual_hours = base_hours * (1 - reduction)
    
    return timedelta(hours=actual_hours)


def determine_fruit(seed_type, land):
    """根据种子和土地决定产出的果实"""
    possible_fruits = FruitType.query.filter_by(seed_type_id=seed_type.id).all()
    if not possible_fruits:
        return None
    
    land_type = land.land_type
    rare_boost = land_type.rare_boost if land_type else 0
    
    # 计算加权随机
    total_weight = 0
    weighted_fruits = []
    
    for fruit in possible_fruits:
        # 稀有度权重调整
        weight = fruit.drop_rate
        if fruit.rarity in ['SR', 'SSR']:
            weight *= (1 + rare_boost)
        weighted_fruits.append((fruit, weight))
        total_weight += weight
    
    # 随机选择
    roll = random.random() * total_weight
    cumulative = 0
    for fruit, weight in weighted_fruits:
        cumulative += weight
        if roll <= cumulative:
            return fruit
    
    return possible_fruits[0]  # 默认返回第一个


# ─────────────────────────────────────────────
# 页面路由
# ─────────────────────────────────────────────

@orchard_bp.route('/')
@login_required
def index():
    """我的家园主页"""
    orchard = get_or_create_user_orchard(current_user.id)
    check_weekly_reset(orchard)
    
    # 获取用户土地
    lands = UserLand.query.filter_by(orchard_id=orchard.id).order_by(UserLand.position).all()
    
    # 更新土地状态（检查是否已成熟）
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for land in lands:
        if land.plant_status == 'growing' and land.matures_at and now >= land.matures_at:
            land.plant_status = 'mature'
    db.session.commit()
    
    # 获取展示柜果实
    showcase_fruits = UserShowcaseFruit.query.filter_by(orchard_id=orchard.id)\
        .order_by(UserShowcaseFruit.position).limit(6).all()
    
    # 获取排行榜数据
    # 本周榜
    weekly_leaderboard = db.session.query(
        User.id, User.username, User.avatar_url,
        UserOrchard.weekly_points, UserOrchard.total_harvests
    ).join(UserOrchard, User.id == UserOrchard.user_id)\
     .order_by(desc(UserOrchard.weekly_points))\
     .limit(10).all()
    
    # 总榜
    total_leaderboard = db.session.query(
        User.id, User.username, User.avatar_url,
        UserOrchard.total_points, UserOrchard.total_harvests
    ).join(UserOrchard, User.id == UserOrchard.user_id)\
     .order_by(desc(UserOrchard.total_points))\
     .limit(10).all()
    
    # 获取当前用户排名
    user_weekly_rank = db.session.query(func.count(UserOrchard.id))\
        .filter(UserOrchard.weekly_points > orchard.weekly_points).scalar() + 1
    user_total_rank = db.session.query(func.count(UserOrchard.id))\
        .filter(UserOrchard.total_points > orchard.total_points).scalar() + 1
    
    # 获取商店数据
    seeds = SeedType.query.filter_by(available=True).all()
    items = OrchardItem.query.filter_by(available=True).all()
    land_types = LandType.query.order_by(LandType.level).all()
    
    # 获取用户背包
    inventory = UserOrchardInventory.query.filter_by(user_id=current_user.id).all()
    
    # 整理背包数据
    seed_inventory = {}
    item_inventory = {}
    for inv in inventory:
        if inv.item_type == 'seed':
            seed = db.session.get(SeedType, inv.item_id)
            if seed:
                seed_inventory[seed.id] = {'seed': seed, 'quantity': inv.quantity}
        elif inv.item_type == 'item':
            item = db.session.get(OrchardItem, inv.item_id)
            if item:
                item_inventory[item.id] = {'item': item, 'quantity': inv.quantity}
    
    # 获取用户可展示的稀有果实（未在展示柜中的）
    showcased_ids = [sf.harvested_fruit_id for sf in showcase_fruits]
    available_rare_fruits = UserHarvestedFruit.query\
        .join(FruitType)\
        .filter(
            UserHarvestedFruit.user_id == current_user.id,
            FruitType.is_showcase_worthy == True,
            ~UserHarvestedFruit.id.in_(showcased_ids) if showcased_ids else True
        ).all()
    
    return render_template('orchard/index.html',
        orchard=orchard,
        lands=lands,
        showcase_fruits=showcase_fruits,
        weekly_leaderboard=weekly_leaderboard,
        total_leaderboard=total_leaderboard,
        user_weekly_rank=user_weekly_rank,
        user_total_rank=user_total_rank,
        seeds=seeds,
        items=items,
        land_types=land_types,
        seed_inventory=seed_inventory,
        item_inventory=item_inventory,
        available_rare_fruits=available_rare_fruits,
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    )


# ─────────────────────────────────────────────
# API 路由
# ─────────────────────────────────────────────

@orchard_bp.route('/api/buy-seed', methods=['POST'])
@login_required
def buy_seed():
    """购买种子"""
    data = request.get_json()
    seed_id = data.get('seed_id')
    quantity = data.get('quantity', 1)
    
    seed = db.session.get(SeedType, seed_id)
    if not seed or not seed.available:
        return jsonify({'success': False, 'message': 'Seed not available'}), 400
    
    total_cost = seed.price * quantity
    if current_user.coins < total_cost:
        return jsonify({'success': False, 'message': 'Not enough coins'}), 400
    
    # 扣除金币
    current_user.coins -= total_cost
    
    # 添加到背包
    inventory = UserOrchardInventory.query.filter_by(
        user_id=current_user.id, item_type='seed', item_id=seed_id
    ).first()
    
    if inventory:
        inventory.quantity += quantity
    else:
        inventory = UserOrchardInventory(
            user_id=current_user.id,
            item_type='seed',
            item_id=seed_id,
            quantity=quantity
        )
        db.session.add(inventory)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Purchased {quantity}x {seed.name}!',
        'coins': current_user.coins,
        'inventory_count': inventory.quantity
    })


@orchard_bp.route('/api/buy-item', methods=['POST'])
@login_required
def buy_item():
    """购买道具"""
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    item = db.session.get(OrchardItem, item_id)
    if not item or not item.available:
        return jsonify({'success': False, 'message': 'Item not available'}), 400
    
    total_cost = item.price * quantity
    if current_user.coins < total_cost:
        return jsonify({'success': False, 'message': 'Not enough coins'}), 400
    
    current_user.coins -= total_cost
    
    inventory = UserOrchardInventory.query.filter_by(
        user_id=current_user.id, item_type='item', item_id=item_id
    ).first()
    
    if inventory:
        inventory.quantity += quantity
    else:
        inventory = UserOrchardInventory(
            user_id=current_user.id,
            item_type='item',
            item_id=item_id,
            quantity=quantity
        )
        db.session.add(inventory)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Purchased {quantity}x {item.name}!',
        'coins': current_user.coins,
        'inventory_count': inventory.quantity
    })


@orchard_bp.route('/api/plant', methods=['POST'])
@login_required
def plant_seed():
    """播种"""
    data = request.get_json()
    land_id = data.get('land_id')
    seed_id = data.get('seed_id')
    
    # 验证土地
    land = db.session.get(UserLand, land_id)
    if not land:
        return jsonify({'success': False, 'message': 'Land not found'}), 404
    
    orchard = get_or_create_user_orchard(current_user.id)
    if land.orchard_id != orchard.id:
        return jsonify({'success': False, 'message': 'Not your land'}), 403
    
    if land.plant_status != 'idle':
        return jsonify({'success': False, 'message': 'Land is not idle'}), 400
    
    # 验证背包种子
    inventory = UserOrchardInventory.query.filter_by(
        user_id=current_user.id, item_type='seed', item_id=seed_id
    ).first()
    
    if not inventory or inventory.quantity < 1:
        return jsonify({'success': False, 'message': 'No seeds in inventory'}), 400
    
    seed = db.session.get(SeedType, seed_id)
    if not seed:
        return jsonify({'success': False, 'message': 'Seed not found'}), 404
    
    # 消耗种子
    inventory.quantity -= 1
    if inventory.quantity <= 0:
        db.session.delete(inventory)
    
    # 更新土地状态
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    mature_delta = calculate_mature_time(seed, land)
    
    land.current_seed_id = seed_id
    land.plant_status = 'growing'
    land.planted_at = now
    land.matures_at = now + mature_delta
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Planted {seed.name}!',
        'land': {
            'id': land.id,
            'status': land.plant_status,
            'seed_icon': seed.icon,
            'matures_at': land.matures_at.isoformat()
        }
    })


@orchard_bp.route('/api/harvest', methods=['POST'])
@login_required
def harvest():
    """收获果实"""
    data = request.get_json()
    land_id = data.get('land_id')
    
    land = db.session.get(UserLand, land_id)
    if not land:
        return jsonify({'success': False, 'message': 'Land not found'}), 404
    
    orchard = get_or_create_user_orchard(current_user.id)
    if land.orchard_id != orchard.id:
        return jsonify({'success': False, 'message': 'Not your land'}), 403
    
    # 检查是否已成熟
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if land.plant_status == 'growing' and land.matures_at and now >= land.matures_at:
        land.plant_status = 'mature'
    
    if land.plant_status != 'mature':
        return jsonify({'success': False, 'message': 'Not ready to harvest'}), 400
    
    seed = land.current_seed
    if not seed:
        return jsonify({'success': False, 'message': 'No plant found'}), 400
    
    # 决定产出的果实
    fruit = determine_fruit(seed, land)
    if not fruit:
        return jsonify({'success': False, 'message': 'No fruit available'}), 400
    
    # 创建收获记录
    harvested = UserHarvestedFruit(
        user_id=current_user.id,
        fruit_type_id=fruit.id,
        land_id=land.id,
        points_earned=fruit.points
    )
    db.session.add(harvested)
    
    # 更新积分
    orchard.total_points += fruit.points
    orchard.weekly_points += fruit.points
    orchard.total_harvests += 1
    
    # 如果是稀有果实，自动添加到展示柜
    auto_showcase = False
    if fruit.is_showcase_worthy:
        showcase_count = UserShowcaseFruit.query.filter_by(orchard_id=orchard.id).count()
        if showcase_count < 6:  # 展示柜最多6个
            showcase_fruit = UserShowcaseFruit(
                orchard_id=orchard.id,
                harvested_fruit_id=harvested.id,
                position=showcase_count
            )
            db.session.add(showcase_fruit)
            auto_showcase = True
    
    # 重置土地状态
    land.current_seed_id = None
    land.plant_status = 'idle'
    land.planted_at = None
    land.matures_at = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Harvested {fruit.name}!',
        'fruit': {
            'name': fruit.name,
            'name_en': fruit.name_en,
            'icon': fruit.icon,
            'rarity': fruit.rarity,
            'points': fruit.points,
            'description': fruit.description,
            'auto_showcase': auto_showcase
        },
        'orchard': {
            'total_points': orchard.total_points,
            'weekly_points': orchard.weekly_points,
            'total_harvests': orchard.total_harvests
        }
    })


@orchard_bp.route('/api/use-item', methods=['POST'])
@login_required
def use_item():
    """使用道具（加速）"""
    data = request.get_json()
    land_id = data.get('land_id')
    item_id = data.get('item_id')
    
    land = db.session.get(UserLand, land_id)
    if not land:
        return jsonify({'success': False, 'message': 'Land not found'}), 404
    
    orchard = get_or_create_user_orchard(current_user.id)
    if land.orchard_id != orchard.id:
        return jsonify({'success': False, 'message': 'Not your land'}), 403
    
    if land.plant_status != 'growing':
        return jsonify({'success': False, 'message': 'No plant growing'}), 400
    
    # 检查背包
    inventory = UserOrchardInventory.query.filter_by(
        user_id=current_user.id, item_type='item', item_id=item_id
    ).first()
    
    if not inventory or inventory.quantity < 1:
        return jsonify({'success': False, 'message': 'No items in inventory'}), 400
    
    item = db.session.get(OrchardItem, item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    # 消耗道具
    inventory.quantity -= 1
    if inventory.quantity <= 0:
        db.session.delete(inventory)
    
    # 应用效果（加速）
    if item.item_type in ['fertilizer', 'water'] and land.matures_at:
        speed_hours = item.effect_value
        land.matures_at -= timedelta(hours=speed_hours)
        
        # 检查是否已经成熟
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if land.matures_at <= now:
            land.plant_status = 'mature'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Used {item.name}!',
        'land': {
            'id': land.id,
            'status': land.plant_status,
            'matures_at': land.matures_at.isoformat() if land.matures_at else None
        }
    })




@orchard_bp.route('/api/showcase/add', methods=['POST'])
@login_required
def add_to_showcase():
    """添加果实到展示柜"""
    data = request.get_json()
    harvested_fruit_id = data.get('fruit_id')
    
    orchard = get_or_create_user_orchard(current_user.id)
    
    # 检查展示柜是否已满
    showcase_count = UserShowcaseFruit.query.filter_by(orchard_id=orchard.id).count()
    if showcase_count >= 6:
        return jsonify({'success': False, 'message': 'Showcase is full'}), 400
    
    # 验证果实
    harvested = db.session.get(UserHarvestedFruit, harvested_fruit_id)
    if not harvested or harvested.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Fruit not found'}), 404
    
    # 检查是否已在展示柜
    existing = UserShowcaseFruit.query.filter_by(
        orchard_id=orchard.id, harvested_fruit_id=harvested_fruit_id
    ).first()
    if existing:
        return jsonify({'success': False, 'message': 'Already in showcase'}), 400
    
    showcase_fruit = UserShowcaseFruit(
        orchard_id=orchard.id,
        harvested_fruit_id=harvested_fruit_id,
        position=showcase_count
    )
    db.session.add(showcase_fruit)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Added to showcase!'
    })


@orchard_bp.route('/api/showcase/remove', methods=['POST'])
@login_required
def remove_from_showcase():
    """从展示柜移除果实"""
    data = request.get_json()
    showcase_id = data.get('showcase_id')
    
    orchard = get_or_create_user_orchard(current_user.id)
    
    showcase_fruit = db.session.get(UserShowcaseFruit, showcase_id)
    if not showcase_fruit or showcase_fruit.orchard_id != orchard.id:
        return jsonify({'success': False, 'message': 'Not found'}), 404
    
    db.session.delete(showcase_fruit)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Removed from showcase!'
    })


@orchard_bp.route('/api/land-status')
@login_required
def get_land_status():
    """获取土地状态（用于实时更新）"""
    orchard = get_or_create_user_orchard(current_user.id)
    lands = UserLand.query.filter_by(orchard_id=orchard.id).order_by(UserLand.position).all()
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    land_data = []
    
    for land in lands:
        # 自动更新成熟状态
        if land.plant_status == 'growing' and land.matures_at and now >= land.matures_at:
            land.plant_status = 'mature'
        
        land_info = {
            'id': land.id,
            'position': land.position,
            'status': land.plant_status,
            'land_type': {
                'name': land.land_type.name if land.land_type else 'Basic',
                'icon': land.land_type.icon if land.land_type else '🟫',
                'level': land.land_type.level if land.land_type else 1
            }
        }
        
        if land.current_seed:
            land_info['seed'] = {
                'name': land.current_seed.name,
                'icon': land.current_seed.icon
            }
        
        if land.matures_at:
            land_info['matures_at'] = land.matures_at.isoformat()
            remaining = (land.matures_at - now).total_seconds()
            land_info['remaining_seconds'] = max(0, remaining)
        
        land_data.append(land_info)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'lands': land_data,
        'server_time': now.isoformat()
    })
