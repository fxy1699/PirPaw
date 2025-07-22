from Agent.base_module import BaseModule


class ChatModule(BaseModule):
    """智能对话模块 - 基于Qwen-Agent"""
    
    name = "智能对话"
    description = "基于Qwen-Agent的智能对话功能，支持多轮对话、工具调用和代码执行"
    version = "1.0.0"
    author = "开发者A"
    
    def __init__(self):
        super().__init__()
        self.agent = None
        self.conversation_history = []
        
    def setup(self, config=None):
        """初始化Qwen-Agent"""
        super().setup(config)
        
        try:
            # 检查是否有API密钥
            api_key = self.config.get('qwen_api_key', '')
            if not api_key:
                print("⚠️ 未配置Qwen API密钥，对话功能将受限")
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
                    'enable_thinking': self.config.get('enable_thinking', True)
                }
            }
            
            # 构建系统指令
            personality = self.config.get('personality', '友好的AI助手')
            system_message = f"""你是一个{personality}，你的名字叫小柏。

你的特点：
1. 性格活泼可爱，语言风格轻松友好
2. 可以帮助用户解决各种问题
3. 擅长编程、学习、工作效率相关的帮助
4. 会关心用户的状态和需求

请用简洁友好的方式回复用户。"""

            # 创建Agent实例
            self.agent = Assistant(
                llm=llm_cfg,
                system_message=system_message,
                function_list=[],  # 暂时不添加工具
                files=[],
                name="DyberPet Assistant"
            )
            
            print(f"✅ {self.name} 初始化成功")
            
        except ImportError:
            print("❌ 未安装qwen-agent，请运行: pip install qwen-agent")
            self.enabled = False
        except Exception as e:
            print(f"❌ {self.name} 初始化失败: {e}")
            self.enabled = False
    
    def handle_message(self, message, context=None):
        """处理对话消息"""
        if not self.enabled or not self.agent:
            return None
        
        # 判断是否是对话请求
        chat_keywords = ['聊天', '对话', '?', '？', '你好', 'hello', '帮助', '问一下']
        if not any(keyword in message.lower() for keyword in chat_keywords):
            return None
        
        try:
            # 添加到对话历史
            self.conversation_history.append({
                'role': 'user',
                'content': message
            })
            
            # 保持对话历史长度
            max_history = self.config.get('max_conversation_history', 10)
            if len(self.conversation_history) > max_history * 2:  # 用户+助手消息
                self.conversation_history = self.conversation_history[-max_history*2:]
            
            # 调用Agent
            response = []
            for chunk in self.agent.run(messages=self.conversation_history):
                response.extend(chunk)
            
            if response:
                # 获取最后一条助手回复
                assistant_response = response[-1].get('content', '抱歉，我没有理解您的问题')
                
                # 添加到对话历史
                self.conversation_history.extend(response)
                
                return f"🤖 {assistant_response}"
            else:
                return "🤖 抱歉，我现在无法回应"
                
        except Exception as e:
            print(f"❌ 对话处理失败: {e}")
            return f"🤖 对话时遇到问题: {str(e)}"
    
    def get_capabilities(self):
        """返回模块能力"""
        capabilities = [
            "智能对话",
            "多轮会话",
            "问题解答",
            "编程帮助",
            "学习辅导"
        ]
        
        if self.config.get('enable_thinking'):
            capabilities.append("深度思考")
            
        return capabilities
    
    def cleanup(self):
        """清理资源"""
        if self.agent:
            # Qwen-Agent没有特殊清理需求
            pass
        self.conversation_history.clear()
        super().cleanup() 