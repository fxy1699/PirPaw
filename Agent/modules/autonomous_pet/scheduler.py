"""
自主行为调度器 - 控制宠物行为的时机
"""

import random
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class AutonomousScheduler:
    """简单的自主行为调度器"""
    
    def __init__(self, brain, behavior_executor, min_interval=5, max_interval=30):
        self.brain = brain
        self.behavior_executor = behavior_executor
        self.min_interval_minutes = min_interval
        self.max_interval_minutes = max_interval
        
        self.last_execution = datetime.now()
        self.next_behavior_time = None  # 新增：跟踪下次行为时间
        self._update_next_behavior_time()  # 初始化下次行为时间
    
    def _update_next_behavior_time(self):
        """更新下次行为时间"""
        interval_seconds = self.get_next_interval()
        self.next_behavior_time = datetime.now() + timedelta(seconds=interval_seconds)
    
    def get_next_interval(self) -> float:
        """获取下次检查的间隔时间（秒）"""
        # 基础随机间隔
        base_minutes = random.uniform(self.min_interval_minutes, self.max_interval_minutes)
        
        # 根据情感状态调整间隔
        if hasattr(self.brain, 'emotions'):
            emotions = self.brain.emotions.emotions
            
            # 如果宠物很无聊或孤独，缩短间隔
            if emotions['boredom'] > 0.7 or emotions['loneliness'] > 0.7:
                base_minutes *= 0.6
            
            # 如果精力很低，延长间隔
            elif emotions['energy'] < 0.3:
                base_minutes *= 1.8
            
            # 如果很开心且精力充沛，稍微缩短间隔
            elif emotions['happiness'] > 0.7 and emotions['energy'] > 0.6:
                base_minutes *= 0.8
        
        # 转换为秒
        return base_minutes * 60
    
    def should_execute_now(self) -> bool:
        """检查是否应该立即执行行为"""
        now = datetime.now()
        time_since_last = (now - self.last_execution).total_seconds() / 60
        
        # 至少等待最小间隔
        if time_since_last < self.min_interval_minutes:
            return False
        
        # 超过最大间隔，强制执行
        if time_since_last >= self.max_interval_minutes:
            return True
        
        # 在最小和最大间隔之间，根据概率决定
        probability = (time_since_last - self.min_interval_minutes) / (self.max_interval_minutes - self.min_interval_minutes)
        return random.random() < probability
    
    def record_execution(self):
        """记录执行时间并更新下次行为时间"""
        self.last_execution = datetime.now()
        self._update_next_behavior_time()
    
    def get_time_until_next_behavior(self) -> Optional[timedelta]:
        """获取距离下次行为的时间"""
        if self.next_behavior_time:
            return self.next_behavior_time - datetime.now()
        return None 