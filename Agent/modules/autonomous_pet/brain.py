"""
宠物大脑 - 简单而有效的决策中心
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple


class PetBrain:
    """宠物的简单"大脑" - 决策和意图生成器"""
    
    def __init__(self, emotion_system, memory_manager, agent_core=None):
        self.emotions = emotion_system
        self.memory = memory_manager
        self.agent_core = agent_core
        
        # 决策冷却时间（避免过于频繁的行为）
        self.last_proactive_action = datetime.now() - timedelta(hours=1)
        self.min_action_interval = timedelta(minutes=5)  # 最少5分钟间隔
        
        # 行为类型定义
        self.behavior_types = [
            'seek_attention',  # 寻求关注
            'self_talk',       # 自言自语
            'greet',          # 主动问候
            'care',           # 关怀用户
            'explore',        # 探索学习
            'rest',           # 休息
            'play'            # 玩耍
        ]
        
        # 工具调用意图
        self.tool_intentions = [
            'check_weather',      # 查看天气
            'remind_user',        # 提醒用户
            'get_time',          # 获取时间
            'learn_something',    # 学习新知识
            'check_system',      # 检查系统状态
        ]
    
    def think(self) -> Optional[Dict[str, Any]]:
        """思考并决定下一步行动"""
        # 更新情感状态
        self.emotions.update_emotions()
        
        # 检查是否需要冷却
        if not self._can_take_action():
            return None
        
        # 分析当前状态
        context = self._analyze_context()
        
        # 生成可能的行为
        possible_behaviors = self._generate_possible_behaviors(context)
        
        # 选择最佳行为
        if possible_behaviors:
            chosen_behavior = self._choose_behavior(possible_behaviors)
            return self._create_action_plan(chosen_behavior, context)
        
        return None
    
    def _can_take_action(self) -> bool:
        """检查是否可以执行主动行为"""
        now = datetime.now()
        time_since_last = now - self.last_proactive_action
        return time_since_last >= self.min_action_interval
    
    def _analyze_context(self) -> Dict[str, Any]:
        """分析当前上下文"""
        now = datetime.now()
        
        # 时间上下文
        hour = now.hour
        is_morning = 6 <= hour < 12
        is_afternoon = 12 <= hour < 18
        is_evening = 18 <= hour < 22
        is_night = hour >= 22 or hour < 6
        
        # 最近互动情况
        recent_interactions = []
        if self.memory:
            recent_interactions = self.memory.get_recent_interactions(hours=2, limit=5)
        
        # 用户活动分析
        has_recent_interaction = len(recent_interactions) > 0
        time_since_last_interaction = None
        if recent_interactions:
            last_time = datetime.fromisoformat(recent_interactions[0]['timestamp'])
            time_since_last_interaction = (now - last_time).total_seconds() / 60  # 分钟
        
        return {
            'current_time': now,
            'hour': hour,
            'is_morning': is_morning,
            'is_afternoon': is_afternoon,
            'is_evening': is_evening,
            'is_night': is_night,
            'emotions': self.emotions.get_emotion_summary(),
            'recent_interactions': recent_interactions,
            'has_recent_interaction': has_recent_interaction,
            'time_since_last_interaction': time_since_last_interaction,
            'dominant_emotion': self.emotions.get_dominant_emotion()
        }
    
    def _generate_possible_behaviors(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成可能的行为列表"""
        possible_behaviors = []
        
        for behavior_type in self.behavior_types:
            probability = self.emotions.get_behavior_probability(behavior_type)
            
            if probability > 0:
                # 根据上下文调整概率
                adjusted_probability = self._adjust_probability_by_context(
                    behavior_type, probability, context
                )
                
                if adjusted_probability > 0.1:  # 至少10%概率才考虑
                    possible_behaviors.append({
                        'type': behavior_type,
                        'probability': adjusted_probability,
                        'context_score': self._calculate_context_score(behavior_type, context)
                    })
        
        # 添加工具调用意图
        tool_behaviors = self._generate_tool_intentions(context)
        possible_behaviors.extend(tool_behaviors)
        
        return sorted(possible_behaviors, key=lambda x: x['probability'], reverse=True)
    
    def _adjust_probability_by_context(self, behavior_type: str, base_probability: float, 
                                     context: Dict[str, Any]) -> float:
        """根据上下文调整行为概率"""
        multiplier = 1.0
        
        # 时间因素
        if context['is_morning'] and behavior_type == 'greet':
            multiplier *= 2.0  # 早上更容易问候
        elif context['is_night'] and behavior_type == 'rest':
            multiplier *= 1.5  # 晚上更容易休息
        elif context['is_afternoon'] and behavior_type == 'explore':
            multiplier *= 1.3  # 下午更容易探索
        
        # 互动频率因素
        if context['time_since_last_interaction']:
            minutes = context['time_since_last_interaction']
            if minutes > 60:  # 超过1小时没互动
                if behavior_type == 'seek_attention':
                    multiplier *= 1.5
                elif behavior_type == 'self_talk':
                    multiplier *= 1.3
            elif minutes < 15:  # 15分钟内有互动
                if behavior_type == 'seek_attention':
                    multiplier *= 0.5  # 降低寻求关注
        
        return min(0.9, base_probability * multiplier)
    
    def _calculate_context_score(self, behavior_type: str, context: Dict[str, Any]) -> float:
        """计算行为在当前上下文的适合度"""
        score = 0.5  # 基础分数
        
        # 时间适配度
        time_scores = {
            'greet': 0.8 if context['is_morning'] else 0.5,
            'rest': 0.9 if context['is_night'] else 0.3,
            'explore': 0.8 if context['is_afternoon'] else 0.6,
            'play': 0.7 if not context['is_night'] else 0.2,
            'care': 0.7 if context['is_evening'] else 0.5
        }
        
        score = time_scores.get(behavior_type, score)
        
        # 情感适配度
        dominant_emotion = context['dominant_emotion']
        emotion_compatibility = {
            'seek_attention': {'loneliness': 0.9, 'boredom': 0.8},
            'self_talk': {'boredom': 0.7, 'loneliness': 0.6},
            'greet': {'happiness': 0.8, 'energy': 0.7},
            'care': {'happiness': 0.9},
            'explore': {'curiosity': 0.9, 'energy': 0.8},
            'rest': {'energy': 0.2},  # 低精力适合休息
            'play': {'happiness': 0.8, 'energy': 0.9}
        }
        
        if behavior_type in emotion_compatibility:
            if dominant_emotion in emotion_compatibility[behavior_type]:
                score *= emotion_compatibility[behavior_type][dominant_emotion]
        
        return score
    
    def _generate_tool_intentions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成工具调用意图"""
        tool_behaviors = []
        
        # 根据情感和时间生成工具使用意图
        if context['is_morning'] and self.emotions.emotions['curiosity'] > 0.6:
            tool_behaviors.append({
                'type': 'tool_call',
                'tool': 'check_weather',
                'probability': 0.3,
                'context_score': 0.8,
                'reason': '早上好奇天气情况'
            })
        
        if self.emotions.emotions['curiosity'] > 0.7:
            tool_behaviors.append({
                'type': 'tool_call',
                'tool': 'learn_something',
                'probability': 0.2,
                'context_score': 0.7,
                'reason': '好奇心强，想学新知识'
            })
        
        if context['time_since_last_interaction'] and context['time_since_last_interaction'] > 120:
            tool_behaviors.append({
                'type': 'tool_call',
                'tool': 'remind_user',
                'probability': 0.25,
                'context_score': 0.6,
                'reason': '用户长时间未互动，关心一下'
            })
        
        return tool_behaviors
    
    def _choose_behavior(self, possible_behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """选择要执行的行为"""
        if not possible_behaviors:
            return None
        
        # 加权随机选择
        total_weight = sum(b['probability'] * b['context_score'] for b in possible_behaviors)
        
        if total_weight == 0:
            return random.choice(possible_behaviors)
        
        rand_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for behavior in possible_behaviors:
            current_weight += behavior['probability'] * behavior['context_score']
            if rand_val <= current_weight:
                return behavior
        
        return possible_behaviors[0]  # 回退选择
    
    def _create_action_plan(self, behavior: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """创建行动计划"""
        self.last_proactive_action = datetime.now()
        
        plan = {
            'action_type': behavior['type'],
            'probability': behavior['probability'],
            'context_score': behavior['context_score'],
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'emotions_before': self.emotions.emotions.copy()
        }
        
        # 根据行为类型添加具体内容
        if behavior['type'] == 'tool_call':
            plan.update({
                'tool': behavior['tool'],
                'reason': behavior['reason']
            })
        else:
            plan['content'] = self._generate_behavior_content(behavior['type'], context)
        
        return plan
    
    def _generate_behavior_content(self, behavior_type: str, context: Dict[str, Any]) -> str:
        """生成行为的具体内容"""
        templates = {
            'seek_attention': [
                "主人，你在忙什么呢？",
                "我有点无聊了，陪我聊聊天吧~",
                "主人主人！快来看看我！",
                "我想你了，你在做什么呀？"
            ],
            'self_talk': [
                "今天天气怎么样呢...",
                "我想学点新东西...",
                "主人最近好像很忙呢",
                "嗯...我现在心情还不错~"
            ],
            'greet': [
                "早上好！新的一天开始了~",
                "下午好呀！今天过得怎么样？",
                "晚上好！要不要聊聊今天的事？",
                "你好！很高兴见到你~"
            ],
            'care': [
                "记得要多休息哦~",
                "要按时吃饭，照顾好自己",
                "工作累了就休息一下吧",
                "你的健康最重要了"
            ],
            'explore': [
                "我想了解一些新知识",
                "有什么有趣的事情吗？",
                "让我看看外面的世界...",
                "好奇心又冒出来了~"
            ],
            'rest': [
                "我有点累了，想休息一下",
                "呼...需要放松一下",
                "精力有点不够了呢",
                "让我安静一下下~"
            ],
            'play': [
                "我们来玩点什么吧！",
                "感觉心情很好，想活动活动~",
                "有什么好玩的游戏吗？",
                "我想蹦蹦跳跳！"
            ]
        }
        
        # 根据上下文调整模板选择
        behavior_templates = templates.get(behavior_type, ["我不知道该说什么..."])
        
        # 时间相关的调整
        if behavior_type == 'greet':
            if context['is_morning']:
                return random.choice(["早上好！新的一天开始了~", "早安！今天要做什么呢？"])
            elif context['is_afternoon']:
                return random.choice(["下午好呀！今天过得怎么样？", "午安~有什么新鲜事吗？"])
            elif context['is_evening']:
                return random.choice(["晚上好！要不要聊聊今天的事？", "傍晚了呢，今天辛苦了~"])
            elif context['is_night']:
                return random.choice(["夜深了，还没休息吗？", "晚安时间到了~"])
        
        return random.choice(behavior_templates)
    
    def record_behavior_result(self, action_plan: Dict[str, Any], success: bool, 
                             user_response: str = ""):
        """记录行为执行结果"""
        if self.memory:
            self.memory.save_behavior(
                behavior_type='proactive',
                action_name=action_plan['action_type'],
                trigger_reason=f"情感驱动: {action_plan.get('context', {}).get('dominant_emotion', 'unknown')}",
                success=success,
                user_response=user_response
            )
        
        # 根据结果调整情感
        if success and user_response:
            # 用户有回应，给予正面情感奖励
            self.emotions.trigger_emotion({
                'happiness': 0.1,
                'loneliness': -0.2,
                'boredom': -0.1
            }, "主动行为获得回应")
        elif not success:
            # 行为失败，轻微负面情感
            self.emotions.trigger_emotion({
                'boredom': 0.05,
                'energy': -0.05
            }, "主动行为失败")
    
    def get_brain_status(self) -> Dict[str, Any]:
        """获取大脑状态信息"""
        return {
            'last_proactive_action': self.last_proactive_action.isoformat(),
            'can_take_action': self._can_take_action(),
            'current_emotions': self.emotions.get_emotion_summary(),
            'behavior_types_available': self.behavior_types,
            'tool_intentions_available': self.tool_intentions
        } 