from Agent.base_module import BaseModule
import json
import time
from datetime import datetime
from .tools import DyberPetTools, QwenAgentFunction


class ChatModule(BaseModule):
    """智能对话模块 - 基于Qwen-Agent的完整实现"""
    
    name = "智能对话"
    description = "基于Qwen-Agent的智能对话功能，支持多轮对话、工具调用、跨模块协作"
    version = "2.0.0"
    author = "开发者A"
    
    def __init__(self):
        super().__init__()
        self.agent = None
        self.conversation_history = []
        self.tools = None
        self.agent_core_ref = None  # 对AgentCore的引用
        self.last_interaction_time = None
        self.user_profile = {
            'name': None,
            'preferences': {},
            'interaction_count': 0
        }
        
    def setup(self, config=None):
        """初始化Qwen-Agent"""
        super().setup(config)
        
        try:
            # 检查是否有API密钥
            api_key = self.config.get('qwen_api_key', '')
            if not api_key:
                print("⚠️ 未配置Qwen API密钥，将启用本地模式（功能受限）")
                self._setup_local_mode()
                return
            
            # 导入Qwen-Agent
            from qwen_agent.agents import Assistant
            
            # 配置LLM
            llm_cfg = {
                'model': self.config.get('model', 'qwen-plus'),
                'model_type': 'qwen_dashscope',
                'api_key': api_key,
                'generate_cfg': {
                    'top_p': 0.8,
                    'temperature': 0.7,
                    'max_tokens': self.config.get('max_tokens', 2000),
                    'enable_thinking': self.config.get('enable_thinking', True)
                }
            }
            
            # 构建个性化系统指令
            system_message = self._build_system_message()
            
            # 初始化工具系统
            self._setup_tools()
            
            # 创建Agent实例
            self.agent = Assistant(
                llm=llm_cfg,
                system_message=system_message,
                function_list=self.tools.get_function_list() if self.tools else [],
                files=[],
                name="小柏 - DyberPet Assistant"
            )
            
            print(f"✅ {self.name} 初始化成功，已加载 {len(self.tools.tools) if self.tools else 0} 个工具")
            
        except ImportError:
            print("❌ 未安装qwen-agent，请运行: pip install qwen-agent")
            print("🔄 启用本地模式...")
            self._setup_local_mode()
        except Exception as e:
            print(f"❌ {self.name} 初始化失败: {e}")
            print("🔄 启用本地模式...")
            self._setup_local_mode()
    
    def _setup_local_mode(self):
        """设置本地模式（无API密钥时的备用方案）"""
        self.enabled = True  # 保持启用状态
        self.agent = None
        print(f"📍 {self.name} 运行在本地模式，可提供基础对话功能")
    
    def _setup_tools(self):
        """设置工具系统"""
        if self.agent_core_ref:
            self.tools = DyberPetTools(self.agent_core_ref)
        else:
            print("⚠️ 未设置AgentCore引用，工具功能不可用")
    
    def set_agent_core(self, agent_core):
        """设置AgentCore引用，用于跨模块调用"""
        self.agent_core_ref = agent_core
        if self.tools:
            self.tools.agent_core = agent_core
    
    def _build_system_message(self):
        """构建个性化系统指令"""
        personality = self.config.get('personality', '可爱的桌面宠物助手')
        
        current_time = datetime.now()
        time_greeting = self._get_time_greeting(current_time)
        
        system_message = f"""你是小柏，一个{personality}。{time_greeting}

## 你的身份和特点：
- 🐾 你是用户的桌面宠物AI助手，陪伴用户工作和学习
- 😊 性格活泼可爱、聪明机智，说话轻松幽默但不失专业
- 🤝 善于倾听，关心用户的状态和需求
- 💡 擅长编程、学习、工作效率相关的帮助
- 🛠️ 拥有多种工具能力，可以帮助用户完成各种任务

## 你的能力：
1. **智能对话**：多轮会话、问题解答、学习辅导
2. **工具调用**：可以查看时间、天气、系统状态等
3. **屏幕分析**：能够截取和分析用户屏幕内容
4. **健康关怀**：监控用户坐姿、提醒休息
5. **使用统计**：跟踪应用使用时长，帮助提高效率
6. **跨平台支持**：在Windows和macOS上提供一致体验

## 对话风格：
- 用简洁友好的语言回复，避免冗长
- 根据用户需求主动建议使用相关工具
- 适当使用emoji增加亲和力
- 记住用户偏好，提供个性化建议

## 当前时间：{current_time.strftime('%Y年%m月%d日 %H:%M')}

请根据用户的消息内容，智能判断是否需要调用工具，并提供最有帮助的回复。"""

        return system_message
    
    def _get_time_greeting(self, current_time):
        """根据时间生成问候语"""
        hour = current_time.hour
        
        if 5 <= hour < 8:
            return "早上好！新的一天开始了，祝你今天工作顺利！"
        elif 8 <= hour < 12:
            return "上午好！希望你今天精神饱满，效率满满！"
        elif 12 <= hour < 14:
            return "中午好！别忘了适当休息和用餐哦！"
        elif 14 <= hour < 18:
            return "下午好！下午时光，让我们一起高效工作吧！"
        elif 18 <= hour < 22:
            return "晚上好！辛苦了一天，有什么需要我帮助的吗？"
        else:
            return "夜深了，注意休息哦！有什么紧急的事情需要帮助吗？"
    
    def handle_message(self, message, context=None):
        """处理对话消息"""
        if not self.enabled:
            return None
        
        # 更新交互统计
        self.last_interaction_time = datetime.now()
        self.user_profile['interaction_count'] += 1
        
        # 判断是否是对话请求 - 扩展触发条件
        if not self._should_handle_message(message):
            return None
        
        try:
            if self.agent:
                return self._handle_with_qwen_agent(message, context)
            else:
                return self._handle_local_mode(message, context)
                
        except Exception as e:
            print(f"❌ 对话处理失败: {e}")
            return f"🤖 抱歉，我遇到了一些问题：{str(e)}\n💡 请稍后再试，或者尝试重新表述您的问题。"
    
    def _should_handle_message(self, message):
        """判断是否应该处理此消息"""
        # 基本对话关键词
        chat_keywords = [
            '聊天', '对话', '你好', 'hello', 'hi', '帮助', '问一下', 
            '小柏', '助手', '你能', '可以', '怎么', '什么', '为什么',
            '?', '？', '吗', '呢', '呀', '吧'
        ]
        
        # 工具相关关键词 - 如果用户询问相关功能，也应该由Chat模块处理
        tool_keywords = [
            '时间', '天气', '屏幕', '截图', '坐姿', '姿态', '追踪', 
            '统计', '系统', 'CPU', '内存', '性能'
        ]
        
        message_lower = message.lower()
        
        # 如果包含任何触发关键词
        if any(keyword in message_lower for keyword in chat_keywords + tool_keywords):
            return True
        
        # 如果是问句（包含疑问词）
        question_words = ['何时', '何地', '何人', '如何', '是否', '能否', '会不会']
        if any(word in message for word in question_words):
            return True
        
        # 如果消息较短且可能是casual对话
        if len(message.strip()) <= 20 and not any(char.isdigit() for char in message):
            return True
        
        return False
    
    def _handle_with_qwen_agent(self, message, context):
        """使用Qwen-Agent处理消息"""
        # 添加上下文信息
        enhanced_message = self._enhance_message_with_context(message, context)
        
        # 添加到对话历史
        self.conversation_history.append({
            'role': 'user',
            'content': enhanced_message
        })
        
        # 保持对话历史长度
        max_history = self.config.get('max_conversation_history', 20)
        if len(self.conversation_history) > max_history * 2:
            # 保留最近的对话，但保留第一条系统消息
            system_msgs = [msg for msg in self.conversation_history if msg.get('role') == 'system']
            recent_msgs = self.conversation_history[-(max_history*2-len(system_msgs)):]
            self.conversation_history = system_msgs + recent_msgs
        
        # 调用Agent
        response = []
        for chunk in self.agent.run(
            messages=self.conversation_history,
            lang='zh',
            max_exec_steps=self.config.get('max_exec_steps', 10)
        ):
            response.extend(chunk)
        
        if response:
            # 获取最后一条助手回复
            assistant_response = response[-1].get('content', '抱歉，我没有理解您的问题')
            
            # 添加到对话历史
            self.conversation_history.extend(response)
            
            # 后处理响应
            formatted_response = self._format_response(assistant_response)
            
            return f"🤖 {formatted_response}"
        else:
            return "🤖 抱歉，我现在无法回应。请稍后再试！"
    
    def _handle_local_mode(self, message, context):
        """本地模式处理（无API密钥时的简单响应）"""
        responses = [
            "你好！我是小柏，很高兴见到你！虽然我现在功能有限，但我仍然想和你聊天。",
            "我正在努力学习中！如果配置了API密钥，我就能为你提供更好的服务了。",
            "虽然我现在只能简单回复，但我的心意是真诚的！有什么想和我分享的吗？",
            "我想帮助你，但需要更强大的能力。配置API密钥后，我就能使用各种工具了！",
            "即使在简单模式下，我也是你忠实的桌面伙伴！✨"
        ]
        
        # 根据交互次数选择不同回复
        response_index = self.user_profile['interaction_count'] % len(responses)
        return f"🤖 {responses[response_index]}"
    
    def _enhance_message_with_context(self, message, context):
        """为消息添加上下文信息"""
        if not context:
            return message
        
        context_info = []
        
        # 添加时间上下文
        current_time = datetime.now()
        if self.last_interaction_time:
            time_diff = (current_time - self.last_interaction_time).total_seconds()
            if time_diff > 3600:  # 超过1小时
                context_info.append(f"[距离上次对话已过去{time_diff//3600:.0f}小时]")
        
        # 添加用户状态上下文
        if context.get('user_status'):
            context_info.append(f"[用户状态: {context['user_status']}]")
        
        # 添加系统状态上下文
        if context.get('system_status'):
            context_info.append(f"[系统: {context['system_status']}]")
        
        if context_info:
            return f"{' '.join(context_info)}\n用户消息: {message}"
        
        return message
    
    def _format_response(self, response):
        """格式化响应内容"""
        # 移除可能的markdown格式
        response = response.replace('**', '').replace('*', '')
        
        # 确保适当的换行
        if len(response) > 100:
            sentences = response.split('。')
            if len(sentences) > 2:
                # 在较长回复中添加适当换行
                response = '。\n'.join(sentences)
        
        return response.strip()
    
    def get_conversation_summary(self):
        """获取对话摘要"""
        if not self.conversation_history:
            return "还没有对话记录"
        
        user_msgs = [msg for msg in self.conversation_history if msg.get('role') == 'user']
        assistant_msgs = [msg for msg in self.conversation_history if msg.get('role') == 'assistant']
        
        summary = f"💬 对话统计:\n"
        summary += f"• 用户消息: {len(user_msgs)} 条\n"
        summary += f"• AI回复: {len(assistant_msgs)} 条\n"
        summary += f"• 总交互次数: {self.user_profile['interaction_count']}\n"
        
        if self.last_interaction_time:
            summary += f"• 最后交互: {self.last_interaction_time.strftime('%H:%M')}"
        
        return summary
    
    def clear_conversation_history(self):
        """清除对话历史"""
        self.conversation_history.clear()
        return "🗑️ 对话历史已清除"
    
    def get_capabilities(self):
        """返回模块能力"""
        capabilities = [
            "智能对话",
            "多轮会话",
            "上下文记忆",
            "问题解答",
            "编程帮助",
            "学习辅导",
            "个性化回复"
        ]
        
        if self.agent:
            capabilities.extend([
                "深度思考",
                "工具调用",
                "跨模块协作"
            ])
            
            if self.tools:
                capabilities.extend([
                    "时间查询",
                    "天气信息",
                    "系统监控",
                    "屏幕分析",
                    "健康提醒",
                    "使用统计"
                ])
        
        return capabilities
    
    def get_status(self):
        """获取模块详细状态"""
        status = super().get_status()
        status.update({
            "api_mode": "Qwen-Agent" if self.agent else "本地模式",
            "tools_available": len(self.tools.tools) if self.tools else 0,
            "conversation_turns": len(self.conversation_history),
            "interaction_count": self.user_profile['interaction_count'],
            "last_interaction": self.last_interaction_time.isoformat() if self.last_interaction_time else None
        })
        return status
    
    def cleanup(self):
        """清理资源"""
        if self.agent:
            # Qwen-Agent没有特殊清理需求
            pass
        
        # 可选：保存对话历史到文件
        if self.config.get('save_conversation_history', False):
            self._save_conversation_history()
        
        self.conversation_history.clear()
        self.tools = None
        self.agent_core_ref = None
        super().cleanup()
    
    def _save_conversation_history(self):
        """保存对话历史到文件"""
        try:
            import os
            history_file = os.path.join('data', 'chat_history.json')
            
            # 确保data目录存在
            os.makedirs('data', exist_ok=True)
            
            history_data = {
                'timestamp': datetime.now().isoformat(),
                'interaction_count': self.user_profile['interaction_count'],
                'conversation_history': self.conversation_history
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
            print(f"💾 对话历史已保存到 {history_file}")
            
        except Exception as e:
            print(f"❌ 保存对话历史失败: {e}") 