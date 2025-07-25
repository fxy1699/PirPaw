"""
轻量级情感系统 - 宠物的"心情管理"
"""

import random
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta


class EmotionSystem:
    """宠物情感系统 - 管理5种基本情感"""
    
    def __init__(self, memory_manager=None):
        self.memory = memory_manager
        
        # 5种基本情感 (0.0-1.0)
        self.emotions = {
            'happiness': 0.7,    # 快乐度
            'energy': 0.8,       # 精力值
            'boredom': 0.3,      # 无聊度
            'curiosity': 0.6,    # 好奇心
            'loneliness': 0.4    # 孤独感
        }
        
        # 情感衰减速度（每小时）
        self.decay_rates = {
            'happiness': -0.05,
            'energy': -0.08,
            'boredom': 0.1,
            'curiosity': -0.03,
            'loneliness': 0.06
        }
        
        self.last_update = datetime.now()
        
        # 从数据库加载最新状态
        if self.memory:
            saved_emotions = self.memory.get_latest_emotion_state()
            self.emotions.update(saved_emotions)
    
    def update_emotions(self, force_save=False):
        """自然衰减情感值"""
        now = datetime.now()
        hours_passed = (now - self.last_update).total_seconds() / 3600
        
        if hours_passed > 0.1:  # 至少6分钟更新一次
            for emotion, decay_rate in self.decay_rates.items():
                change = decay_rate * hours_passed
                self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion] + change))
            
            self.last_update = now
            
            # 定期保存到数据库
            if force_save or hours_passed > 1.0:
                self.save_emotions("自然衰减")
    
    def trigger_emotion(self, emotion_changes: Dict[str, float], reason: str = ""):
        """触发情感变化"""
        old_emotions = self.emotions.copy()
        
        for emotion, change in emotion_changes.items():
            if emotion in self.emotions:
                self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion] + change))
        
        # 保存变化
        if self.memory:
            self.memory.save_emotion_state(self.emotions, f"情感触发: {reason}")
        
        print(f"😊 情感变化: {reason}")
        for emotion, change in emotion_changes.items():
            if emotion in old_emotions:
                old_val = old_emotions[emotion]
                new_val = self.emotions[emotion]
                print(f"   {self._emotion_emoji(emotion)} {emotion}: {old_val:.2f} → {new_val:.2f} ({change:+.2f})")
    
    def get_current_emotions(self) -> dict:
        """获取当前所有情感状态"""
        # 首先更新情感状态
        self.update_emotions()
        return self.emotions.copy()
    
    def get_dominant_emotion(self) -> str:
        """获取当前主导情感"""
        # 加权计算主导情感
        weights = {
            'happiness': self.emotions['happiness'],
            'energy': self.emotions['energy'] * 0.8,
            'boredom': self.emotions['boredom'] * 1.2,  # 无聊更容易主导
            'curiosity': self.emotions['curiosity'] * 0.9,
            'loneliness': self.emotions['loneliness'] * 1.1  # 孤独感更明显
        }
        
        return max(weights, key=weights.get)
    
    def get_mood_description(self) -> str:
        """获取心情描述"""
        dominant = self.get_dominant_emotion()
        value = self.emotions[dominant]
        
        if dominant == 'happiness':
            if value > 0.8: return "超级开心"
            elif value > 0.6: return "很开心"
            elif value > 0.4: return "有点开心"
            else: return "不太开心"
            
        elif dominant == 'energy':
            if value > 0.8: return "精力充沛"
            elif value > 0.6: return "很有活力"
            elif value > 0.4: return "有点累了"
            else: return "好困啊"
            
        elif dominant == 'boredom':
            if value > 0.8: return "超级无聊"
            elif value > 0.6: return "很无聊"
            elif value > 0.4: return "有点无聊"
            else: return "不无聊"
            
        elif dominant == 'curiosity':
            if value > 0.8: return "超级好奇"
            elif value > 0.6: return "很好奇"
            elif value > 0.4: return "有点好奇"
            else: return "不太好奇"
            
        elif dominant == 'loneliness':
            if value > 0.8: return "很孤独"
            elif value > 0.6: return "有点孤独"
            elif value > 0.4: return "还好"
            else: return "不孤独"
        
        return "平静"
    
    def should_trigger_behavior(self, behavior_type: str) -> bool:
        """判断是否应该触发某种行为"""
        self.update_emotions()
        
        triggers = {
            'seek_attention': self.emotions['loneliness'] > 0.7 or self.emotions['boredom'] > 0.8,
            'play': self.emotions['energy'] > 0.6 and self.emotions['happiness'] > 0.5,
            'rest': self.emotions['energy'] < 0.3,
            'explore': self.emotions['curiosity'] > 0.7 and self.emotions['energy'] > 0.4,
            'self_talk': self.emotions['boredom'] > 0.6 and self.emotions['loneliness'] > 0.5,
            'greet': self.emotions['happiness'] > 0.6 and self.emotions['energy'] > 0.5,
            'care': self.emotions['loneliness'] < 0.3 and self.emotions['happiness'] > 0.7
        }
        
        return triggers.get(behavior_type, False)
    
    def get_behavior_probability(self, behavior_type: str) -> float:
        """获取行为触发概率"""
        if not self.should_trigger_behavior(behavior_type):
            return 0.0
        
        base_probabilities = {
            'seek_attention': 0.3,
            'play': 0.2,
            'rest': 0.4,
            'explore': 0.15,
            'self_talk': 0.1,
            'greet': 0.25,
            'care': 0.1
        }
        
        # 根据情感状态调整概率
        emotion_multipliers = {
            'seek_attention': self.emotions['loneliness'] * 1.5 + self.emotions['boredom'],
            'play': self.emotions['energy'] * self.emotions['happiness'],
            'rest': (1.0 - self.emotions['energy']) * 1.5,
            'explore': self.emotions['curiosity'] * self.emotions['energy'],
            'self_talk': self.emotions['boredom'] * self.emotions['loneliness'],
            'greet': self.emotions['happiness'] * self.emotions['energy'],
            'care': self.emotions['happiness'] * (1.0 - self.emotions['loneliness'])
        }
        
        base_prob = base_probabilities.get(behavior_type, 0.1)
        multiplier = emotion_multipliers.get(behavior_type, 1.0)
        
        return min(0.8, base_prob * multiplier)  # 最高80%概率
    
    def save_emotions(self, notes: str = ""):
        """保存当前情感状态"""
        if self.memory:
            self.memory.save_emotion_state(self.emotions, notes)
    
    def get_emotion_summary(self) -> Dict[str, Any]:
        """获取情感摘要"""
        return {
            'emotions': self.emotions.copy(),
            'dominant_emotion': self.get_dominant_emotion(),
            'mood_description': self.get_mood_description(),
            'last_update': self.last_update.isoformat()
        }
    
    def _emotion_emoji(self, emotion: str) -> str:
        """获取情感对应的emoji"""
        emojis = {
            'happiness': '😊',
            'energy': '⚡',
            'boredom': '😴',
            'curiosity': '🤔',
            'loneliness': '😢'
        }
        return emojis.get(emotion, '❓')
    
    def simulate_interaction_effects(self):
        """模拟用户互动的情感效果"""
        # 用户互动通常带来正面效果
        effects = {
            'happiness': random.uniform(0.1, 0.3),
            'energy': random.uniform(0.05, 0.2),
            'boredom': random.uniform(-0.3, -0.1),
            'curiosity': random.uniform(0.05, 0.15),
            'loneliness': random.uniform(-0.4, -0.2)
        }
        
        self.trigger_emotion(effects, "用户互动")
    
    def simulate_time_effects(self, hours: float):
        """模拟时间流逝的效果"""
        for emotion, decay_rate in self.decay_rates.items():
            change = decay_rate * hours
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion] + change))
        
        self.save_emotions(f"时间流逝 {hours:.1f}小时") 