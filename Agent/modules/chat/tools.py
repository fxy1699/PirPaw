"""
Chat模块的自定义工具集
让Qwen-Agent能够调用其他模块的功能
"""

import json
from typing import Dict, Any, Optional


class DyberPetTools:
    """DyberPet专用工具集，供Qwen-Agent调用"""
    
    def __init__(self, agent_core=None):
        self.agent_core = agent_core
        self.tools = []
        self._register_tools()
    
    def _register_tools(self):
        """注册所有可用工具"""
        self.tools = [
            {
                'name': 'check_time',
                'description': '获取当前时间和日期信息',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_weather',
                'description': '获取指定城市的天气信息',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'city': {
                            'type': 'string',
                            'description': '城市名称，如"北京"、"上海"等'
                        }
                    },
                    'required': ['city']
                }
            },
            {
                'name': 'check_system_status',
                'description': '检查系统性能状态，包括CPU、内存使用情况',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'detail_level': {
                            'type': 'string',
                            'enum': ['basic', 'detailed'],
                            'description': '详细程度：basic为基础信息，detailed为详细信息'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'capture_screen',
                'description': '截取用户屏幕并分析内容，可以理解当前显示的信息',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'analysis_type': {
                            'type': 'string',
                            'enum': ['general', 'code', 'document', 'error'],
                            'description': '分析类型：general通用分析，code代码分析，document文档分析，error错误诊断'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'check_posture',
                'description': '检查用户当前坐姿和健康状态',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'get_app_usage',
                'description': '获取应用使用时长统计信息',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'period': {
                            'type': 'string',
                            'enum': ['today', 'week', 'month'],
                            'description': '统计周期：today今天，week本周，month本月'
                        }
                    },
                    'required': []
                }
            },
            {
                'name': 'start_app_tracking',
                'description': '开始应用使用时长追踪',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'stop_app_tracking',
                'description': '停止应用使用时长追踪',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        ]
    
    def get_function_list(self):
        """返回符合Qwen-Agent格式的工具函数列表"""
        # 创建具体的工具函数，避免闭包问题
        functions = []
        
        # 时间工具
        def check_time():
            """获取当前时间和日期信息"""
            return self._call_time_tool()
        
        # 天气工具  
        def get_weather(city: str = "北京"):
            """获取指定城市的天气信息"""
            return self._call_weather_tool(city)
        
        # 系统监控工具
        def check_system_status(detail_level: str = "basic"):
            """检查系统性能状态，包括CPU、内存使用情况"""
            return self._call_system_tool(detail_level)
        
        # 屏幕分析工具
        def capture_screen(analysis_type: str = "general"):
            """截取用户屏幕并分析内容，可以理解当前显示的信息"""
            return self._call_vision_tool(analysis_type)
        
        # 姿态检测工具
        def check_posture():
            """检查用户当前坐姿和健康状态"""
            return self._call_camera_tool()
        
        # 应用使用统计工具
        def get_app_usage(period: str = "today"):
            """获取应用使用时长统计信息"""
            return self._call_tracker_tool(period)
        
        # 开始追踪工具
        def start_app_tracking():
            """开始应用使用时长追踪"""
            return self._call_tracker_start()
        
        # 停止追踪工具
        def stop_app_tracking():
            """停止应用使用时长追踪"""
            return self._call_tracker_stop()
        
        functions = [
            check_time,
            get_weather, 
            check_system_status,
            capture_screen,
            check_posture,
            get_app_usage,
            start_app_tracking,
            stop_app_tracking
        ]
        
        return functions
    
    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """执行函数调用"""
        if not self.agent_core:
            return "❌ Agent核心未初始化"
        
        try:
            if function_name == 'check_time':
                return self._call_time_tool()
            
            elif function_name == 'get_weather':
                city = arguments.get('city', '北京')
                return self._call_weather_tool(city)
            
            elif function_name == 'check_system_status':
                detail_level = arguments.get('detail_level', 'basic')
                return self._call_system_tool(detail_level)
            
            elif function_name == 'capture_screen':
                analysis_type = arguments.get('analysis_type', 'general')
                return self._call_vision_tool(analysis_type)
            
            elif function_name == 'check_posture':
                return self._call_camera_tool()
            
            elif function_name == 'get_app_usage':
                period = arguments.get('period', 'today')
                return self._call_tracker_tool(period)
            
            elif function_name == 'start_app_tracking':
                return self._call_tracker_start()
            
            elif function_name == 'stop_app_tracking':
                return self._call_tracker_stop()
            
            else:
                return f"❌ 未知的函数: {function_name}"
                
        except Exception as e:
            return f"❌ 执行函数 {function_name} 失败: {e}"
    
    def _call_time_tool(self) -> str:
        """调用时间工具"""
        responses = self.agent_core.process_message("现在几点了")
        return responses[0] if responses else "获取时间失败"
    
    def _call_weather_tool(self, city: str) -> str:
        """调用天气工具"""
        responses = self.agent_core.process_message(f"{city}的天气怎么样")
        return responses[0] if responses else f"获取{city}天气失败"
    
    def _call_system_tool(self, detail_level: str) -> str:
        """调用系统监控工具"""
        if detail_level == 'detailed':
            message = "系统CPU内存磁盘详细信息"
        else:
            message = "系统性能如何"
        
        responses = self.agent_core.process_message(message)
        return responses[0] if responses else "获取系统信息失败"
    
    def _call_vision_tool(self, analysis_type: str) -> str:
        """调用视觉分析工具"""
        if analysis_type == 'code':
            message = "看屏幕分析代码"
        elif analysis_type == 'document':
            message = "看屏幕分析文档"
        elif analysis_type == 'error':
            message = "看屏幕分析错误"
        else:
            message = "看一下我的屏幕"
        
        responses = self.agent_core.process_message(message)
        return responses[0] if responses else "屏幕分析失败"
    
    def _call_camera_tool(self) -> str:
        """调用摄像头姿态检测"""
        responses = self.agent_core.process_message("检查我的坐姿")
        return responses[0] if responses else "姿态检测失败"
    
    def _call_tracker_tool(self, period: str) -> str:
        """调用应用追踪工具"""
        if period == 'week':
            message = "本周使用时长统计"
        elif period == 'month':
            message = "本月应用统计"
        else:
            message = "今天使用情况"
        
        responses = self.agent_core.process_message(message)
        return responses[0] if responses else "获取使用统计失败"
    
    def _call_tracker_start(self) -> str:
        """启动应用追踪"""
        responses = self.agent_core.process_message("启动应用追踪")
        return responses[0] if responses else "启动追踪失败"
    
    def _call_tracker_stop(self) -> str:
        """停止应用追踪"""
        responses = self.agent_core.process_message("停止应用追踪")
        return responses[0] if responses else "停止追踪失败" 