"""
DyberPet 聊天窗口
与Agent系统集成的聊天界面
"""

import os
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from qfluentwidgets import *


class ChatWindow(QWidget):
    """聊天窗口"""
    
    # 信号
    message_sent = Signal(str)  # 发送消息信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.agent_executor = None  # Agent执行器
        self.chat_history = []  # 聊天历史
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("🤖 DyberPet智能聊天")
        self.setFixedSize(400, 500)
        
        # 设置窗口属性
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)  # 显示时激活窗口
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        title_label = TitleLabel("🐾 与宠物聊天")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(350)
        layout.addWidget(self.chat_display)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.input_field = LineEdit()
        self.input_field.setPlaceholderText("输入指令，如：让小猫睡觉、走路、现在的状态...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setEnabled(True)  # 确保输入框启用
        self.input_field.setFocus()  # 设置焦点
        input_layout.addWidget(self.input_field)
        
        self.send_button = PushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # 状态栏
        self.status_label = CaptionLabel("准备就绪")
        layout.addWidget(self.status_label)
        
        # 快捷按钮
        shortcuts_layout = QHBoxLayout()
        
        quick_buttons = [
            ("😴 睡觉", "让小猫睡觉"),
            ("🚶 走路", "走路"),
            ("📊 状态", "现在的状态"),
            ("🔄 切换", "切换到Kitty")
        ]
        
        for text, command in quick_buttons:
            btn = PushButton(text)
            btn.clicked.connect(lambda checked, cmd=command: self.quick_command(cmd))
            shortcuts_layout.addWidget(btn)
        
        layout.addLayout(shortcuts_layout)
        
        # 初始化欢迎信息
        self.add_system_message("🎉 欢迎使用DyberPet智能聊天！")
        self.add_system_message("💡 你可以用自然语言控制宠物，比如：")
        self.add_system_message("   • 让小猫睡觉")
        self.add_system_message("   • 走路")
        self.add_system_message("   • 现在的状态")
        self.add_system_message("   • 切换到其他宠物")
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            ChatWindow {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            LineEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-family: 'Microsoft YaHei';
                font-size: 13px;
            }
            LineEdit:focus {
                border-color: #0078d4;
                background-color: #ffffff;
            }
        """)
        
    def set_agent_executor(self, executor):
        """设置Agent执行器"""
        print(f"🔧 设置Agent执行器: {executor}")
        print(f"🔧 执行器类型: {type(executor)}")
        self.agent_executor = executor
        if executor:
            self.status_label.setText("✅ Agent已连接")
            self.add_system_message("🔗 Agent系统已连接，可以开始聊天了！")
            print("✅ Agent执行器设置成功")
        else:
            self.status_label.setText("❌ Agent未连接")
            print("❌ Agent执行器为空")
            
    def quick_command(self, command):
        """快捷命令"""
        self.input_field.setText(command)
        self.send_message()
        
    def send_message(self):
        """发送消息"""
        print(f"🎯 send_message被调用")
        message = self.input_field.text().strip()
        print(f"💬 输入消息: '{message}'")
        
        if not message:
            print("⚠️ 消息为空，不处理")
            return
            
        # 清空输入框
        self.input_field.clear()
        
        # 显示用户消息
        self.add_user_message(message)
        
        # 处理消息
        self.process_message(message)
        
    def process_message(self, message):
        """处理消息"""
        print(f"🔄 process_message被调用，消息: '{message}'")
        print(f"🔍 agent_executor存在: {self.agent_executor is not None}")
        
        if not self.agent_executor:
            print("❌ agent_executor为空")
            self.add_system_message("❌ Agent系统未连接")
            return
            
        try:
            print("🤖 开始处理消息...")
            self.status_label.setText("🤖 处理中...")
            QApplication.processEvents()  # 更新UI
            
            # 调用Agent处理
            print(f"📞 调用agent_executor.handle_message('{message}')")
            result = self.agent_executor.handle_message(message)
            print(f"📋 Agent返回结果: {result}")
            
            if result:
                self.add_bot_message(result)
            else:
                self.add_bot_message("🤔 抱歉，我没能理解这个指令。请尝试其他表达方式。")
                
            self.status_label.setText("✅ 处理完成")
            print("✅ 消息处理完成")
            
        except Exception as e:
            print(f"❌ 处理异常: {e}")
            import traceback
            print(f"📋 异常详情: {traceback.format_exc()}")
            self.add_system_message(f"❌ 处理错误: {e}")
            self.status_label.setText("❌ 处理失败")
            
    def add_user_message(self, message):
        """添加用户消息"""
        html = f"""
        <div style="margin: 8px 0; text-align: right;">
            <span style="background-color: #0078d4; color: white; padding: 8px 12px; 
                         border-radius: 18px; display: inline-block; max-width: 80%;">
                👤 {message}
            </span>
        </div>
        """
        self.chat_display.append(html)
        self.scroll_to_bottom()
        
    def add_bot_message(self, message):
        """添加机器人消息"""
        html = f"""
        <div style="margin: 8px 0; text-align: left;">
            <span style="background-color: #e1f5fe; color: #333; padding: 8px 12px; 
                         border-radius: 18px; display: inline-block; max-width: 80%;">
                🤖 {message}
            </span>
        </div>
        """
        self.chat_display.append(html)
        self.scroll_to_bottom()
        
    def add_system_message(self, message):
        """添加系统消息"""
        html = f"""
        <div style="margin: 4px 0; text-align: center;">
            <span style="background-color: #f0f0f0; color: #666; padding: 4px 8px; 
                         border-radius: 12px; font-size: 11px;">
                {message}
            </span>
        </div>
        """
        self.chat_display.append(html)
        self.scroll_to_bottom()
        
    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def showEvent(self, event):
        """显示事件"""
        print("📺 showEvent 被调用")
        super().showEvent(event)
        # 确保输入框获得焦点
        self.input_field.setFocus()
        print("🔍 聊天窗口已显示，输入框已获得焦点")
        print(f"🔍 窗口几何信息: pos=({self.x()},{self.y()}), size=({self.width()}x{self.height()})")
        print(f"🔍 窗口标志: {self.windowFlags()}")
        print(f"🔍 父窗口: {self.parent()}")
        
    def force_show(self):
        """强制显示聊天窗口"""
        print("🚀 force_show 被调用")
        
        # 确保窗口属性正确
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        
        # 强制显示
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        
        # 处理事件循环
        QApplication.processEvents()
        
        print(f"🚀 强制显示完成，可见性: {self.isVisible()}")
        
    def closeEvent(self, event):
        """关闭事件"""
        self.hide()  # 隐藏而不是关闭
        event.ignore() 