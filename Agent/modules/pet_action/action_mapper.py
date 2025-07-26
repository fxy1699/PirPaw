"""
自然语言动作映射系统 (ActionMapper)
将用户的自然语言描述映射到具体的宠物动作
"""

import re
import json
import os
from typing import Dict, List, Optional, Tuple, Union
from fuzzywuzzy import fuzz


class ActionMapper:
    """自然语言到动作的智能映射系统"""
    
    def __init__(self):
        """初始化动作映射器"""
        self.action_mappings = self._load_default_mappings()
        self.pet_specific_mappings = {}
        self.context_rules = self._load_context_rules()
        
        print("🗺️ ActionMapper 初始化完成")
    
    def _load_default_mappings(self) -> Dict[str, Dict]:
        """加载默认的动作映射配置"""
        return {
            # 基础动作映射
            "basic_actions": {
                "站立|待机|静止|不动|默认|default": "default",
                "向上|往上|上移|up": "up", 
                "向下|往下|下移|down": "down",
                "向左|往左|左移|left": "left",
                "向右|往右|右移|right": "right",
                "拖拽|拖动|抓取|drag": "drag",
                "下落|掉落|落下|fall": "fall",
                "落地|着陆|on_floor": "on_floor"
            },
            
            # 移动动作映射
            "movement_actions": {
                "走路|行走|移动|散步|walk": ["left_walk", "right_walk"],
                "向左走|左行|往左走|left_walk": "left_walk",
                "向右走|右行|往右走|right_walk": "right_walk",
                "跑步|奔跑|快跑|run": ["left_walk", "right_walk"],  # 如果没有专门的跑步动作，使用行走
                "移动到|去到|前往": ["left_walk", "right_walk"]
            },
            
            # 情感动作映射
            "emotional_actions": {
                "开心|高兴|快乐|兴奋|愉快|happy": "happy",
                "悲伤|难过|沮丧|伤心|sad": "sad", 
                "愤怒|生气|不高兴|气愤|angry": "angry",
                "惊讶|震惊|吃惊|surprised": "surprised",
                "害羞|脸红|embarrassed": "shy",
                "疲惫|累了|tired": "tired"
            },
            
            # 生活动作映射
            "life_actions": {
                "睡觉|休息|睡眠|打盹|小憩|sleep": ["fall_asleep", "sleep"],
                "入睡|准备睡觉|fall_asleep": "fall_asleep",
                "吃东西|进食|用餐|eat": "eat",
                "喝水|饮水|drink": "drink",
                "玩耍|游戏|娱乐|play": "play"
            },
            
            # 表演动作映射
            "performance_actions": {
                "跳舞|舞蹈|dance|dancing": "dancing",
                "唱歌|歌唱|sing|singing": "singing",
                "表演|演出|show|perform": "dancing",
                "飞行|飞|fly|flying": "flying",
                "施法|魔法|magic|spell": "casting_spell",
                "变身|变形|transform": "transforming"
            },
            
            # 交互动作映射
            "interactive_actions": {
                "拍拍|摸摸|抚摸|pat|patpat": "patpat",
                "专注|工作|学习|集中注意力|focus": "focus",
                "喂食|给食物|feed": "feed",
                "打招呼|问好|hello|hi": "greeting",
                "再见|拜拜|goodbye|bye": "goodbye"
            },
            
            # 特殊状态映射
            "special_states": {
                "无聊|boring": "bored",
                "思考|想事情|thinking": "thinking", 
                "观察|看周围|looking": "looking",
                "等待|waiting": "waiting"
            },
            
            # 新增：食物动作映射
            "food_actions": {
                "吃蛋糕|来个蛋糕|eat_cake": "eat_cake",
                "吃水母|吃果冻|eat_jelly": "eat_jelly", 
                "吃死人手指|恐怖食物|eat_deadfinger": "eat_deadfinger"
            },
            
            # 新增：特殊行为映射
            "special_behaviors": {
                "打劫|抢劫|当强盗|做坏事|rob": "rob",
                "点击|互动|鼠标点击|触摸|click": "click",
                "呼吸|深呼吸|放松|冥想|breath": "breath",
                "看电视|看视频|追剧|观看|watch_tv": "watch_tv",
                "做梦|梦境|分享梦境|梦想|dream": "dream"
            }
        }
    
    def _load_context_rules(self) -> Dict[str, Dict]:
        """加载上下文规则"""
        return {
            # 基于时间的规则
            "time_based": {
                "morning": {
                    "preferred_actions": ["stretch", "wake_up", "energetic"],
                    "keywords": ["早上|上午|morning"]
                },
                "noon": {
                    "preferred_actions": ["active", "play", "energetic"],
                    "keywords": ["中午|noon|midday"]
                },
                "evening": {
                    "preferred_actions": ["relax", "calm", "rest"],
                    "keywords": ["晚上|evening|night"]
                },
                "night": {
                    "preferred_actions": ["sleep", "rest", "quiet"],
                    "keywords": ["深夜|夜晚|late night"]
                }
            },
            
            # 基于情绪的规则
            "mood_based": {
                "happy": {
                    "trigger_keywords": ["开心|快乐|高兴"],
                    "preferred_actions": ["happy", "play", "dance", "jump"]
                },
                "sad": {
                    "trigger_keywords": ["伤心|难过|悲伤"], 
                    "preferred_actions": ["sad", "rest", "comfort"]
                },
                "tired": {
                    "trigger_keywords": ["累|疲惫|困"],
                    "preferred_actions": ["rest", "sleep", "relax"]
                },
                "energetic": {
                    "trigger_keywords": ["有活力|精神|兴奋"],
                    "preferred_actions": ["play", "jump", "active"]
                }
            },
            
            # 基于状态的规则
            "state_based": {
                "low_hp": {
                    "condition": "hp < 30",
                    "preferred_actions": ["sleep", "rest", "eat"],
                    "blocked_actions": ["intense_exercise", "long_walk"]
                },
                "high_fv": {
                    "condition": "fv > 80", 
                    "preferred_actions": ["play", "happy", "active"],
                    "enhanced_probability": 1.5
                }
            }
        }
    
    def map_message_to_actions(self, message: str, pet_info: Dict = None, context: Dict = None) -> List[Dict]:
        """
        将用户消息映射到动作列表
        
        Args:
            message: 用户输入的消息
            pet_info: 当前宠物信息
            context: 上下文信息（时间、状态等）
        
        Returns:
            映射结果列表，包含动作名称、置信度、类型等信息
        """
        message = message.lower().strip()
        results = []
        
        # 1. 精确关键词匹配
        exact_matches = self._exact_keyword_match(message, pet_info)
        results.extend(exact_matches)
        
        # 2. 模糊匹配
        fuzzy_matches = self._fuzzy_match(message, pet_info)
        results.extend(fuzzy_matches)
        
        # 3. 语义理解（简化版）
        semantic_matches = self._semantic_match(message, pet_info)
        results.extend(semantic_matches)
        
        # 4. 应用上下文规则
        results = self._apply_context_rules(results, context)
        
        # 5. 去重和排序
        results = self._deduplicate_and_sort(results)
        
        return results[:5]  # 返回前5个最佳匹配
    
    def _exact_keyword_match(self, message: str, pet_info: Dict = None) -> List[Dict]:
        """精确关键词匹配"""
        results = []
        
        for category, mappings in self.action_mappings.items():
            for keywords, actions in mappings.items():
                # 支持正则表达式匹配
                if re.search(keywords, message):
                    print(f"🔍 关键词匹配: '{keywords}' -> {actions}")
                    if isinstance(actions, str):
                        actions = [actions]
                    
                    for action in actions:
                        # 不在这里过滤动作支持，让主模块处理
                        print(f"✅ 动作 {action} 添加到映射结果")
                        results.append({
                            "action": action,
                            "confidence": 0.95,
                            "match_type": "exact_keyword",
                            "category": category,
                            "matched_keyword": keywords.split('|')[0]
                        })
        
        return results
    
    def _fuzzy_match(self, message: str, pet_info: Dict = None) -> List[Dict]:
        """模糊匹配"""
        results = []
        
        if not pet_info:
            return results
        
                 # 对宠物的所有动作进行模糊匹配
        if pet_info:
            for action_name, action_info in pet_info.get("actions", {}).items():
                # 计算与动作名的相似度
                name_similarity = fuzz.partial_ratio(message, action_name)
                desc_similarity = fuzz.partial_ratio(message, action_info.get("description", ""))
                
                max_similarity = max(name_similarity, desc_similarity)
                
                if max_similarity > 60:  # 相似度阈值
                    print(f"🔍 模糊匹配: {action_name} (相似度: {max_similarity}%)")
                    results.append({
                        "action": action_name,
                        "confidence": max_similarity / 100.0,
                        "match_type": "fuzzy",
                        "category": "pet_specific",
                        "similarity": max_similarity
                    })
        
        return results
    
    def _semantic_match(self, message: str, pet_info: Dict = None) -> List[Dict]:
        """语义匹配（简化版）"""
        results = []
        
        # 检测动作意图
        intent_patterns = {
            "让宠物": r"让.*?(睡觉|走路|站立|休息)",
            "想要": r"想要.*?(看到|让).*?(睡觉|走路|站立|休息)",
            "可以": r"可以.*?(睡觉|走路|站立|休息)",
            "执行": r"执行.*?(睡觉|走路|站立|休息)",
            "做": r"做.*?(什么|睡觉|走路|站立|休息)"
        }
        
        for intent, pattern in intent_patterns.items():
            match = re.search(pattern, message)
            if match:
                action_word = match.group(1)
                # 递归调用自己来映射提取的动作词
                sub_results = self.map_message_to_actions(action_word, pet_info)
                for result in sub_results:
                    result["confidence"] *= 0.8  # 语义匹配置信度稍低
                    result["match_type"] = "semantic"
                    results.append(result)
        
        return results
    
    def _apply_context_rules(self, results: List[Dict], context: Dict = None) -> List[Dict]:
        """应用上下文规则"""
        if not context:
            return results
        
        # 应用状态规则
        pet_status = context.get("pet_status", {})
        hp = pet_status.get("hp", 100)
        fv = pet_status.get("fv", 50)
        
        for result in results:
            action = result["action"]
            
            # 低血量时降低高强度动作的置信度
            if hp < 30 and action in ["left_walk", "right_walk", "play", "jump"]:
                result["confidence"] *= 0.5
                result["context_note"] = "宠物血量较低，不建议高强度活动"
            
            # 高好感度时提高互动动作的置信度
            if fv > 80 and action in ["play", "happy", "patpat"]:
                result["confidence"] *= 1.2
                result["context_note"] = "宠物心情很好，适合互动"
        
        return results
    
    def _deduplicate_and_sort(self, results: List[Dict]) -> List[Dict]:
        """去重和排序"""
        # 按动作名去重，保留置信度最高的
        action_map = {}
        for result in results:
            action = result["action"]
            if action not in action_map or result["confidence"] > action_map[action]["confidence"]:
                action_map[action] = result
        
        # 按置信度排序
        sorted_results = sorted(action_map.values(), key=lambda x: x["confidence"], reverse=True)
        
        return sorted_results
    
    def _pet_supports_action(self, action: str, pet_info: Dict) -> bool:
        """检查宠物是否支持指定动作"""
        if not pet_info:
            return False
        
        # 检查基础动作
        basic_actions = pet_info.get("basic_actions", {})
        if action in basic_actions.values():
            return True
        
        # 检查所有动作
        actions = pet_info.get("actions", {})
        if action in actions:
            return True
        
        # 检查随机动作组
        for random_act in pet_info.get("random_actions", []):
            if action in random_act.get("act_list", []):
                return True
        
        return False
    
    def suggest_actions(self, pet_info: Dict, context: Dict = None) -> List[Dict]:
        """
        根据当前状态推荐动作
        
        Args:
            pet_info: 宠物信息
            context: 上下文信息
        
        Returns:
            推荐的动作列表
        """
        suggestions = []
        
        if not pet_info:
            return suggestions
        
        # 基于宠物状态推荐
        pet_status = context.get("pet_status", {}) if context else {}
        hp = pet_status.get("hp", 100)
        fv = pet_status.get("fv", 50)
        
        # 低血量推荐
        if hp < 30:
            suggestions.extend([
                {"action": "sleep", "reason": "血量较低，建议休息", "priority": "high"},
                {"action": "rest", "reason": "恢复体力", "priority": "high"}
            ])
        
        # 高好感度推荐
        if fv > 80:
            suggestions.extend([
                {"action": "play", "reason": "心情很好，可以玩耍", "priority": "medium"},
                {"action": "happy", "reason": "表达开心的心情", "priority": "medium"}
            ])
        
        # 基于时间推荐
        import datetime
        current_hour = datetime.datetime.now().hour
        
        if 6 <= current_hour < 10:  # 早上
            suggestions.append({"action": "stretch", "reason": "早上适合伸展运动", "priority": "low"})
        elif 20 <= current_hour or current_hour < 6:  # 晚上/深夜
            suggestions.append({"action": "sleep", "reason": "夜深了，该休息了", "priority": "medium"})
        
        return suggestions
    
    def add_custom_mapping(self, keywords: str, actions: Union[str, List[str]], category: str = "custom"):
        """
        添加自定义映射
        
        Args:
            keywords: 关键词（支持正则）
            actions: 对应的动作
            category: 分类
        """
        if category not in self.action_mappings:
            self.action_mappings[category] = {}
        
        self.action_mappings[category][keywords] = actions
        print(f"✅ 添加自定义映射: {keywords} -> {actions}")
    
    def get_mapping_stats(self) -> Dict:
        """获取映射统计信息"""
        stats = {
            "total_categories": len(self.action_mappings),
            "total_mappings": sum(len(mappings) for mappings in self.action_mappings.values()),
            "categories": {}
        }
        
        for category, mappings in self.action_mappings.items():
            stats["categories"][category] = {
                "count": len(mappings),
                "keywords": list(mappings.keys())[:3]  # 显示前3个作为示例
            }
        
        return stats 