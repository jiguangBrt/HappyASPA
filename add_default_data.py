"""
Flask CLI 命令：向数据库填充默认初始数据（防重复插入）

使用方法（在激活了虚拟环境的终端中运行）：
    flask add-default-data
"""

import click
from flask.cli import with_appcontext
from models import db, ListeningExercise


@click.command(name='add-default-data')
@with_appcontext
def add_default_data():
    """向数据库插入默认初始数据（已存在则跳过，不会重复插入）"""
    print("🚀 开始填充默认数据...")

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
                "Matt Cutts suggests: Try it for 30 days. This approach has worked for him, "
                "taking one of the most boring months of his life and turning it into something "
                "memorable. The idea is surprisingly simple: think about something you've always "
                "wanted to add to your life and try it for the next 30 days. It turns out, "
                "30 days is just about the right amount of time to add a new habit or subtract "
                "one, like watching the news or eating sugar."
            ),
            'difficulty': 2,
            'category': 'TED Talk',
            'duration_seconds': 189,
        },
    ]

    for data in listening_defaults:
        if ListeningExercise.query.filter_by(title=data['title']).first():
            print(f"  ⏩ 听力练习已存在，跳过：{data['title']}")
        else:
            exercise = ListeningExercise(**data)
            db.session.add(exercise)
            print(f"  ✅ 插入听力练习：{data['title']}")

    # ─────────────────────────────────────────────
    # 提交
    # ─────────────────────────────────────────────
    db.session.commit()
    print("🎉 默认数据填充完毕！")
