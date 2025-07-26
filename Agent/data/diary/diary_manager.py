#!/usr/bin/env python3
"""
DyberPet 日记本管理器
负责记录和管理宠物的交互历史、截屏记录等
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from PIL import Image

class DiaryManager:
    """日记本管理器"""
    
    def __init__(self, db_path: str = None):
        """初始化日记管理器"""
        if db_path is None:
            # 默认数据库路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, 'pet_diary.db')
        
        self.db_path = db_path
        self.thumbnails_dir = os.path.join(os.path.dirname(db_path), 'thumbnails')
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 主表：日记条目
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    entry_type TEXT NOT NULL,  -- 'interaction', 'screenshot', 'chat', 'status_change', 'system'
                    title TEXT NOT NULL,
                    content TEXT,  -- JSON格式存储详细内容
                    pet_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 截屏记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diary_entry_id INTEGER,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    resolution TEXT,  -- "1920x1080"
                    thumbnail_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            # 交互记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diary_entry_id INTEGER,
                    interaction_type TEXT NOT NULL,  -- 'feed', 'pat', 'drag', 'menu_action', 'bubble'
                    details TEXT,  -- JSON格式存储详情
                    duration INTEGER,  -- 持续时间(秒)
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            # 聊天记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diary_entry_id INTEGER,
                    user_message TEXT,
                    pet_response TEXT,
                    function_calls TEXT,  -- JSON格式存储功能调用
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (diary_entry_id) REFERENCES diary_entries (id)
                )
            ''')
            
            # 新增梦境记录表和相关操作方法
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dream_diary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    content TEXT,
                    told_user BOOLEAN DEFAULT 0
                )
            ''')
            
            # 新增日志总结表和相关操作方法
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    content TEXT,
                    told_user BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
            print("✅ 日记数据库初始化完成")
    
    def add_screenshot_entry(self, file_path: str, pet_name: str = None) -> int:
        """添加截屏记录"""
        try:
            # 获取文件信息
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            resolution = self._get_image_resolution(file_path)
            
            # 生成缩略图
            thumbnail_path = self._create_thumbnail(file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 添加日记条目
                title = f"📸 截屏 - {os.path.basename(file_path)}"
                content = json.dumps({
                    "file_path": file_path,
                    "file_size": file_size,
                    "resolution": resolution
                }, ensure_ascii=False)
                
                cursor.execute('''
                    INSERT INTO diary_entries (entry_type, title, content, pet_name)
                    VALUES (?, ?, ?, ?)
                ''', ('screenshot', title, content, pet_name))
                
                entry_id = cursor.lastrowid
                
                # 添加截屏详细记录
                cursor.execute('''
                    INSERT INTO screenshots (diary_entry_id, file_path, file_size, resolution, thumbnail_path)
                    VALUES (?, ?, ?, ?, ?)
                ''', (entry_id, file_path, file_size, resolution, thumbnail_path))
                
                conn.commit()
                print(f"✅ 截屏记录已添加: {title}")
                return entry_id
                
        except Exception as e:
            print(f"❌ 添加截屏记录失败: {e}")
            return None
    
    def add_interaction_entry(self, interaction_type: str, details: Dict, pet_name: str = None, duration: int = None) -> int:
        """添加交互记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 生成标题
                title_map = {
                    'feed': '🍎 喂食',
                    'pat': '👋 抚摸',
                    'drag': '🖱️ 拖拽',
                    'menu_action': '📋 菜单操作',
                    'bubble': '💭 气泡提示',
                    'status_change': '📊 状态变化'
                }
                title = title_map.get(interaction_type, f"🔄 {interaction_type}")
                
                # 添加详细信息到标题
                if 'action' in details:
                    title += f" - {details['action']}"
                elif 'item_name' in details:
                    title += f" - {details['item_name']}"
                
                content = json.dumps(details, ensure_ascii=False)
                
                # 添加日记条目
                cursor.execute('''
                    INSERT INTO diary_entries (entry_type, title, content, pet_name)
                    VALUES (?, ?, ?, ?)
                ''', ('interaction', title, content, pet_name))
                
                entry_id = cursor.lastrowid
                
                # 添加交互详细记录
                cursor.execute('''
                    INSERT INTO interactions (diary_entry_id, interaction_type, details, duration)
                    VALUES (?, ?, ?, ?)
                ''', (entry_id, interaction_type, content, duration))
                
                conn.commit()
                print(f"✅ 交互记录已添加: {title}")
                return entry_id
                
        except Exception as e:
            print(f"❌ 添加交互记录失败: {e}")
            return None
    
    def add_chat_entry(self, user_message: str, pet_response: str, function_calls: List = None, pet_name: str = None) -> int:
        """添加聊天记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 生成标题（取用户消息前20个字符）
                title = f"💬 对话 - {user_message[:20]}{'...' if len(user_message) > 20 else ''}"
                
                content = json.dumps({
                    "user_message": user_message,
                    "pet_response": pet_response,
                    "function_calls": function_calls or []
                }, ensure_ascii=False)
                
                # 添加日记条目
                cursor.execute('''
                    INSERT INTO diary_entries (entry_type, title, content, pet_name)
                    VALUES (?, ?, ?, ?)
                ''', ('chat', title, content, pet_name))
                
                entry_id = cursor.lastrowid
                
                # 添加聊天详细记录
                cursor.execute('''
                    INSERT INTO chat_records (diary_entry_id, user_message, pet_response, function_calls)
                    VALUES (?, ?, ?, ?)
                ''', (entry_id, user_message, pet_response, json.dumps(function_calls or [], ensure_ascii=False)))
                
                conn.commit()
                print(f"✅ 聊天记录已添加: {title}")
                return entry_id
                
        except Exception as e:
            print(f"❌ 添加聊天记录失败: {e}")
            return None
    
    def add_autonomous_behavior_entry(self, behavior_type: str, action_name: str, content: str, 
                                     trigger_reason: str = "", emotions_before: Dict = None, 
                                     emotions_after: Dict = None, pet_name: str = None,
                                     action_name_original: str = None) -> int:
        """添加自主行为记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 生成标题
                behavior_emoji = {
                    'greet': '👋',
                    'play': '🎮', 
                    'care': '💝',
                    'seek_attention': '🔔',
                    'explore': '🔍',
                    'rest': '😴',
                    'self_talk': '💭',
                    'tool_call': '🛠️'
                }
                
                emoji = behavior_emoji.get(action_name_original, '🤖')
                # 如果是工具调用，则在标题中注明调用的工具名称
                if action_name_original == 'tool_call' and content:
                    title = f"{emoji} 自主行为 - 调用工具 - {content}"
                else:
                    title = f"{emoji} 自主行为 - {action_name}"
                
                # 构建详细内容
                details = {
                    "behavior_type": behavior_type,
                    "action_name": action_name,
                    "content": content,
                    "trigger_reason": trigger_reason,
                    "emotions_before": emotions_before or {},
                    "emotions_after": emotions_after or {}
                }
                
                content_json = json.dumps(details, ensure_ascii=False)
                
                # 添加日记条目
                cursor.execute('''
                    INSERT INTO diary_entries (entry_type, title, content, pet_name)
                    VALUES (?, ?, ?, ?)
                ''', ('autonomous_behavior', title, content_json, pet_name))
                
                entry_id = cursor.lastrowid
                
                # 添加交互详细记录（复用interactions表）
                cursor.execute('''
                    INSERT INTO interactions (diary_entry_id, interaction_type, details, duration)
                    VALUES (?, ?, ?, ?)
                ''', (entry_id, 'autonomous_behavior', content_json, None))
                
                conn.commit()
                print(f"✅ 自主行为记录已添加: {title}")
                return entry_id
                
        except Exception as e:
            print(f"❌ 添加自主行为记录失败: {e}")
            return None
    
    def get_entries(self, entry_type: str = None, limit: int = 50, offset: int = 0, 
                   start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """获取日记条目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建查询条件
                conditions = []
                params = []
                
                if entry_type:
                    conditions.append("entry_type = ?")
                    params.append(entry_type)
                
                if start_date:
                    conditions.append("timestamp >= ?")
                    params.append(start_date.isoformat())
                
                if end_date:
                    conditions.append("timestamp <= ?")
                    params.append(end_date.isoformat())
                
                where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
                
                query = f'''
                    SELECT id, timestamp, entry_type, title, content, pet_name, created_at
                    FROM diary_entries
                    {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                '''
                
                params.extend([limit, offset])
                cursor.execute(query, params)
                
                entries = []
                for row in cursor.fetchall():
                    entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'entry_type': row[2],
                        'title': row[3],
                        'content': json.loads(row[4]) if row[4] else {},
                        'pet_name': row[5],
                        'created_at': row[6]
                    }
                    entries.append(entry)
                
                return entries
                
        except Exception as e:
            print(f"❌ 获取日记条目失败: {e}")
            return []
    
    def get_screenshot_details(self, entry_id: int) -> Optional[Dict]:
        """获取截屏详细信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT file_path, file_size, resolution, thumbnail_path, created_at
                    FROM screenshots
                    WHERE diary_entry_id = ?
                ''', (entry_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'file_path': row[0],
                        'file_size': row[1],
                        'resolution': row[2],
                        'thumbnail_path': row[3],
                        'created_at': row[4]
                    }
                return None
                
        except Exception as e:
            print(f"❌ 获取截屏详情失败: {e}")
            return None
    
    def search_entries(self, keyword: str, entry_type: str = None) -> List[Dict]:
        """搜索日记条目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                conditions = ["(title LIKE ? OR content LIKE ?)"]
                params = [f"%{keyword}%", f"%{keyword}%"]
                
                if entry_type:
                    conditions.append("entry_type = ?")
                    params.append(entry_type)
                
                where_clause = " WHERE " + " AND ".join(conditions)
                
                query = f'''
                    SELECT id, timestamp, entry_type, title, content, pet_name, created_at
                    FROM diary_entries
                    {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT 100
                '''
                
                cursor.execute(query, params)
                
                entries = []
                for row in cursor.fetchall():
                    entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'entry_type': row[2],
                        'title': row[3],
                        'content': json.loads(row[4]) if row[4] else {},
                        'pet_name': row[5],
                        'created_at': row[6]
                    }
                    entries.append(entry)
                
                return entries
                
        except Exception as e:
            print(f"❌ 搜索日记条目失败: {e}")
            return []
    
    def get_statistics(self, days: int = 7) -> Dict:
        """获取统计信息"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总条目数
                cursor.execute('''
                    SELECT COUNT(*) FROM diary_entries 
                    WHERE timestamp >= ?
                ''', (start_date.isoformat(),))
                total_entries = cursor.fetchone()[0]
                
                # 按类型统计
                cursor.execute('''
                    SELECT entry_type, COUNT(*) 
                    FROM diary_entries 
                    WHERE timestamp >= ?
                    GROUP BY entry_type
                ''', (start_date.isoformat(),))
                type_stats = dict(cursor.fetchall())
                
                # 每日统计
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) 
                    FROM diary_entries 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                ''', (start_date.isoformat(),))
                daily_stats = dict(cursor.fetchall())
                
                return {
                    'total_entries': total_entries,
                    'type_statistics': type_stats,
                    'daily_statistics': daily_stats,
                    'period_days': days
                }
                
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}
    
    def cleanup_old_entries(self, days: int = 90):
        """清理旧记录"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取要删除的截屏文件
                cursor.execute('''
                    SELECT s.file_path, s.thumbnail_path
                    FROM screenshots s
                    JOIN diary_entries d ON s.diary_entry_id = d.id
                    WHERE d.timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                files_to_delete = cursor.fetchall()
                
                # 删除数据库记录
                cursor.execute('DELETE FROM diary_entries WHERE timestamp < ?', (cutoff_date.isoformat(),))
                deleted_count = cursor.rowcount
                
                conn.commit()
                
                # 删除文件
                for file_path, thumbnail_path in files_to_delete:
                    try:
                        if file_path and os.path.exists(file_path):
                            os.remove(file_path)
                        if thumbnail_path and os.path.exists(thumbnail_path):
                            os.remove(thumbnail_path)
                    except Exception as e:
                        print(f"⚠️ 删除文件失败 {file_path}: {e}")
                
                print(f"✅ 已清理 {deleted_count} 条旧记录")
                return deleted_count
                
        except Exception as e:
            print(f"❌ 清理旧记录失败: {e}")
            return 0
    
    def _get_image_resolution(self, file_path: str) -> str:
        """获取图片分辨率"""
        try:
            if os.path.exists(file_path):
                with Image.open(file_path) as img:
                    return f"{img.width}x{img.height}"
        except Exception:
            pass
        return "unknown"
    
    def _create_thumbnail(self, file_path: str, size: Tuple[int, int] = (200, 200)) -> Optional[str]:
        """创建缩略图"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # 生成缩略图路径
            date_folder = datetime.now().strftime('%Y/%m/%d')
            thumb_dir = os.path.join(self.thumbnails_dir, date_folder)
            os.makedirs(thumb_dir, exist_ok=True)
            
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            thumb_filename = f"{name}_thumb{ext}"
            thumb_path = os.path.join(thumb_dir, thumb_filename)
            
            # 创建缩略图
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumb_path, quality=85)
            
            return thumb_path
            
        except Exception as e:
            print(f"⚠️ 创建缩略图失败: {e}")
            return None

    def get_dream_by_date(self, date):
        """根据日期获取梦境记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT content, told_user FROM dream_diary WHERE date=?', (date,))
            row = cursor.fetchone()
            if row:
                return {'content': row[0], 'told_user': bool(row[1])}
            return None

    def save_dream(self, date, content):
        """保存梦境记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO dream_diary (date, content, told_user) VALUES (?, ?, 0)', (date, content))
            conn.commit()

    def mark_dream_told(self, date):
        """标记梦境已讲过"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE dream_diary SET told_user=1 WHERE date=?', (date,))
            conn.commit()

    def get_log_summary_by_date(self, date):
        """根据日期获取日志总结记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT content, told_user FROM log_summary WHERE date=?', (date,))
            row = cursor.fetchone()
            if row:
                return {'content': row[0], 'told_user': bool(row[1])}
            return None

    def save_log_summary(self, date, content):
        """保存日志总结记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO log_summary (date, content, told_user) VALUES (?, ?, 0)', (date, content))
            conn.commit()


# 全局实例
diary_manager = DiaryManager()

if __name__ == "__main__":
    # 测试代码
    print("🧪 测试日记管理器...")
    
    # 测试添加记录
    diary_manager.add_interaction_entry('pat', {'action': '抚摸', 'duration': 5}, 'TestPet')
    diary_manager.add_chat_entry('你好', '主人好！今天过得怎么样？', [], 'TestPet')
    
    # 测试获取记录
    entries = diary_manager.get_entries(limit=10)
    print(f"📋 获取到 {len(entries)} 条记录")
    
    # 测试统计
    stats = diary_manager.get_statistics()
    print(f"📊 统计信息: {stats}")
    
    print("✅ 测试完成！") 