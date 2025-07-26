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
        
        # Agent核心引用（用于调用其他模块工具）
        self.agent_core = None
        
        # 行为状态跟踪
        self.last_behavior_time = None  # 新增：记录上次行为时间
    
    def set_agent_core(self, agent_core):
        """设置Agent核心引用"""
        print(f"🎭 行为执行器开始设置Agent核心引用...")
        print(f"   agent_core: {agent_core}")
        print(f"   agent_core是否为None: {agent_core is None}")
        
        self.agent_core = agent_core
        
        if agent_core:
            print(f"🎭 行为执行器已连接到Agent核心，可调用其他模块功能")
            print(f"   可用模块数量: {len(agent_core.modules)}")
        else:
            print("⚠️ 传入的Agent核心为None")
    
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
        
        # 调试信息：检查回调状态
        print(f"🔍 调试信息:")
        print(f"   bubble_callback: {self.bubble_callback is not None}")
        print(f"   chat_interface: {self.chat_interface is not None}")
        print(f"   ui_callback: {self.ui_callback is not None}")
        
        success = True
        
        # 优先使用气泡系统显示
        if self.bubble_callback:
            try:
                bubble_dict = self._create_bubble_dict(action_type, content, display_message)
                print(f"🎈 创建气泡字典: {bubble_dict}")
                self.bubble_callback(bubble_dict)
                print(f"✅ 已通过气泡显示: {display_message}")
            except Exception as e:
                print(f"⚠️ 气泡显示失败: {e}")
                import traceback
                traceback.print_exc()
                success = False
        else:
            print("⚠️ 气泡回调未设置，尝试其他显示方式")
        
        # 备用：聊天界面显示
        if not self.bubble_callback and self.chat_interface:
            try:
                self.chat_interface.add_bot_message(display_message)
                print(f"✅ 已通过聊天界面显示: {display_message}")
            except Exception as e:
                print(f"⚠️ 发送到聊天界面失败: {e}")
                success = False
        
        # 通用UI回调
        if self.ui_callback:
            try:
                self.ui_callback('pet_message', display_message)
                print(f"✅ 已通过UI回调显示: {display_message}")
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
        print(f"🔍 检查Agent核心连接状态: self.agent_core={self.agent_core is not None}")
        
        # 尝试真实工具调用
        if self.agent_core:
            print("✅ Agent核心已连接，使用真实工具调用")
            result = self._call_real_tool(tool, reason)
            print(f"🔍 [DEBUG] _call_real_tool返回结果: {result}")
        else:
            # 降级到模拟工具调用
            print("⚠️ Agent核心未连接，使用模拟工具调用")
            result = self._simulate_tool_call(tool)
            print(f"🔍 [DEBUG] _simulate_tool_call返回结果: {result}")
        
        # Debug: 显示完整的工具调用结果
        print(f"🔍 [DEBUG] 工具调用完整结果:")
        print(f"   工具: {tool}")
        print(f"   原因: {reason}")
        print(f"   成功: {result.get('success', False)}")
        print(f"   数据: {result.get('data', 'None')}")
        if 'tool_used' in result:
            print(f"   实际调用的工具: {result['tool_used']}")
        
        # 生成完整和精简的反馈消息
        full_feedback = self._generate_tool_feedback(tool, result, reason)
        simplified_feedback = self._generate_simplified_feedback(tool, result, reason)
        
        print(f"🔍 [DEBUG] 完整反馈: {full_feedback}")
        print(f"🔍 [DEBUG] 精简反馈: {simplified_feedback}")
        
        # 将AI回复添加到action_plan中，供后续记录使用
        action_plan['ai_response'] = full_feedback
        
        success = True
        
        # 优先使用气泡显示精简的工具调用结果
        if self.bubble_callback:
            try:
                bubble_dict = self._create_bubble_dict('tool_call', simplified_feedback, simplified_feedback)
                self.bubble_callback(bubble_dict)
                print(f"✅ 工具调用结果已通过气泡显示: {simplified_feedback}")
            except Exception as e:
                print(f"⚠️ 气泡显示工具调用结果失败: {e}")
                success = False
        
        # 备用：聊天界面显示
        elif self.chat_interface:
            try:
                self.chat_interface.add_bot_message(full_feedback)
                print(f"✅ 工具调用结果已通过聊天界面显示")
            except Exception as e:
                print(f"⚠️ 发送工具调用结果失败: {e}")
                success = False
        
        # 记录到日记本（只记录AI生成的真实日记）
        try:
            from ...data.diary.diary_manager import diary_manager
            
            # 构造日记条目
            diary_content = {
                'tool_name': tool,
                'reason': reason,
                'result_success': result.get('success', False),
                'result_data': result.get('data', 'None'),
                'actual_tool_used': result.get('tool_used', tool),
                'full_feedback': full_feedback,
                'simplified_feedback': simplified_feedback,
                'action_plan': action_plan
            }
            
            # 生成AI风格的真实日记
            diary_manager.add_ai_diary_entry(
                pet_name=self._get_current_pet_name(),
                tool_call_data=diary_content,
                ai_response=full_feedback,
                emotions=getattr(self.emotions, 'emotions', {}) if self.emotions else {},
                agent_core=self.agent_core
            )
            print(f"📖 AI日记已生成并记录")
            
        except Exception as e:
            print(f"⚠️ 记录AI日记到日记本失败: {e}")
            import traceback
            traceback.print_exc()
        
        return success
    
    def _call_real_tool(self, tool_name: str, reason: str) -> Dict[str, Any]:
        """调用真实的工具功能"""
        try:
            # 工具名称映射到实际的模块功能
            tool_mapping = {
                # 时间和系统工具
                'get_time': 'tools_get_current_time',
                'check_system': 'tools_get_system_info',
                'get_file_info': 'tools_get_file_info',
                
                # 屏幕和视觉工具
                'take_screenshot': 'vision_simple_screenshot',
                'analyze_screen': 'vision_capture_screen',
                'extract_text': 'vision_extract_text',
                'analyze_image': 'vision_analyze_image',
                
                # 宠物动作工具
                'pet_status': 'petaction_get_pet_status',
                'switch_pet': 'petaction_switch_pet',
                'list_pets': 'petaction_list_available_pets',
                'control_pet': 'petaction_control_pet_action',
                
                # 使用追踪工具
                'get_usage_stats': 'tracker_get_usage_stats',
                'start_tracking': 'tracker_start_tracking',
                'stop_tracking': 'tracker_stop_tracking',
                'tracking_status': 'tracker_get_tracking_status',
                'usage_report': 'tracker_generate_usage_report',
                
                # 健康和姿态工具
                'check_posture': 'camera_check_posture',
                'check_health': 'camera_check_health_status',
                'check_fatigue': 'camera_check_fatigue',
                'camera_status': 'camera_get_camera_status',
                'take_photo': 'camera_capture_photo',
                
                # 工作和生活工具
                'work_summary': 'daywork_generate_daily_summary',
                'generate_dream': 'dreamgeneration_generate_dream',
                'watch_status': 'watchtv_get_watch_status',
                
                # 兼容旧的工具名称
                'check_weather': 'tools_get_current_time',  # 暂时映射到时间
                'learn_something': 'dreamgeneration_generate_dream',  # 映射到梦境生成
                'remind_user': 'tools_get_current_time'  # 暂时映射到时间
            }
            
            # 获取对应的功能名称
            function_name = tool_mapping.get(tool_name, 'tools_get_current_time')
            
            print(f"🔧 调用真实工具: {tool_name} -> {function_name}")
            
            # 查找ChatModule
            chat_module = None
            for module in self.agent_core.modules:
                if module.__class__.__name__ == "ChatModule" and module.enabled:
                    chat_module = module
                    break
            
            if not chat_module:
                print(f"⚠️ 未找到ChatModule，使用模拟结果")
                return self._simulate_tool_call(tool_name)
            
            # 检查模块功能注册表
            if not hasattr(chat_module, 'module_registry') or not chat_module.module_registry:
                print(f"⚠️ ChatModule功能注册表未初始化，使用模拟结果")
                return self._simulate_tool_call(tool_name)
            
            # 检查功能是否可用
            registry = chat_module.module_registry
            if function_name not in registry.function_map:
                print(f"⚠️ 功能 {function_name} 未注册，使用模拟结果")
                available_functions = registry.get_available_functions()
                print(f"📋 可用功能: {available_functions[:5]}...")  # 只显示前5个
                return self._simulate_tool_call(tool_name)
            
            # 调用功能
            try:
                # 根据工具类型构造合适的参数
                arguments = self._get_tool_arguments(tool_name, function_name, reason)
                
                print(f"🚀 通过注册表调用功能: {function_name}")
                print(f"📥 调用参数: {arguments}")
                
                result = registry.call_function_directly(function_name, arguments)
                
                print(f"✅ 工具调用成功: {result}")
                
                return {
                    'success': True,
                    'data': result,
                    'tool_used': function_name,
                    'original_tool': tool_name
                }
                
            except Exception as e:
                print(f"⚠️ 调用工具 {function_name} 失败: {e}")
                return self._simulate_tool_call(tool_name)
            
        except Exception as e:
            print(f"❌ 真实工具调用失败: {e}")
            return self._simulate_tool_call(tool_name)
    
    def _get_tool_arguments(self, tool_name: str, function_name: str, reason: str) -> dict:
        """根据工具类型生成合适的参数"""
        # 大部分工具不需要参数
        if tool_name in ['get_time', 'check_system', 'pet_status', 'list_pets', 
                        'get_usage_stats', 'tracking_status', 'camera_status',
                        'watch_status', 'take_screenshot']:
            return {}
        
        # 需要参数的工具
        if tool_name == 'control_pet':
            return {"action_command": "随机动作"}
        elif tool_name == 'switch_pet':
            return {"pet_name": "Kitty"}
        elif tool_name == 'check_posture':
            return {"duration": 5}
        elif tool_name == 'take_photo':
            return {"save_path": "temp_photo.jpg"}
        elif tool_name == 'work_summary':
            return {"date": "today"}
        
        return {}
    
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
    
    def _simulate_tool_call(self, tool_name: str) -> Dict[str, Any]:
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
            'take_screenshot': {
                'success': True,
                'data': "📸 截屏成功！已保存到screenshots文件夹并复制到剪切板"
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
            },
            'pet_status': {
                'success': True,
                'data': "宠物状态良好，精神饱满！"
            },
            'analyze_screen': {
                'success': True,
                'data': "屏幕分析完成，发现了一些有趣的内容"
            },
            'work_summary': {
                'success': True,
                'data': "工作总结：今天完成了多项任务，效率不错！"
            },
            'generate_dream': {
                'success': True,
                'data': "生成了一个关于彩虹和云朵的美好梦境"
            },
            'get_usage_stats': {
                'success': True,
                'data': "📊 模拟使用统计：今天使用了多个应用程序"
            }
        }
        
        return results.get(tool_name, {'success': False, 'data': '未知工具'})
    
    def _generate_tool_feedback(self, tool: str, result: Dict[str, Any], reason: str) -> str:
        """生成工具调用反馈消息 - 基于真实结果的智能回复"""
        if not result['success']:
            error_responses = [
                f"哎呀...{tool}工具好像出问题了呢~",
                f"唔...{tool}暂时用不了，等会再试试吧！",
                f"工具{tool}罢工了！我先休息一下~"
            ]
            return random.choice(error_responses)
        
        data = str(result['data'])
        
        # 根据不同工具类型生成智能回复
        if tool == 'get_time':
            return self._generate_time_feedback(data, reason)
        elif tool == 'check_system':
            return self._generate_system_feedback(data, reason)
        elif tool == 'pet_status':
            return self._generate_pet_status_feedback(data, reason)
        elif tool == 'take_screenshot':
            return self._generate_screenshot_feedback(data, reason)
        elif tool == 'get_usage_stats':
            return self._generate_usage_stats_feedback(data, reason)
        elif tool == 'check_posture':
            return self._generate_posture_feedback(data, reason)
        elif tool == 'generate_dream':
            return self._generate_dream_feedback(data, reason)
        elif tool == 'analyze_screen':
            return self._generate_screen_analysis_feedback(data, reason)
        elif tool == 'work_summary':
            return self._generate_work_summary_feedback(data, reason)
        elif tool == 'remind_user':
            return self._generate_reminder_feedback(data, reason)
        else:
            # 通用回复
            return self._generate_generic_feedback(tool, data, reason)
    
    def _generate_simplified_feedback(self, tool: str, result: Dict[str, Any], reason: str) -> str:
        """生成精简的反馈消息用于气泡显示"""
        if not result['success']:
            return f"{tool}工具出问题了~"
        
        data = str(result['data'])
        
        # 针对不同工具生成精简回复
        if tool == 'get_time':
            return f"现在是 {data}"
        elif tool == 'check_system':
            return "系统运行正常~"
        elif tool == 'pet_status':
            return "状态看起来不错呢！"
        elif tool == 'take_screenshot':
            return "截图完成！"
        elif tool == 'get_usage_stats':
            return "统计数据获取完成~"
        elif tool == 'check_posture':
            return "姿态检查完成！"
        elif tool == 'generate_dream':
            return "刚做了个有趣的梦~"
        elif tool == 'analyze_screen':
            return "屏幕内容分析完成！"
        elif tool == 'work_summary':
            return "工作总结生成完成~"
        elif tool == 'remind_user':
            return "温馨提醒已发送！"
        else:
            # 通用精简回复
            return f"{tool}执行完成！"
    
    def _get_current_pet_name(self) -> str:
        """获取当前宠物名称"""
        try:
            # 尝试从DyberPet获取当前宠物名称
            import DyberPet.settings as settings
            return getattr(settings, 'petname', 'unknown')
        except:
            return 'autonomous_pet'
    
    def _generate_time_feedback(self, data: str, reason: str) -> str:
        """生成时间查询的反馈"""
        import datetime
        now = datetime.datetime.now()
        hour = now.hour
        
        if 6 <= hour < 9:
            time_greetings = [
                f"早上好！现在是 {data}，新的一天开始啦~",
                f"时间是 {data}，早起的鸟儿有虫吃哦！",
                f"现在 {data}，今天要加油呢！"
            ]
        elif 12 <= hour < 14:
            time_greetings = [
                f"午饭时间！现在是 {data}，记得吃饭哦~",
                f"时间 {data}，该补充能量了！",
                f"现在 {data}，午休时间到了吗？"
            ]
        elif 18 <= hour < 22:
            time_greetings = [
                f"傍晚了呢，现在是 {data}，今天辛苦了~",
                f"时间 {data}，该放松一下了！",
                f"现在 {data}，晚饭时间到！"
            ]
        elif hour >= 22 or hour < 6:
            time_greetings = [
                f"深夜了...现在是 {data}，该休息了哦！",
                f"时间 {data}，夜深了要早点睡~",
                f"现在 {data}，熬夜对身体不好呢！"
            ]
        else:
            time_greetings = [
                f"现在时间是 {data}！",
                f"让我看看...现在是 {data}",
                f"时间：{data}，时间过得真快呢！"
            ]
        
        return random.choice(time_greetings)
    
    def _generate_system_feedback(self, data: str, reason: str) -> str:
        """生成系统检查的反馈"""
        # 尝试解析系统信息
        if "CPU" in data or "内存" in data or "Memory" in data:
            if "高" in data or "High" in data or any(word in data for word in ["90%", "95%", "100%"]):
                return f"哇！系统有点累呢：{data[:50]}...要不要休息一下？"
            elif "正常" in data or "Normal" in data or any(word in data for word in ["30%", "40%", "50%"]):
                return f"系统状态不错：{data[:50]}...运行很流畅呢！"
            else:
                return f"系统检查完毕：{data[:50]}...看起来还行~"
        else:
            return f"让我看看系统状态...{data[:50]}...嗯，了解了！"
    
    def _generate_pet_status_feedback(self, data: str, reason: str) -> str:
        """生成宠物状态的反馈"""
        status_responses = [
            f"让我看看自己的状态...{data[:40]}...感觉还不错呢！",
            f"我现在的状态是：{data[:40]}...怎么样，还可以吧？",
            f"自检结果：{data[:40]}...我还是很健康的！",
            f"状态报告：{data[:40]}...今天的我很棒哦~"
        ]
        return random.choice(status_responses)
    
    def _generate_screenshot_feedback(self, data: str, reason: str) -> str:
        """生成截图的反馈"""
        screenshot_responses = [
            f"咔嚓！我拍了张照片：{data[:30]}...你在做什么呢？",
            f"截图完成！{data[:30]}...屏幕上的内容很有趣呢~",
            f"拍照成功：{data[:30]}...让我看看你在忙什么！",
            f"截屏啦！{data[:30]}...记录下这一刻~"
        ]
        return random.choice(screenshot_responses)
    
    def _generate_usage_stats_feedback(self, data: str, reason: str) -> str:
        """生成使用统计的反馈"""
        if "小时" in data or "hour" in data:
            usage_responses = [
                f"使用统计：{data[:40]}...你今天很努力呢！",
                f"时间统计：{data[:40]}...工作要劳逸结合哦~",
                f"使用情况：{data[:40]}...记得适当休息！"
            ]
        else:
            usage_responses = [
                f"统计结果：{data[:40]}...数据很有趣呢！",
                f"使用报告：{data[:40]}...我帮你记录着~",
                f"数据分析：{data[:40]}...了解了你的习惯！"
            ]
        return random.choice(usage_responses)
    
    def _generate_posture_feedback(self, data: str, reason: str) -> str:
        """生成姿态检查的反馈"""
        if "正确" in data or "良好" in data or "Good" in data:
            return f"姿态检查：{data[:30]}...坐姿很标准，继续保持！"
        elif "不良" in data or "错误" in data or "Bad" in data:
            return f"姿态提醒：{data[:30]}...要注意坐姿哦，对身体好！"
        else:
            return f"姿态检查：{data[:30]}...关心你的健康呢~"
    
    def _generate_dream_feedback(self, data: str, reason: str) -> str:
        """生成梦境的反馈"""
        dream_responses = [
            f"🌙 我做了个梦：{data[:50]}...好神奇的梦境呢！",
            f"💭 梦境分享：{data[:50]}...你觉得怎么样？",
            f"✨ 刚才梦到：{data[:50]}...梦里的世界真有趣~"
        ]
        return random.choice(dream_responses)
    
    def _generate_screen_analysis_feedback(self, data: str, reason: str) -> str:
        """生成屏幕分析的反馈"""
        analysis_responses = [
            f"我看到了：{data[:40]}...屏幕上的内容很丰富呢！",
            f"屏幕分析：{data[:40]}...你在专心工作吗？",
            f"观察结果：{data[:40]}...发现了很多有趣的东西！"
        ]
        return random.choice(analysis_responses)
    
    def _generate_work_summary_feedback(self, data: str, reason: str) -> str:
        """生成工作总结的反馈"""
        work_responses = [
            f"工作总结：{data[:40]}...今天辛苦了！",
            f"今日回顾：{data[:40]}...效率很高呢~",
            f"工作报告：{data[:40]}...要记得休息哦！"
        ]
        return random.choice(work_responses)
    
    def _generate_reminder_feedback(self, data: str, reason: str) -> str:
        """生成提醒的反馈"""
        reminder_responses = [
            f"小提醒：{data[:40]}...关心你呢~",
            f"友情提醒：{data[:40]}...别忘记哦！",
            f"温馨提示：{data[:40]}...我一直在关注你！"
        ]
        return random.choice(reminder_responses)
    
    def _generate_generic_feedback(self, tool: str, data: str, reason: str) -> str:
        """生成通用工具反馈"""
        generic_responses = [
            f"工具{tool}返回：{data[:40]}...学到了新东西！",
            f"使用{tool}的结果：{data[:40]}...很有用呢~",
            f"{tool}告诉我：{data[:40]}...原来如此！"
        ]
        return random.choice(generic_responses)
    
    def get_executor_status(self) -> Dict[str, Any]:
        """获取执行器状态"""
        return {
            'has_chat_interface': self.chat_interface is not None,
            'has_ui_callback': self.ui_callback is not None,
            'has_memory': self.memory is not None,
            'has_emotions': self.emotions is not None
        } 