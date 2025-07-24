from Agent.base_module import BaseModule
import time
import json
import os
import sys
import threading
from datetime import datetime, timedelta


class TrackerModule(BaseModule):
    """应用使用时长追踪模块 - 跨平台应用使用统计"""

    name = "使用追踪"
    description = "跨平台应用使用时长统计和分析，支持Windows和macOS"
    version = "1.0.0"
    author = "开发者E"

    def __init__(self):
        super().__init__()
        self.tracker = None
        self.tracking_active = False
        self.tracking_thread = None

    def setup(self, config=None):
        """初始化追踪功能"""
        super().setup(config)

        try:
            # 初始化应用追踪器
            data_file = self.config.get('data_file', 'data/app_usage.json')
            interval = self.config.get('tracking_interval', 5)
            
            # 确保data目录存在
            data_dir = os.path.dirname(data_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"📁 创建数据目录: {data_dir}")
            
            self.tracker = CrossPlatformAppTracker(
                interval=interval,
                data_file=data_file
            )
            
            print(f"✅ {self.name} 初始化成功，支持{self.tracker.os_type}系统")
            
            # 如果配置了自动启动，则开始追踪
            if self.config.get('auto_start', False):
                self.start_background_tracking()

        except Exception as e:
            print(f"❌ {self.name} 初始化失败: {e}")
            self.enabled = False

    def handle_message(self, message, context=None):
        """处理追踪相关请求"""
        if not self.enabled:
            return None

        # 判断是否是追踪相关请求
        tracker_keywords = ['使用时长', '应用统计', '追踪', '时间统计', '使用情况', '应用时间', '统计报告']
        if not any(keyword in message for keyword in tracker_keywords):
            return None

        try:
            if any(keyword in message for keyword in ['开始', '启动', '开启']):
                return self.start_tracking_command()
            elif any(keyword in message for keyword in ['停止', '结束', '关闭']):
                return self.stop_tracking_command()
            elif any(keyword in message for keyword in ['报告', '统计', '查看', '显示']):
                return self.generate_report_command(message)
            elif any(keyword in message for keyword in ['状态', '是否在']):
                return self.get_tracking_status()
            else:
                return self.get_usage_overview()

        except Exception as e:
            print(f"❌ 追踪处理失败: {e}")
            return f"📊 应用追踪遇到问题: {str(e)}"

    def start_tracking_command(self):
        """启动应用追踪"""
        if self.tracking_active:
            return "📊 应用使用追踪已经在运行中"
        
        try:
            self.start_background_tracking()
            return "📊 应用使用追踪已启动，正在后台记录您的应用使用情况"
        except Exception as e:
            return f"📊 启动追踪失败: {e}"

    def stop_tracking_command(self):
        """停止应用追踪"""
        if not self.tracking_active:
            return "📊 应用追踪未在运行"
        
        try:
            self.stop_background_tracking()
            return "📊 应用使用追踪已停止，数据已保存"
        except Exception as e:
            return f"📊 停止追踪失败: {e}"

    def generate_report_command(self, message):
        """生成使用报告"""
        if not self.tracker:
            return "📊 追踪器未初始化"

        try:
            # 解析请求的日期范围
            if '今天' in message:
                days = 1
            elif '本周' in message or '一周' in message:
                days = 7
            elif '本月' in message:
                days = 30
            else:
                days = 1  # 默认今天

            return self.get_usage_report(days)

        except Exception as e:
            return f"📊 生成报告失败: {e}"

    def get_tracking_status(self):
        """获取追踪状态"""
        status = "📊 应用追踪状态:\n"
        status += f"• 追踪状态: {'运行中' if self.tracking_active else '已停止'}\n"
        status += f"• 支持系统: {self.tracker.os_type if self.tracker else '未知'}\n"
        status += f"• 检查间隔: {self.config.get('tracking_interval', 5)}秒\n"
        
        if self.tracker and self.tracker.current_app:
            status += f"• 当前应用: {self.tracker.current_app}"
        
        return status

    def get_usage_overview(self):
        """获取使用概览"""
        if not self.tracker:
            return "📊 追踪器未初始化，请先启动追踪功能"

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            usage_data = self.tracker.load_data()
            
            if today not in usage_data:
                return "📊 今天还没有使用数据，请先启动追踪功能"

            today_data = usage_data[today]
            total_seconds = sum(app_data["total_seconds"] for app_data in today_data.values())
            
            if total_seconds == 0:
                return "📊 今天还没有记录到应用使用时间"

            # 获取使用时间最长的前3个应用
            sorted_apps = sorted(today_data.items(), 
                               key=lambda x: x[1]["total_seconds"], 
                               reverse=True)[:3]

            overview = f"📊 今天应用使用概览:\n"
            overview += f"• 总使用时间: {str(timedelta(seconds=int(total_seconds)))}\n"
            overview += f"• 主要应用:\n"
            
            for app, data in sorted_apps:
                duration = str(timedelta(seconds=int(data["total_seconds"])))
                overview += f"  - {app}: {duration}\n"

            return overview

        except Exception as e:
            return f"📊 获取概览失败: {e}"

    def get_usage_report(self, days=1):
        """获取详细使用报告"""
        if not self.tracker:
            return "📊 追踪器未初始化"

        try:
            usage_data = self.tracker.load_data()
            report = f"📊 最近{days}天应用使用报告:\n\n"

            # 获取指定天数的数据
            target_dates = []
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                target_dates.append(date)

            total_time_all_days = 0
            for date in target_dates:
                if date in usage_data:
                    day_data = usage_data[date]
                    day_total = sum(app_data["total_seconds"] for app_data in day_data.values())
                    total_time_all_days += day_total
                    
                    if day_total > 0:
                        report += f"📅 {date}:\n"
                        report += f"  总时长: {str(timedelta(seconds=int(day_total)))}\n"
                        
                        # 显示前5个应用
                        sorted_apps = sorted(day_data.items(), 
                                           key=lambda x: x[1]["total_seconds"], 
                                           reverse=True)[:5]
                        
                        for app, data in sorted_apps:
                            duration = str(timedelta(seconds=int(data["total_seconds"])))
                            report += f"  • {app}: {duration}\n"
                        report += "\n"

            if total_time_all_days > 0:
                report += f"📈 {days}天总计: {str(timedelta(seconds=int(total_time_all_days)))}\n"
                avg_per_day = total_time_all_days / days
                report += f"📊 日均使用: {str(timedelta(seconds=int(avg_per_day)))}"
            else:
                report = f"📊 最近{days}天没有使用数据"

            return report

        except Exception as e:
            return f"📊 生成报告失败: {e}"

    def start_background_tracking(self):
        """在后台线程中启动追踪"""
        if self.tracking_active:
            return

        self.tracking_active = True
        self.tracking_thread = threading.Thread(target=self._background_tracking_loop, daemon=True)
        self.tracking_thread.start()

    def stop_background_tracking(self):
        """停止后台追踪"""
        self.tracking_active = False
        if self.tracking_thread and self.tracking_thread.is_alive():
            self.tracking_thread.join(timeout=2)
        
        # 保存最后的数据
        if self.tracker and self.tracker.current_app and self.tracker.current_start_time:
            duration = (datetime.now() - self.tracker.current_start_time).total_seconds()
            self.tracker.track_usage(duration)

    def _background_tracking_loop(self):
        """后台追踪循环"""
        try:
            while self.tracking_active:
                if self.tracker:
                    app, window = self.tracker.get_active_application()
                    
                    if app and (app != self.tracker.current_app or window != self.tracker.current_window):
                        # 记录上一个应用的使用时间
                        if self.tracker.current_app and self.tracker.current_start_time:
                            duration = (datetime.now() - self.tracker.current_start_time).total_seconds()
                            self.tracker.track_usage(duration)
                        
                        # 更新当前应用
                        self.tracker.current_app = app
                        self.tracker.current_window = window
                        self.tracker.current_start_time = datetime.now()
                
                time.sleep(self.tracker.interval)
                
        except Exception as e:
            print(f"❌ 后台追踪出错: {e}")
            self.tracking_active = False

    def get_capabilities(self):
        """返回模块能力"""
        capabilities = [
            "应用使用时长统计",
            "跨平台支持(Windows/macOS)",
            "实时后台追踪",
            "使用报告生成",
            "应用切换监控"
        ]

        if self.config.get('auto_start'):
            capabilities.append("自动启动追踪")

        return capabilities

    def cleanup(self):
        """清理资源"""
        if self.tracking_active:
            self.stop_background_tracking()
        super().cleanup()

    # ============ Function Call 接口 ============
    
    def get_function_definitions(self) -> list:
        """获取Tracker模块的Function Call工具定义"""
        return [
            {
                "name": "get_usage_stats",
                "description": "获取应用使用时长统计信息，可以查看今天、本周或本月的使用情况",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["today", "week", "month"],
                            "description": "统计周期：today今天，week本周，month本月"
                        },
                        "detail_level": {
                            "type": "string",
                            "enum": ["summary", "detailed"],
                            "description": "详细程度：summary概要信息，detailed详细信息"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "start_tracking",
                "description": "开始应用使用时长追踪",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "stop_tracking", 
                "description": "停止应用使用时长追踪",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_tracking_status",
                "description": "获取当前追踪状态和实时信息",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "generate_usage_report",
                "description": "生成详细的使用报告，包含分析和建议",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "报告天数，默认1天",
                            "minimum": 1,
                            "maximum": 30
                        }
                    },
                    "required": []
                }
            }
        ]
    
    def call_function(self, function_name: str, arguments: dict):
        """调用Tracker模块的具体功能"""
        if not self.enabled:
            raise RuntimeError(f"模块 {self.name} 已禁用")
        
        if function_name == "get_usage_stats":
            return self._function_get_usage_stats(arguments)
        elif function_name == "start_tracking":
            return self._function_start_tracking(arguments)
        elif function_name == "stop_tracking":
            return self._function_stop_tracking(arguments)
        elif function_name == "get_tracking_status":
            return self._function_get_tracking_status(arguments)
        elif function_name == "generate_usage_report":
            return self._function_generate_usage_report(arguments)
        else:
            raise ValueError(f"未知功能: {function_name}")
    
    def _function_get_usage_stats(self, arguments: dict):
        """Function Call: 获取使用统计"""
        period = arguments.get("period", "today")
        detail_level = arguments.get("detail_level", "summary")
        
        if period == "today":
            if detail_level == "summary":
                return self.get_usage_overview()
            else:
                return self.get_usage_report(days=1)
        elif period == "week":
            return self.get_usage_report(days=7)
        elif period == "month":
            return self.get_usage_report(days=30)
        else:
            return self.get_usage_overview()
    
    def _function_start_tracking(self, arguments: dict):
        """Function Call: 开始追踪"""
        if self.tracking_active:
            return "⚠️ 追踪已经在运行中"
        
        self.start_background_tracking()
        return "✅ 已开始应用使用追踪"
    
    def _function_stop_tracking(self, arguments: dict):
        """Function Call: 停止追踪"""
        if not self.tracking_active:
            return "⚠️ 追踪未在运行"
        
        self.stop_background_tracking()
        return "✅ 已停止应用使用追踪"
    
    def _function_get_tracking_status(self, arguments: dict):
        """Function Call: 获取追踪状态"""
        status = self.get_tracking_status()
        return f"📊 追踪状态:\n{status}"
    
    def _function_generate_usage_report(self, arguments: dict):
        """Function Call: 生成使用报告"""
        days = arguments.get("days", 1)
        report = self.get_usage_report(days=days)
        return f"📈 {days}天使用报告:\n{report}"


class CrossPlatformAppTracker:
    """从test.py移植过来的跨平台应用追踪器"""
    
    def __init__(self, interval=5, data_file="app_usage.json"):
        self.interval = interval
        self.data_file = data_file
        self.usage_data = self.load_data()
        self.current_app = None
        self.current_window = None
        self.current_start_time = None
        self.os_type = self.detect_os()
        
        self.initialize_os_specifics()

    def detect_os(self):
        """检测当前操作系统"""
        if sys.platform.startswith('win32'):
            return "windows"
        elif sys.platform.startswith('darwin'):
            return "macos"
        else:
            raise Exception(f"不支持的操作系统: {sys.platform}")

    def initialize_os_specifics(self):
        """初始化特定于操作系统的组件"""
        if self.os_type == "windows":
            try:
                global win32gui, ctypes
                import win32gui
                import ctypes
                ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            except ImportError:
                raise Exception("Windows版本需要pywin32库，请先安装: pip install pywin32")

    def load_data(self):
        """加载已保存的使用数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_data(self):
        """保存使用数据到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage_data, f, indent=2, ensure_ascii=False)

    def get_active_application(self):
        """根据操作系统获取当前活跃的应用程序和窗口"""
        if self.os_type == "windows":
            return self._windows_get_active_app()
        elif self.os_type == "macos":
            return self._macos_get_active_app()

    def _windows_get_active_app(self):
        """Windows系统获取当前活跃应用和窗口"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            app_name = "Unknown"
            if window_title:
                if "-" in window_title:
                    app_name = window_title.split("-")[-1].strip()
                elif "|" in window_title:
                    app_name = window_title.split("|")[-1].strip()
                elif "—" in window_title:
                    app_name = window_title.split("—")[-1].strip()
                else:
                    app_name = window_title
            
            return app_name, window_title
            
        except Exception as e:
            return None, None

    def _macos_get_active_app(self):
        """macOS系统获取当前活跃应用和窗口"""
        try:
            import subprocess
            
            app_script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            return frontApp
            '''
            app_name = subprocess.check_output(
                ['osascript', '-e', app_script], 
                text=True
            ).strip()
            
            window_script = '''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set windowTitle to name of first window of frontApp
            end tell
            return windowTitle
            '''
            try:
                window_title = subprocess.check_output(
                    ['osascript', '-e', window_script], 
                    text=True
                ).strip()
            except:
                window_title = "Unknown Window"
                
            return app_name, window_title
            
        except Exception as e:
            return None, None

    def track_usage(self, duration):
        """记录应用使用时间"""
        if not self.current_app:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.usage_data:
            self.usage_data[today] = {}
        if self.current_app not in self.usage_data[today]:
            self.usage_data[today][self.current_app] = {
                "total_seconds": 0,
                "windows": {}
            }
        
        self.usage_data[today][self.current_app]["total_seconds"] += duration
        
        window_key = self.current_window or "Unknown Window"
        if window_key not in self.usage_data[today][self.current_app]["windows"]:
            self.usage_data[today][self.current_app]["windows"][window_key] = 0
        self.usage_data[today][self.current_app]["windows"][window_key] += duration
        
        self.save_data() 