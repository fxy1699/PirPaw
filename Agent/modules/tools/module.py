from Agent.base_module import BaseModule
import datetime
import os
import platform
import psutil


class ToolsModule(BaseModule):
    """系统工具模块 - 提供各种实用工具功能"""
    
    name = "系统工具"
    description = "提供时间查询、天气信息、系统监控等实用工具"
    version = "1.0.0"
    author = "开发者D"
    
    def __init__(self):
        super().__init__()
        self.enabled_tools = []
        
    def setup(self, config=None):
        """初始化工具模块"""
        super().setup(config)
        
        try:
            # 获取启用的工具列表
            self.enabled_tools = self.config.get('enabled_tools', [
                'time', 'weather', 'system_info', 'file_operations'
            ])
            
            print(f"✅ {self.name} 初始化成功，启用工具: {', '.join(self.enabled_tools)}")
            
        except Exception as e:
            print(f"❌ {self.name} 初始化失败: {e}")
            self.enabled = False
    
    def handle_message(self, message, context=None):
        """处理工具相关请求"""
        if not self.enabled:
            return None
        
        # 时间相关
        if any(keyword in message for keyword in ['时间', '几点', '现在', '日期']):
            if 'time' in self.enabled_tools:
                return self.get_current_time()
        
        # 天气相关 - 已迁移到Chat模块（高德天气API）
        # elif any(keyword in message for keyword in ['天气', '温度', '下雨', '晴天']):
        #     if 'weather' in self.enabled_tools:
        #         return self.get_weather_info(message)
        
        # 系统信息
        elif any(keyword in message for keyword in ['系统', 'CPU', '内存', '磁盘', '性能']):
            if 'system_info' in self.enabled_tools:
                return self.get_system_info(message)
        
        # 文件操作
        elif any(keyword in message for keyword in ['文件', '文档', '打开', '查找']):
            if 'file_operations' in self.enabled_tools:
                return self.handle_file_operations(message)
        
        return None
    
    def get_current_time(self):
        """获取当前时间"""
        try:
            now = datetime.datetime.now()
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][now.weekday()]
            
            time_str = f"⏰ 现在时间: {now.strftime('%Y年%m月%d日')} {weekday} {now.strftime('%H:%M:%S')}"
            
            # 添加一些额外信息
            if now.hour < 6:
                time_str += "\n🌙 深夜了，注意休息"
            elif now.hour < 12:
                time_str += "\n🌅 上午好！"
            elif now.hour < 18:
                time_str += "\n☀️ 下午好！"
            else:
                time_str += "\n🌆 晚上好！"
                
            return time_str
            
        except Exception as e:
            return f"⏰ 获取时间失败: {e}"
    
    def get_weather_info(self, message):
        """获取天气信息 - 提示用户使用Chat模块的天气功能"""
        try:
            # 从消息中提取城市名
            city = self.config.get('default_city', '北京')
            cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '西安', '武汉']
            for c in cities:
                if c in message:
                    city = c
                    break
            
            # 提示用户使用更准确的天气功能
            weather_info = f"🌤️ {city}天气查询:\n"
            weather_info += "💡 为了获取最准确的天气信息，建议您:\n"
            weather_info += "• 使用Chat模块询问天气（如: '北京天气怎么样？'）\n"
            weather_info += "• Chat模块已集成高德天气API，提供实时准确数据\n"
            weather_info += "\n🔄 工具模块将保留基础功能，Chat模块提供增强体验"
            
            return weather_info
            
        except Exception as e:
            return f"🌤️ 天气查询失败: {e}"
    
    def get_system_info(self, message):
        """获取系统信息"""
        try:
            info = "💻 系统信息:\n"
            
            # 基本系统信息
            if '系统' in message:
                info += f"• 操作系统: {platform.system()} {platform.release()}\n"
                info += f"• 处理器: {platform.processor()}\n"
            
            # CPU信息
            if 'CPU' in message or '处理器' in message:
                cpu_percent = psutil.cpu_percent(interval=1)
                info += f"• CPU使用率: {cpu_percent}%\n"
                info += f"• CPU核心数: {psutil.cpu_count()}\n"
            
            # 内存信息
            if '内存' in message:
                memory = psutil.virtual_memory()
                memory_gb = memory.total / (1024**3)
                memory_used_gb = memory.used / (1024**3)
                info += f"• 内存: {memory_used_gb:.1f}GB / {memory_gb:.1f}GB ({memory.percent}%)\n"
            
            # 磁盘信息
            if '磁盘' in message:
                disk = psutil.disk_usage('/')
                disk_total_gb = disk.total / (1024**3)
                disk_used_gb = disk.used / (1024**3)
                info += f"• 磁盘: {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB ({disk.percent:.1f}%)\n"
            
            # 如果没有指定具体信息，显示概览
            if info == "💻 系统信息:\n":
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                info += f"• CPU: {cpu_percent}%\n"
                info += f"• 内存: {memory.percent}%\n"
                info += f"• 系统: {platform.system()}"
            
            return info
            
        except Exception as e:
            return f"💻 获取系统信息失败: {e}"
    
    def handle_file_operations(self, message):
        """处理文件操作"""
        try:
            if '打开' in message:
                return self.open_file_dialog(message)
            elif '查找' in message:
                return self.search_files(message)
            else:
                return self.get_file_info()
                
        except Exception as e:
            return f"📁 文件操作失败: {e}"
    
    def open_file_dialog(self, message):
        """打开文件对话框（模拟）"""
        return "📁 文件操作功能:\n• 可以通过右键菜单访问文件管理功能\n• 支持快速打开常用文件夹\n• 支持文件搜索和管理"
    
    def search_files(self, message):
        """搜索文件"""
        return "🔍 文件搜索功能:\n• 支持按文件名搜索\n• 支持按文件类型筛选\n• 支持按修改时间排序\n💡 具体搜索功能请使用系统文件管理器"
    
    def get_file_info(self):
        """获取文件信息"""
        try:
            home_dir = os.path.expanduser("~")
            desktop_dir = os.path.join(home_dir, "Desktop")
            
            info = "📁 常用文件夹:\n"
            if os.path.exists(desktop_dir):
                desktop_files = len([f for f in os.listdir(desktop_dir) 
                                   if os.path.isfile(os.path.join(desktop_dir, f))])
                info += f"• 桌面: {desktop_files} 个文件\n"
            
            info += f"• 用户目录: {home_dir}\n"
            info += "💡 可以通过具体指令管理文件"
            
            return info
            
        except Exception as e:
            return f"📁 文件信息获取失败: {e}"
    
    def get_capabilities(self):
        """返回工具能力"""
        capabilities = []
        
        if 'time' in self.enabled_tools:
            capabilities.extend(["时间查询", "日期信息"])
        
        if 'weather' in self.enabled_tools:
            capabilities.extend(["天气查询", "温度信息"])
        
        if 'system_info' in self.enabled_tools:
            capabilities.extend(["系统监控", "性能查看", "硬件信息"])
        
        if 'file_operations' in self.enabled_tools:
            capabilities.extend(["文件管理", "文件搜索"])
            
        return capabilities
    
    def cleanup(self):
        """清理资源"""
        self.enabled_tools.clear()
        super().cleanup() 