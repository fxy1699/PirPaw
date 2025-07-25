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


class AgentCommunicationThread(QThread):
    """Agent通信线程"""
    
    # 信号定义
    message_processing_started = Signal(str)   # 开始处理消息
    message_processing_completed = Signal(list)  # 处理完成，返回结果列表
    message_processing_failed = Signal(str)   # 处理失败，返回错误信息
    
    def __init__(self, agent_executor):
        super().__init__()
        self.agent_executor = agent_executor
        self.message_queue = []
        self.processing = False
        
        # 用于线程间通信的条件变量
        self.condition = QWaitCondition()
        self.mutex = QMutex()
    
    def process_message(self, message):
        """添加消息到处理队列"""
        with QMutexLocker(self.mutex):
            self.message_queue.append(message)
            self.condition.wakeOne()
    
    def run(self):
        """后台线程主循环"""
        while True:
            with QMutexLocker(self.mutex):
                # 等待有消息需要处理
                while not self.message_queue and not self.isInterruptionRequested():
                    self.condition.wait(self.mutex)
                
                if self.isInterruptionRequested():
                    break
                
                if self.message_queue:
                    message = self.message_queue.pop(0)
                    self.processing = True
            
            try:
                # 发送开始处理信号
                self.message_processing_started.emit(message)
                
                # 在后台线程中调用Agent处理
                if self.agent_executor:
                    results = self.agent_executor.process_message(message)
                    self.message_processing_completed.emit(results if results else [])
                else:
                    self.message_processing_failed.emit("Agent系统未连接")
                    
            except Exception as e:
                error_msg = f"处理消息时出错: {e}"
                print(f"❌ {error_msg}")
                self.message_processing_failed.emit(error_msg)
            finally:
                self.processing = False
    
    def stop(self):
        """停止线程"""
        self.requestInterruption()
        with QMutexLocker(self.mutex):
            self.condition.wakeOne()
        self.wait()


class ChatWindow(QWidget):
    """聊天窗口"""
    
    # 信号
    message_sent = Signal(str)  # 发送消息信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.agent_executor = None  # Agent执行器
        self.chat_history = []  # 聊天历史
        self.communication_thread = None  # Agent通信线程
        
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
        
        # 初始化欢迎信息和状态监控
        self.init_welcome_messages()
        
    def init_welcome_messages(self):
        """初始化欢迎信息和状态监控"""
        # 初始化欢迎信息
        self.add_system_message("🎉 欢迎使用DyberPet智能聊天！")
        self.add_system_message("💡 你可以用自然语言控制宠物，比如：")
        self.add_system_message("   • 让小猫睡觉")
        self.add_system_message("   • 走路")
        self.add_system_message("   • 现在的状态")
        self.add_system_message("   • 切换到其他宠物")
        
        # 检查Agent初始化状态并设置状态监控
        self.agent_status_shown = False
        self.check_agent_status()
        
        # 设置状态监控定时器
        self.status_check_timer = QTimer()
        self.status_check_timer.timeout.connect(self.check_agent_status)
        self.status_check_timer.start(2000)  # 每2秒检查一次
    
    def check_agent_status(self):
        """检查Agent系统状态"""
        app = QApplication.instance()
        
        if hasattr(app, 'agent_initializing') and app.agent_initializing:
            if not self.agent_status_shown:
                self.add_system_message("🤖 Agent核心正在后台线程中初始化，UI集成将在主线程中完成...")
                self.agent_status_shown = True
        elif hasattr(app, 'chat_integration_success'):
            if app.chat_integration_success and self.agent_status_shown:
                self.add_system_message("✅ Agent系统完全初始化完成，现在可以使用智能聊天功能了！")
                self.status_check_timer.stop()  # 停止状态检查
                self.setup_agent_communication()  # 设置Agent通信
            elif not app.chat_integration_success and self.agent_status_shown:
                self.add_system_message("⚠️ Agent系统初始化失败，部分功能可能不可用")
                self.status_check_timer.stop()  # 停止状态检查
    
    def setup_agent_communication(self):
        """设置Agent通信线程"""
        if self.agent_executor and not self.communication_thread:
            print("🔧 设置Agent通信线程...")
            self.communication_thread = AgentCommunicationThread(self.agent_executor)
            
            # 连接信号
            self.communication_thread.message_processing_started.connect(self.on_message_processing_started)
            self.communication_thread.message_processing_completed.connect(self.on_message_processing_completed)
            self.communication_thread.message_processing_failed.connect(self.on_message_processing_failed)
            
            # 启动通信线程
            self.communication_thread.start()
            print("✅ Agent通信线程已启动")
    
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
        
        # 使用通信线程处理消息
        self.process_message_threaded(message)
    
    def process_message_threaded(self, message):
        """通过通信线程处理消息"""
        print(f"🔄 通过通信线程处理消息: '{message}'")
        
        if not self.agent_executor:
            print("❌ agent_executor为空")
            self.add_system_message("❌ Agent系统未连接")
            return
        
        # 检查Agent是否正在初始化
        app = QApplication.instance()
        if hasattr(app, 'agent_initializing') and app.agent_initializing:
            self.add_system_message("🤖 Agent系统正在初始化中，请稍后再试...")
            return
        
        # 如果通信线程还没设置，尝试设置
        if not self.communication_thread:
            self.setup_agent_communication()
        
        if self.communication_thread:
            # 通过通信线程处理消息
            self.communication_thread.process_message(message)
        else:
            # 降级到同步处理
            self.process_message_sync(message)
    
    def process_message_sync(self, message):
        """同步处理消息（降级方案）"""
        print(f"🔄 同步处理消息: '{message}'")
        
        try:
            # 简单的UI反馈
            self.status_label.setText("🤖 处理中...")
            self.input_field.setEnabled(False)
            QApplication.processEvents()  # 立即更新UI
            
            # 调用Agent处理
            results = self.agent_executor.process_message(message)
            
            if results and len(results) > 0:
                # 显示所有模块的响应
                for result in results:
                    if result and result.strip():
                        self.add_bot_message(result)
            else:
                self.add_bot_message("🤔 抱歉，我没能理解这个指令。请尝试其他表达方式。")
                
        except Exception as e:
            print(f"❌ 处理异常: {e}")
            self.add_system_message(f"❌ 处理错误: {e}")
        finally:
            # 恢复UI状态
            self.status_label.setText("准备就绪")
            self.input_field.setEnabled(True)
            self.input_field.setFocus()
    
    # 信号槽处理函数
    def on_message_processing_started(self, message):
        """消息开始处理"""
        print(f"📥 开始处理消息: '{message}'")
        self.status_label.setText("🤖 AI思考中...")
        self.input_field.setEnabled(False)
    
    def on_message_processing_completed(self, results):
        """消息处理完成"""
        print(f"✅ 消息处理完成，结果: {results}")
        
        if results and len(results) > 0:
            # 显示所有模块的响应
            for result in results:
                if result and result.strip():
                    self.add_bot_message(result)
        else:
            self.add_bot_message("🤔 抱歉，我没能理解这个指令。请尝试其他表达方式。")
        
        # 恢复UI状态
        self.status_label.setText("准备就绪")
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
    
    def on_message_processing_failed(self, error_msg):
        """消息处理失败"""
        print(f"❌ 消息处理失败: {error_msg}")
        self.add_system_message(f"❌ 处理错误: {error_msg}")
        
        # 恢复UI状态
        self.status_label.setText("准备就绪")
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        
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
        print("🔄 聊天窗口关闭事件被触发")
        
        # 停止通信线程
        if self.communication_thread:
            print("🛑 停止Agent通信线程...")
            self.communication_thread.stop()
            self.communication_thread = None
        
        # 停止状态检查定时器
        if hasattr(self, 'status_check_timer'):
            self.status_check_timer.stop()
        
        print("🔄 隐藏窗口")
        self.hide()  # 隐藏而不是关闭
        event.ignore()
    
    def hideEvent(self, event):
        """隐藏事件"""
        print("👁️ 聊天窗口被隐藏")
        super().hideEvent(event)
    
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
        print(f"🔍 窗口状态: visible={self.isVisible()}, minimized={self.isMinimized()}, hidden={self.isHidden()}")
    
    def check_window_status(self):
        """检查窗口状态"""
        print(f"🔍 聊天窗口状态检查:")
        print(f"   - isVisible: {self.isVisible()}")
        print(f"   - isMinimized: {self.isMinimized()}")  
        print(f"   - isHidden: {self.isHidden()}")
        print(f"   - isActiveWindow: {self.isActiveWindow()}")
        print(f"   - windowState: {self.windowState()}")
        print(f"   - geometry: {self.geometry()}")
        return self.isVisible() and not self.isMinimized() and not self.isHidden() 