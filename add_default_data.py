"""
Flask CLI 命令：向数据库填充或更新默认初始数据（支持更新新增列）

使用方法（在激活了虚拟环境的终端中运行）：
    flask add-default-data
"""

import click
import json
import os
from flask.cli import with_appcontext
# 👇 确保导入了 ForumLike 和 ForumFavorite
from models import db, ListeningExercise, SpeakingExercise, VocabularyWord, AcademicScenario, User, ForumPost, ForumComment, ForumLike, ForumFavorite
@click.command(name='add-default-data')
@with_appcontext
def add_default_data():
    """向数据库插入或更新默认初始数据（包含单词、听力、口语、学术情景）"""
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
            db.session.flush() # 刷新获取 ID
        dummy_users.append(u)

# 👇 [核心修复]：每次运行前，先清理掉官方导师之前发的旧帖子，强行重新洗牌
    old_posts = ForumPost.query.filter_by(user_id=tutor_user.id).all()
    for p in old_posts:
        db.session.delete(p)
    db.session.commit()
    # 👆 修复结束
    
    forum_defaults = [
        {
            'title': 'Effective ways to memorize GRE/IELTS vocabulary?',
            'content': 'I\'ve been using flashcards, but I keep forgetting words after a week. It feels like I\'m stuck in a loop. Any tips on long-term retention?',
            'category': 'Vocabulary',
            'views': 152,
            'likes': 4,       # 设定点赞数
            'favorites': 3,   # 设定收藏数
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
            # 1. 创建帖子
            new_post = ForumPost(
                title=data['title'],
                content=data['content'],
                category=data['category'],
                board='guide',
                user_id=tutor_user.id,
                views=data['views']
            )
            db.session.add(new_post)
            db.session.flush() # 刷新以获取 new_post.id
            
            # 2. 创建评论
            for comment_text in data['comments']:
                new_comment = ForumComment(
                    post_id=new_post.id,
                    user_id=tutor_user.id,
                    content=comment_text
                )
                db.session.add(new_comment)
            
            # 3. [新增] 让群演进行点赞
            for i in range(data['likes']):
                if i < len(dummy_users):
                    db.session.add(ForumLike(post_id=new_post.id, user_id=dummy_users[i].id))
                    
            # 4. [新增] 让群演进行收藏
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