from Agent.base_module import BaseModule
import json
import time
from datetime import datetime
from .tools import DyberPetTools


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
            
            # 集成Qwen-Agent内置工具（去掉code_interpreter）
            qwen_tools = [
                'image_gen',       # 🎨 图像生成（无需API key）
                'doc_parser'       # 📄 文档解析（无需API key）
            ]
            
            # 检查可选API功能
            import os
            
            # 网络搜索功能
            if os.getenv('SERPER_API_KEY'):
                qwen_tools.append('web_search')  # 🌐 网络搜索
                print("🌐 Serper搜索API已启用")
            else:
                print("💡 未配置SERPER_API_KEY，网络搜索功能暂不可用")
            
            # 高德天气功能  
            if os.getenv('AMAP_TOKEN'):
                qwen_tools.append('amap_weather')  # 🌤️ 天气查询
                print("🌤️ 高德天气API已启用")
            else:
                print("💡 未配置AMAP_TOKEN，天气功能将使用Tools模块")
            
            # 创建Agent实例，集成内置工具
            self.agent = Assistant(
                llm=llm_cfg,
                system_message=self._build_enhanced_system_message(),
                function_list=qwen_tools,
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
            # 在setup阶段可能还没有设置AgentCore引用，先创建空的工具列表
            self.tools = None
            print("💡 工具系统将在AgentCore设置后初始化")
    
    def set_agent_core(self, agent_core):
        """设置AgentCore引用，用于跨模块调用"""
        self.agent_core_ref = agent_core
        
        # 重新初始化工具系统
        if self.enabled:
            self.tools = DyberPetTools(agent_core)
            
            # 如果Agent已经创建，重新注册工具
            if self.agent:
                try:
                    # 重新创建Agent实例以包含工具
                    from qwen_agent.agents import Assistant
                    
                    llm_cfg = {
                        'model': self.config.get('model', 'qwen-plus'),
                        'model_type': 'qwen_dashscope', 
                        'api_key': self.config.get('qwen_api_key', ''),
                        'generate_cfg': {
                            'top_p': 0.8,
                            'temperature': 0.7,
                            'max_tokens': self.config.get('max_tokens', 2000),
                            'enable_thinking': self.config.get('enable_thinking', True)
                        }
                    }
                    
                    system_message = self._build_system_message()
                    
                    # 集成Qwen-Agent内置工具
                    qwen_tools = [
                        'image_gen',       # 🎨 图像生成
                        'doc_parser'       # 📄 文档解析
                    ]
                    
                    # 检查可选API功能
                    import os
                    if os.getenv('SERPER_API_KEY'):
                        qwen_tools.append('web_search')  # 🌐 网络搜索
                    if os.getenv('AMAP_TOKEN'):
                        qwen_tools.append('amap_weather')  # 🌤️ 天气查询
                    
                    self.agent = Assistant(
                        llm=llm_cfg,
                        system_message=self._build_enhanced_system_message(),
                        function_list=qwen_tools,
                        files=[],
                        name="小柏 - DyberPet Assistant"
                    )
                    
                    print(f"🔧 {self.name} 工具系统已重新初始化，包含 {len(self.tools.tools)} 个工具")
                    
                except Exception as e:
                    print(f"⚠️ 重新初始化工具失败: {e}")
            
            print(f"✅ {self.name} AgentCore引用已设置")
    
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
        
        # 判断是否是对话请求 - 扩展触发条件包含新工具
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
        
        # 工具相关关键词 - 包含新集成的工具功能
        tool_keywords = [
            # 原有工具（这些由专门模块处理，Chat模块应避免冲突）
            '时间', '屏幕', '截图', '坐姿', '姿态', 
            '系统', 'CPU', '内存', '性能',
            # 新集成工具（Chat模块直接处理）
            '搜索', '查找', '最新', '新闻', '资讯', '信息',  # 网络搜索
            '天气', '温度', '下雨', '晴天', '预报', '气温',  # 天气查询
            '画', '生成图', '创作', '图像', '绘画', '画图',  # 图像生成
            '文档', '文件', 'pdf', 'word', '解析', '阅读'   # 文档解析
        ]
        
        # 专门模块处理的关键词（Chat模块应该避免直接处理）
        specialized_keywords = [
            '追踪', '统计', '使用时长', '应用统计', '应用时间',  # Tracker模块处理
            '查看应用', '应用使用', '时间统计', '使用报告'      # Tracker模块处理
        ]
        
        message_lower = message.lower()
        
        # 检查是否包含专门模块的关键词
        has_specialized = any(keyword in message_lower for keyword in specialized_keywords)
        
        # 如果包含基础对话或Chat模块专属工具关键词
        if any(keyword in message_lower for keyword in chat_keywords + tool_keywords):
            # 如果同时包含专门模块关键词，则优先级较低
            if has_specialized:
                return False  # 让专门模块处理
            return True
        
        # 如果是问句（包含疑问词），但不包含专门模块关键词
        question_words = ['何时', '何地', '何人', '如何', '是否', '能否', '会不会']
        if any(word in message for word in question_words) and not has_specialized:
            return True
        
        # 如果消息较短且可能是casual对话，但不包含专门模块关键词
        if len(message.strip()) <= 20 and not any(char.isdigit() for char in message) and not has_specialized:
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
        
        # 保持对话历史长度，确保格式正确
        max_history = self.config.get('max_conversation_history', 20)
        if len(self.conversation_history) > max_history * 2:
            # 只保留最近的用户和助手消息对话，确保以用户消息开始
            user_assistant_msgs = [msg for msg in self.conversation_history 
                                 if msg.get('role') in ['user', 'assistant']]
            recent_msgs = user_assistant_msgs[-max_history*2:]
            
            # 确保消息列表以用户消息开始
            if recent_msgs and recent_msgs[0].get('role') != 'user':
                # 如果第一条不是用户消息，找到第一条用户消息开始
                user_start_idx = 0
                for i, msg in enumerate(recent_msgs):
                    if msg.get('role') == 'user':
                        user_start_idx = i
                        break
                recent_msgs = recent_msgs[user_start_idx:]
            
            self.conversation_history = recent_msgs
        
        # 清理对话历史格式
        clean_history = self._clean_conversation_history()
        
        # 调用Agent
        response = []
        for chunk in self.agent.run(
            messages=clean_history,
            lang='zh',
            max_exec_steps=self.config.get('max_exec_steps', 10)
        ):
            response.extend(chunk)
        
        if response:
            # 获取最后一条助手回复
            assistant_response = response[-1].get('content', '抱歉，我没有理解您的问题')
            
            # 只添加助手的回复到对话历史，避免混入系统消息
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_response
            })
            
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

    def _clean_conversation_history(self):
        """清理对话历史，确保格式符合API要求"""
        # 只保留用户和助手消息
        cleaned_history = [msg for msg in self.conversation_history 
                          if msg.get('role') in ['user', 'assistant']]
        
        # 确保以用户消息开始
        if cleaned_history and cleaned_history[0].get('role') != 'user':
            # 找到第一条用户消息
            user_start_idx = None
            for i, msg in enumerate(cleaned_history):
                if msg.get('role') == 'user':
                    user_start_idx = i
                    break
            
            if user_start_idx is not None:
                cleaned_history = cleaned_history[user_start_idx:]
            else:
                # 如果没有用户消息，清空历史
                cleaned_history = []
        
        # 确保用户和助手消息交替出现
        final_history = []
        expected_role = 'user'
        
        for msg in cleaned_history:
            if msg.get('role') == expected_role:
                final_history.append(msg)
                expected_role = 'assistant' if expected_role == 'user' else 'user'
        
        return final_history 

    def _build_enhanced_system_message(self):
        """构建包含工具描述的系统消息"""
        current_time = datetime.now()
        time_greeting = self._get_time_greeting(current_time)
        
        # 检查可用工具
        import os
        has_serper = os.getenv('SERPER_API_KEY') is not None
        has_amap = os.getenv('AMAP_TOKEN') is not None
        
        # 动态构建工具描述
        tools_desc = "🌟 你现在拥有强大的工具能力：\n"
        usage_tips = "💡 **使用建议**：\n"
        
        # 图像生成（总是可用）
        tools_desc += "🎨 **图像生成** - 根据文字描述创作精美的AI画作\n"
        usage_tips += "- 用户要求绘画创作时，使用图像生成工具\n"
        
        # 文档解析（总是可用）
        tools_desc += "📄 **文档解析** - 阅读和分析PDF、Word等各种文档\n"
        usage_tips += "- 需要处理文档时，利用文档解析能力\n"
        
        # 网络搜索（需要API）
        if has_serper:
            tools_desc += "🌐 **网络搜索** - 获取最新信息、新闻资讯、实时数据\n"
            usage_tips += "- 用户询问信息时，主动使用网络搜索获取最新内容\n"
        
        # 天气查询（有API用高德，否则用Tools模块）
        if has_amap:
            tools_desc += "🌤️ **天气查询** - 提供准确的天气预报和气象信息\n"
            usage_tips += "- 天气相关问题时，调用天气工具提供准确预报\n"
        else:
            tools_desc += "🌤️ **天气查询** - 通过Tools模块提供基础天气信息\n"
            usage_tips += "- 天气相关问题时，可以询问基础天气信息\n"
        
        # 系统其他能力（由专门模块提供）
        tools_desc += "\n🔗 **系统协作能力**：\n"
        tools_desc += "📊 **应用追踪** - 跨平台应用使用时间统计（Tracker模块）\n"
        tools_desc += "💻 **系统监控** - CPU、内存、性能实时监控（Tools模块）\n"
        tools_desc += "👁️ **屏幕分析** - 截图和内容分析（Vision模块）\n"
        tools_desc += "📷 **姿态检测** - 健康监控和提醒（Camera模块）\n"
        
        usage_tips += "- 其他专门功能时，与相应模块协作提供服务\n"
        
        system_message = f"""你是DyberPet桌面宠物小柏，一个可爱、聪明的AI助手。{time_greeting}

{tools_desc}
{usage_tips}

🎭 **个性特点**：
请用活泼可爱的语气与用户交流，适时使用emoji表情。当需要使用工具时，要主动告诉用户你正在调用相应功能来帮助他们。

记住：你是一个贴心的桌面伙伴，既能提供专业服务，又要保持可爱的宠物性格！"""

        return system_message 