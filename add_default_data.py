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
    # 2. Listening Exercises（听力练习）
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
            'reference_material': '<strong>PR Comment:</strong> "This HashMap approach will cause memory spikes. Consider using an LRU cache."<br><strong>Your Goal:</strong> Defend your logic without sounding defensive.',
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
            'reference_material': '<strong>Safety Protocol v2.1:</strong> "Scaffolding above 15m must feature double-bracing in high-wind zones (>40km/h)."<br><strong>Weather Forecast:</strong> 50km/h gusts expected tomorrow.',
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
            'reference_material': '<strong>Data Output:</strong> Shapiro-Wilk test indicates significant deviation from normality (p < 0.01). ANOVA is invalid.',
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
            'reference_material': '<strong>Spec Sheet:</strong> Alloy Al-7075 (Unavailable).<br><strong>Alternative:</strong> Ti-6Al-4V (Available, +15% weight, +40% tensile strength).',
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
            'reference_material': '<strong>Incident Log:</strong> Multi-vehicle collision at HWY-4 Mile 28. Hazmat spill detected. Estimated clearance time: 4 hours.',
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
            'reference_material': '<strong>Syllabus Note:</strong> "Final Essay due Friday. Topic: Modern Ethics." (No other details provided).',
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