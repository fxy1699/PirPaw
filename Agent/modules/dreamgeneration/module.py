"""
梦境生成样例：
梦境关键词：Mournful 哀伤的、Lonely 孤独的、Grieving 悲痛的
那天晚上，我做了一个梦，仿佛自己置身于一片无尽的荒野之中。四周除了风声就是寂静，连鸟儿都不愿停留。我独自一人漫步在这片荒凉之地，脚下是枯黄的草，天空中飘着几朵厚重的乌云，遮住了阳光，让整个世界都显得格外阴沉。走着走着，前方出现了一座古老的石桥，桥下流淌着一条清澈见底的小河，但河水却呈现出一种莫名的悲伤蓝。正当我准备过桥时，突然发现桥中央坐着一个身影，背对着我，长发随风轻轻摇曳。我慢慢靠近，想要看清她的面容，却发现那不过是自己内心的倒影——一个孤独而哀伤的灵魂，在这无人问津的世界里默默哭泣。那一刻，所有的悲痛化作了泪水，与桥下的流水融为一体，流向远方未知的地方。
"""

from Agent.base_module import BaseModule
import random
import os
from typing import Optional, List, Dict

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
import random
import threading
from Agent.data.diary.diary_manager import DiaryManager

class DreamGenerationModule(BaseModule):
    """梦境生成模块 - 基于自主宠物情绪状态生成梦境文本"""

    name = "梦境生成"
    description = "基于宠物当前情绪状态生成富有想象力的梦境文本"
    version = "2.0.0"
    author = "开发者A"

    def __init__(self):
        super().__init__()
        self.diary_manager = None
        
        # 情绪关键词映射表 - 将5维情绪映射到具体的梦境关键词
        self.emotion_keywords_mapping = {
            'happiness': {
                'high': ['Joyful 喜悦的', 'Elated 兴高采烈的', 'Blissful 幸福的', 'Radiant 光芒四射的', 'Euphoric 欣快的'],
                'medium': ['Content 满足的', 'Cheerful 开朗的', 'Pleased 愉快的', 'Delighted 欣喜的', 'Optimistic 乐观的'],
                'low': ['Melancholic 忧郁的', 'Subdued 低沉的', 'Wistful 若有所思的', 'Pensive 沉思的', 'Reflective 反思的']
            },
            'energy': {
                'high': ['Vibrant 充满活力的', 'Dynamic 动态的', 'Energetic 精力充沛的', 'Vigorous 精力旺盛的', 'Spirited 精神饱满的'],
                'medium': ['Steady 稳定的', 'Balanced 平衡的', 'Calm 平静的', 'Gentle 温和的', 'Peaceful 和平的'],
                'low': ['Tired 疲倦的', 'Weary 疲惫的', 'Sluggish 迟缓的', 'Lethargic 无精打采的', 'Exhausted 精疲力竭的']
            },
            'boredom': {
                'high': ['Restless 不安的', 'Monotonous 单调的', 'Stagnant 停滞的', 'Tedious 乏味的', 'Uninspired 缺乏灵感的'],
                'medium': ['Routine 例行的', 'Ordinary 普通的', 'Neutral 中性的', 'Familiar 熟悉的', 'Predictable 可预测的'],
                'low': ['Engaged 投入的', 'Fascinated 着迷的', 'Absorbed 专注的', 'Captivated 被吸引的', 'Stimulated 受刺激的']
            },
            'curiosity': {
                'high': ['Inquisitive 好奇的', 'Exploratory 探索的', 'Wondering 疑惑的', 'Investigative 调查的', 'Mysterious 神秘的'],
                'medium': ['Interested 感兴趣的', 'Attentive 专注的', 'Observant 观察的', 'Thoughtful 深思的', 'Contemplative 沉思的'],
                'low': ['Indifferent 冷漠的', 'Disinterested 不感兴趣的', 'Apathetic 无动于衷的', 'Passive 被动的', 'Detached 超然的']
            },
            'loneliness': {
                'high': ['Lonely 孤独的', 'Isolated 孤立的', 'Abandoned 被遗弃的', 'Solitary 独居的', 'Desolate 荒凉的'],
                'medium': ['Introspective 内省的', 'Contemplative 沉思的', 'Reflective 反思的', 'Meditative 冥想的', 'Quiet 安静的'],
                'low': ['Connected 连接的', 'Accompanied 有陪伴的', 'Social 社交的', 'Warm 温暖的', 'Embraced 被拥抱的']
            }
        }
        # self.dream_bot = self._init_agent_service()

    def setup(self, config=None):
        """初始化模块"""
        super().setup(config)
        
        # 在 setup 时实例化 diary manager
        if self.diary_manager is None:
            self.diary_manager = DiaryManager()

        # 如果已经有agent_core引用，尝试连接自主宠物模块
        if hasattr(self, 'agent_core') and self.agent_core:
            self._connect_to_autonomous_pet()
        # 启动主动梦境交互线程
        self._dream_thread_stop = False
        self._dream_thread = threading.Thread(target=self._dream_interaction_loop)
        self._dream_thread.daemon = True
        self._dream_thread.start()
        print(" 梦境主动交互线程已启动")

    def _dream_interaction_loop(self):
        """主动梦境交互线程"""
        import random
        import time
        from datetime import datetime
        
        is_debug = True
        while not self._dream_thread_stop:
            if not is_debug:
                # 等待 10-20 分钟
                sleep_minutes = random.randint(10, 20)
                print(f"🌙 梦境线程将等待 {sleep_minutes} 分钟后开始交互")
                time.sleep(sleep_minutes * 60)
            else:
                sleep_minutes = 1
                print(f"🌙 梦境交互 Debug 模式，梦境线程将等待 {sleep_minutes} 分钟后开始交互")
                time.sleep(sleep_minutes * 60)
            try:
                # 检查今天的梦境
                today_dream = self.diary_manager.get_today_dream()
                print(f"梦境数据库中存储的内容： {today_dream}")

                if today_dream and today_dream['told_user']:
                    # 梦境已存在且用户已看过，退出线程
                    print("🌙 今日梦境已告诉用户，退出主动交互")
                    break
                
                elif today_dream and not today_dream['told_user']:
                    # 梦境存在但未告诉用户，主动提醒
                    self._send_dream_reminder(today_dream['content'])
                    break
                
                else:
                    # 没有梦境，生成新梦境
                    self._generate_and_send_dream()
                    break
                    
            except Exception as e:
                print(f"❌ 梦境主动交互失败: {e}")
                break
            if is_debug:
                # debug 模式启动直接执行，然后等待10-20分钟
                sleep_minutes = random.randint(10, 20)
                print(f"🌙 梦境线程将等待 {sleep_minutes} 分钟后开始交互")
                time.sleep(sleep_minutes * 60)

    def _send_dream_reminder(self, dream_content: str):
        """发送梦境提醒"""
        import random
        
        # 随机选择提醒话语
        reminder_messages = [
            "你昨天睡得怎么样呀？我昨天做了一个梦，我刚刚写在日记里了，吓死我了差点就忘了",
            "诶，我想起来了！我昨晚做了一个很奇怪的梦，已经记在日记本里了，你要不要看看？",
            "对了对了，我昨晚做梦了！刚才整理日记的时候想起来了，差点就忘了告诉你",
            "我昨晚做了一个梦，现在才想起来要跟你说，已经写在日记里了，你要看看吗？",
            "突然想起来，我昨晚做了个梦，刚才整理日记的时候记起来了，差点就忘了",
            "我昨晚的梦好有意思，刚才写日记的时候想起来了，你要不要听听看？",
            "诶，我昨晚做梦了！刚才翻日记本的时候想起来了，差点就忘了跟你说"
        ]
        
        selected_message = random.choice(reminder_messages)
        
        # 使用 autonomous_pet 的 bubble_callback 发送气泡消息
        if hasattr(self, 'agent_core') and self.agent_core:
            try:
                # 查找自主宠物模块
                autonomous_pet_module = None
                for module in self.agent_core.modules:
                    if hasattr(module, 'name') and '自主宠物' in module.name:
                        autonomous_pet_module = module
                        break
                
                if autonomous_pet_module and hasattr(autonomous_pet_module, '_trigger_bubble'):
                    # 创建气泡字典
                    bubble_dict = {
                        'message': selected_message,
                        'bubble_type': 'autonomous_dream',
                        'icon': None,
                        'start_audio': None,
                        'end_audio': None
                    }
                    # 调用气泡回调
                    autonomous_pet_module._trigger_bubble(bubble_dict)
                    print(f"🎈 梦境提醒气泡已发送: {selected_message}")
                elif hasattr(self.agent_core, 'add_bot_message'):
                    self.agent_core.add_bot_message(selected_message)
                    print(f"💬 梦境提醒已发送到聊天界面: {selected_message}")
                else:
                    print(f"🌙 梦境提醒: {selected_message}")
            except Exception as e:
                print(f"❌ 发送梦境提醒失败: {e}")
        else:
            print(f"🌙 梦境提醒: {selected_message}")
    
    def _generate_and_send_dream(self):
        """生成并发送新梦境"""
        try:
            # 生成梦境
            # 调用 agent_core 的 process_message("你昨天做了什么梦")
            if hasattr(self, 'agent_core') and self.agent_core:
                try:
                    # process_message 可能是同步或异步，这里假设为同步
                    self.agent_core.process_message("你昨天做了什么梦")
                except Exception as e:
                    print(f"❌ 调用 agent_core 生成梦境失败: {e}")
            else:
                print("⚠️ agent_core 不可用，无法生成梦境")
                dream_result = None
    
            # 判断今日是否已经有梦境，如果有则说明生成成功
            has_today_dream = False
            try:
                if self.diary_manager:
                    today_dream = self.diary_manager.get_today_dream()
                    if today_dream:
                        has_today_dream = True
            except Exception as e:
                print(f"❌ 检查今日梦境失败: {e}")
                has_today_dream = False
    
            if has_today_dream:
                # 发送梦境提醒
                reminder_messages = [
                    "我昨晚做了一个梦，已经写在日记里了，你要不要看看？",
                    "诶，我昨晚做梦了！已经记在日记本里了，你要听听吗？",
                    "我昨晚做了个很奇怪的梦，已经写在日记里了，你要看看吗？",
                    "我昨晚做梦了，已经记在日记本里了，差点就忘了告诉你",
                    "我昨晚做了个梦，现在写在日记里了，你要不要看看？"
                ]
                
                selected_message = random.choice(reminder_messages)
                
                # 发送消息给用户
                if hasattr(self, 'agent_core') and self.agent_core:
                    try:
                        # 查找自主宠物模块
                        autonomous_pet_module = None
                        for module in self.agent_core.modules:
                            if hasattr(module, 'name') and '自主宠物' in module.name:
                                autonomous_pet_module = module
                                break
                            
                        if autonomous_pet_module and hasattr(autonomous_pet_module, '_trigger_bubble'):
                            # 创建气泡字典
                            bubble_dict = {
                                'message': selected_message,
                                'bubble_type': 'autonomous_dream',
                                'icon': 'dream',  # 可以根据实际情况调整
                                'start_audio': None,
                                'end_audio': None
                            }
                            # 调用气泡回调
                            autonomous_pet_module._trigger_bubble(bubble_dict)
                            print(f"🎈 新梦境提醒气泡已发送: {selected_message}")
                        elif hasattr(self.agent_core, 'add_bot_message'):
                            self.agent_core.add_bot_message(selected_message)
                            print(f"💬 新梦境提醒已发送到聊天界面: {selected_message}")
                        else:
                            print(f"🌙 新梦境提醒: {selected_message}")
                    except Exception as e:
                        print(f"❌ 发送新梦境提醒失败: {e}")
                else:
                    print(f"🌙 新梦境提醒: {selected_message}")
                    
            else:
                print("❌ 生成梦境失败")
                
        except Exception as e:
            print(f"❌ 生成并发送梦境失败: {e}")
    
    def _get_current_pet_name(self) -> str:
        """获取当前宠物名称"""
        try:
            if hasattr(self, 'agent_core') and self.agent_core:
                pet_module = self.agent_core.get_module('petaction')
                if pet_module and hasattr(pet_module, 'current_pet_name'):
                    return pet_module.current_pet_name
            return "宠物"
        except:
            return "宠物"
    
    def cleanup(self):
        """清理资源"""
        self._dream_thread_stop = True
        if hasattr(self, '_dream_thread') and self._dream_thread.is_alive():
            self._dream_thread.join(timeout=5)
        super().cleanup()

    def set_agent_core(self, agent_core):
        """设置Agent核心引用，用于访问其他模块"""
        self.agent_core = agent_core
        
        # 尝试连接自主宠物模块
        self._connect_to_autonomous_pet()
    
    def _connect_to_autonomous_pet(self):
        """连接到自主宠物模块"""
        if hasattr(self, 'agent_core') and self.agent_core:
            try:
                for module in self.agent_core.modules:
                    if hasattr(module, 'name') and '自主宠物' in module.name:
                        self.autonomous_pet_module = module
                        print(f"✅ 梦境生成已连接到自主宠物模块")
                        return True
                print(f"⚠️ 未找到自主宠物模块，将使用默认情绪生成")
            except Exception as e:
                print(f"⚠️ 连接自主宠物模块失败: {e}")
        return False

    def _get_pet_emotions(self) -> Dict[str, float]:
        """获取宠物当前情绪状态"""
        if self.autonomous_pet_module and hasattr(self.autonomous_pet_module, 'emotions'):
            try:
                # 获取当前情绪状态
                emotions = self.autonomous_pet_module.emotions.get_current_emotions()
                print(f"🎭 获取到宠物情绪状态: {emotions}")
                return emotions
            except Exception as e:
                print(f"⚠️ 获取宠物情绪失败: {e}")
        
        # 如果无法获取，返回默认情绪
        print(f"⚠️ 使用默认情绪状态")
        return {
            'happiness': 0.5,
            'energy': 0.5,
            'boredom': 0.5,
            'curiosity': 0.5,
            'loneliness': 0.5
        }

    def _emotions_to_keywords(self, emotions: Dict[str, float]) -> List[str]:
        """将情绪数值转换为最相近的关键词"""
        keywords = []
        
        # 对每个情绪维度，根据数值选择对应的关键词
        for emotion, value in emotions.items():
            if emotion in self.emotion_keywords_mapping:
                # 根据数值确定等级
                if value >= 0.7:
                    level = 'high'
                elif value >= 0.4:
                    level = 'medium'
                else:
                    level = 'low'
                
                # 从对应等级随机选择一个关键词
                available_keywords = self.emotion_keywords_mapping[emotion][level]
                selected_keyword = random.choice(available_keywords)
                keywords.append(selected_keyword)
        
        # 选择最突出的3个情绪维度
        # 计算每个情绪的"强度"（偏离中性值0.5的程度）
        emotion_intensities = {}
        for emotion, value in emotions.items():
            # 计算偏离中性值的程度
            intensity = abs(value - 0.5)
            emotion_intensities[emotion] = intensity
        
        # 按强度排序，选择前3个
        top_emotions = sorted(emotion_intensities.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 只返回最突出的3个情绪对应的关键词
        final_keywords = []
        for emotion, _ in top_emotions:
            if emotion in self.emotion_keywords_mapping:
                value = emotions[emotion]
                if value >= 0.7:
                    level = 'high'
                elif value >= 0.4:
                    level = 'medium'
                else:
                    level = 'low'
                
                available_keywords = self.emotion_keywords_mapping[emotion][level]
                selected_keyword = random.choice(available_keywords)
                final_keywords.append(selected_keyword)
        
        return final_keywords

    def _get_emotion_keywords(self):
        """获取基于宠物真实情绪的关键词（替代原来的随机方法）"""
        # 获取宠物当前情绪
        emotions = self._get_pet_emotions()
        
        # 转换为关键词
        keywords = self._emotions_to_keywords(emotions)
        
        print(f"🎭 情绪映射: {emotions} -> {keywords}")
        
        return keywords

    def _init_agent_service(self):
        try:
            llm_cfg = {'model': 'qwen-max'}
            system = '你扮演船长索霖的梦境生成助手，能够根据小熊猫船长的心情关键词，创作一段有画面感的梦境场景或故事。梦境应富有想象力、细节丰富、情感饱满，体现船长索霖的冒险精神和内心阳光。'
            bot = Assistant(
                llm=llm_cfg,
                name='梦境生成助手',
                description='生成梦境文本',
                system_message=system,
                function_list=[],
            )
            return bot
        except Exception as e:
            print(f"⚠️ 梦境生成模块初始化失败: {e}")
            print("💡 梦境生成功能将使用简化模式")
            return None

    def handle_message(self, message: str, context=None):
        """
        仅当消息包含“梦”字时，才生成梦境文本，否则返回 None
        """
        if "梦" not in message:
            return None
        try:
            keywords = self._get_emotion_keywords()
            return self._generate_dream(keywords)
        except Exception as e:
            print(f"❌ 梦境生成处理失败: {e}")
            return "抱歉，梦境生成功能暂时不可用。"

    def get_capabilities(self) -> list:
        return [
            "根据关键词生成梦境文本"
        ]

    def get_function_definitions(self) -> list:
        return [
            {
                "name": "generate_dream",
                "description": "根据随机的关键词生成梦境文本",
                "parameters": []
            }
        ]
    
    def call_function(self, function_name: str, arguments: dict):
        """调用模块功能"""
        if function_name == "generate_dream":
            keywords = self._get_emotion_keywords()
            return self._generate_dream(keywords)
        else:
            raise ValueError(f"未知的功能: {function_name}")

    def _generate_dream(self, keywords: list) -> str:
        """
        调用大模型，根据心情关键词生成梦境文本
        """
        # 构造 prompt
        keywords_str = '、'.join(keywords)
        print(f"[DEBUG] 梦境关键词：{keywords_str}")
        
        # 如果dream_bot不可用，使用简化模式
        # if not self.dream_bot:
        #     return self._generate_simple_dream(keywords_str)
        
        prompt = (
            f"请以船长索霖的身份，以以下心情为主题，创作一段有画面感的梦境场景或故事，要求细节丰富、情感饱满，富有想象力。\n"
            f"要求以第一人称描述，以船长跟船员讲故事的口吻叙述，体现小熊猫船长的冒险精神和内心阳光。200字左右。仅描述梦境，不要透露有关提示词的内容。"
            f"心情关键词：{keywords_str}\n"
            f"梦境："
        )
        return prompt
        # # 调用大模型生成
        # response = ""
        # try:
        #     response = []
        #     for response in self.dream_bot.run(messages=[{"role": "user", "content": prompt}]):
        #         continue
        #         # print(f"[DEBUG] bot response: {response}")
        #     response = response[0]["content"]
        # except Exception as e:
        #     print(f"❌ 梦境生成失败: {e}")
        #     response = self._generate_simple_dream(keywords_str)
        # return response
    
    def _generate_simple_dream(self, keywords_str: str) -> str:
        """简化模式：生成基础梦境文本"""
        # 预定义的梦境模板
        dream_templates = [
          f"那天晚上，本船长做了一个梦。梦中我置身于一个充满{keywords_str}氛围的世界里，就像在探索新大陆一样。四周的景象让我感到深深的情感共鸣，仿佛整个世界都在诉说着内心的故事。船员，船长大人的梦境可是很有深度的！",
            f"在梦里，本船长经历了一段奇妙的旅程。{keywords_str}的情绪如影随形，让我在梦境中体验到了前所未有的感受。就像在海上冒险一样刺激！",
            f"本船长做了一个关于{keywords_str}的梦。梦中的场景如此真实，让我醒来后仍然沉浸在那份独特的情感中。船员，船长大人连做梦都在冒险呢！"
        ]
        
        import random
        return random.choice(dream_templates)
