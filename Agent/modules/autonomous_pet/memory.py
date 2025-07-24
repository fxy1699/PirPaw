"""
SQLite记忆管理系统 - 宠物的"大脑存储"
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class PetMemory:
    """宠物记忆管理器 - 使用SQLite存储所有数据"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认数据库路径
            db_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'autonomous_pet.db')
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 情感状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                happiness REAL DEFAULT 0.5,
                energy REAL DEFAULT 0.5,
                boredom REAL DEFAULT 0.5,
                curiosity REAL DEFAULT 0.5,
                loneliness REAL DEFAULT 0.5,
                notes TEXT
            )
        ''')
        
        # 互动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                type TEXT,  -- 'user_message', 'pet_action', 'tool_call'
                content TEXT,
                response TEXT,
                emotion_before TEXT,  -- JSON格式的情感状态
                emotion_after TEXT,   -- JSON格式的情感状态
                success BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # 行为记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                behavior_type TEXT,  -- 'proactive', 'reactive'
                action_name TEXT,
                trigger_reason TEXT,
                success BOOLEAN DEFAULT TRUE,
                user_response TEXT
            )
        ''')
        
        # 学习偏好表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,      -- 'topic', 'timing', 'behavior'
                item TEXT,
                preference_score REAL DEFAULT 0.0,  -- -1.0 到 1.0
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, item)
            )
        ''')
        
        # 宠物状态表（当前状态）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pet_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"🗄️ 宠物记忆数据库初始化完成: {self.db_path}")
    
    def save_emotion_state(self, emotions: Dict[str, float], notes: str = ""):
        """保存情感状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO emotions (happiness, energy, boredom, curiosity, loneliness, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            emotions.get('happiness', 0.5),
            emotions.get('energy', 0.5),
            emotions.get('boredom', 0.5),
            emotions.get('curiosity', 0.5),
            emotions.get('loneliness', 0.5),
            notes
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_emotion_state(self) -> Dict[str, float]:
        """获取最新情感状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT happiness, energy, boredom, curiosity, loneliness
            FROM emotions 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'happiness': result[0],
                'energy': result[1],
                'boredom': result[2],
                'curiosity': result[3],
                'loneliness': result[4]
            }
        else:
            # 默认情感状态
            return {
                'happiness': 0.5,
                'energy': 0.5,
                'boredom': 0.5,
                'curiosity': 0.5,
                'loneliness': 0.5
            }
    
    def save_interaction(self, interaction_type: str, content: str, response: str = "", 
                        emotion_before: Dict = None, emotion_after: Dict = None, success: bool = True):
        """保存互动记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions (type, content, response, emotion_before, emotion_after, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            interaction_type,
            content,
            response,
            json.dumps(emotion_before) if emotion_before else None,
            json.dumps(emotion_after) if emotion_after else None,
            success
        ))
        
        conn.commit()
        conn.close()
    
    def save_behavior(self, behavior_type: str, action_name: str, trigger_reason: str, 
                     success: bool = True, user_response: str = ""):
        """保存行为记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO behaviors (behavior_type, action_name, trigger_reason, success, user_response)
            VALUES (?, ?, ?, ?, ?)
        ''', (behavior_type, action_name, trigger_reason, success, user_response))
        
        conn.commit()
        conn.close()
    
    def update_preference(self, category: str, item: str, score_delta: float):
        """更新偏好分数（增量更新）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 先查询现有分数
        cursor.execute('''
            SELECT preference_score FROM preferences 
            WHERE category = ? AND item = ?
        ''', (category, item))
        
        result = cursor.fetchone()
        
        if result:
            # 更新现有记录
            new_score = max(-1.0, min(1.0, result[0] + score_delta))  # 限制在-1到1之间
            cursor.execute('''
                UPDATE preferences 
                SET preference_score = ?, last_updated = CURRENT_TIMESTAMP
                WHERE category = ? AND item = ?
            ''', (new_score, category, item))
        else:
            # 插入新记录
            new_score = max(-1.0, min(1.0, score_delta))
            cursor.execute('''
                INSERT INTO preferences (category, item, preference_score)
                VALUES (?, ?, ?)
            ''', (category, item, new_score))
        
        conn.commit()
        conn.close()
    
    def get_preferences(self, category: str = None) -> List[Dict]:
        """获取偏好设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT category, item, preference_score, last_updated
                FROM preferences 
                WHERE category = ?
                ORDER BY preference_score DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT category, item, preference_score, last_updated
                FROM preferences 
                ORDER BY preference_score DESC
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'category': row[0],
                'item': row[1],
                'score': row[2],
                'last_updated': row[3]
            }
            for row in results
        ]
    
    def get_recent_interactions(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """获取最近的互动记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT timestamp, type, content, response, success
            FROM interactions 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (since_time, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'type': row[1],
                'content': row[2],
                'response': row[3],
                'success': row[4]
            }
            for row in results
        ]
    
    def get_behavior_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取行为统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_time = datetime.now() - timedelta(days=days)
        
        # 行为类型统计
        cursor.execute('''
            SELECT behavior_type, COUNT(*) as count
            FROM behaviors 
            WHERE timestamp > ?
            GROUP BY behavior_type
        ''', (since_time,))
        
        behavior_types = dict(cursor.fetchall())
        
        # 成功率统计
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
            FROM behaviors 
            WHERE timestamp > ?
        ''', (since_time,))
        
        result = cursor.fetchone()
        total, successful = result[0], result[1]
        success_rate = (successful / total * 100) if total > 0 else 0
        
        conn.close()
        
        return {
            'behavior_types': behavior_types,
            'total_behaviors': total,
            'success_rate': success_rate,
            'period_days': days
        }
    
    def set_pet_state(self, key: str, value: Any):
        """设置宠物状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO pet_state (key, value, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, json.dumps(value) if not isinstance(value, str) else value))
        
        conn.commit()
        conn.close()
    
    def get_pet_state(self, key: str, default=None):
        """获取宠物状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value FROM pet_state WHERE key = ?
        ''', (key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0]
        return default
    
    def cleanup_old_data(self, days: int = 30):
        """清理旧数据（保留最近N天）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 清理旧的情感记录（保留每天最后一条）
        cursor.execute('''
            DELETE FROM emotions 
            WHERE timestamp < ? 
            AND id NOT IN (
                SELECT MAX(id) 
                FROM emotions 
                WHERE timestamp < ?
                GROUP BY DATE(timestamp)
            )
        ''', (cutoff_time, cutoff_time))
        
        # 清理旧的互动记录
        cursor.execute('''
            DELETE FROM interactions WHERE timestamp < ?
        ''', (cutoff_time,))
        
        # 清理旧的行为记录
        cursor.execute('''
            DELETE FROM behaviors WHERE timestamp < ?
        ''', (cutoff_time,))
        
        conn.commit()
        conn.close()
        
        print(f"🧹 已清理{days}天前的旧数据") 