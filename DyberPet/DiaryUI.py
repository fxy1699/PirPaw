#!/usr/bin/env python3
"""
DyberPet 日记本UI界面
显示宠物的交互历史、截屏记录等
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QScrollArea, QFrame, QPushButton, QLineEdit,
                           QComboBox, QDateEdit, QTextEdit, QGroupBox,
                           QGridLayout, QSplitter, QTabWidget, QProgressBar,
                           QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, QThread, Signal, QDate, QTimer
from PySide6.QtGui import QPixmap, QFont, QIcon, QPalette

# 添加Agent路径以导入DiaryManager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Agent'))
from data.diary.diary_manager import diary_manager

import DyberPet.settings as settings
basedir = settings.BASEDIR

class DiaryEntryWidget(QFrame):
    """单个日记条目的UI组件"""
    
    def __init__(self, entry: Dict, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #fafafa;
                margin: 5px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
                border-color: #bbb;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # 头部信息
        header_layout = QHBoxLayout()
        
        # 类型图标和标题
        type_icons = {
            'screenshot': '📸',
            'interaction': '🔄',
            'chat': '💬',
            'status_change': '📊',
            'system': '⚙️'
        }
        
        icon = type_icons.get(self.entry['entry_type'], '📝')
        title_label = QLabel(f"{icon} {self.entry['title']}")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 时间
        time_str = datetime.fromisoformat(self.entry['timestamp']).strftime('%m-%d %H:%M')
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #666; font-size: 9px;")
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # 内容预览
        content = self.entry.get('content', {})
        if self.entry['entry_type'] == 'screenshot':
            self._add_screenshot_content(layout, content)
        elif self.entry['entry_type'] == 'chat':
            self._add_chat_content(layout, content)
        elif self.entry['entry_type'] == 'interaction':
            self._add_interaction_content(layout, content)
        else:
            # 通用内容显示
            content_text = str(content)[:100] + ('...' if len(str(content)) > 100 else '')
            content_label = QLabel(content_text)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #333; font-size: 9px;")
            layout.addWidget(content_label)
    
    def _add_screenshot_content(self, layout: QVBoxLayout, content: Dict):
        """添加截屏内容"""
        # 获取截屏详细信息
        screenshot_info = diary_manager.get_screenshot_details(self.entry['id'])
        
        info_layout = QHBoxLayout()
        
        # 缩略图（如果存在）
        if screenshot_info and screenshot_info.get('thumbnail_path'):
            thumb_path = screenshot_info['thumbnail_path']
            if os.path.exists(thumb_path):
                thumbnail = QLabel()
                pixmap = QPixmap(thumb_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumbnail.setPixmap(scaled_pixmap)
                    thumbnail.setFixedSize(60, 60)
                    thumbnail.setStyleSheet("border: 1px solid #ccc;")
                    info_layout.addWidget(thumbnail)
        
        # 文件信息
        info_text = ""
        if 'file_size' in content:
            size_mb = content['file_size'] / (1024 * 1024)
            info_text += f"大小: {size_mb:.1f}MB\n"
        if 'resolution' in content:
            info_text += f"分辨率: {content['resolution']}"
        
        if info_text:
            info_label = QLabel(info_text)
            info_label.setStyleSheet("color: #666; font-size: 8px;")
            info_layout.addWidget(info_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
    
    def _add_chat_content(self, layout: QVBoxLayout, content: Dict):
        """添加聊天内容"""
        if 'user_message' in content:
            user_msg = content['user_message'][:80] + ('...' if len(content['user_message']) > 80 else '')
            user_label = QLabel(f"👤 {user_msg}")
            user_label.setStyleSheet("color: #333; font-size: 9px; margin-left: 10px;")
            user_label.setWordWrap(True)
            layout.addWidget(user_label)
        
        if 'pet_response' in content:
            pet_msg = content['pet_response'][:80] + ('...' if len(content['pet_response']) > 80 else '')
            pet_label = QLabel(f"🐾 {pet_msg}")
            pet_label.setStyleSheet("color: #555; font-size: 9px; margin-left: 10px;")
            pet_label.setWordWrap(True)
            layout.addWidget(pet_label)
    
    def _add_interaction_content(self, layout: QVBoxLayout, content: Dict):
        """添加交互内容"""
        details = []
        for key, value in content.items():
            if key in ['action', 'item_name', 'duration']:
                details.append(f"{key}: {value}")
        
        if details:
            details_text = " | ".join(details)
            details_label = QLabel(details_text)
            details_label.setStyleSheet("color: #666; font-size: 8px;")
            layout.addWidget(details_label)

class DiaryWindow(QWidget):
    """日记本主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("📖 DiaryWindow 初始化开始...")
        self.current_entries = []
        
        try:
            print("📖 设置UI...")
            self.setup_ui()
            print("📖 UI设置完成，开始加载数据...")
            self.load_entries()
            print("📖 数据加载完成")
        except Exception as e:
            print(f"❌ DiaryWindow 初始化失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_entries)
        self.refresh_timer.start(30000)  # 30秒刷新一次
        print("📖 DiaryWindow 初始化完成")
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("🐾 DyberPet 日记本")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon(os.path.join(basedir, 'res/icons/icon.png')))
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 顶部控制面板
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)
        
        # 主内容区域
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：日记列表
        self.diary_list = self._create_diary_list()
        content_splitter.addWidget(self.diary_list)
        
        # 右侧：统计面板
        stats_panel = self._create_stats_panel()
        content_splitter.addWidget(stats_panel)
        
        content_splitter.setSizes([700, 300])
        main_layout.addWidget(content_splitter)
        
        # 底部状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        main_layout.addWidget(self.status_label)
    
    def _create_control_panel(self) -> QWidget:
        """创建控制面板"""
        panel = QGroupBox("筛选和搜索")
        layout = QHBoxLayout(panel)
        
        # 类型筛选
        layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['全部', '截屏', '交互', '聊天', '状态变化', '系统'])
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.type_combo)
        
        # 日期筛选
        layout.addWidget(QLabel("日期:"))
        self.date_combo = QComboBox()
        self.date_combo.addItems(['全部', '今天', '昨天', '近7天', '近30天'])
        self.date_combo.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.date_combo)
        
        # 搜索框
        layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词搜索...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_edit)
        
        layout.addStretch()
        
        # 功能按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.load_entries)
        layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_diary)
        layout.addWidget(self.export_btn)
        
        self.cleanup_btn = QPushButton("🗑️ 清理")
        self.cleanup_btn.clicked.connect(self.cleanup_old_entries)
        layout.addWidget(self.cleanup_btn)
        
        return panel
    
    def _create_diary_list(self) -> QScrollArea:
        """创建日记列表"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 内容容器
        self.diary_container = QWidget()
        self.diary_layout = QVBoxLayout(self.diary_container)
        self.diary_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.diary_container)
        return scroll_area
    
    def _create_stats_panel(self) -> QWidget:
        """创建统计面板"""
        panel = QGroupBox("统计信息")
        layout = QVBoxLayout(panel)
        
        # 统计标签页
        self.stats_tabs = QTabWidget()
        
        # 概览标签页
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        self.total_label = QLabel("总条目: 0")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        overview_layout.addWidget(self.total_label)
        
        self.type_stats_layout = QVBoxLayout()
        overview_layout.addLayout(self.type_stats_layout)
        
        overview_layout.addStretch()
        self.stats_tabs.addTab(overview_tab, "📊 概览")
        
        # 趋势标签页
        trend_tab = QWidget()
        trend_layout = QVBoxLayout(trend_tab)
        
        self.daily_stats_layout = QVBoxLayout()
        trend_layout.addLayout(self.daily_stats_layout)
        
        trend_layout.addStretch()
        self.stats_tabs.addTab(trend_tab, "📈 趋势")
        
        layout.addWidget(self.stats_tabs)
        return panel
    
    def load_entries(self):
        """加载日记条目"""
        try:
            # 获取筛选条件
            entry_type = self._get_filter_type()
            start_date, end_date = self._get_filter_dates()
            
            # 加载数据
            if self.search_edit.text().strip():
                # 搜索模式
                entries = diary_manager.search_entries(
                    self.search_edit.text().strip(), 
                    entry_type
                )
            else:
                # 正常筛选模式
                entries = diary_manager.get_entries(
                    entry_type=entry_type,
                    start_date=start_date,
                    end_date=end_date,
                    limit=100
                )
            
            self.current_entries = entries
            self._update_diary_list()
            self._update_statistics()
            
            self.status_label.setText(f"已加载 {len(entries)} 条记录")
            
        except Exception as e:
            print(f"❌ 加载日记条目失败: {e}")
            self.status_label.setText(f"加载失败: {str(e)}")
    
    def _update_diary_list(self):
        """更新日记列表显示"""
        # 清空现有内容
        for i in reversed(range(self.diary_layout.count())):
            child = self.diary_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新条目
        if not self.current_entries:
            no_data_label = QLabel("📝 暂无记录")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #999; font-size: 14px; padding: 50px;")
            self.diary_layout.addWidget(no_data_label)
        else:
            for entry in self.current_entries:
                entry_widget = DiaryEntryWidget(entry)
                self.diary_layout.addWidget(entry_widget)
        
        self.diary_layout.addStretch()
    
    def _update_statistics(self):
        """更新统计信息"""
        try:
            stats = diary_manager.get_statistics(days=7)
            
            # 更新总数
            total = stats.get('total_entries', 0)
            self.total_label.setText(f"总条目: {total}")
            
            # 更新类型统计
            self._clear_layout(self.type_stats_layout)
            type_stats = stats.get('type_statistics', {})
            
            type_names = {
                'screenshot': '📸 截屏',
                'interaction': '🔄 交互',
                'chat': '💬 聊天',
                'status_change': '📊 状态',
                'system': '⚙️ 系统'
            }
            
            for entry_type, count in type_stats.items():
                name = type_names.get(entry_type, entry_type)
                label = QLabel(f"{name}: {count}")
                self.type_stats_layout.addWidget(label)
            
            # 更新每日统计
            self._clear_layout(self.daily_stats_layout)
            daily_stats = stats.get('daily_statistics', {})
            
            for date, count in list(daily_stats.items())[:7]:  # 显示最近7天
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date_str = date_obj.strftime('%m-%d')
                
                # 简单的进度条显示
                max_count = max(daily_stats.values()) if daily_stats else 1
                progress = int((count / max_count) * 100)
                
                day_layout = QHBoxLayout()
                day_label = QLabel(f"{date_str}:")
                day_label.setFixedWidth(50)
                day_layout.addWidget(day_label)
                
                progress_bar = QProgressBar()
                progress_bar.setMaximum(100)
                progress_bar.setValue(progress)
                progress_bar.setTextVisible(True)
                progress_bar.setFormat(f"{count}")
                day_layout.addWidget(progress_bar)
                
                self.daily_stats_layout.addLayout(day_layout)
                
        except Exception as e:
            print(f"❌ 更新统计信息失败: {e}")
    
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
        self.load_entries()
    
    def on_search_changed(self):
        """搜索内容改变"""
        # 延迟搜索，避免频繁查询
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.load_entries)
        self.search_timer.start(500)  # 500ms延迟
    
    def export_diary(self):
        """导出日记"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出日记", f"diary_export_{datetime.now().strftime('%Y%m%d')}.json",
                "JSON文件 (*.json);;所有文件 (*)"
            )
            
            if file_path:
                import json
                
                # 准备导出数据
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'total_entries': len(self.current_entries),
                    'entries': self.current_entries
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
                self.load_entries()  # 重新加载
            except Exception as e:
                QMessageBox.critical(self, "清理失败", f"清理过程中出现错误:\n{str(e)}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = DiaryWindow()
    window.show()
    sys.exit(app.exec_()) 