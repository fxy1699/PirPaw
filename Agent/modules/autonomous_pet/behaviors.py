"""
行为执行器 - 将决策转化为实际行动
"""

import random
from datetime import datetime
from typing import Dict, Any, Optional


class BehaviorExecutor:
    """行为执行器 - 负责执行大脑决定的行为"""
    
    def __init__(self, memory_manager, emotion_system):
        self.memory = memory_manager
        self.emotions = emotion_system
        
        # UI接口
        self.chat_interface = None
        self.ui_callback = None
        self.bubble_callback = None  # 新增：气泡接口
        
        # 行为状态跟踪
        self.last_behavior_time = None  # 新增：记录上次行为时间
        
    def set_chat_interface(self, chat_interface):
        """设置聊天界面接口"""
        self.chat_interface = chat_interface
    
    def set_ui_callback(self, callback):
        """设置UI回调函数"""
        self.ui_callback = callback
    
    def set_bubble_callback(self, bubble_callback):
        """设置气泡回调函数"""
        self.bubble_callback = bubble_callback
    
    def execute_behavior(self, action_plan: Dict[str, Any]) -> bool:
        """执行行为计划"""
        try:
            # 记录行为执行时间
            self.last_behavior_time = datetime.now()
            
            action_type = action_plan['action_type']
            
            print(f"🎭 执行行为: {action_type}")
            
            if action_type == 'tool_call':
                return self._execute_tool_call(action_plan)
            else:
                return self._execute_social_behavior(action_plan)
                
        except Exception as e:
            print(f"❌ 行为执行失败: {e}")
            return False
    
    def _execute_social_behavior(self, action_plan: Dict[str, Any]) -> bool:
        """执行社交行为（自言自语、寻求关注等）"""
        content = action_plan.get('content', '...')
        action_type = action_plan['action_type']
        
        # 构造显示消息
        display_message = self._format_behavior_message(action_type, content)
        
        # 输出到控制台（总是执行）
        print(f"🐱 宠物说: {display_message}")
        
        success = True
        
        # 优先使用气泡系统显示
        if self.bubble_callback:
            try:
                bubble_dict = self._create_bubble_dict(action_type, content, display_message)
                self.bubble_callback(bubble_dict)
                print(f"✅ 已通过气泡显示: {display_message}")
            except Exception as e:
                print(f"⚠️ 气泡显示失败: {e}")
                success = False
        
        # 备用：聊天界面显示
        elif self.chat_interface:
            try:
                self.chat_interface.add_bot_message(display_message)
            except Exception as e:
                print(f"⚠️ 发送到聊天界面失败: {e}")
                success = False
        
        # 通用UI回调
        if self.ui_callback:
            try:
                self.ui_callback('pet_message', display_message)
            except Exception as e:
                print(f"⚠️ UI回调失败: {e}")
        
        # 记录行为
        if self.memory:
            self.memory.save_behavior(
                behavior_type='proactive',
                action_name=action_type,
                trigger_reason=f"自主决策: {action_plan.get('reason', '情感驱动')}",
                success=success
            )
        
        return success
    
    def _execute_tool_call(self, action_plan: Dict[str, Any]) -> bool:
        """执行工具调用行为"""
        tool = action_plan.get('tool', 'unknown')
        reason = action_plan.get('reason', '好奇心驱动')
        
        print(f"🔧 宠物想要使用工具: {tool} (原因: {reason})")
        
        # 模拟工具调用结果
        result = self._simulate_tool_call(tool)
        
        # 生成反馈消息
        feedback = self._generate_tool_feedback(tool, result, reason)
        
        # 显示反馈
        print(f"🐱 宠物说: {feedback}")
        
        success = True
        
        # 优先使用气泡显示工具调用结果
        if self.bubble_callback:
            try:
                bubble_dict = {
                    'message': feedback,
                    'bubble_type': f'autonomous_tool_{tool}',
                    'icon': 'system',
                    'start_audio': 'system',
                    'end_audio': None
                }
                self.bubble_callback(bubble_dict)
                print(f"✅ 工具调用结果已通过气泡显示")
            except Exception as e:
                print(f"⚠️ 气泡显示工具调用结果失败: {e}")
                success = False
        
        # 备用：聊天界面显示
        elif self.chat_interface:
            try:
                self.chat_interface.add_bot_message(feedback)
            except Exception as e:
                print(f"⚠️ 发送工具调用结果失败: {e}")
                success = False
        
        # 记录工具调用
        if self.memory:
            self.memory.save_interaction(
                interaction_type='tool_call',
                content=f"使用工具: {tool}",
                response=feedback,
                success=success
            )
        
        return success
    
    def _format_behavior_message(self, action_type: str, content: str) -> str:
        """格式化行为消息"""
        prefixes = {
            'seek_attention': '🙋‍♀️ ',
            'self_talk': '💭 ',
            'greet': '👋 ',
            'care': '🤗 ',
            'explore': '🔍 ',
            'rest': '😴 ',
            'play': '🎮 '
        }
        
        prefix = prefixes.get(action_type, '🐱 ')
        return f"{prefix}{content}"
    
    def _create_bubble_dict(self, action_type: str, content: str, display_message: str) -> Dict[str, Any]:
        """创建气泡数据字典，支持长文本自动分割和播放"""
        # 根据行为类型选择图标和音效
        icon_mapping = {
            'seek_attention': 'system',
            'self_talk': None,
            'greet': 'system', 
            'care': 'system',
            'explore': 'system',
            'rest': None,
            'play': 'system'
        }
        
        audio_mapping = {
            'seek_attention': 'system',
            'greet': 'system',
            'care': 'system',
            'play': 'system'
        }
        
        # 处理长文本：如果超过15个字符，需要分割
        max_length = 15
        
        if len(content) <= max_length:
            # 短文本，直接显示
            bubble_dict = {
                'message': content,
                'bubble_type': f'autonomous_{action_type}',
                'icon': icon_mapping.get(action_type),
                'start_audio': audio_mapping.get(action_type),
                'end_audio': None
            }
        else:
            # 长文本，需要分割成多个气泡自动播放
            text_segments = self._split_text_for_bubbles(content, max_length)
            
            # 创建第一个气泡（立即显示）
            bubble_dict = {
                'message': text_segments[0],
                'bubble_type': f'autonomous_{action_type}',
                'icon': icon_mapping.get(action_type),
                'start_audio': audio_mapping.get(action_type),
                'end_audio': None,
                # 添加自动播放信息
                'auto_play': True,
                'segments': text_segments[1:],  # 剩余的文本段
                'segment_delay': 2000,  # 每段间隔2秒
                'current_segment': 0
            }
        
        return bubble_dict
    
    def _split_text_for_bubbles(self, text: str, max_length: int) -> list:
        """将长文本智能分割为适合气泡显示的短段"""
        if len(text) <= max_length:
            return [text]
        
        segments = []
        current_segment = ""
        
        # 优先按标点符号分割
        punctuation = ['。', '！', '？', '，', '；', '：', '、']
        
        i = 0
        while i < len(text):
            char = text[i]
            current_segment += char
            
            # 如果遇到标点符号且长度合适，结束当前段
            if char in punctuation and len(current_segment) <= max_length:
                segments.append(current_segment.strip())
                current_segment = ""
            # 如果长度达到上限，强制分割
            elif len(current_segment) >= max_length:
                # 尝试在合适的位置分割（避免分割单词）
                if current_segment[-1] in punctuation:
                    segments.append(current_segment.strip())
                    current_segment = ""
                else:
                    # 回退到最近的标点符号或空格
                    split_pos = max_length
                    for j in range(len(current_segment) - 1, max(0, len(current_segment) - 5), -1):
                        if current_segment[j] in punctuation + [' ', '　']:
                            split_pos = j + 1
                            break
                    
                    segments.append(current_segment[:split_pos].strip())
                    current_segment = current_segment[split_pos:]
            
            i += 1
        
        # 添加剩余部分
        if current_segment.strip():
            segments.append(current_segment.strip())
        
        # 确保每段都不超过最大长度
        final_segments = []
        for segment in segments:
            if len(segment) <= max_length:
                final_segments.append(segment)
            else:
                # 强制按长度分割
                for k in range(0, len(segment), max_length):
                    final_segments.append(segment[k:k + max_length])
        
        return final_segments
    
    def _simulate_tool_call(self, tool: str) -> Dict[str, Any]:
        """模拟工具调用（简单版本）"""
        results = {
            'check_weather': {
                'success': True,
                'data': f"今天{random.choice(['晴天', '多云', '小雨', '阴天'])}，温度{random.randint(15, 30)}°C"
            },
            'get_time': {
                'success': True,
                'data': datetime.now().strftime("%H:%M")
            },
            'learn_something': {
                'success': True,
                'data': random.choice([
                    "学到了：猫咪一天要睡14-16小时",
                    "学到了：Python是一种很受欢迎的编程语言",
                    "学到了：地球上有超过70%的面积被海洋覆盖",
                    "学到了：人类的大脑约有860亿个神经元"
                ])
            },
            'remind_user': {
                'success': True,
                'data': "提醒：记得定期休息，保护眼睛哦！"
            },
            'check_system': {
                'success': True,
                'data': f"系统运行正常，当前时间 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
        }
        
        return results.get(tool, {'success': False, 'data': '未知工具'})
    
    def _generate_tool_feedback(self, tool: str, result: Dict[str, Any], reason: str) -> str:
        """生成工具调用反馈消息"""
        if not result['success']:
            return f"呜...{tool}工具好像用不了了。"
        
        data = result['data']
        
        feedback_templates = {
            'check_weather': [
                f"我查了下天气：{data}！",
                f"今天的天气是：{data}呢~",
                f"天气情况：{data}，记得适当添衣哦！"
            ],
            'get_time': [
                f"现在时间是 {data}！",
                f"让我看看...现在是 {data}",
                f"时间：{data}，时间过得真快呢！"
            ],
            'learn_something': [
                f"我刚刚{data}！好有趣～",
                f"学习时间！{data}",
                f"又涨知识了：{data}"
            ],
            'remind_user': [
                f"小提醒：{data}",
                f"关心你一下：{data}",
                f"友情提醒：{data}"
            ],
            'check_system': [
                f"系统检查结果：{data}",
                f"让我看看系统状态...{data}",
                f"检查完毕：{data}"
            ]
        }
        
        templates = feedback_templates.get(tool, [f"工具 {tool} 返回：{data}"])
        return random.choice(templates)
    
    def get_executor_status(self) -> Dict[str, Any]:
        """获取执行器状态"""
        return {
            'has_chat_interface': self.chat_interface is not None,
            'has_ui_callback': self.ui_callback is not None,
            'has_memory': self.memory is not None,
            'has_emotions': self.emotions is not None
        } 