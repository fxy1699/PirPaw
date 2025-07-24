"""
梦境生成样例：
梦境关键词：Mournful 哀伤的、Lonely 孤独的、Grieving 悲痛的
那天晚上，我做了一个梦，仿佛自己置身于一片无尽的荒野之中。四周除了风声就是寂静，连鸟儿都不愿停留。我独自一人漫步在这片荒凉之地，脚下是枯黄的草，天空中飘着几朵厚重的乌云，遮住了阳光，让整个世界都显得格外阴沉。走着走着，前方出现了一座古老的石桥，桥下流淌着一条清澈见底的小河，但河水却呈现出一种莫名的悲伤蓝。正当我准备过桥时，突然发现桥中央坐着一个身影，背对着我，长发随风轻轻摇曳。我慢慢靠近，想要看清她的面容，却发现那不过是自己内心的倒影——一个孤独而哀伤的灵魂，在这无人问津的世界里默默哭泣。那一刻，所有的悲痛化作了泪水，与桥下的流水融为一体，流向远方未知的地方。
"""

from Agent.base_module import BaseModule
import random
import os
from typing import Optional

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
import random

class DreamGenerationModule(BaseModule):
    """梦境生成模块 - 根据关键词生成梦境文本"""

    name = "梦境生成"
    description = "根据输入的关键词生成富有想象力的梦境文本"
    version = "1.0.0"
    author = "开发者A"

    def __init__(self):
        super().__init__()
        self.emotion_json = [
            {
                "name": "Happy 开心的",
                "prob": 6,
                "fine-grained": [
                    {"name": "Content 舒适满足", "prob": 8},
                    {"name": "Joyful 喜悦的", "prob": 7},
                    {"name": "Elated 兴高采烈的", "prob": 6},
                    {"name": "Inspired 受到启发的", "prob": 5},
                    {"name": "Delighted 欣喜的", "prob": 4},
                    {"name": "Cheerful 开朗的", "prob": 3},
                    {"name": "Ecstatic 狂喜的", "prob": 2}
                ]
            },
            {
                "name": "Sad 伤心的",
                "prob": 3,
                "fine-grained": [
                    {"name": "Depressed 沮丧的", "prob": 8},
                    {"name": "Grieving 悲痛的", "prob": 7},
                    {"name": "Lonely 孤独的", "prob": 6},
                    {"name": "Heartbroken 心碎的", "prob": 5},
                    {"name": "Mournful 哀伤的", "prob": 4},
                    {"name": "Despondent 绝望的", "prob": 3}
                ]
            },
            {
                "name": "Angry 生气的",
                "prob": 2,
                "fine-grained": [
                    {"name": "Annoyed 恼怒的", "prob": 8},
                    {"name": "Frustrated 沮丧的（因受阻）", "prob": 7},
                    {"name": "Furious 愤怒的", "prob": 6},
                    {"name": "Enraged 暴怒的", "prob": 5},
                    {"name": "Livid 气极的", "prob": 4},
                    {"name": "Hostile 敌对的", "prob": 3}
                ]
            },
            {
                "name": "Fearful 害怕的",
                "prob": 3,
                "fine-grained": [
                    {"name": "Anxious 焦虑的", "prob": 8},
                    {"name": "Terrified 极度恐惧的", "prob": 7},
                    {"name": "Nervous 紧张的", "prob": 6},
                    {"name": "Panicked 惊慌失措的", "prob": 5},
                    {"name": "Apprehensive 忧虑的", "prob": 4},
                    {"name": "Uneasy 不安的", "prob": 3}
                ]
            },
            {
                "name": "Surprised 惊讶的",
                "prob": 1,
                "fine-grained": [
                    {"name": "Astonished 震惊的", "prob": 8},
                    {"name": "Shocked 震撼的", "prob": 7},
                    {"name": "Amazed 惊异的", "prob": 6},
                    {"name": "Stunned 目瞪口呆的", "prob": 5},
                    {"name": "Dazed 恍惚的", "prob": 4},
                    {"name": "Flabbergasted 大吃一惊的", "prob": 3}
                ]
            },
            {
                "name": "Disgusted 讨厌的",
                "prob": 1,
                "fine-grained": [
                    {"name": "Repulsed 厌恶的", "prob": 8},
                    {"name": "Loathing 憎恶的", "prob": 7},
                    {"name": "Revulsion 强烈反感", "prob": 6},
                    {"name": "Nauseated 作呕的", "prob": 5},
                    {"name": "Detestable 可憎的", "prob": 4},
                    {"name": "Contemptuous 蔑视的", "prob": 3}
                ]
            },
            {
                "name": "Love 喜爱的",
                "prob": 3,
                "fine-grained": [
                    {"name": "Affectionate 有感情的", "prob": 8},
                    {"name": "Passionate 热情的", "prob": 7},
                    {"name": "Devoted 忠诚的", "prob": 6},
                    {"name": "Adoring 崇拜的", "prob": 5},
                    {"name": "Cherishing 珍爱的", "prob": 4},
                    {"name": "Romantic 浪漫的", "prob": 3}
                ]
            },
            {
                "name": "Hopeful 有希望的",
                "prob": 2,
                "fine-grained": [
                    {"name": "Eager 热切的", "prob": 8},
                    {"name": "Anticipating 期待的", "prob": 7},
                    {"name": "Yearning 渴望的", "prob": 6},
                    {"name": "Aspiring 有抱负的", "prob": 5},
                    {"name": "Optimistic 乐观的", "prob": 4},
                    {"name": "Expectant 期盼的", "prob": 3}
                ]
            }
        ]
        self.dream_bot = self._init_agent_service()

    def _init_agent_service(self):
        llm_cfg = {'model': 'qwen-max'}
        system = '你扮演一个梦境文本生成助手，能够根据用户提供的心情关键词，创作一段有画面感的梦境场景或故事。梦境应富有想象力、细节丰富、情感饱满。'
        bot = Assistant(
            llm=llm_cfg,
            name='梦境生成助手',
            description='生成梦境文本',
            system_message=system,
            function_list=[],
        )
        return bot

    def _get_emotion_keywords(self):
        emotion_weights = [emotion['prob'] for emotion in self.emotion_json]
        selected_emotion_index = random.choices(range(len(self.emotion_json)), weights=emotion_weights, k=1)[0]
        fine_grained_emotions = self.emotion_json[selected_emotion_index]['fine-grained']
        fine_grained_weights = [emotion['prob'] for emotion in fine_grained_emotions]
        selected_fine_grained_indices = random.choices(range(len(fine_grained_emotions)), weights=fine_grained_weights, k=3)
        selected_fine_grained_emotions = [fine_grained_emotions[i]['name'] for i in selected_fine_grained_indices]
        return selected_fine_grained_emotions

    def handle_message(self, message: str, context=None):
        """
        仅当消息包含“梦”字时，才生成梦境文本，否则返回 None
        """
        if "梦" not in message:
            return None
        keywords = self._get_emotion_keywords()
        return self._generate_dream(keywords)

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

    def _generate_dream(self, keywords: list) -> str:
        """
        调用大模型，根据心情关键词生成梦境文本
        """
        # 构造 prompt
        keywords_str = '、'.join(keywords)
        print(f"[DEBUG] 梦境关键词：{keywords_str}")
        prompt = (
            f"请以以下心情为主题，创作一段有画面感的梦境场景或故事，要求细节丰富、情感饱满，富有想象力。\n"
            f"要求以第一人称描述，以跟朋友讲故事的口吻叙述。200字左右。仅描述梦境，不要透露有关提示词的内容。"
            f"心情关键词：{keywords_str}\n"
            f"梦境："
        )
        # 调用大模型生成
        response = ""
        try:
            response = []
            for response in self.dream_bot.run(messages=[{"role": "user", "content": prompt}]):
                continue
                # print(f"[DEBUG] bot response: {response}")
            response = response[0]["content"]
        except Exception as e:
            response = f"梦境生成失败：{e}"
        return response
