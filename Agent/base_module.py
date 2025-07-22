class BaseModule:
    """所有模块的基类，接口极简"""
    
    # 每个模块必须定义这些属性
    name = "模块名称"
    description = "模块功能描述"
    version = "1.0.0"
    author = "开发者姓名"
    
    def __init__(self):
        self.enabled = True
        self.config = {}
        self.initialized = False
    
    def setup(self, config=None):
        """模块初始化，可选实现"""
        if config:
            self.config.update(config)
        self.initialized = True
        print(f"🔧 {self.name} 模块初始化完成")
    
    def handle_message(self, message, context=None):
        """处理消息，必须实现"""
        raise NotImplementedError("子类必须实现 handle_message 方法")
    
    def get_capabilities(self):
        """返回模块能力列表，可选实现"""
        return []
    
    def get_status(self):
        """获取模块状态"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.initialized,
            "author": self.author,
            "version": self.version
        }
    
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