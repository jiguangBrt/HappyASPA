"""
Flask CLI 命令：向数据库填充或更新默认初始数据（支持更新新增列）
数据库同步:
flask db upgrade
数据库修改:创建迁移脚本
flask db migrate -m "add_new_table"
添加默认数据：
    flask add-default-data
整合数据库多个头部:
flask db merge heads -m "Merge database branches"
  然后执行:flask db upgrade
"""

import click
import json
import os
from flask.cli import with_appcontext

# 👇 确保导入了所有需要的模型，包括新增的 ShadowingExercise 和 ShadowingAudio
from models import (
    db, ListeningExercise, SpeakingExercise, VocabularyWord, 
    AcademicScenario, User, ForumPost, ForumComment, 
    ForumLike, ForumFavorite, ShadowingExercise, ShadowingAudio
)

@click.command(name='add-default-data')
@with_appcontext
def add_default_data():
    """向数据库插入或更新默认初始数据（包含单词、听力、口语、学术情景、跟读练习、论坛）"""
    print("🚀 开始填充/更新默认数据...")

    # ─────────────────────────────────────────────
    # 0. 创建系统默认导师账号 (用于发布论坛干货)
    # ─────────────────────────────────────────────
    tutor_user = User.query.filter_by(username='HappyASPA_Tutor').first()
    if not tutor_user:
        tutor_user = User(
            username='HappyASPA_Tutor',
            email='tutor@happyaspa.com',
            # 👇 新增：导师出场自带满级属性和发帖特权
            coins=9999,
            gaokao_score=150.0,
            ielts_score=9.0,
            toefl_score=120,
            gre_score=340,
            is_guide_qualified=True 
        )
        tutor_user.set_password('happyaspa2026') # 默认密码
        db.session.add(tutor_user)
        db.session.commit() # 先提交以获取 tutor_user.id
        print("  👤 已创建系统默认导师账号: HappyASPA_Tutor (满级认证)")

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
            'category': 'Motivation',
            'accent': 'American',
            'duration_seconds': 207,
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
            "category": "Science",
            'accent': 'Dutch',
            "duration_seconds": 396,
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
            "category": "Education",
            'accent': 'Australian',
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
            "category": "Society",
            'accent': 'American',
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
        {
    "title": "20 Things NOT to do in UK",
    "description": "Locals in the UK share advice on what foreigners and tourists should never do to avoid offending people, getting in trouble, or causing accidents while visiting the country.",
    "audio_url": "/static/video/20 Things NOT to do in UK.mp4",
    "subtitle_url": "/static/subtitles/20_Things_NOT_to_do_in_UK_Truth_from_Locals.vtt",
    "transcript": "This video gathers opinions from British locals about behaviors foreigners should avoid. Key points include: do not walk slowly in crowded areas, do not spit, always have your card ready at tube gates, don't assume weather predictions, avoid littering, do not leave gates open in rural areas, and do not discuss sensitive topics like Brexit casually. Instead, interact politely with locals, respect rules, and be considerate of others.",
    "difficulty": 3,
    "category": "Culture",
    "accent": "British",
    "duration_seconds": 690,
    "questions": [
        {
            "time": 35.6,
            "question": "What should foreigners never do on crowded streets in the UK?",
            "options": [
                "Walk slowly in front of others",
                "Walk in groups",
                "Take pictures of everything",
                "Stop to talk to locals"
            ],
            "answer": 0
        },
        {
            "time": 142.0,
            "question": "What is a safety concern for tourists in rural UK areas?",
            "options": [
                "Feeding wildlife",
                "Leaving gates open or letting dogs off leads",
                "Walking alone at night",
                "Taking selfies with animals"
            ],
            "answer": 1
        },
        {
            "time": 220.0,
            "question": "How should tourists behave on public transport in London?",
            "options": [
                "Walk slowly and block others",
                "Use apps and walk faster",
                "Take photos of transport stops",
                "Chat loudly with friends"
            ],
            "answer": 1
        },
        {
            "time": 358.0,
            "question": "Which topics are suggested to avoid discussing as a foreigner in the UK?",
            "options": [
                "Local cuisine",
                "Weather",
                "Brexit",
                "Public transport"
            ],
            "answer": 2
        },
        {
            "time": 410.0,
            "question": "Overall, what is the main advice for foreigners visiting the UK?",
            "options": [
                "Behave politely, respect rules, and be considerate",
                "Avoid visiting big cities",
                "Do not interact with locals",
                "Always take guided tours"
            ],
            "answer": 0
        }
    ]
        },
        {
    'title': 'Music Dreams Empower Young Chinese Artists',
    'description': (
        'A TED-style talk by Harry Hui about empowering young Chinese artists, '
        'sharing stories of perseverance, passion, and creativity in the music industry.'
    ),
    'audio_url': '/static/video/Harry Hui_ Music dreams empower young Chinese artists.mp4',
    'subtitle_url': '/static/subtitles/Harry_Hui_Music_dreams_empower_young_Chinese_artists.vtt',
    'transcript': (
        'Harry Hui has been in television production and creation in Asia for 15 years, '
        'mostly around music, celebrating and promoting Chinese artists. '
        'He shares stories of young artists overcoming challenges, following their dreams, '
        'and balancing tradition with modernity in their creative pursuits.'
    ),
    'difficulty': 3,
    'category': 'Motivation',
    'accent': 'Chinese',
    'duration_seconds': 410,
    'questions': [
        {
            "time": 103.0,
            "question": "How long has Harry Hui been working in television production and creation?",
            "options": [
                "5 years",
                "10 years",
                "15 years",
                "20 years"
            ],
            "answer": 2
        },
        {
            "time": 206.0,
            "question": "How did the first boy practice singing a Backstreet Boys song perfectly?",
            "options": [
                "He took English lessons",
                "He repeatedly played and sang the song",
                "He went abroad to learn",
                "He joined a band tour"
            ],
            "answer": 1
        },
        {
            "time": 309.0,
            "question": "Why did Waying, the girl from Shenyang, leave the competition?",
            "options": [
                "Family opposed her",
                "Her boyfriend asked her to quit",
                "She was injured",
                "She was busy with studies"
            ],
            "answer": 1
        },
    ]
},
        {
    'title': 'Iran-Saudi Relations and Regional Politics',
    'description': (
        'An interview with Hossein Amirabdollahian, Iran’s Deputy Foreign Minister in charge of '
        'Arab and African Affairs, discussing Iran-Saudi relations and regional political issues.'
    ),
    'audio_url': '/static/video/Hossein AMIRABDOLLAHIAN.mp4',
    'subtitle_url': '/static/subtitles/Hossein_AMIRABDOLLAHIAN.vtt',
    'transcript': (
        'Hossein Amirabdollahian discusses Iran’s view on Saudi Arabia, emphasizing willingness '
        'to cooperate on regional political solutions in places like Yemen, Lebanon, Iraq, and Syria. '
        'He comments on changes in Saudi leadership, the impact of military interventions, '
        'and expresses cautious optimism for future negotiations.'
    ),
    'difficulty': 5,
    'category': 'Politics',
    'accent': 'Iranian',
    'duration_seconds': 207,
    'questions': [
        {
            "time": 52.0,
            "question": "According to Amirabdollahian, what is the main issue between Iran and Saudi Arabia?",
            "options": [
                "Bilateral trade disputes",
                "Different ideas about regional situations",
                "Religious conflicts",
                "Border disputes"
            ],
            "answer": 1
        },
        {
            "time": 104.0,
            "question": "What event complicated Iran-Saudi relations according to the speaker?",
            "options": [
                "Death of King Abdullah",
                "Signing a trade agreement",
                "A sports event",
                "Opening of new embassies"
            ],
            "answer": 0
        },
        {
            "time": 156.0,
            "question": "How does Amirabdollahian describe the future prospects of negotiations?",
            "options": [
                "Pessimistic due to ongoing conflicts",
                "Neutral and indifferent",
                "Optimistic and ready for cooperation",
                "Uncertain and refusing talks"
            ],
            "answer": 2
        }
    ]
},
        {
    "title": "YS Jagan on Congress and Political Alliances",
    "description": "YS Jagan discusses his independent political stance in Andhra Pradesh, critiques the Congress-TDP alliance, and explains why he keeps all political options open.",
    "audio_url": "/static/video/YS Jagan Exclusive Interview in INDIA TODAY.mp4",
    "subtitle_url": "/static/subtitles/YS_Jagan_Exclusive_Interview_in_INDIA_TODAY.vtt",
    "transcript": "YS Jagan explains that he does not rely on Rahul Gandhi or any external support. He criticizes the Congress-TDP alliance in Telangana, saying such politics are unethical and misleading. He emphasizes maintaining independence and credibility in politics.",
    "difficulty": 4,
    "category": "Politics",
    "accent": "Indian",
    "duration_seconds": 282,
    "questions": [
        {
            "time": 120.0,
            "question": "What is YS Jagan's main stance regarding external political support?",
            "options": [
                "He relies fully on Congress support.",
                "He is open to support but remains independent.",
                "He opposes all other parties completely.",
                "He plans to join the Congress in the future."
            ],
            "answer": 1
        },
        {
            "time": 150.0,
            "question": "How does YS Jagan view the Congress-TDP alliance in Telangana?",
            "options": [
                "As a strong and credible partnership.",
                "As an unethical and opportunistic political move.",
                "As irrelevant to Andhra Pradesh politics.",
                "As a model for future alliances."
            ],
            "answer": 1
        },
        {
            "time": 180.0,
            "question": "What is the main idea of this segment?",
            "options": [
                "YS Jagan supports Congress-TDP collaboration.",
                "YS Jagan maintains political independence and criticizes opportunism.",
                "YS Jagan plans to leave politics.",
                "YS Jagan focuses on personal political gain only."
            ],
            "answer": 1
        }
    ]
}
        
        
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
    # 4. Academic Scenarios (学术情景模拟)
    # ─────────────────────────────────────────────
    
    # 清理旧的学术情景
    AcademicScenario.query.delete()
    db.session.commit()
    print("  🗑️ 已清空旧版学术情景，准备刷入最新数据...")

    scenario_defaults = [
        {
            'title': 'Asking About Project Requirements',
            'category': 'Computer Science',
            'difficulty': 1,
            'background': 'You are starting your final programming project, but you are not sure if you are allowed to use external code libraries or if you have to write everything from scratch.',
            'role': 'A student asking their Computer Science professor for clarification on the project rules.',
            'tasks': [
                'Politely greet the professor and mention the final project.',
                'Ask if using external libraries or packages is allowed.',
                'Ask how the code should be submitted (e.g., as a ZIP file or via GitHub).'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Keep your questions direct and polite. For example: "Hi Professor, I have a quick question about the final project. Are we allowed to use external libraries like NumPy, or do we need to write all the functions from scratch?"',
            'prep_time_seconds': 60
        },
        {
            'title': 'Accepting a Correction in Class',
            'category': 'Civil Engineering',
            'difficulty': 1,
            'background': 'You are giving a short presentation on basic building materials in your Intro to Civil Engineering class. A classmate points out that you accidentally mixed up the words "cement" and "concrete" on your slides.',
            'role': 'A first-year student gracefully handling a small mistake during a presentation.',
            'tasks': [
                'Thank the classmate for pointing out the mistake.',
                'Acknowledge the mix-up without panicking or over-apologizing.',
                'Quickly state the correct information and continue the presentation.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Don\'t panic! Mix-ups happen all the time. A natural and confident response is: "Oh, you are completely right, thank you for catching that! I accidentally swapped the terms on this slide. Cement is just the ingredient, and concrete is the final product. Anyway, moving on to the next slide..."',
            'prep_time_seconds': 60
        },
        {
            'title': 'Asking for Help with a Math Problem',
            'category': 'Applied Mathematics',
            'difficulty': 1,
            'background': 'You are doing your math homework, but you keep getting the wrong answer for Question 5. You go to the professor\'s office hours to ask for help.',
            'role': 'A confused student asking the professor to check their homework steps.',
            'tasks': [
                'Say hello and tell the professor which homework question you are doing.',
                'Show the professor your work.',
                'Ask them to point out where you made a mistake.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Keep it simple and show your effort. Try: "Hi Professor, I am working on Question 5, but my answer doesn\'t match the textbook. Here is my work. Could you show me where I went wrong?"',
            'prep_time_seconds': 60
        },
        {
            'title': 'Asking for Help in the Lab',
            'category': 'Mechanical Engineering',
            'difficulty': 1,
            'background': 'You are printing a model for your engineering class in the student lab. Suddenly, the 3D printer stops working and a red light turns on.',
            'role': 'A student reporting a machine problem to the lab assistant.',
            'tasks': [
                'Tell the lab assistant which machine you are using.',
                'Explain what happened (it stopped and showed a red light).',
                'Ask what you should do next.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Just describe what you see. "Excuse me, I was using 3D printer number 2, but it just stopped and a red light came on. I didn\'t touch anything. What should I do now?"',
            'prep_time_seconds': 60
        },
        {
            'title': 'Asking for Missing Traffic Data',
            'category': 'Traffic Control',
            'difficulty': 2,
            'background': 'Your group is designing a safer crosswalk for a campus intersection. Your partner has not sent you their data on morning pedestrian traffic, and the project is due tomorrow.',
            'role': 'A group leader asking a classmate for their part of the traffic data.',
            'tasks': [
                'Remind your classmate that the crosswalk project is due tomorrow.',
                'Ask if they need help organizing the pedestrian data.',
                'Ask them to send the numbers by tonight so you can finish the charts.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Be friendly but mention exactly what you need. Try: "Hi! Just a quick reminder that our crosswalk project is due tomorrow. Do you need any help with the pedestrian data? Please send me your numbers by tonight so I can finish the charts."',
            'prep_time_seconds': 90
        },
        {
            'title': 'Asking for a Short Extension',
            'category': 'General Topic',
            'difficulty': 1,
            'background': 'You have a bad cold and cannot finish your homework due tomorrow. You talk to your Teaching Assistant (TA) to ask for one more day.',
            'role': 'A sick student asking the TA for permission to submit homework late.',
            'tasks': [
                'Say your name and which class you are in.',
                'Explain that you are sick with a bad cold.',
                'Ask nicely if you can hand in the homework one day late.'
            ],
            'reference_material': '<strong>💡 Speaking Tip:</strong> Be polite and get straight to the point. "Hi, I\'m in your Tuesday morning class. I have a bad cold and I\'m feeling really sick today. Is it possible to hand in the homework one day late?"',
            'prep_time_seconds': 60
        }
    ]

    for data in scenario_defaults:
        scenario = AcademicScenario(**data)
        db.session.add(scenario)
        print(f"  ✅ 正在插入新学术情景：{data['title']}")

    # ─────────────────────────────────────────────
    # 4.5. 🎙️ Shadowing Practice (沉浸式跟读练习)
    # ─────────────────────────────────────────────
    # 🌟 修复：先清空关联的音频表 (ShadowingAudio)，再清空主表 (ShadowingExercise)
    ShadowingAudio.query.delete() 
    ShadowingExercise.query.delete()
    db.session.commit()
    print("  🗑️ 已清空旧版跟读练习及音频数据，准备刷入最新数据...")

    shadowing_defaults = [
        {
            'title': 'Using the Coffee Machine',
            'focus': 'Practice polite requests and apologies for interrupting. Focus on linking words like "could you" and the rising intonation when asking for help.',
            'text': '"Hi, sorry to bother you. I\'m trying to use the new coffee machine in the lounge, but I can\'t figure it out. Could you quickly show me how to make an espresso?"',
            'duration_str': '~0:35',
            'word_count': 32,
            'audios': {
                'us': '/static/audio/shadowing/coffee_us.mp3',
                'gb': '/static/audio/shadowing/coffee_gb.mp3',
                'au': '/static/audio/shadowing/coffee_au.mp3'
            }
        },
        {
            'title': 'Asking for Clarification',
            'focus': 'Practice formal academic tone. Focus on clear pronunciation of multi-syllable words like "equation" and "variable".',
            'text': '"Excuse me, Professor? I\'m having a little trouble understanding the second half of this equation. Could you explain how you derived that final variable?"',
            'duration_str': '~0:40',
            'word_count': 24,
            'audios': {
                'us': '/static/audio/shadowing/clarification_us.mp3',
                'gb': '/static/audio/shadowing/clarification_gb.mp3',
                'au': '/static/audio/shadowing/clarification_au.mp3'
            }
        },
        {
            'title': 'Planning a Study Session',
            'focus': 'Practice a casual, friendly rhythm. Master the natural linking in phrases like "are you free to" and "grab a table".',
            'text': '"Hey, are you free to go over the biology notes after the lecture? We could grab a table at the library and compare our study guides."',
            'duration_str': '~0:45',
            'word_count': 26,
            'audios': {
                'us': '/static/audio/shadowing/study_us.mp3',
                'gb': '/static/audio/shadowing/study_gb.mp3',
                'au': '/static/audio/shadowing/study_au.mp3'
            }
        },
        {
            'title': 'Presentation Introduction',
            'focus': 'Practice confident public speaking. Learn to pause effectively at punctuation marks and stress key information words.',
            'text': '"Good morning, everyone. Today, our group is going to discuss the impact of renewable energy on local economies. Let\'s start by looking at this graph on the first slide."',
            'duration_str': '~0:50',
            'word_count': 29,
            'audios': {
                'us': '/static/audio/shadowing/presentation_us.mp3',
                'gb': '/static/audio/shadowing/presentation_gb.mp3',
                'au': '/static/audio/shadowing/presentation_au.mp3'
            }
        }
    ]

    for data in shadowing_defaults:
        exercise = ShadowingExercise(
            title=data['title'],
            focus=data['focus'],
            text=data['text'],
            duration_str=data['duration_str'],
            word_count=data['word_count']
        )
        db.session.add(exercise)
        db.session.flush() # 刷新以获取 exercise.id

        for accent_code, audio_url in data['audios'].items():
            audio = ShadowingAudio(
                exercise_id=exercise.id,
                accent_code=accent_code,
                audio_url=audio_url
            )
            db.session.add(audio)
            
        print(f"  ✅ 正在插入跟读练习：{data['title']} (包含 {len(data['audios'])} 种口音)")


    # ─────────────────────────────────────────────
    # 5. Forum Posts & Comments (🌟 论坛干货数据 + 互动数据 🌟)
    # ─────────────────────────────────────────────
    # [新增] 创建 5 个"群演"学生账号，用来给帖子点赞和收藏
    dummy_users = []
    for i in range(1, 6):
        username = f'HappyStudent_{i}'
        u = User.query.filter_by(username=username).first()
        if not u:
            # 👇 新增：模拟真实生态，偶数ID是认证大神，奇数是普通小白
            is_qualified = (i % 2 == 0) 
            u = User(
                username=username, 
                email=f'student{i}@happyaspa.com',
                coins=10 * i, # 给点初始金币
                gaokao_score=140.0 if is_qualified else 110.0,
                is_guide_qualified=is_qualified
            )
            u.set_password('123456')
            db.session.add(u)
            db.session.flush() 
        dummy_users.append(u)

    old_posts = ForumPost.query.filter_by(user_id=tutor_user.id).all()
    for p in old_posts:
        db.session.delete(p)
    db.session.commit()
    
    forum_defaults = [
        {
            'title': 'Effective ways to memorize GRE/IELTS vocabulary?',
            'content': 'I\'ve been using flashcards, but I keep forgetting words after a week. It feels like I\'m stuck in a loop. Any tips on long-term retention?',
            'category': 'Vocabulary',
            'views': 152,
            'likes': 4,
            'favorites': 3,
            'comments': [
                'Spaced repetition is key! Also, try learning the etymology (roots, prefixes, suffixes) of the words.',
                'Try creating bizarre or funny mental images for the words you struggle with.'
            ]
        },
        {
            'title': 'When to use Present Perfect vs. Past Simple?',
            'content': 'I always get confused between "I have done" and "I did". Can someone explain the rule of thumb clearly?',
            'category': 'Grammar',
            'views': 230,
            'likes': 5,
            'favorites': 5,
            'comments': [
                'Here is the golden rule: Use Past Simple for finished actions in a finished time period. Use Present Perfect for actions that happened at an unspecified time before now.',
                'A quick tip: If you use words like "yesterday", you MUST use Past Simple.'
            ]
        },
        {
            'title': 'How to catch "connected speech" in fast English?',
            'content': 'When native speakers talk fast, words blend together and I completely lose track of the sentence. How can I practice?',
            'category': 'Listening',
            'views': 188,
            'likes': 3,
            'favorites': 2,
            'comments': [
                'Start by studying connected speech rules like assimilation, elision, and linking. A great exercise is "shadowing".',
                'Don\'t try to hear every single word! Focus on the stressed words (usually nouns, verbs, adjectives).'
            ]
        },
        {
            'title': 'Overcoming the fear of speaking with native speakers',
            'content': 'I know the grammar and vocabulary, but my mind goes blank and my heart races when I actually have to speak. How do you build confidence?',
            'category': 'Speaking',
            'views': 305,
            'likes': 5,
            'favorites': 4,
            'comments': [
                'It\'s totally normal! Try to reframe your mindset: native speakers don\'t judge your grammar; they just want to communicate.',
                'Accept that making mistakes is a crucial part of the process.'
            ]
        },
        {
            'title': 'Structuring an IELTS/TOEFL Task 2 Essay',
            'content': 'Does anyone have a reliable template or structure for agree/disagree essays? I always run out of time.',
            'category': 'Writing',
            'views': 275,
            'likes': 4,
            'favorites': 5,
            'comments': [
                'A solid 4-paragraph structure works best: 1) Introduction. 2) Body 1. 3) Body 2. 4) Conclusion. Keep your topic sentences crystal clear!'
            ]
        },
        {
            'title': 'Skimming vs. Scanning: When to use which?',
            'content': 'I always run out of time on academic reading tests. I try to read every word. How do I effectively balance skimming and scanning?',
            'category': 'Reading',
            'views': 140,
            'likes': 2,
            'favorites': 1,
            'comments': [
                'Skimming is for getting the "gist" or main idea. Scanning is for finding specific facts without reading the whole text.'
            ]
        },
        {
            'title': 'Best Pomodoro intervals for language study?',
            'content': 'Do you guys prefer 25/5 or 50/10 intervals for studying languages? I feel like 25 minutes is too short to get into the zone.',
            'category': 'General',
            'views': 95,
            'likes': 1,
            'favorites': 0,
            'comments': [
                'For intense cognitive tasks like reading academic papers, 50/10 allows for deep work. But for repetitive tasks like vocabulary, 25/5 is perfect.'
            ]
        }
    ]

    print("💬 正在导入论坛精华内容 (包含点赞和收藏互动)...")
    for data in forum_defaults:
        post = ForumPost.query.filter_by(title=data['title']).first()
        if not post:
            new_post = ForumPost(
                title=data['title'],
                content=data['content'],
                category=data['category'],
                board='guide',
                user_id=tutor_user.id,
                views=data['views']
            )
            db.session.add(new_post)
            db.session.flush() 
            
            for comment_text in data['comments']:
                new_comment = ForumComment(
                    post_id=new_post.id,
                    user_id=tutor_user.id,
                    content=comment_text
                )
                db.session.add(new_comment)
            
            for i in range(data['likes']):
                if i < len(dummy_users):
                    db.session.add(ForumLike(post_id=new_post.id, user_id=dummy_users[i].id))
                    
            for i in range(data['favorites']):
                if i < len(dummy_users):
                    db.session.add(ForumFavorite(post_id=new_post.id, user_id=dummy_users[i].id))
                    
            print(f"  ✅ 已发布干货贴：{data['category']} - {data['title'][:20]}... (获赞:{data['likes']}, 收藏:{data['favorites']})")
        else:
             print(f"  ⏭️ 帖子已存在，跳过：{data['title'][:20]}...")

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