from Agent.base_module import BaseModule
import json
import time
from datetime import datetime
from .tools import DyberPetTools
from .module_function_registry import ModuleFunctionRegistry
import copy


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
        self.module_registry = None
        self.agent_core_ref = None  # 对AgentCore的引用
        self.last_interaction_time = None
        self.user_profile = {
            'name': None,
            'preferences': {},
            'interaction_count': 0
        }
        self.using_local_mode = False
        self._function_calls_available = False
        
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
            
            # 确保API密钥设置到环境变量中（qwen-agent需要）
            import os
            os.environ['DASHSCOPE_API_KEY'] = api_key
            print(f"🔑 已设置DASHSCOPE_API_KEY环境变量")
            
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
            
            # 初始化模块功能注册系统
            self._setup_module_functions()
            
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
            
            # 暂时只使用qwen内置工具创建Agent，模块功能稍后集成
            all_tools = qwen_tools

            # 注释掉可能引起问题的MCP配置
            # all_tools.append({
            #     "mcpServers": {
            #         "RedNote MCP": {
            #             "command": "npx",
            #             "args": [
            #                 "rednote-mcp",
            #                 "--stdio"
            #             ]
            #         }
            #     }
            # })
            
            # 创建Agent实例，集成所有工具
            self.agent = Assistant(
                llm=llm_cfg,
                system_message=self._build_enhanced_system_message(),
                function_list=all_tools,
                files=[],
                name="小柏 - DyberPet Assistant"
            )
            
            print(f"✅ {self.name} 初始化成功，已加载 {len(self.tools.tools) if self.tools else 0} 个工具")
            
        except ImportError as e:
            print(f"❌ 导入qwen-agent失败: {e}")
            print("🔄 启用本地模式...")
            self._setup_local_mode()
        except Exception as e:
            print(f"❌ {self.name} 初始化失败: {e}")
            print(f"🔍 异常类型: {type(e).__name__}")
            import traceback
            print(f"🔍 详细错误信息:")
            traceback.print_exc()
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
                    
                    # 集成模块Function Call工具
                    module_functions = []
                    if self.module_registry:
                        try:
                            module_tools = self.module_registry.get_function_list_for_qwen_agent()
                            module_functions.extend(module_tools)
                            print(f"🔗 重新初始化时集成了 {len(module_tools)} 个模块功能")
                        except Exception as e:
                            print(f"⚠️ 重新初始化时集成模块功能失败: {e}")
                    
                    # 合并所有工具
                    all_tools = qwen_tools + module_functions
                    
                    self.agent = Assistant(
                        llm=llm_cfg,
                        system_message=self._build_enhanced_system_message(),
                        function_list=all_tools,
                        files=[],
                        name="小柏 - DyberPet Assistant"
                    )
                    
                    print(f"🔧 {self.name} 工具系统已重新初始化，包含 {len(self.tools.tools)} 个工具")
                    
                except Exception as e:
                    print(f"⚠️ 重新初始化工具失败: {e}")
        
        # 初始化或更新模块注册系统
        if not self.module_registry:
            try:
                self.module_registry = ModuleFunctionRegistry(agent_core)
                print(f"🔧 模块功能注册系统已初始化")
            except Exception as e:
                print(f"❌ 模块功能注册系统初始化失败: {e}")
        else:
            self.module_registry.agent_core = agent_core
            
        print(f"✅ {self.name} AgentCore引用已设置")
    
    def _setup_module_functions(self):
        """初始化模块功能注册系统"""
        try:
            # 如果AgentCore引用还没设置，先创建空的注册系统
            self.module_registry = ModuleFunctionRegistry(self.agent_core_ref)
            print(f"🔧 模块功能注册系统初始化成功")
        except Exception as e:
            print(f"❌ 模块功能注册系统初始化失败: {e}")
            # 创建空的注册系统，等待AgentCore引用设置后再初始化
            self.module_registry = None
    
    def register_all_modules(self, modules):
        """注册所有模块的功能到Function Call系统"""
        if not self.module_registry:
            return
        
        try:
            # 过滤掉Chat模块自身，避免循环调用
            filtered_modules = [m for m in modules if not isinstance(m, ChatModule)]
            self.module_registry.register_modules(filtered_modules)
            
            print(f"🔗 已注册 {len(filtered_modules)} 个模块功能到智能对话系统")
            
            # 重新集成Function Call功能到qwen-agent
            self._integrate_function_calls()
            
        except Exception as e:
            print(f"❌ 模块功能注册失败: {e}")
    
    def _integrate_function_calls(self):
        """将Function Call功能集成到qwen-agent"""
        if not self.agent or not self.module_registry:
            return
        
        try:
            # 暂时简化：不重新创建Agent，而是在现有基础上添加Function Call支持
            # 设置标志表示Function Call可用
            self._function_calls_available = True
            
            # 获取模块功能数量用于显示
            available_functions = self.module_registry.get_available_functions()
            print(f"✅ Function Call系统已就绪，包含 {len(available_functions)} 个模块功能")
            
        except Exception as e:
            print(f"❌ Function Call系统设置失败: {e}")
            self._function_calls_available = False
    
    def _try_function_call(self, message):
        """尝试将消息匹配到Function Call"""
        if not self.module_registry:
            return None
        
        message_lower = message.lower()
        
        # 应用使用时长相关
        if any(word in message_lower for word in ['应用', '使用时长', '时间统计', '应用统计', '使用情况']):
            try:
                print(f"📊 Function Call: 获取应用使用统计")
                result = self.module_registry.call_function_directly(
                    "tracker_get_usage_stats", 
                    {"period": "today", "detail_level": "summary"}
                )
                return f"📊 应用使用统计:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 宠物动作相关
        if any(word in message_lower for word in ['睡觉', '走路', '跳舞', '站立', '动作', '小猫', '宠物']):
            try:
                print(f"🐾 Function Call: 控制宠物动作")
                result = self.module_registry.call_function_directly(
                    "petaction_control_pet_action", 
                    {"action_command": message}
                )
                return f"🐾 宠物动作:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 宠物状态查询
        if any(word in message_lower for word in ['状态', '现在的', '当前', '宠物信息']):
            try:
                print(f"📋 Function Call: 获取宠物状态")
                result = self.module_registry.call_function_directly(
                    "petaction_get_pet_status", {}
                )
                return f"📋 宠物状态:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 屏幕截图相关
        if any(word in message_lower for word in ['截图', '屏幕', '看看', '分析界面']):
            try:
                print(f"📷 Function Call: 截取屏幕")
                result = self.module_registry.call_function_directly(
                    "vision_capture_screen", 
                    {"analysis_type": "general"}
                )
                return f"📷 屏幕分析:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 追踪控制
        if any(word in message_lower for word in ['开始追踪', '启动追踪']):
            try:
                print(f"▶️ Function Call: 开始追踪")
                result = self.module_registry.call_function_directly(
                    "tracker_start_tracking", {}
                )
                return f"▶️ {result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        if any(word in message_lower for word in ['停止追踪', '结束追踪']):
            try:
                print(f"⏹️ Function Call: 停止追踪")
                result = self.module_registry.call_function_directly(
                    "tracker_stop_tracking", {}
                )
                return f"⏹️ {result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 新增：时间查询
        if any(word in message_lower for word in ['时间', '几点', '现在时间', '当前时间']):
            try:
                print(f"🕐 Function Call: 获取当前时间")
                result = self.module_registry.call_function_directly(
                    "tools_get_current_time", {}
                )
                return f"🕐 {result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 新增：系统信息查询
        if any(word in message_lower for word in ['系统', 'cpu', '内存', '性能', '电脑状态']):
            try:
                print(f"💻 Function Call: 获取系统信息")
                result = self.module_registry.call_function_directly(
                    "tools_get_system_info", {}
                )
                return f"💻 系统信息:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 新增：文件信息查询
        if any(word in message_lower for word in ['文件', '文件夹', '磁盘', '存储']):
            try:
                print(f"📁 Function Call: 获取文件信息")
                result = self.module_registry.call_function_directly(
                    "tools_get_file_info", {}
                )
                return f"📁 文件系统信息:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 新增：追踪状态查询
        if any(word in message_lower for word in ['追踪状态', '追踪情况', '是否在追踪']):
            try:
                print(f"📊 Function Call: 获取追踪状态")
                result = self.module_registry.call_function_directly(
                    "tracker_get_tracking_status", {}
                )
                return f"📊 追踪状态:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # 新增：梦境生成
        if any(word in message_lower for word in ['梦', '梦境', '做梦', '生成梦', '讲个梦']):
            try:
                print(f"🌙 Function Call: 生成梦境")
                
                # 导入日记管理器
                from Agent.data.diary.diary_manager import DiaryManager
                diary_manager = DiaryManager()
                
                # 检查今天是否已经有梦境记录
                today_dream = diary_manager.get_today_dream()
                
                if today_dream:
                    # 今天已经有梦境且未告诉用户，重新描述
                    dream_content = today_dream['content']
                    return f"🌙 重新描述下面的梦境，内容基本保持同一性，但是表述略有区别。鉴于梦境很容易遗忘，说错一些细节也是可以的。下面是梦境原始文本:\n{dream_content}"
                    
                else:
                    # 今天还没有梦境，生成新的
                    result = self.module_registry.call_function_directly(
                        "dreamgeneration_generate_dream", {}
                    )
                    return f"🌙 梦境生成:\n{result}"
                    
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
                return "抱歉，我现在无法处理梦境相关的请求。"

        if any(word in message_lower for word in ['工作', '总结', '工作总结']):
            try:
                print(f"📊 Function Call: 工作总结")
                result = self.module_registry.call_function_directly(
                    "daywork_generate_daily_summary", {}
                )
                return f"📊 工作总结:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        # camera
        if any(word in message_lower for word in ['坐姿', '姿态', '健康', '疲劳', '摄像头', '拍照', '拍张照']):
            try:
                print(f"📷 Function Call: 检查坐姿")
                # 如果是拍照，就触发拍照功能
                if any(word in message_lower for word in ['拍照', '拍张照', '拍张照片']):
                    result = self.module_registry.call_function_directly(
                        "camera_capture_photo", {}
                    )
                    return f"📷 拍照成功:\n{result}"
                else:
                    result = self.module_registry.call_function_directly(
                        "camera_check_posture", {}
                    )
                    return f"📷 坐姿检查:\n{result}"
            except Exception as e:
                print(f"❌ Function Call执行失败: {e}")
        
        return None
    
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

## 工具使用规则：
- 当用户明确要求"画图"、"生成图片"、"创作图像"时，才使用图像生成工具
- 对于梦境分享、故事叙述等文本内容，优先用文字回复和互动
- 根据用户实际需求智能判断是否调用工具

## 当前时间：{current_time.strftime('%Y-%m-%d %H:%M')}

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
        """处理对话消息 - 优先使用qwen-agent的Function Call"""
        if not self.enabled:
            print(f"❌ ChatModule未启用，跳过消息: '{message}'")
            return None
        
        print(f"📝 ChatModule处理消息: '{message}'")
        
        # 更新交互统计
        self.last_interaction_time = datetime.now()
        self.user_profile['interaction_count'] += 1
        
        # 检查是否有Function Call功能可用
        has_function_calls = (self.agent and not self.using_local_mode and 
                             self.module_registry and 
                             hasattr(self, '_function_calls_available') and
                             self._function_calls_available)
        
        print(f"🔧 Function Call状态: agent={self.agent is not None}, local_mode={self.using_local_mode}, registry={self.module_registry is not None}, available={getattr(self, '_function_calls_available', False)}")
        
        if has_function_calls:
            # 如果有Function Call功能，优先处理所有消息
            print(f"🤖 Function Call模式接管消息处理")
            try:
                # 首先尝试Function Call处理
                function_result = self._try_function_call(message)
                # if function_result:
                #     print(f"✅ Function Call处理成功")
                #     return function_result
                
                # 如果没有匹配的Function Call，使用qwen-agent处理
                # print(f"🔄 Function Call无匹配，使用qwen-agent处理")
                return self._handle_with_qwen_agent(message, context, function_result)
            except Exception as e:
                print(f"❌ Function Call处理失败: {e}")
                # 失败时降级到传统模式
                return None
        else:
            # 没有Function Call功能时，使用传统的过滤逻辑
            should_handle = self._should_handle_message(message)
            print(f"🎯 传统模式过滤结果: {should_handle}")
            
            if not should_handle:
                print(f"❌ 消息被过滤，不处理: '{message}'")
                return None
            
            try:
                if self.agent:
                    print(f"🤖 使用qwen-agent处理")
                    return self._handle_with_qwen_agent(message, context)
                else:
                    print(f"🏠 使用本地模式处理")
                    return self._handle_local_mode(message, context)
                    
            except Exception as e:
                print(f"❌ 对话处理失败: {e}")
                return f"🤖 抱歉，我遇到了一些问题：{str(e)}\n💡 请稍后再试，或者尝试重新表述您的问题。"
    
    def _should_handle_message(self, message):
        """判断是否应该处理此消息"""
        # 基本对话关键词（扩展更全面的词汇）
        chat_keywords = [
            '聊天', '对话', '你好', 'hello', 'hi', '帮助', '问一下', 
            '小柏', '助手', '你能', '可以', '怎么', '什么', '为什么',
            '?', '？', '吗', '呢', '呀', '吧',
            # 新增：身份询问相关
            '你', '你是', '是谁', '介绍', '自己', '身份',
            # 新增：常见对话词
            '谢谢', '再见', '好的', '知道了', '明白', '不错'
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
        question_words = ['何时', '何地', '何人', '如何', '是否', '能否', '会不会', '谁', '哪里', '什么时候']
        if any(word in message for word in question_words) and not has_specialized:
            return True
        
        # 如果消息较短且可能是casual对话，但不包含专门模块关键词
        if len(message.strip()) <= 20 and not any(char.isdigit() for char in message) and not has_specialized:
            return True
        
        # 最后的兜底策略：如果消息不为空且不包含专门模块关键词，就处理
        if message.strip() and not has_specialized:
            print(f"🔍 兜底处理消息: '{message}'")
            return True
        
        return False

    def _enhance_message_with_function_result(self, message, function_result):
        """为消息添加上下文信息"""
        if not message:
            return message
        
        # 添加函数调用结果
        if function_result:
            message += f"\n\n{function_result}"
            
            # 如果是梦境生成结果，添加特殊指令禁用图片生成
            if "🌙 梦境生成:" in function_result:
                message += "\n\n[系统指令：这是梦境分享，请只用文字回复和互动，不要生成图片]"
        
        return message
    
    def _handle_with_qwen_agent(self, message, context, function_result=None):
        """使用Qwen-Agent处理消息"""
        # 添加上下文信息
        enhanced_message = self._enhance_message_with_context(message, context)
        conversation_history = copy.deepcopy(self.conversation_history)

        # 添加到对话历史
        self.conversation_history.append({
            'role': 'user',
            'content': enhanced_message
        })

        enhanced_message = self._enhance_message_with_function_result(enhanced_message, function_result)
        conversation_history.append({
            'role': 'user',
            'content': enhanced_message
        })
        
        # 保持对话历史长度，确保格式正确
        max_history = self.config.get('max_conversation_history', 20)
        if len(conversation_history) > max_history * 2:
            # 只保留最近的用户和助手消息对话，确保以用户消息开始
            user_assistant_msgs = [msg for msg in conversation_history 
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
            conversation_history = recent_msgs
        
        # 清理对话历史格式
        clean_history = self._clean_conversation_history(conversation_history)

        for msg in clean_history:
            print('\nself msg', msg)
        
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
            
            # 判断是否是梦境生成内容，如果是则存储
            if self._is_dream_generation_response(message, formatted_response):
                self._store_dream_if_new(formatted_response)
            
            # 记录到日记本 - 修复function_calls参数
            function_calls = function_result if function_result else []
            self._add_chat_to_diary(message, formatted_response, function_calls)
            
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
        response = responses[response_index]
        
        # 记录到日记本
        self._add_chat_to_diary(message, response, [])
        
        return f"🤖 {response}"
    
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
    
    def _add_chat_to_diary(self, user_message: str, pet_response: str, function_calls: list):
        """添加聊天记录到日记本"""
        try:
            # 过滤掉日记生成过程的对话
            if self._is_diary_generation_message(user_message):
                print(f"🚫 跳过日记生成过程的对话记录")
                return
                
            import os
            import sys
            
            # 添加数据路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, '..', '..', 'data', 'diary')
            sys.path.append(data_dir)
            
            from diary_manager import diary_manager
            
            # 获取当前宠物名称
            import DyberPet.settings as settings
            pet_name = getattr(settings, 'petname', 'Unknown')
            
            # 记录聊天
            diary_manager.add_chat_entry(user_message, pet_response, function_calls, pet_name)
            print(f"✅ 聊天记录已添加到日记本")
        except Exception as e:
            print(f"⚠️ 添加聊天记录到日记本失败: {e}")
    
    def _is_diary_generation_message(self, message: str) -> bool:
        """判断是否是日记生成过程的消息"""
        diary_keywords = [
            "请根据以下信息，写一篇",
            "写一篇日记",
            "生成日记",
            "日记内容",
            "根据工具调用结果",
            "像真实日记一样"
        ]
        
        for keyword in diary_keywords:
            if keyword in message:
                return True
        return False
    
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

    def _clean_conversation_history(self, history):
        """清理对话历史，确保格式符合API要求"""
        # 只保留用户和助手消息
        cleaned_history = [msg for msg in history 
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

    def _get_current_pet_name(self) -> str:
        """获取当前宠物名称"""
        try:
            # 尝试从各种可能的来源获取宠物名称
            if hasattr(self, 'agent_core') and self.agent_core:
                pet_module = self.agent_core.get_module('petaction')
                if pet_module and hasattr(pet_module, 'current_pet_name'):
                    return pet_module.current_pet_name
            
            # 默认返回
            return "宠物"
        except:
            return "宠物" 

    def _is_dream_generation_response(self, message: str, response: str) -> bool:
        """判断是否是梦境生成响应"""
        # 检查用户消息是否包含梦境相关关键词
        dream_keywords = ['梦', '梦境', '做梦', '生成梦', '讲个梦']
        message_lower = message.lower()
        
        is_dream_request = any(word in message_lower for word in dream_keywords)
        
        # 检查响应是否包含梦境相关内容
        response_lower = response.lower()
        dream_response_indicators = ['梦', '梦见', '梦境', '做梦']
        is_dream_response = any(indicator in response_lower for indicator in dream_response_indicators)
        
        return is_dream_request  # 这里的判断和生成梦境的判断保持一致
    
    def _store_dream_if_new(self, dream_content: str):
        """如果是新梦境则存储"""
        try:
            from Agent.data.diary.diary_manager import DiaryManager
            diary_manager = DiaryManager()
            
            # 检查今天是否已经有梦境记录
            today_dream = diary_manager.get_today_dream()
            
            # 只有在今天没有梦境记录时才存储
            if not today_dream:
                from datetime import datetime
                today = datetime.now().strftime('%Y-%m-%d')
                
                diary_manager.add_dream_entry(
                    dream_content=dream_content,
                    date=today,
                    pet_name=self._get_current_pet_name()
                )
                print(f"✅ 新梦境已存储到日记: {today}")
            else:
                print(f"ℹ️ 今天已有梦境记录，跳过存储")
                
        except Exception as e:
            print(f"❌ 存储梦境失败: {e}") 