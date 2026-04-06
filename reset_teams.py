from app import create_app
from models import db, Team, team_members

app = create_app()

with app.app_context():
    try:
        print("⏳ 正在清理团队测试数据...")
        
        # 1. 清空 team_members 关联表里的所有关系
        db.session.execute(team_members.delete())
        
        # 2. 清除掉所有的 Team 队伍记录
        deleted_teams = db.session.query(Team).delete()
        
        # 提交更改
        db.session.commit()
        
        print(f"✨ 清洗完成！共解散了 {deleted_teams} 个团队，清空了所有队员关系。")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 清洗失败，报错信息: {e}")