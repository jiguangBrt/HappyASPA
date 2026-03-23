"""
Flask CLI 命令：向数据库填充或更新默认初始数据（支持更新新增列）

使用方法（在激活了虚拟环境的终端中运行）：
    flask add-default-data
"""

import click
import json
import os
from flask.cli import with_appcontext
from models import db, ListeningExercise, SpeakingExercise, VocabularyWord, AcademicScenario

@click.command(name='add-default-data')
@with_appcontext
def add_default_data():
    """向数据库插入或更新默认初始数据（包含单词、听力、口语、学术情景）"""
    print("🚀 开始填充/更新默认数据...")

    # ─────────────────────────────────────────────
    # 1. 导入单词数据
    # ─────────────────────────────────────────────
    words_json_path = os.path.join(os.path.dirname(__file__), 'words.json')
    if not os.path.exists(words_json_path):
        print(f"⚠️ 警告：{words_json_path} 不存在，跳过单词导入。")
    else:
        print("📖 正在导入单词数据...")
        with open(words_json_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)

        added = 0
        updated = 0
        for item in words_data:
            word = VocabularyWord.query.get(item['id'])
            if word:
                if (word.word != item['word'] or
                        word.definition != item['meaning'] or  
                        word.category != item['category']):
                    word.word = item['word']
                    word.definition = item['meaning']
                    word.category = item['category']
                    updated += 1
            else:
                word = VocabularyWord(
                    id=item['id'],
                    word=item['word'],
                    definition=item['meaning'],  
                    category=item['category']
                )
                db.session.add(word)
                added += 1

        print(f"   ✅ 单词导入完成：新增 {added} 条，更新 {updated} 条。")

    # ─────────────────────────────────────────────
    # 2. Listening Exercises（听力练习）- 包含了主分支新增的3篇！
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
                    "time": 47.0,
                    "question": "What does the speaker say about the 30-day duration?",
                    "options": [
                        "It is too short to form a habit.",
                        "It is just the right amount of time to add a new habit.",
                        "It is longer than most people can handle.",
                        "It is only suitable for physical challenges."
                    ],
                    "answer": 1
                },
                {
                    "time": 92.0,
                    "question": "What did the speaker do during his first 30-day challenge?",
                    "options": [
                        "He took a picture every day.",
                        "He rode his bike to work every day.",
                        "He climbed a mountain every day.",
                        "Both A and B."
                    ],
                    "answer": 3
                },
                {
                    "time": 142.0,
                    "question": "What can be inferred from the speaker’s experience of writing a novel in 30 days?",
                    "options": [
                        "Writing a novel is easier than expected.",
                        "You can accomplish big things by breaking them into daily tasks.",
                        "It is necessary to have previous writing experience.",
                        "The novel he wrote was a bestseller."
                    ],
                    "answer": 1
                },
                {
                    "time": 188.0,
                    "question": " What is the main idea of the talk?",
                    "options": [
                        "You should try to write a novel in 30 days.",
                        "It is impossible to change your life in a month.",
                        "Taking small steps for 30 days can lead to new habits.",
                        "Only big challenges are worth trying."
                    ],
                    "answer": 2
                }
            ]
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
    # 3. Speaking Exercises（口语练习 - English Corner）
    # ─────────────────────────────────────────────
    speaking_defaults = [
        {
            'title': 'Self Introduction',
            'prompt': 'Talk about your academic background and study goals (2-3 minutes).',
            'difficulty': 1,
            'category': 'General Speaking',
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
    # 4. Academic Scenarios (学术情景模拟) - 🌟 定制版 🌟
    # ─────────────────────────────────────────────
    
    # [清理步骤] 找出并删除旧的两个话题
    titles_to_remove = ['Requesting a Deadline Extension', 'Disagreeing with a Classmate']
    for old_title in titles_to_remove:
        old_scen = AcademicScenario.query.filter_by(title=old_title).first()
        if old_scen:
            db.session.delete(old_scen)
            print(f"  🗑️ 已自动删除旧版情景：{old_title}")
    db.session.commit() # 先提交删除，防止名字冲突

    # [新增步骤] 插入 6 个全新定制话题
    scenario_defaults = [
        {
            'title': 'Defending a Code Review',
            'category': 'Computer Science',
            'difficulty': 3,
            'background': 'You submitted a pull request for a new caching module. A senior developer left a comment suggesting your implementation is inefficient and consumes too much memory during peak loads.',
            'role': 'A junior software engineer explaining algorithmic choices to a senior developer in a team meeting.',
            'tasks': [
                'Acknowledge the senior developer\'s concern politely.',
                'Explain the time-space tradeoff you considered (e.g., faster lookups vs. higher memory).',
                'Propose a hybrid solution or ask for specific optimization advice.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Start by acknowledging the feedback constructively (e.g., "Thanks for the review. I agree memory is a concern..."). Then, pivot to your rationale ("However, I prioritized lookup speed because..."). End by showing you are open to compromise.',
            'prep_time_seconds': 120
        },
        {
            'title': 'Reporting a Safety Violation',
            'category': 'Civil Engineering',
            'difficulty': 3,
            'background': 'During a bridge construction project, you notice that the current scaffolding setup violates the updated wind resistance safety guidelines.',
            'role': 'A site engineer raising a critical safety concern to the strict Project Manager.',
            'tasks': [
                'Clearly state the specific safety violation.',
                'Explain the potential risks given the upcoming weather forecast.',
                'Suggest an immediate structural modification to secure the site.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Keep your tone urgent but professional. Use objective facts rather than opinions (e.g., "The current setup violates OSHA guidelines under tomorrow\'s wind conditions"). Don\'t just report the problem; propose a clear, immediate action.',
            'prep_time_seconds': 120
        },
        {
            'title': 'Explaining a Statistical Anomaly',
            'category': 'Applied Mathematics',
            'difficulty': 2,
            'background': 'In a collaborative research meeting, a biologist questions why you used a non-parametric statistical test instead of a standard ANOVA for their dataset.',
            'role': 'A statistical consultant explaining mathematical reasoning to a non-math expert.',
            'tasks': [
                'Explain what assumptions the dataset violated (e.g., non-normal distribution).',
                'Describe why the non-parametric test is more reliable for this specific data.',
                'Assure the biologist of the validity of the final p-value.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Avoid overly dense mathematical jargon. Bridge the gap by explaining <em>why</em> the standard test failed (the data wasn\'t normally distributed) and reassure your colleague that your alternative method is robust and standard practice.',
            'prep_time_seconds': 90
        },
        {
            'title': 'Proposing a Material Substitution',
            'category': 'Mechanical Engineering',
            'difficulty': 2,
            'background': 'The specific aluminum alloy needed for a new engine casing is out of stock. You need to propose using a slightly heavier but stronger titanium alloy to the lead designer.',
            'role': 'A manufacturing engineer proposing a critical design change.',
            'tasks': [
                'Inform the designer of the supply chain issue.',
                'Propose the titanium alloy as an alternative.',
                'Briefly compare the thermal and weight differences to justify the change.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Deliver the bad news (out of stock) quickly, and immediately follow up with your solution. Highlight the silver lining—emphasize how the titanium alloy\'s superior thermal strength makes up for its heavier weight.',
            'prep_time_seconds': 90
        },
        {
            'title': 'Justifying a Route Diversion',
            'category': 'Traffic Control',
            'difficulty': 3,
            'background': 'A major accident has occurred on Highway 4. You initiated a massive traffic diversion through a residential zone, which has angered local city officials.',
            'role': 'A traffic control center supervisor explaining the emergency decision to a city council member.',
            'tasks': [
                'Politely validate the council member\'s frustration regarding the residential traffic.',
                'Explain the severity of the highway blockage that forced your hand.',
                'Outline the temporary nature of the diversion and mitigation steps taken.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Empathy first. Validate their frustration ("I completely understand why the residents are upset"). Then, firmly explain the emergency (hazmat spill) that forced the decision, emphasizing that public safety was the priority.',
            'prep_time_seconds': 120
        },
        {
            'title': 'Seeking Assignment Clarification',
            'category': 'General Topic',
            'difficulty': 1,
            'background': 'You received an essay prompt for your elective course, but it is extremely vague about the required formatting, word count, and citation style.',
            'role': 'A student asking the Teaching Assistant (TA) for clarification during office hours.',
            'tasks': [
                'Politely introduce yourself and mention the specific assignment.',
                'Ask clear questions regarding the word count and citation style.',
                'Ask if they have a rubric or an example of a past successful paper.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Be respectful of the TA\'s time. Instead of saying "I don\'t know what to do," show that you\'ve read the syllabus and ask highly specific questions (e.g., "Could you clarify if we should use APA or MLA format?").',
            'prep_time_seconds': 60
        }
    ]

    for data in scenario_defaults:
        scenario = AcademicScenario.query.filter_by(title=data['title']).first()
        if scenario:
            print(f"  🔄 学术情景已存在，正在同步更新：{data['title']}")
            for key, value in data.items():
                setattr(scenario, key, value)
        else:
            print(f"  ✅ 正在插入新学术情景：{data['title']}")
            scenario = AcademicScenario(**data)
            db.session.add(scenario)


    # ─────────────────────────────────────────────
    # 提交更改
    # ─────────────────────────────────────────────
    try:
        db.session.commit()
        print("🎉 所有默认数据填充/同步完毕！")
    except Exception as e:
        db.session.rollback()
        print(f"❌ 数据库提交失败，已回滚。错误详情: {str(e)}")

if __name__ == '__main__':
    add_default_data()