class BaseModule:
    """Agent模块基类 - 所有功能模块的父类"""
    
    # 模块基本信息
    name = "未命名模块"
    description = "模块描述"
    version = "1.0.0"
    author = "开发者"
    
    def __init__(self):
        self.enabled = True
        self.config = {}
        self.initialized = False
        
    def setup(self, config=None):
        """初始化模块，子类应重写此方法"""
        self.config = config or {}
        self.initialized = True
        print(f"🔧 {self.name} 模块初始化完成")
    
    def handle_message(self, message: str, context=None):
        """处理消息，子类应重写此方法"""
        return None
    
    def get_capabilities(self) -> list:
        """获取模块能力描述，子类应重写此方法返回能力列表"""
        return []
    
    def enable(self):
        """启用模块"""
        self.enabled = True
        print(f"✅ {self.name} 模块已启用")
    
    def disable(self):
        """禁用模块"""
        self.enabled = False
        print(f"❌ {self.name} 模块已禁用")
    
    def cleanup(self):
        """清理资源，可选实现"""
        print(f"🧹 {self.name} 模块清理完成")

    def get_status(self):
        """获取模块状态"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.initialized,
            "author": self.author,
            "version": self.version,
            "description": self.description
        }

    # ============ Function Call 接口 ============
    
    def get_function_definitions(self) -> list:
        """
        获取模块的Function Call工具定义
        子类应重写此方法，返回符合OpenAI Function Call格式的工具定义
        
        Returns:
            list: 工具定义列表，格式如下:
            [
                {
                    "name": "function_name",
                    "description": "功能描述", 
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {
                                "type": "string",
                                "description": "参数描述"
                            }
                        },
                        "required": ["param1"]
                    }
                }
            ]
        """
        return []
    
    def call_function(self, function_name: str, arguments: dict):
        """
        调用模块的特定功能
        子类应重写此方法，实现具体的功能调用
        
        Args:
            function_name (str): 要调用的功能名称
            arguments (dict): 功能参数
            
        Returns:
            任意类型: 功能执行结果
        """
        raise NotImplementedError(f"模块 {self.name} 未实现 call_function 方法")
    
    def get_function_list(self):
        """
        获取可供qwen-agent调用的函数列表
        这个方法会自动根据get_function_definitions()生成实际的Python函数
        
        Returns:
            list: Python函数列表
        """
        functions = []
        definitions = self.get_function_definitions()
        
        for definition in definitions:
            func_name = definition["name"]
            
            # 动态创建函数
            def create_function(name):
                def function(**kwargs):
                    try:
                        result = self.call_function(name, kwargs)
                        return str(result) if result is not None else f"{name} 执行完成"
                    except Exception as e:
                        return f"❌ {name} 执行失败: {str(e)}"
                
                # 设置函数元数据
                function.__name__ = name
                function.__doc__ = definition.get("description", f"调用{self.name}模块的{name}功能")
                
                return function
            
            functions.append(create_function(func_name))
        
        return functions 