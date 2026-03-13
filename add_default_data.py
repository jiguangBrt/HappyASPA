"""
Flask CLI 命令：向数据库填充或更新默认初始数据（支持更新新增列）

使用方法（在激活了虚拟环境的终端中运行）：
    flask add-default-data
"""

import click
from flask.cli import with_appcontext
from models import db, ListeningExercise, SpeakingExercise


@click.command(name='add-default-data')
@with_appcontext
def add_default_data():
    """向数据库插入或更新默认初始数据（支持 Listening 和 Speaking）"""
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
                {
                    "time": 35.0,
                    "question": "What did the speaker do during his first 30-day challenge?",
                    "options": [
                        "He wrote a novel.",
                        "He took a picture every day.",
                        "He climbed a mountain.",
                        "He biked to work every day."
                    ],
                    "answer": 1
                },
                {
                    "time": 70.0,
                    "question": "What happened when the speaker gave up sugar for 30 days?",
                    "options": [
                        "He lost weight.",
                        "He felt more energetic.",
                        "He ate a lot of sugar on day 31.",
                        "He never ate sugar again."
                    ],
                    "answer": 2
                },
                {
                    "time": 120.0,
                    "question": "What is the speaker's final advice to the audience?",
                    "options": [
                        "Start a 30-day challenge right now.",
                        "Think about something you've always wanted to try and give it a shot.",
                        "Only try challenges that are easy.",
                        "Don't tell anyone about your goals."
                    ],
                    "answer": 1
                }
            ]
        },
    ]

    for data in listening_defaults:
        exercise = ListeningExercise.query.filter_by(title=data['title']).first()
        if exercise:
            print(f"  🔄 听力练习已存在，正在同步更新：{data['title']}")
            for key, value in data.items():
                setattr(exercise, key, value)
        else:
            print(f"  ✅ 正在插入新听力练习：{data['title']}")
            exercise = ListeningExercise(**data)
            db.session.add(exercise)

    # ─────────────────────────────────────────────
    # Speaking Exercises（口语练习）
    # ─────────────────────────────────────────────

    speaking_defaults = [
        {
            'title': 'Self Introduction',
            'prompt': 'Talk about your academic background and study goals (2-3 minutes).',
            'difficulty': 1,
            'category': 'Interview',
        },
        {
            'title': 'Describe a Research Topic',
            'prompt': 'Explain your favorite research topic and why it interests you (3-5 minutes).',
            'difficulty': 2,
            'category': 'Presentation',
        },
    ]

    for data in speaking_defaults:
        exercise = SpeakingExercise.query.filter_by(title=data['title']).first()
        if exercise:
            print(f"  🔄 口语练习已存在，正在同步更新：{data['title']}")
            for key, value in data.items():
                setattr(exercise, key, value)
        else:
            print(f"  ✅ 正在插入新口语练习：{data['title']}")
            exercise = SpeakingExercise(**data)
            db.session.add(exercise)

    # ─────────────────────────────────────────────
    # 提交更改
    # ─────────────────────────────────────────────
    try:
        db.session.commit()
        print("🎉 所有默认数据填充/同步完毕！")
    except Exception as e:
        db.session.rollback()
        print(f"❌ 数据库提交失败，已回滚。错误详情: {str(e)}")