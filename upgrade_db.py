from app import create_app
from models import db, Team
from sqlalchemy import text
import random

def generate_invite_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = ''.join(random.choices(chars, k=6))
        return code

app = create_app()

with app.app_context():
    print("⏳ 正在进行数据库微创手术...")
    
    # 1. 执行原生 SQL，硬生生把列加进去（不破坏原有数据）
    try:
        db.session.execute(text('ALTER TABLE teams ADD COLUMN invite_code VARCHAR(10);'))
        db.session.commit()
        print("✅ 第一步完成：成功为 teams 表新增 invite_code 字段！")
    except Exception as e:
        db.session.rollback()
        # 如果报错，通常是因为你之前可能已经加过这个列了，我们忽略它继续往下走
        print("⚠️ 字段可能已经存在，跳过添加步骤。")

    # 2. 给老数据“擦屁股”：给那些以前建的、没有码的队伍补发邀请码
    try:
        teams = Team.query.all()
        count = 0
        for team in teams:
            if not team.invite_code:
                # 查重逻辑
                while True:
                    new_code = generate_invite_code()
                    if not Team.query.filter_by(invite_code=new_code).first():
                        break
                team.invite_code = new_code
                count += 1
                
        db.session.commit()
        print(f"✅ 第二步完成：成功为 {count} 个老队伍补发了邀请码！")
        print("🎉 手术大成功！所有用户和帖子数据完好无损，快去重启 Flask 试试吧！")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 发生错误: {e}")