"""
🌳 Academic Orchard Blueprint (我的家园)
功能模块：荣誉果实陈列室、学识农田核心区、丰收排行榜
"""
from datetime import datetime, date, timedelta, timezone
from time_utils import utcnow_naive
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, desc
import random

from models import (
    db, User,Team,
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


# ─── 收获权重：稀有度 + 土地 + 照料（浇水 / 施肥品质）────────────────
RARITY_TIER = {'N': 0, 'R': 1, 'SR': 2, 'SSR': 3}
WEIGHT_FLOOR = 1e-9
# 每次浇水对「照料分」的贡献（仅抬高 R+ 档位权重）
CARE_PER_WATER = 0.10
# 肥料：累加 item.effect_value；系数偏大——一茬通常只能施 1～2 次肥，单次要对稀有权重足够明显
CARE_PER_FERTILIZER_EFFECT = 0.18
# 照料分上限，避免无限叠道具刷爆稀有
CARE_RAW_SCORE_CAP = 4.0
# 照料分 × 稀有阶梯 → 乘在 R+ 权重上：tier 越高越吃照料
CARE_TIER_COEF = 0.18


def rarity_tier(rarity):
    if not rarity:
        return 0
    return RARITY_TIER.get(str(rarity).strip().upper(), 0)


def _care_raw_score(water_count, fertilizer_quality_sum):
    w = max(0, int(water_count or 0))
    f = max(0.0, float(fertilizer_quality_sum or 0.0))
    raw = w * CARE_PER_WATER + f * CARE_PER_FERTILIZER_EFFECT
    return min(raw, CARE_RAW_SCORE_CAP)


def care_rare_multiplier(water_count, fertilizer_quality_sum, tier):
    """
    仅 tier>=1（R/SR/SSR）生效；N 不受照料影响。
    浇水次数越多、累计肥料 effect 越高，稀有档相对权重越高。
    """
    if tier <= 0:
        return 1.0
    raw = _care_raw_score(water_count, fertilizer_quality_sum)
    return 1.0 + raw * CARE_TIER_COEF * tier


def determine_fruit(seed_type, land, rng=None):
    """
    加权随机产出果实。
    - drop_rate：相对权重
    - 土地 rare_boost：抬高 SR/SSR
    - 本轮 crop_water_count / crop_fertilizer_quality：抬高 R+（肥料用 effect_value 累计，好肥更强）
    """
    possible_fruits = (
        FruitType.query.filter_by(seed_type_id=seed_type.id).order_by(FruitType.id).all()
    )
    if not possible_fruits:
        return None
    if len(possible_fruits) == 1:
        return possible_fruits[0]

    land_type = land.land_type
    rare_boost = float(land_type.rare_boost if land_type else 0) or 0.0
    water = getattr(land, 'crop_water_count', None)
    if water is None:
        water = 0
    fert = getattr(land, 'crop_fertilizer_quality', None)
    if fert is None:
        fert = 0.0

    weighted = []
    for fruit in possible_fruits:
        tier = rarity_tier(fruit.rarity)
        weight = max(float(fruit.drop_rate or 0), WEIGHT_FLOOR)
        if fruit.rarity in ('SR', 'SSR'):
            weight *= 1.0 + rare_boost
        if tier > 0:
            weight *= care_rare_multiplier(water, fert, tier)
        weighted.append((fruit, weight))

    total_weight = sum(w for _, w in weighted)
    if total_weight <= 0:
        return possible_fruits[0]

    roll_fn = rng if rng is not None else random.random
    roll = roll_fn() * total_weight
    cumulative = 0.0
    for fruit, weight in weighted:
        cumulative += weight
        if roll <= cumulative:
            return fruit
    return possible_fruits[-1]


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
    now = utcnow_naive()
    for land in lands:
        if land.plant_status == 'growing' and land.matures_at and now >= land.matures_at:
            land.plant_status = 'mature'
    db.session.commit()

    # 统一按 UTC 传给前端，避免本地时区解释 naive datetime 导致计时偏移
    land_timing_map = {}
    for land in lands:
        start_ts = None
        end_ts = None
        if land.planted_at:
            start_ts = land.planted_at.replace(tzinfo=timezone.utc).timestamp()
        if land.matures_at:
            end_ts = land.matures_at.replace(tzinfo=timezone.utc).timestamp()
        land_timing_map[land.id] = {
            'start_ts': start_ts,
            'end_ts': end_ts,
        }
    
    # 获取展示柜果实
    showcase_fruits = UserShowcaseFruit.query.filter_by(orchard_id=orchard.id)\
        .order_by(UserShowcaseFruit.position).all()
    
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

    # ==========================================
    # 👇 NEW: 团队总排行榜逻辑 👇
    # ==========================================
    from models import Team  # 确保能查到 Team 模型
    all_teams = Team.query.all()
    # 使用 models.py 中定义的 total_team_points 属性，从大到小排序，取前 10 名
    team_leaderboard = sorted(all_teams, key=lambda t: t.total_team_points, reverse=True)[:10]
    
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
    
    # 获取用户可展示果实（未在展示柜中的，包含所有稀有度）
    showcased_ids = [sf.harvested_fruit_id for sf in showcase_fruits]
    available_rare_fruits = UserHarvestedFruit.query\
        .join(FruitType)\
        .filter(
            UserHarvestedFruit.user_id == current_user.id,
            ~UserHarvestedFruit.id.in_(showcased_ids) if showcased_ids else True
        ).all()
    
    # 最终渲染页面，把所有数据传给前端
    return render_template('orchard/index.html',
        orchard=orchard,
        lands=lands,
        showcase_fruits=showcase_fruits,
        weekly_leaderboard=weekly_leaderboard,
        total_leaderboard=total_leaderboard,
        team_leaderboard=team_leaderboard,  # 👈 新增：把刚才算好的团队榜单传进去！
        user_weekly_rank=user_weekly_rank,
        user_total_rank=user_total_rank,
        seeds=seeds,
        items=items,
        land_types=land_types,
        seed_inventory=seed_inventory,
        item_inventory=item_inventory,
        available_rare_fruits=available_rare_fruits,
        land_timing_map=land_timing_map,
        now=utcnow_naive()
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
    now = utcnow_naive()
    mature_delta = calculate_mature_time(seed, land)
    
    land.current_seed_id = seed_id
    land.plant_status = 'growing'
    land.planted_at = now
    land.matures_at = now + mature_delta
    land.crop_water_count = 0
    land.crop_fertilizer_quality = 0.0

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
    now = utcnow_naive()
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
    
    # 收获后自动添加到展示柜（包含所有稀有度）
    auto_showcase = False
    showcase_count = UserShowcaseFruit.query.filter_by(orchard_id=orchard.id).count()
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
    land.crop_water_count = 0
    land.crop_fertilizer_quality = 0.0

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
    
    # 应用效果（推进进度，不改变总生长时长）
    if item.item_type in ['fertilizer', 'water'] and land.matures_at:
        speed_hours = item.effect_value
        delta = timedelta(hours=speed_hours)
        # 同时前移 planted_at 与 matures_at：
        # - 总时长（matures_at - planted_at）保持不变
        # - 已用时增加，剩余时间减少
        if land.planted_at:
            land.planted_at -= delta
        land.matures_at -= delta
        
        # 检查是否已经成熟
        now = utcnow_naive()
        if land.matures_at <= now:
            land.plant_status = 'mature'

        # 照料累计：影响收获时稀有果权重（肥料品质 = effect_value，越大越强）
        if item.item_type == 'water':
            land.crop_water_count = (land.crop_water_count or 0) + 1
        elif item.item_type == 'fertilizer':
            land.crop_fertilizer_quality = float(land.crop_fertilizer_quality or 0) + float(
                item.effect_value or 0
            )

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Used {item.name}!',
        'land': {
            'id': land.id,
            'status': land.plant_status,
            'matures_at': land.matures_at.isoformat() if land.matures_at else None,
            'crop_water_count': land.crop_water_count or 0,
            'crop_fertilizer_quality': float(land.crop_fertilizer_quality or 0),
        }
    })




@orchard_bp.route('/api/showcase/add', methods=['POST'])
@login_required
def add_to_showcase():
    """添加果实到展示柜"""
    data = request.get_json()
    harvested_fruit_id = data.get('fruit_id')
    
    orchard = get_or_create_user_orchard(current_user.id)
    
    # 当前展示数量用于顺序追加 position
    showcase_count = UserShowcaseFruit.query.filter_by(orchard_id=orchard.id).count()
    
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
    
    now = utcnow_naive()
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

        if land.plant_status == 'growing':
            land_info['crop_care'] = {
                'water_count': land.crop_water_count or 0,
                'fertilizer_quality': float(land.crop_fertilizer_quality or 0),
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
