#!/usr/bin/env python3
"""
DyberPet 日记本UI界面
显示宠物的交互历史、截屏记录等
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict

# 尝试导入pytz，如果失败则使用简化版本
try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    print("⚠️ pytz未安装，使用简化时间显示")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QScrollArea, QFrame, QPushButton, QLineEdit,
                           QComboBox, QDateEdit, QTextEdit, QGroupBox,
                           QGridLayout, QSplitter, QTabWidget, QProgressBar,
                           QMessageBox, QFileDialog, QSpacerItem, QSizePolicy,
                           QDialog)
from PySide6.QtCore import Qt, QThread, Signal, QDate, QTimer, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon, QPalette, QCursor

# 添加Agent路径以导入DiaryManager
agent_path = os.path.join(os.path.dirname(__file__), '..', 'Agent')
sys.path.append(agent_path)

# 尝试导入diary_manager
try:
    from data.diary.diary_manager import diary_manager
    print("✅ diary_manager导入成功")
except ImportError as e:
    print(f"❌ diary_manager导入失败: {e}")
    # 尝试另一种导入方式
    try:
        diary_data_path = os.path.join(agent_path, 'data', 'diary')
        sys.path.append(diary_data_path)
        from diary_manager import diary_manager
        print("✅ diary_manager导入成功（备用方式）")
    except ImportError as e2:
        print(f"❌ diary_manager导入完全失败: {e2}")
        # 创建一个空的替代对象
        class DummyDiaryManager:
            def get_entries(self, **kwargs):
                return []
            def get_screenshot_details(self, entry_id):
                return None
            def search_entries(self, keyword, entry_type=None):
                return []
        diary_manager = DummyDiaryManager()
        print("⚠️ 使用虚拟diary_manager")

import DyberPet.settings as settings
from DyberPet.StoryManager import story_manager
basedir = settings.BASEDIR

def _convert_to_shanghai_time_helper(timestamp_str: str) -> datetime:
    """转换时间戳为上海时间 - 全局辅助函数"""
    try:
        if HAS_PYTZ:
            # 使用pytz进行精确时区转换
            shanghai_tz = pytz.timezone('Asia/Shanghai')
            
            # 解析时间戳
            if timestamp_str.endswith('Z'):
                # UTC时间
                utc_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif '+' in timestamp_str or timestamp_str.endswith('00:00'):
                # 带时区的时间
                utc_time = datetime.fromisoformat(timestamp_str)
            else:
                # 无时区信息，假设为UTC
                utc_time = datetime.fromisoformat(timestamp_str)
                utc_time = pytz.utc.localize(utc_time)
            
            # 如果没有时区信息，添加UTC时区
            if utc_time.tzinfo is None:
                utc_time = pytz.utc.localize(utc_time)
            
            # 转换为上海时间
            return utc_time.astimezone(shanghai_tz)
        else:
            # 简化版本：假设时间戳是UTC，直接加8小时
            if timestamp_str.endswith('Z'):
                utc_time = datetime.fromisoformat(timestamp_str.replace('Z', ''))
            else:
                utc_time = datetime.fromisoformat(timestamp_str.split('+')[0])
            
            # 加8小时转换为北京时间
            return utc_time + timedelta(hours=8)
        
    except Exception as e:
        print(f"⚠️ 时间转换失败: {e}, 使用原始时间")
        # 如果转换失败，返回原始时间
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', ''))
        except:
            return datetime.now()

class DetailViewDialog(QDialog):
    """详细内容查看对话框"""
    
    def __init__(self, entry: Dict, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.text_widgets = []  # 存储需要自适应高度的文本控件
        try: 
            print(f"📖 创建详细对话框: {entry.get('title', 'Unknown')}")
            self.setup_ui()
            
            # 如果是梦境类型，标记为已告诉用户
            if entry.get('entry_type') == 'dream':
                self._mark_dream_as_told()
            
            print("✅ 详细对话框创建成功")
        except Exception as e:
            print(f"❌ 详细对话框创建失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _make_text_auto_height(self, text_edit: QTextEdit, min_height: int = 100, max_height: int = 500):
        """为QTextEdit添加自适应高度功能"""
        self.text_widgets.append((text_edit, min_height, max_height))
        
        def adjust_height():
            try:
                document = text_edit.document()
                # 确保宽度计算正确
                available_width = max(text_edit.width() - 40, 200)  # 减去padding和滚动条
                document.setTextWidth(available_width)
                content_height = document.size().height()
                
                # 计算合适的高度
                new_height = max(min_height, min(int(content_height + 30), max_height))
                text_edit.setFixedHeight(new_height)
            except Exception as e:
                print(f"调整文本高度失败: {e}")
        
        # 延迟调整，确保控件已经完全初始化
        QTimer.singleShot(50, adjust_height)
        
        return adjust_height
    
    def resizeEvent(self, event):
        """窗口大小改变时重新调整所有文本控件的高度"""
        super().resizeEvent(event)
        
        # 延迟调整，确保布局已经更新
        QTimer.singleShot(100, self._readjust_all_text_heights)
    
    def _readjust_all_text_heights(self):
        """重新调整所有文本控件的高度"""
        for text_edit, min_height, max_height in self.text_widgets:
            try:
                document = text_edit.document()
                available_width = max(text_edit.width() - 40, 200)
                document.setTextWidth(available_width)
                content_height = document.size().height()
                new_height = max(min_height, min(int(content_height + 30), max_height))
                text_edit.setFixedHeight(new_height)
            except Exception as e:
                print(f"重新调整文本高度失败: {e}")
                
    def _mark_dream_as_told(self):
        """标记梦境为已告诉用户"""
        try:
            # 导入日记管理器
            from Agent.data.diary.diary_manager import DiaryManager
            diary_manager = DiaryManager()
            
            # 从 entry 中获取日期
            content = self.entry.get('content', {})
            if isinstance(content, str):
                import json
                content = json.loads(content)
            
            dream_date = content.get('date')
            if dream_date:
                # 标记梦境为已告诉用户
                diary_manager.mark_dream_told(dream_date)
                print(f"✅ 梦境已标记为已告诉用户: {dream_date}")
                
        except Exception as e:
            print(f"⚠️ 标记梦境状态失败: {e}")
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(f"📖 详细内容 - {self.entry['title']}")
        self.setModal(False)  # 改为非模态，允许其他窗口获得焦点
        self.resize(900, 700)  # 增加窗口大小，提供更好的内容显示空间
        
        # 设置窗口标志，移除置顶行为
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        
        layout = QVBoxLayout(self)
        
        # 标题和时间
        header_layout = QHBoxLayout()
        
        # 获取上海时间
        shanghai_time = _convert_to_shanghai_time_helper(self.entry['timestamp'])
        
        title_label = QLabel(self.entry['title'])
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        time_label = QLabel(shanghai_time.strftime('%Y-%m-%d %H:%M:%S'))
        time_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 内容区域
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 根据类型显示不同内容
        entry_type = self.entry.get('entry_type')
        
        if entry_type == 'screenshot':
            self._add_screenshot_detail(content_layout)
        elif entry_type == 'chat':
            self._add_chat_detail(content_layout)
        elif entry_type == 'interaction':
            self._add_interaction_detail(content_layout)
        elif entry_type == 'autonomous_behavior':
            self._add_autonomous_behavior_detail(content_layout)
        elif self.entry['entry_type'] == 'ai_diary':
            self._add_ai_diary_detail(content_layout)
        elif entry_type == 'dream':
            self._add_dream_detail(content_layout)  # 新增梦境详情显示
        else:
            # 通用内容显示
            content_group = QGroupBox("📋 内容详情")
            detail_layout = QVBoxLayout(content_group)
            
            detail_text = QTextEdit()
            detail_text.setPlainText(str(self.entry.get('content', {})))
            detail_text.setReadOnly(True)
            
            # 使用通用的自适应高度函数
            self._make_text_auto_height(detail_text, min_height=150, max_height=600)
            
            detail_text.setStyleSheet("background: #fafafa; border: 1px solid #ddd; border-radius: 4px; padding: 8px;")
            detail_layout.addWidget(detail_text)
            
            content_layout.addWidget(content_group)
        
        content_scroll.setWidget(content_widget)
        layout.addWidget(content_scroll)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def _add_screenshot_detail(self, layout: QVBoxLayout):
        """添加截屏详细内容"""
        content = self.entry.get('content', {})
        screenshot_info = diary_manager.get_screenshot_details(self.entry['id'])
        
        # 基本信息
        info_group = QGroupBox("📋 基本信息")
        info_layout = QVBoxLayout(info_group)
        
        if 'file_size' in content:
            size_mb = content['file_size'] / (1024 * 1024)
            info_layout.addWidget(QLabel(f"📁 文件大小: {size_mb:.2f} MB"))
        
        if 'resolution' in content:
            info_layout.addWidget(QLabel(f"📐 分辨率: {content['resolution']}"))
        
        if screenshot_info:
            info_layout.addWidget(QLabel(f"📂 文件路径: {screenshot_info.get('file_path', 'N/A')}"))
        
        layout.addWidget(info_group)
        
        # 截屏图像
        if screenshot_info and screenshot_info.get('file_path'):
            file_path = screenshot_info['file_path']
            if os.path.exists(file_path):
                image_group = QGroupBox("🖼️ 截屏图像")
                image_layout = QVBoxLayout(image_group)
                
                image_label = QLabel()
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 缩放到合适大小，保持比例
                    scaled_pixmap = pixmap.scaled(700, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    image_label.setStyleSheet("border: 1px solid #ddd; background: white; padding: 10px;")
                    
                    # 添加点击提示
                    hint_label = QLabel("💡 点击图像可以用系统默认程序打开完整图像")
                    hint_label.setStyleSheet("color: #666; font-size: 10px; text-align: center;")
                    hint_label.setAlignment(Qt.AlignCenter)
                    
                    # 让图像可以点击
                    image_label.setCursor(QCursor(Qt.PointingHandCursor))
                    image_label.mousePressEvent = lambda event: self._open_image_externally(file_path)
                    
                    image_layout.addWidget(image_label)
                    image_layout.addWidget(hint_label)
                
                layout.addWidget(image_group)
    
    def _add_chat_detail(self, layout: QVBoxLayout):
        """添加聊天详细内容"""
        content = self.entry.get('content', {})
        
        if 'user_message' in content:
            user_group = QGroupBox("👤 用户消息")
            user_layout = QVBoxLayout(user_group)
            user_text = QTextEdit()
            user_text.setPlainText(content['user_message'])
            user_text.setReadOnly(True)
            
            # 使用通用的自适应高度函数
            self._make_text_auto_height(user_text, min_height=100, max_height=400)
            
            user_text.setStyleSheet("background: #e3f2fd; border: 1px solid #ddd; border-radius: 4px; padding: 8px;")
            user_layout.addWidget(user_text)
            layout.addWidget(user_group)
        
        if 'pet_response' in content:
            pet_group = QGroupBox("🐾 宠物回复")
            pet_layout = QVBoxLayout(pet_group)
            pet_text = QTextEdit()
            pet_text.setPlainText(content['pet_response'])
            pet_text.setReadOnly(True)
            
            # 使用通用的自适应高度函数
            self._make_text_auto_height(pet_text, min_height=120, max_height=500)
            
            pet_text.setStyleSheet("background: #f1f8e9; border: 1px solid #ddd; border-radius: 4px; padding: 8px;")
            pet_layout.addWidget(pet_text)
            layout.addWidget(pet_group)
        
        if 'function_calls' in content and content['function_calls']:
            func_group = QGroupBox("🔧 功能调用")
            func_layout = QVBoxLayout(func_group)
            func_text = QTextEdit()
            func_text.setPlainText(str(content['function_calls']))
            func_text.setReadOnly(True)
            
            # 使用通用的自适应高度函数
            self._make_text_auto_height(func_text, min_height=80, max_height=300)
            
            func_text.setStyleSheet("background: #fff3e0; border: 1px solid #ddd; border-radius: 4px; padding: 8px;")
            func_layout.addWidget(func_text)
            layout.addWidget(func_group)
    
    def _add_interaction_detail(self, layout: QVBoxLayout):
        """添加交互详细内容"""
        content = self.entry.get('content', {})
        
        detail_group = QGroupBox("🔄 交互详情")
        detail_layout = QVBoxLayout(detail_group)
        
        for key, value in content.items():
            if key == 'action':
                detail_layout.addWidget(QLabel(f"🎯 动作: {value}"))
            elif key == 'item_name':
                detail_layout.addWidget(QLabel(f"🎁 物品: {value}"))
            elif key == 'duration':
                detail_layout.addWidget(QLabel(f"⏱️ 持续时间: {value}秒"))
            elif key == 'click_count':
                detail_layout.addWidget(QLabel(f"👆 点击次数: {value}"))
            elif key == 'reward_factor':
                detail_layout.addWidget(QLabel(f"💰 奖励倍数: {value}"))
            else:
                detail_layout.addWidget(QLabel(f"{key}: {value}"))
        
        layout.addWidget(detail_group)
    
    def _add_general_detail(self, layout: QVBoxLayout):
        """添加通用详细内容"""
        content = self.entry.get('content', {})
        
        detail_group = QGroupBox("📋 详细内容")
        detail_layout = QVBoxLayout(detail_group)
        
        detail_text = QTextEdit()
        detail_text.setPlainText(str(content))
        detail_text.setReadOnly(True)
        detail_text.setStyleSheet("background: #fafafa; border: 1px solid #ddd; border-radius: 4px; padding: 8px;")
        detail_layout.addWidget(detail_text)
        
        layout.addWidget(detail_group)
    
    def _add_autonomous_behavior_detail(self, layout: QVBoxLayout):
        """添加自主行为详细内容"""
        content = self.entry.get('content', {})
        
        if isinstance(content, str):
            try:
                import json
                content = json.loads(content)
            except:
                content = {}
        
        # 基本信息组
        basic_group = QGroupBox("🤖 自主行为信息")
        basic_layout = QGridLayout(basic_group)
        
        action_name = content.get('action_name', '未知行为')
        behavior_type = content.get('behavior_type', '未知类型')
        trigger_reason = content.get('trigger_reason', '未知原因')
        behavior_content = content.get('content', '')
        
        # 现在 action_name 已经是自然化的中文，直接使用
        display_name = action_name
        
        basic_layout.addWidget(QLabel("行为类型:"), 0, 0)
        basic_layout.addWidget(QLabel(f"🤖 {display_name}"), 0, 1)
        
        basic_layout.addWidget(QLabel("触发原因:"), 1, 0)
        basic_layout.addWidget(QLabel(f"🎯 {trigger_reason}"), 1, 1)
        
        if behavior_content:
            basic_layout.addWidget(QLabel("行为内容:"), 2, 0)
            content_label = QLabel(behavior_content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("padding: 4px; background: #f5f5f5; border-radius: 4px;")
            basic_layout.addWidget(content_label, 2, 1)
        
        layout.addWidget(basic_group)
        
        # AI回复内容组
        ai_response = content.get('ai_response', '')
        if ai_response:
            ai_group = QGroupBox("🤖 AI回复内容")
            ai_layout = QVBoxLayout(ai_group)
            
            ai_text = QTextEdit()
            ai_text.setPlainText(ai_response)
            ai_text.setReadOnly(True)
            
            # 使用通用的自适应高度函数
            self._make_text_auto_height(ai_text, min_height=120, max_height=500)
            
            ai_text.setStyleSheet("background: #e8f5e8; border: 1px solid #ddd; border-radius: 4px; padding: 8px; font-family: 'Microsoft YaHei', sans-serif;")
            ai_layout.addWidget(ai_text)
            
            layout.addWidget(ai_group)
        
        # 情绪状态对比组
        emotions_before = content.get('emotions_before', {})
        emotions_after = content.get('emotions_after', {})
        
        if emotions_before or emotions_after:
            emotion_group = QGroupBox("😊 情绪状态变化")
            emotion_layout = QVBoxLayout(emotion_group)
            
            emotion_names = {
                'happiness': '😊 快乐度',
                'energy': '⚡ 活力值',
                'boredom': '😴 无聊度',
                'curiosity': '🤔 好奇心',
                'loneliness': '😢 孤独感'
            }
            
            for emotion_key, emotion_name in emotion_names.items():
                before_val = emotions_before.get(emotion_key, 0)
                after_val = emotions_after.get(emotion_key, 0)
                
                if before_val != after_val:
                    change = after_val - before_val
                    change_text = f"{'↗️' if change > 0 else '↘️'} {change:+.2f}"
                    emotion_text = f"{emotion_name}: {before_val:.2f} → {after_val:.2f} ({change_text})"
                else:
                    emotion_text = f"{emotion_name}: {before_val:.2f} (无变化)"
                
                emotion_label = QLabel(emotion_text)
                emotion_label.setStyleSheet("padding: 2px; font-family: 'Consolas', monospace;")
                emotion_layout.addWidget(emotion_label)
            
            layout.addWidget(emotion_group)
    
    def _add_ai_diary_detail(self, layout: QVBoxLayout):
        """添加AI日记详细内容"""
        content = self.entry.get('content', {})
        
        if isinstance(content, str):
            try:
                import json
                content = json.loads(content)
            except:
                content = {}
        # 获取AI生成的日记内容
        generated_content = content.get('generated_content', '')
        original_tool_call = content.get('original_tool_call', {})
        ai_response = content.get('ai_response', '')
        emotions = content.get('emotions', {})
        
        # AI日记内容组
        diary_group = QGroupBox("📝 AI生成的日记")
        diary_layout = QVBoxLayout(diary_group)
        
        if generated_content:
            diary_text = QTextEdit()
            diary_text.setPlainText(generated_content)
            diary_text.setReadOnly(True)
            
            # 使用通用的自适应高度函数
            self._make_text_auto_height(diary_text, min_height=150, max_height=600)
            
            diary_text.setStyleSheet("background: #f8fff8; border: 1px solid #ddd; border-radius: 4px; padding: 12px; font-family: 'Microsoft YaHei', sans-serif; font-size: 11px; line-height: 1.6;")
            diary_layout.addWidget(diary_text)
        
        layout.addWidget(diary_group)
        
        # 原始信息组
        if original_tool_call:
            original_group = QGroupBox("🛠️ 基于的工具调用")
            original_layout = QGridLayout(original_group)
            
            tool_name = original_tool_call.get('tool_name', '未知工具')
            reason = original_tool_call.get('reason', '未知原因')
            result_data = original_tool_call.get('result_data', '')
            
            original_layout.addWidget(QLabel("工具:"), 0, 0)
            original_layout.addWidget(QLabel(f"🛠️ {tool_name}"), 0, 1)
            
            original_layout.addWidget(QLabel("原因:"), 1, 0)
            original_layout.addWidget(QLabel(f"🎯 {reason}"), 1, 1)
            
            if result_data:
                original_layout.addWidget(QLabel("结果:"), 2, 0)
                result_label = QLabel(result_data[:100] + ('...' if len(result_data) > 100 else ''))
                result_label.setWordWrap(True)
                result_label.setStyleSheet("padding: 4px; background: #f5f5f5; border-radius: 4px;")
                original_layout.addWidget(result_label, 2, 1)
            
            layout.addWidget(original_group)
        
        # 移除AI原始回复显示部分
        # if ai_response:
        #     response_group = QGroupBox("🤖 AI原始回复")
        #     response_layout = QVBoxLayout(response_group)
        #     
        #     response_text = QTextEdit()
        #     response_text.setPlainText(ai_response)
        #     response_text.setReadOnly(True)
        #     response_text.setMaximumHeight(150)
        #     response_text.setStyleSheet("background: #f0f8ff; border: 1px solid #ddd; border-radius: 4px; padding: 8px; font-family: 'Microsoft YaHei', sans-serif;")
        #     response_layout.addWidget(response_text)
        #     
        #     layout.addWidget(response_group)
    
    def _add_dream_detail(self, layout: QVBoxLayout):
        """添加梦境详细内容"""
        content = self.entry.get('content', {})
        
        if isinstance(content, str):
            try:
                import json
                content = json.loads(content)
            except:
                content = {}
    
        # 基本信息组
        basic_group = QGroupBox("💭 梦境信息")
        basic_layout = QGridLayout(basic_group)
        
        dream_date = content.get('date', '未知日期')
        dream_content = content.get('dream_content', '')
        told_user = content.get('told_user', False)
        
        basic_layout.addWidget(QLabel("梦境日期:"), 0, 0)
        basic_layout.addWidget(QLabel(f"💭 {dream_date}"), 0, 1)
        
        basic_layout.addWidget(QLabel("状态:"), 1, 0)
        status_text = "✅ 已告诉用户" if told_user else "⏳ 未告诉用户"
        basic_layout.addWidget(QLabel(status_text), 1, 1)
        
        if dream_content:
            basic_layout.addWidget(QLabel("梦境内容:"), 2, 0)
            content_label = QLabel(dream_content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("padding: 8px; background: #f0f8ff; border-radius: 6px; font-size: 12px;")
            basic_layout.addWidget(content_label, 2, 1)
        
        layout.addWidget(basic_group)
    
    def _open_image_externally(self, file_path: str):
        """用系统默认程序打开图像"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.run(['start', file_path], shell=True, check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开图像文件:\n{str(e)}")

class PetStoryDialog(QDialog):
    """宠物背景故事查看对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("📚 宠物背景故事")
        self.setModal(False)
        self.resize(900, 700)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        
        layout = QVBoxLayout(self)
        
        # 顶部控制栏
        control_layout = QHBoxLayout()
        
        # 宠物选择下拉框
        control_layout.addWidget(QLabel("选择宠物:"))
        self.pet_combo = QComboBox()
        self.pet_combo.currentTextChanged.connect(self.on_pet_changed)
        control_layout.addWidget(self.pet_combo)
        
        control_layout.addStretch()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.load_pet_stories)
        control_layout.addWidget(refresh_btn)
        
        layout.addLayout(control_layout)
        
        # 故事内容显示区域
        self.story_text = QTextEdit()
        self.story_text.setReadOnly(True)
        self.story_text.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.story_text)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # 加载数据
        self.load_pet_stories()
    
    def load_pet_stories(self):
        """加载所有宠物故事"""
        try:
            # 获取所有可用的故事
            all_stories = story_manager.get_all_available_stories()
            
            # 更新下拉框
            current_selection = self.pet_combo.currentText()
            self.pet_combo.clear()
            
            # 获取当前宠物
            current_pet = getattr(settings, 'petname', None)
            
            # 添加选项
            pet_names = list(all_stories.keys())
            self.pet_combo.addItems(pet_names)
            
            # 设置当前宠物为默认选择
            if current_pet and current_pet in pet_names:
                self.pet_combo.setCurrentText(current_pet)
            elif current_selection and current_selection in pet_names:
                self.pet_combo.setCurrentText(current_selection)
            elif pet_names:
                self.pet_combo.setCurrentIndex(0)
            
            # 显示故事
            self.on_pet_changed()
            
        except Exception as e:
            print(f"❌ 加载宠物故事失败: {e}")
            self.story_text.setPlainText("加载故事时出现错误，请稍后重试。")
    
    def on_pet_changed(self):
        """当选择的宠物改变时"""
        selected_pet = self.pet_combo.currentText()
        if selected_pet:
            try:
                story_data = story_manager.get_pet_story(selected_pet)
                if story_data:
                    formatted_story = story_manager.format_story_for_display(story_data)
                    # 转换markdown格式为富文本显示
                    self.story_text.setMarkdown(formatted_story)
                else:
                    self.story_text.setPlainText("未找到该宠物的故事信息。")
            except Exception as e:
                print(f"❌ 显示宠物故事失败: {e}")
                self.story_text.setPlainText("显示故事时出现错误。")

class DiaryEntryWidget(QFrame):
    """单个日记条目的UI组件 - 优化版本"""
    
    # 类级别的样式缓存，避免重复创建
    _base_style = """
        QFrame {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #fafafa;
            margin: 4px;
            padding: 12px;
        }
        QFrame:hover {
            background-color: #f5f5f5;
            border-color: #d0d0d0;
        }
    """
    
    def __init__(self, entry: Dict, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setup_ui()
        
        # 让整个卡片可以点击
        self.setCursor(QCursor(Qt.PointingHandCursor))
    
    def setup_ui(self):
        """设置UI - 优化版本"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(self._base_style)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 头部信息
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # 类型图标和标题
        type_info = self._get_type_info(self.entry['entry_type'])
        
        title_label = QLabel(f"{type_info['icon']} {self.entry['title']}")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {type_info['color']}; margin: 0;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 时间 - 转换为上海时间
        shanghai_time = _convert_to_shanghai_time_helper(self.entry['timestamp'])
        time_str = shanghai_time.strftime('%m-%d %H:%M')
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #999; font-size: 9px; margin: 0;")
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # 内容预览 - 延迟加载复杂内容
        self._add_content_preview(layout)
        
        # 添加点击提示
        hint_label = QLabel("💡 点击查看详细内容")
        hint_label.setStyleSheet("color: #999; font-size: 8px; text-align: center;")
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)
    
    def _convert_to_shanghai_time(self, timestamp_str: str) -> datetime:
        """转换时间戳为上海时间"""
        return _convert_to_shanghai_time_helper(timestamp_str)
    
    def _get_type_info(self, entry_type: str) -> Dict[str, str]:
        """获取类型信息 - 缓存优化"""
        type_map = {
            'screenshot': {'icon': '📸', 'color': '#4CAF50'},
            'interaction': {'icon': '🔄', 'color': '#FF9800'}, 
            'chat': {'icon': '💬', 'color': '#2196F3'},
            'status_change': {'icon': '📊', 'color': '#9C27B0'},
            'system': {'icon': '⚙️', 'color': '#607D8B'},
            'autonomous_behavior': {'icon': '🤖', 'color': '#E91E63'},  # 新增自主行为类型
            'ai_diary': {'icon': '📝', 'color': '#00BCD4'} # 新增AI日记类型
        }
        return type_map.get(entry_type, {'icon': '📝', 'color': '#666'})
    
    def _add_content_preview(self, layout: QVBoxLayout):
        """添加内容预览 - 简化版本"""
        content = self.entry.get('content', {})
        
        if self.entry['entry_type'] == 'screenshot':
            self._add_simple_screenshot_info(layout, content)
        elif self.entry['entry_type'] == 'chat':
            self._add_simple_chat_info(layout, content)
        elif self.entry['entry_type'] == 'interaction':
            self._add_simple_interaction_info(layout, content)
        elif self.entry['entry_type'] == 'autonomous_behavior':
            self._add_simple_autonomous_behavior_info(layout, content)
        elif self.entry['entry_type'] == 'ai_diary':
            self._add_simple_ai_diary_info(layout, content)
        else:
            # 通用内容显示
            content_text = str(content)[:80] + ('...' if len(str(content)) > 80 else '')
            content_label = QLabel(content_text)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #555; font-size: 9px;")
            layout.addWidget(content_label)
    
    def _add_simple_screenshot_info(self, layout: QVBoxLayout, content: Dict):
        """简化的截屏信息显示"""
        info_parts = []
        if 'file_size' in content:
            size_mb = content['file_size'] / (1024 * 1024)
            info_parts.append(f"📁 {size_mb:.1f}MB")
        if 'resolution' in content:
            info_parts.append(f"📐 {content['resolution']}")
        
        if info_parts:
            info_label = QLabel(" | ".join(info_parts))
            info_label.setStyleSheet("color: #666; font-size: 9px;")
            layout.addWidget(info_label)
        
        # 添加缩略图预览
        screenshot_info = diary_manager.get_screenshot_details(self.entry['id'])
        if screenshot_info and screenshot_info.get('thumbnail_path'):
            thumb_path = screenshot_info['thumbnail_path']
            if os.path.exists(thumb_path):
                thumbnail = QLabel()
                pixmap = QPixmap(thumb_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumbnail.setPixmap(scaled_pixmap)
                    thumbnail.setFixedSize(60, 60)
                    thumbnail.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; background: white;")
                    thumbnail.setAlignment(Qt.AlignCenter)
                    layout.addWidget(thumbnail)
    
    def _add_simple_chat_info(self, layout: QVBoxLayout, content: Dict):
        """简化的聊天信息显示"""
        if 'user_message' in content:
            user_msg = content['user_message'][:60] + ('...' if len(content['user_message']) > 60 else '')
            user_label = QLabel(f"👤 {user_msg}")
            user_label.setStyleSheet("color: #333; font-size: 9px; padding: 2px 6px; background: #e3f2fd; border-radius: 4px;")
            user_label.setWordWrap(True)
            layout.addWidget(user_label)
        
        if 'pet_response' in content:
            pet_msg = content['pet_response'][:60] + ('...' if len(content['pet_response']) > 60 else '')
            pet_label = QLabel(f"🐾 {pet_msg}")
            pet_label.setStyleSheet("color: #555; font-size: 9px; padding: 2px 6px; background: #f1f8e9; border-radius: 4px;")
            pet_label.setWordWrap(True)
            layout.addWidget(pet_label)
    
    def _add_simple_interaction_info(self, layout: QVBoxLayout, content: Dict):
        """简化的交互信息显示"""
        details = []
        for key, value in content.items():
            if key == 'action':
                details.append(f"🎯 {value}")
            elif key == 'item_name':
                details.append(f"🎁 {value}")
            elif key == 'duration':
                details.append(f"⏱️ {value}s")
            elif key == 'click_count':
                details.append(f"👆 {value}次")
        
        if details:
            details_text = " | ".join(details[:3])  # 最多显示3个详情
            details_label = QLabel(details_text)
            details_label.setStyleSheet("color: #666; font-size: 9px; padding: 2px 6px; background: #fff3e0; border-radius: 4px;")
            layout.addWidget(details_label)
    
    def _add_simple_autonomous_behavior_info(self, layout: QVBoxLayout, content: Dict):
        """简化的自主行为信息显示"""
        if isinstance(content, str):
            try:
                import json
                content = json.loads(content)
            except:
                content = {}
        
        action_name = content.get('action_name', '未知行为')
        behavior_content = content.get('content', '')
        trigger_reason = content.get('trigger_reason', '未知原因')
        ai_response = content.get('ai_response', '')  # 新增：AI回复内容
        
        # 现在 action_name 已经是自然化的中文，直接使用
        display_name = action_name
        
        behavior_text = f"🤖 {display_name}"
        if behavior_content:
            behavior_text += f"\n💭 {behavior_content[:50]}{'...' if len(behavior_content) > 50 else ''}"
        if trigger_reason:
            behavior_text += f"\n🎯 触发: {trigger_reason}"
        
        # 新增：显示AI回复概要
        if ai_response:
            # 截取AI回复的前30个字符作为预览
            ai_preview = ai_response[:30] + ('...' if len(ai_response) > 30 else '')
            behavior_text += f"\n🤖 AI: {ai_preview}"
        
        behavior_label = QLabel(behavior_text)
        behavior_label.setStyleSheet("color: #555; font-size: 9px; padding: 2px 6px; background: #fce4ec; border-radius: 4px;")
        behavior_label.setWordWrap(True)
        layout.addWidget(behavior_label)
    
    def _add_simple_ai_diary_info(self, layout: QVBoxLayout, content: Dict):
        """简化的AI日记信息显示"""
        if isinstance(content, str):
            try:
                import json
                content = json.loads(content)
            except:
                content = {}
        
        # 获取AI生成的日记内容
        generated_content = content.get('generated_content', '')
        original_tool_call = content.get('original_tool_call', {})
        ai_response = content.get('ai_response', '')
        emotions = content.get('emotions', {})
        
        # 显示日记内容的前50个字符作为预览
        diary_preview = generated_content[:50] + ('...' if len(generated_content) > 50 else '')
        
        ai_diary_text = f"📝 AI日记"
        if diary_preview:
            ai_diary_text += f"\n{diary_preview}"
        ai_diary_text += f"\n🛠️ 基于: {original_tool_call.get('tool_name', '未知工具')}"
        
        ai_diary_label = QLabel(ai_diary_text)
        ai_diary_label.setStyleSheet("color: #333; font-size: 9px; padding: 2px 6px; background: #e8f5e8; border-radius: 4px; border-left: 3px solid #4CAF50;")
        ai_diary_label.setWordWrap(True)
        layout.addWidget(ai_diary_label)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self._show_detail_dialog()
        super().mousePressEvent(event)
    
    def _show_detail_dialog(self):
        """显示详细内容对话框"""
        dialog = DetailViewDialog(self.entry, self.parent())
        dialog.exec()

class DiaryWindow(QWidget):
    """日记本主窗口 - 优化版本"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("📖 DiaryWindow 初始化开始...")
        
        # 初始化变量
        self.current_entries = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self._loading = False
        
        try:
            print("📖 检查diary_manager...")
            # 测试diary_manager是否可用
            try:
                test_entries = diary_manager.get_entries(limit=1)
                print(f"📖 diary_manager测试成功，返回{len(test_entries)}条记录")
            except Exception as dm_error:
                print(f"❌ diary_manager测试失败: {dm_error}")
                raise dm_error
            
            print("📖 设置UI...")
            self.setup_ui()
            print("📖 UI设置完成，延迟加载数据...")
            
            # 延迟加载数据，避免初始化时卡顿
            QTimer.singleShot(100, self.load_entries)
            
            # 定时刷新
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.load_entries)
            self.refresh_timer.start(60000)  # 60秒刷新一次，减少频率
            
            print("📖 DiaryWindow 初始化完成")
            
        except Exception as e:
            print(f"❌ DiaryWindow 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 显示错误信息给用户
            try:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "日记本初始化失败", 
                                   f"日记本无法启动，错误信息：\n{str(e)}\n\n请检查Agent/data/diary目录是否存在。")
            except:
                pass
    
    def setup_ui(self):
        """设置UI - 优化版本"""
        self.setWindowTitle("🐾 DyberPet 日记本")
        self.setGeometry(100, 100, 1100, 750)
        self.setWindowIcon(QIcon(os.path.join(basedir, 'res/icons/icon.png')))
        
        # 设置窗口标志，允许其他应用覆盖此窗口
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        
        # 简化的窗口样式，移除不支持的属性
        self.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei';
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px 0 6px;
                color: #333;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
            QComboBox, QLineEdit {
                padding: 4px 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # 顶部控制面板
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)
        
        # 主内容区域
        content_layout = QHBoxLayout()
        
        # 左侧：日记列表（占大部分空间）
        diary_section = self._create_diary_section()
        content_layout.addWidget(diary_section, 3)
        
        # 右侧：统计面板
        stats_panel = self._create_stats_panel()
        content_layout.addWidget(stats_panel, 1)
        
        main_layout.addLayout(content_layout)
        
        # 底部状态栏和翻页控件
        bottom_layout = self._create_bottom_layout()
        main_layout.addLayout(bottom_layout)
    
    def _create_control_panel(self) -> QWidget:
        """创建控制面板"""
        panel = QGroupBox("🔍 筛选和搜索")
        layout = QHBoxLayout(panel)
        layout.setSpacing(12)
        
        # 类型筛选
        layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['全部', '截屏', '交互', '聊天', '状态变化', '系统'])
        self.type_combo.setMinimumWidth(80)
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.type_combo)
        
        # 日期筛选
        layout.addWidget(QLabel("日期:"))
        self.date_combo = QComboBox()
        self.date_combo.addItems(['全部', '今天', '昨天', '近7天', '近30天'])
        self.date_combo.setMinimumWidth(80)
        self.date_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.date_combo)
        
        # 搜索框
        layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词...")
        self.search_edit.setMinimumWidth(150)
        self.search_edit.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_edit)
        
        layout.addStretch()
        
        # 功能按钮
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("刷新")
        self.refresh_btn.setMaximumWidth(35)
        self.refresh_btn.clicked.connect(self.load_entries)
        layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📤")
        self.export_btn.setToolTip("导出")
        self.export_btn.setMaximumWidth(35)
        self.export_btn.clicked.connect(self.export_diary)
        layout.addWidget(self.export_btn)
        
        self.cleanup_btn = QPushButton("🗑️")
        self.cleanup_btn.setToolTip("清理旧记录")
        self.cleanup_btn.setMaximumWidth(35)
        self.cleanup_btn.clicked.connect(self.cleanup_old_entries)
        layout.addWidget(self.cleanup_btn)
        
        self.story_btn = QPushButton("📚")
        self.story_btn.setToolTip("宠物背景故事")
        self.story_btn.setMaximumWidth(35)
        self.story_btn.clicked.connect(self.show_pet_story)
        layout.addWidget(self.story_btn)
        
        return panel
    
    def _create_diary_section(self) -> QWidget:
        """创建日记列表区域"""
        section = QGroupBox("📝 日记记录")
        layout = QVBoxLayout(section)
        
        # 滚动区域 - 简化样式
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 15px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        # 内容容器
        self.diary_container = QWidget()
        self.diary_layout = QVBoxLayout(self.diary_container)
        self.diary_layout.setAlignment(Qt.AlignTop)
        self.diary_layout.setSpacing(3)
        
        self.scroll_area.setWidget(self.diary_container)
        layout.addWidget(self.scroll_area)
        
        return section
    
    def _create_stats_panel(self) -> QWidget:
        """创建统计面板"""
        panel = QGroupBox("📊 统计信息")
        layout = QVBoxLayout(panel)
        
        # 总数显示
        self.total_label = QLabel("总条目: 0")
        self.total_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.total_label.setStyleSheet("color: #2196F3; margin: 8px 0;")
        layout.addWidget(self.total_label)
        
        # 类型统计
        stats_group = QGroupBox("类型分布")
        self.type_stats_layout = QVBoxLayout(stats_group)
        layout.addWidget(stats_group)
        
        # 趋势统计
        trend_group = QGroupBox("最近活动")
        self.daily_stats_layout = QVBoxLayout(trend_group)
        layout.addWidget(trend_group)
        
        layout.addStretch()
        return panel
    
    def _create_bottom_layout(self) -> QHBoxLayout:
        """创建底部布局"""
        layout = QHBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 10px; padding: 4px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 翻页控件
        self.page_info_label = QLabel("第 1 页，共 1 页")
        self.page_info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.page_info_label)
        
        self.first_btn = QPushButton("⏮️")
        self.first_btn.setMaximumWidth(35)
        self.first_btn.setToolTip("首页")
        self.first_btn.clicked.connect(self.go_to_first_page)
        layout.addWidget(self.first_btn)
        
        self.prev_btn = QPushButton("◀️")
        self.prev_btn.setMaximumWidth(35)
        self.prev_btn.setToolTip("上一页")
        self.prev_btn.clicked.connect(self.go_to_prev_page)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("▶️")
        self.next_btn.setMaximumWidth(35)
        self.next_btn.setToolTip("下一页")
        self.next_btn.clicked.connect(self.go_to_next_page)
        layout.addWidget(self.next_btn)
        
        self.last_btn = QPushButton("⏭️")
        self.last_btn.setMaximumWidth(35)
        self.last_btn.setToolTip("末页")
        self.last_btn.clicked.connect(self.go_to_last_page)
        layout.addWidget(self.last_btn)
        
        return layout
    
    def load_entries(self):
        """加载日记条目 - 优化版本"""
        if self._loading:
            return
            
        self._loading = True
        self.status_label.setText("加载中...")
        
        try:
            # 获取筛选条件
            entry_type = self._get_filter_type()
            start_date, end_date = self._get_filter_dates()
            
            # 加载数据（限制数量提高性能）
            if self.search_edit.text().strip():
                all_entries = diary_manager.search_entries(
                    self.search_edit.text().strip(), 
                    entry_type
                )
            else:
                all_entries = diary_manager.get_entries(
                    entry_type=entry_type,
                    start_date=start_date,
                    end_date=end_date,
                    limit=500  # 减少数据量
                )
            
            # 计算分页
            total_items = len(all_entries)
            self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
            
            # 确保当前页在有效范围内
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            
            # 获取当前页的数据
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            self.current_entries = all_entries[start_idx:end_idx]
            
            # 延迟更新UI，避免阻塞
            QTimer.singleShot(10, lambda: self._update_ui_delayed(all_entries, total_items))
            
        except Exception as e:
            print(f"❌ 加载日记条目失败: {e}")
            self.status_label.setText(f"加载失败: {str(e)}")
        finally:
            self._loading = False
    
    def _update_ui_delayed(self, all_entries: List[Dict], total_items: int):
        """延迟更新UI"""
        try:
            self._update_diary_list()
            self._update_statistics(all_entries)
            self._update_pagination_controls()
            
            self.status_label.setText(f"已加载 {len(self.current_entries)} 条记录（共 {total_items} 条）")
        except Exception as e:
            print(f"❌ 更新UI失败: {e}")
            self.status_label.setText("更新失败")
    
    def _update_diary_list(self):
        """更新日记列表显示 - 优化版本"""
        # 清空现有内容
        for i in reversed(range(self.diary_layout.count())):
            child = self.diary_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新条目
        if not self.current_entries:
            no_data_label = QLabel("📝 暂无记录")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #999; font-size: 14px; padding: 40px; background: white; border-radius: 8px; margin: 15px;")
            self.diary_layout.addWidget(no_data_label)
        else:
            # 批量创建，减少单个创建的开销
            for entry in self.current_entries:
                entry_widget = DiaryEntryWidget(entry)
                self.diary_layout.addWidget(entry_widget)
        
        self.diary_layout.addStretch()
    
    def _update_statistics(self, all_entries: List[Dict]):
        """更新统计信息 - 优化版本"""
        try:
            # 更新总数
            total = len(all_entries)
            self.total_label.setText(f"总条目: {total}")
            
            # 更新类型统计
            self._clear_layout(self.type_stats_layout)
            type_stats = {}
            for entry in all_entries:
                entry_type = entry['entry_type']
                type_stats[entry_type] = type_stats.get(entry_type, 0) + 1
            
            type_names = {
                'screenshot': '📸 截屏',
                'interaction': '🔄 交互',
                'chat': '💬 聊天',
                'status_change': '📊 状态',
                'system': '⚙️ 系统',
                'autonomous_behavior': '🤖 自主行为',
                'ai_diary': '📝 AI日记'
            }
            
            for entry_type, count in type_stats.items():
                name = type_names.get(entry_type, entry_type)
                label = QLabel(f"{name}: {count}")
                label.setStyleSheet("color: #555; font-size: 10px; margin: 1px 0;")
                self.type_stats_layout.addWidget(label)
            
            # 更新每日统计（只统计最近30条，提高性能）
            self._clear_layout(self.daily_stats_layout)
            daily_stats = {}
            for entry in all_entries[-30:]:
                date = entry['timestamp'][:10]
                daily_stats[date] = daily_stats.get(date, 0) + 1
            
            # 显示最近5天
            sorted_dates = sorted(daily_stats.keys(), reverse=True)[:5]
            for date in sorted_dates:
                count = daily_stats[date]
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date_str = date_obj.strftime('%m-%d')
                
                day_layout = QHBoxLayout()
                day_label = QLabel(f"{date_str}:")
                day_label.setFixedWidth(35)
                day_label.setStyleSheet("color: #666; font-size: 9px;")
                day_layout.addWidget(day_label)
                
                progress_bar = QProgressBar()
                progress_bar.setMaximum(max(daily_stats.values()) if daily_stats else 1)
                progress_bar.setValue(count)
                progress_bar.setTextVisible(True)
                progress_bar.setFormat(f"{count}")
                progress_bar.setMaximumHeight(16)
                progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #ddd;
                        border-radius: 3px;
                        text-align: center;
                        font-size: 8px;
                    }
                    QProgressBar::chunk {
                        background-color: #4CAF50;
                        border-radius: 2px;
                    }
                """)
                day_layout.addWidget(progress_bar)
                
                self.daily_stats_layout.addLayout(day_layout)
                
        except Exception as e:
            print(f"❌ 更新统计信息失败: {e}")
    
    def _update_pagination_controls(self):
        """更新翻页控件状态"""
        self.page_info_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        
        self.first_btn.setEnabled(self.current_page > 1)
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        self.last_btn.setEnabled(self.current_page < self.total_pages)
    
    def go_to_first_page(self):
        """跳转到首页"""
        if self.current_page > 1:
            self.current_page = 1
            self.load_entries()
    
    def go_to_prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_entries()
    
    def go_to_next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_entries()
    
    def go_to_last_page(self):
        """跳转到末页"""
        if self.current_page < self.total_pages:
            self.current_page = self.total_pages
            self.load_entries()
    
    def _clear_layout(self, layout):
        """清空布局"""
        for i in reversed(range(layout.count())):
            child = layout.itemAt(i)
            if child.widget():
                child.widget().setParent(None)
            elif child.layout():
                self._clear_layout(child.layout())
    
    def _get_filter_type(self) -> str:
        """获取类型筛选"""
        type_map = {
            '全部': None,
            '截屏': 'screenshot',
            '交互': 'interaction',
            '聊天': 'chat',
            '状态变化': 'status_change',
            '系统': 'system'
        }
        return type_map.get(self.type_combo.currentText())
    
    def _get_filter_dates(self) -> tuple:
        """获取日期筛选"""
        date_text = self.date_combo.currentText()
        now = datetime.now()
        
        if date_text == '今天':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return start, now
        elif date_text == '昨天':
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            return start, end
        elif date_text == '近7天':
            start = now - timedelta(days=7)
            return start, now
        elif date_text == '近30天':
            start = now - timedelta(days=30)
            return start, now
        else:
            return None, None
    
    def on_filter_changed(self):
        """筛选条件改变"""
        if not self._loading:
            self.current_page = 1
            self.load_entries()
    
    def on_search_changed(self):
        """搜索内容改变"""
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(lambda: [setattr(self, 'current_page', 1), self.load_entries()])
        self.search_timer.start(800)  # 增加延迟到800ms
    
    def export_diary(self):
        """导出日记"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出日记", f"diary_export_{datetime.now().strftime('%Y%m%d')}.json",
                "JSON文件 (*.json);;所有文件 (*)"
            )
            
            if file_path:
                import json
                
                # 获取所有条目用于导出
                all_entries = diary_manager.get_entries(limit=10000)
                
                # 准备导出数据
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'total_entries': len(all_entries),
                    'entries': all_entries
                }
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "导出成功", f"日记已导出到:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出过程中出现错误:\n{str(e)}")
    
    def cleanup_old_entries(self):
        """清理旧记录"""
        reply = QMessageBox.question(
            self, "确认清理", 
            "是否清理90天前的旧记录？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                deleted_count = diary_manager.cleanup_old_entries(days=90)
                QMessageBox.information(self, "清理完成", f"已清理 {deleted_count} 条旧记录")
                self.current_page = 1
                self.load_entries()
            except Exception as e:
                QMessageBox.critical(self, "清理失败", f"清理过程中出现错误:\n{str(e)}")
    
    def show_pet_story(self):
        """显示宠物背景故事"""
        try:
            # 如果故事窗口已存在，则激活它
            if hasattr(self, 'story_window') and self.story_window is not None:
                try:
                    self.story_window.show()
                    self.story_window.raise_()
                    self.story_window.activateWindow()
                    return
                except:
                    self.story_window = None
            
            # 创建新的故事窗口
            self.story_window = PetStoryDialog(self)
            self.story_window.show()
            
        except Exception as e:
            print(f"❌ 打开宠物故事失败: {e}")
            QMessageBox.critical(self, "错误", f"无法打开宠物故事:\n{str(e)}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        # 关闭故事窗口
        if hasattr(self, 'story_window') and self.story_window is not None:
            try:
                self.story_window.close()
            except:
                pass
        
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = DiaryWindow()
    window.show()
    sys.exit(app.exec()) 