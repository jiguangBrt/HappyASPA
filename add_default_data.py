"""
Flask CLI 命令：向数据库填充或更新默认初始数据（支持更新新增列）

使用方法（在激活了虚拟环境的终端中运行）：
    flask add-default-data
"""

import click
from flask.cli import with_appcontext
from models import db, ListeningExercise, SpeakingExercise


@click.command(name="add-default-data")
@with_appcontext
def add_default_data():
    """向数据库插入或更新默认初始数据（支持 Listening 和 Speaking）"""
    print("🚀 开始填充/更新默认数据...")

    # ─────────────────────────────────────────────
    # Listening Exercises（听力练习）
    # ─────────────────────────────────────────────

    listening_defaults = [
        {
            "title": "Try Something New for 30 Days",
            "description": (
                "A TED Talk by Matt Cutts encouraging people to try new things "
                "for 30 days to build positive habits and make life more memorable."
            ),
            "audio_url": "/static/video/TrySomethingNewFor30Days.mp4",
            "subtitle_url": "/static/subtitles/English_Try_something_new_for_30_days.vtt",
            "transcript": (
                "Is there something you've always meant to do, wanted to do, but just … haven't? "
                "Matt Cutts suggests: Try it for 30 days. This approach has worked for him, "
                "taking one of the most boring months of his life and turning it into something "
                "memorable. The idea is surprisingly simple: think about something you've always "
                "wanted to add to your life and try it for the next 30 days. It turns out, "
                "30 days is just about the right amount of time to add a new habit or subtract "
                "one, like watching the news or eating sugar."
            ),
            "difficulty": 2,
            "category": "TED Talk",
            "duration_seconds": 189,
            "questions": [
                {
                    "time": 47.0,
                    "question": "What does the speaker say about the 30-day duration?",
                    "options": [
                        "It is too short to form a habit.",
                        "It is just the right amount of time to add a new habit.",
                        "It is longer than most people can handle.",
                        "It is only suitable for physical challenges.",
                    ],
                    "answer": 1,
                },
                {
                    "time": 92.0,
                    "question": "What did the speaker do during his first 30-day challenge?",
                    "options": [
                        "He took a picture every day.",
                        "He rode his bike to work every day.",
                        "He climbed a mountain every day.",
                        "Both A and B.",
                    ],
                    "answer": 3,
                },
                {
                    "time": 142.0,
                    "question": "What can be inferred from the speaker’s experience of writing a novel in 30 days?",
                    "options": [
                        "Writing a novel is easier than expected.",
                        "You can accomplish big things by breaking them into daily tasks.",
                        "It is necessary to have previous writing experience.",
                        "The novel he wrote was a bestseller.",
                    ],
                    "answer": 1,
                },
                {
                    "time": 188.0,
                    "question": " What is the main idea of the talk?",
                    "options": [
                        "You should try to write a novel in 30 days.",
                        "It is impossible to change your life in a month.",
                        "Taking small steps for 30 days can lead to new habits.",
                        "Only big challenges are worth trying.",
                    ],
                    "answer": 2,
                },
            ],
        },
        {
            "title": "How a dead duck changed my life",
            "description": "A TED Talk by Kees Moeliker about an unusual scientific observation involving a duck.",
            "audio_url": "/static/video/How a dead duck changed my life.mp4",
            "subtitle_url": "/static/subtitles/How_a_dead_duck_changed_my_life.vtt",
            "transcript": (
                "This is the Natural History Museum in Rotterdam, where I work as a curator. "
                "On an ordinary day in 1995, a loud bang against the window changed my life — a duck had collided with the glass and died. "
                "Next to it stood another duck, also male, which then mounted the dead duck and began to copulate. "
                "As a biologist, I realized this was a rare case of homosexual necrophilia, something never formally documented before. "
                "I observed and recorded the behavior for over an hour, then collected the specimen for the museum. "
                "Although it took me several years to publish the finding due to the difficulty in explaining it, I eventually documented it scientifically. "
                "This unusual observation later earned me an Ig Nobel Prize, which celebrates research that first makes people laugh and then think. "
                "The experience changed my career, leading me to study and collect remarkable examples of unusual animal behavior. "
                "It also highlights a serious issue: many birds die each year from collisions with glass, which we should work to prevent."
            ),
            "difficulty": 4,
            "category": "TED Talk",
            "duration_seconds": 216,
            "questions": [
                {
                    "time": 90.0,
                    "question": "What unusual event did the speaker witness outside his office?",
                    "options": [
                        "Two ducks fighting",
                        "A duck hitting the window and dying",
                        "A bird stealing food",
                        "A duck building a nest",
                    ],
                    "answer": 1,
                },
                {
                    "time": 180.0,
                    "question": "Why did the speaker wait several years before publishing his findings?",
                    "options": [
                        "He lost his notes",
                        "He was too busy",
                        "He couldn’t explain the behavior",
                        "The museum didn’t allow it",
                    ],
                    "answer": 2,
                },
                {
                    "time": 270.0,
                    "question": "What is the purpose of the Ig Nobel Prize?",
                    "options": [
                        "To reward serious scientific discoveries",
                        "To make people laugh and then think",
                        "To fund research projects",
                        "To support young scientists",
                    ],
                    "answer": 1,
                },
            ],
        },
        {
            "title": "The key to effective educational science videos",
            "description": "Derek Muller explains why some educational videos fail and how to make them more effective.",
            "audio_url": "/static/video/The key to effective educational science videos.mp4",
            "subtitle_url": "/static/subtitles/The_key_to_effective_educational_science_videos.vtt",
            "transcript": (
                "Derek Muller explores how to create effective educational science videos. "
                "In his PhD research, he tested whether students actually learned from traditional explanatory videos. "
                "Although students found these videos clear and easy to understand, their test scores showed almost no improvement. "
                "This revealed a problem: students often believe they understand concepts but fail to correct their misconceptions. "
                "To address this, Muller experimented with a different video style that included dialogue and conflicting ideas. "
                "In these videos, one person expressed common misunderstandings, while another guided the discussion toward the correct explanation. "
                "Although students found this approach more confusing, they learned significantly more because they had to think actively. "
                "The key insight is that learning requires mental effort, and effective videos should challenge learners' existing beliefs. "
                "Muller now applies this approach in his YouTube channel, Veritasium, emphasizing the importance of starting with misconceptions."
            ),
            "difficulty": 4,
            "category": "Science / TED Talk",
            "duration_seconds": 379,
            "questions": [
                {
                    "time": 90.0,
                    "question": "In the basketball example, what force acts on the ball after it is released?",
                    "options": [
                        "Upward force that decreases",
                        "No force at all",
                        "Downward constant force",
                        "Changing forces in different directions",
                    ],
                    "answer": 2,
                },
                {
                    "time": 180.0,
                    "question": "What surprising result did the speaker find after students watched the explanatory video?",
                    "options": [
                        "Their scores improved a lot",
                        "Their scores stayed almost the same",
                        "They refused to take the test",
                        "They got all answers correct",
                    ],
                    "answer": 1,
                },
                {
                    "time": 270.0,
                    "question": "Why was the dialogue-style video more effective?",
                    "options": [
                        "It was shorter",
                        "It was easier to understand",
                        "It made students think more actively",
                        "It had better animation",
                    ],
                    "answer": 2,
                },
            ],
        },
        {
            "title": "Creativity, Humor, and WTF!",
            "description": "A TEDx talk by Safwat Saleem about using creativity and humor to cope with frustration and difficult experiences.",
            "audio_url": "/static/video/Creativity, Humor, and WTF!.mp4",
            "subtitle_url": "/static/subtitles/Creativity_Humor_and_WTF.vtt",
            "transcript": (
                "The speaker begins by joking that he was not listed on the program because people might not show up if they knew he was speaking. "
                "He talks about feeling overwhelmed by negativity in the news, especially during a tense political period in the United States. "
                "To cope with these frustrations, he started creating art as a response to things that upset him. "
                "His artwork expressed his feelings about politics and society, and unexpectedly resonated with many people online. "
                "Encouraged by this, he began collecting stories from others and turning them into creative works like animations and posters. "
                "He shares a humorous story about his young son denying responsibility for an accident, which adds a lighthearted moment. "
                "He also shares a more serious story about someone whose father disappeared and died without reconciliation, showing the emotional depth of these experiences. "
                "Through these stories, he realized that life can be difficult, but creativity and humor can help people process challenges and move forward."
            ),
            "difficulty": 5,
            "category": "TED Talk",
            "duration_seconds": 510,
            "questions": [
                {
                    "time": 15.0,
                    "question": "Why does the speaker say he was not listed on the program?",
                    "options": [
                        "He was late",
                        "He is not popular",
                        "People might not attend if they knew he was speaking",
                        "He forgot to sign up",
                    ],
                    "answer": 2,
                },
                {
                    "time": 125.0,
                    "question": "What did the speaker do to cope with the overwhelming situation he faced?",
                    "options": [
                        "Ignored the news",
                        "Started arguing online",
                        "Created art to express his feelings",
                        "Moved to another place",
                    ],
                    "answer": 2,
                },
                {
                    "time": 320.0,
                    "question": "What is the purpose of the funny story about his son?",
                    "options": [
                        "To teach parenting skills",
                        "To criticize children",
                        "To show how humor can be found in everyday life",
                        "To change the topic completely",
                    ],
                    "answer": 2,
                },
            ],
        },
    ]

    for data in listening_defaults:
        exercise = ListeningExercise.query.filter_by(title=data["title"]).first()
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
            "title": "Self Introduction",
            "prompt": "Talk about your academic background and study goals (2-3 minutes).",
            "difficulty": 1,
            "category": "General Speaking",
        },
        {
            "title": "Describe a Research Topic",
            "prompt": "Explain your favorite research topic and why it interests you (3-5 minutes).",
            "difficulty": 2,
            "category": "Presentation",
        },
    ]

    for data in speaking_defaults:
        exercise = SpeakingExercise.query.filter_by(title=data["title"]).first()
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
