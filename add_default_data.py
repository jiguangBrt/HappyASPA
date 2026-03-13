"""
Flask CLI 命令：向数据库填充或更新默认初始数据（支持更新新增列）

使用方法：
    flask add-default-data
"""

import click
from flask.cli import with_appcontext
from models import db, ListeningExercise


@click.command(name='add-default-data')
@with_appcontext
def add_default_data():
    """向数据库插入或更新默认初始数据"""
    print("🚀 开始填充/更新默认数据...")

    # ─────────────────────────────────────────────
    # Listening Exercises（听力练习）
    # ─────────────────────────────────────────────

    listening_defaults = [
        {
            'title': 'Try Something New for 30 Days',
            'description': (
                'A TED Talk by Matt Cutts encouraging people to try new things '
                'for 30 days to build positive habits and make life more memorable.'
            ),
            'audio_url': '/static/video/TrySomethingNewFor30Days.mp4',
            'subtitle_url': '/static/subtitles/English_Try_something_new_for_30_days.vtt',
            'transcript': (
                "Is there something you've always meant to do, wanted to do, but just … haven't? "
                "Matt Cutts suggests: Try it for 30 days. This approach has worked for him..."
            ),
            'difficulty': 2,
            'category': 'TED Talk',
            'duration_seconds': 189,
            # 假设这是你新增的列，或者包含更新后的内容
            'questions': [
                {
                    "time": 5.0,
                    "question": "What is the main idea of the talk?",
                    "options": [
                        "You should try to write a novel in 30 days.",
                        "Taking small steps for 30 days can lead to new habits.",
                        "It is impossible to change your life in a month.",
                        "Only big challenges are worth trying."
                    ],
                    "answer": 1
                },
                # ... 其他题目
            ]
        },
    ]

    for data in listening_defaults:
        # 1. 尝试查询是否存在该标题的记录
        exercise = ListeningExercise.query.filter_by(title=data['title']).first()

        if exercise:
            # 2. 如果存在，遍历数据字典，更新每一个字段
            print(f"  🔄 检测到已存在，正在更新内容：{data['title']}")
            for key, value in data.items():
                setattr(exercise, key, value)
        else:
            # 3. 如果不存在，创建新记录
            print(f"  ✅ 正在插入新练习：{data['title']}")
            exercise = ListeningExercise(**data)
            db.session.add(exercise)

    # ─────────────────────────────────────────────
    # 提交更改
    # ─────────────────────────────────────────────
    try:
        db.session.commit()
        print("🎉 默认数据填充/更新完毕！")
    except Exception as e:
        db.session.rollback()
        print(f"❌ 出错了，已回滚：{str(e)}")