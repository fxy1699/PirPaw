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
                           QMessageBox, QFileDialog, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QDate, QTimer, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon, QPalette

# 添加Agent路径以导入DiaryManager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Agent'))
from data.diary.diary_manager import diary_manager

import DyberPet.settings as settings
basedir = settings.BASEDIR

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
        
        # 时间
        time_str = datetime.fromisoformat(self.entry['timestamp']).strftime('%m-%d %H:%M')
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #999; font-size: 9px; margin: 0;")
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # 内容预览 - 延迟加载复杂内容
        self._add_content_preview(layout)
    
    def _get_type_info(self, entry_type: str) -> Dict[str, str]:
        """获取类型信息 - 缓存优化"""
        type_map = {
            'screenshot': {'icon': '📸', 'color': '#4CAF50'},
            'interaction': {'icon': '🔄', 'color': '#FF9800'}, 
            'chat': {'icon': '💬', 'color': '#2196F3'},
            'status_change': {'icon': '📊', 'color': '#9C27B0'},
            'system': {'icon': '⚙️', 'color': '#607D8B'}
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
            print("📖 设置UI...")
            self.setup_ui()
            print("📖 UI设置完成，延迟加载数据...")
            
            # 延迟加载数据，避免初始化时卡顿
            QTimer.singleShot(100, self.load_entries)
            
        except Exception as e:
            print(f"❌ DiaryWindow 初始化失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_entries)
        self.refresh_timer.start(60000)  # 60秒刷新一次，减少频率
        print("📖 DiaryWindow 初始化完成")
    
    def setup_ui(self):
        """设置UI - 优化版本"""
        self.setWindowTitle("🐾 DyberPet 日记本")
        self.setGeometry(100, 100, 1100, 750)
        self.setWindowIcon(QIcon(os.path.join(basedir, 'res/icons/icon.png')))
        
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
                'system': '⚙️ 系统'
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
    sys.exit(app.exec()) 