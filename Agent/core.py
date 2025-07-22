import json
import os
from typing import List, Dict, Any
from . import auto_discover_modules


class AgentCore:
    """核心管理器，不到100行代码"""
    
    def __init__(self, config_path=None):
        """初始化Agent核心"""
        self.modules = []
        self.config = {}
        
        # 加载配置
        self.load_config(config_path)
        
        # 自动发现并初始化模块
        self.initialize_modules()
        
        print(f"🚀 Agent系统启动完成，加载了 {len(self.modules)} 个模块")
    
    def load_config(self, config_path=None):
        """加载配置文件"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"📄 配置文件加载完成: {config_path}")
            else:
                # 创建默认配置
                self.config = self.get_default_config()
                self.save_config(config_path)
                print(f"📄 创建默认配置文件: {config_path}")
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "enabled_modules": ["chat", "vision", "camera", "tools"],
            "global_settings": {
                "language": "zh-CN",
                "debug_mode": False
            },
            "module_configs": {
                "chat": {
                    "qwen_api_key": "",
                    "model": "qwen-plus"
                },
                "vision": {
                    "auto_capture": False
                },
                "camera": {
                    "privacy_mode": True
                },
                "tools": {
                    "enabled_tools": ["time", "weather", "system_info"]
                }
            }
        }
    
    def save_config(self, config_path=None):
        """保存配置文件"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")

    def initialize_modules(self):
        """初始化所有模块"""
        # 自动发现模块
        discovered_modules = auto_discover_modules()

        # 根据配置启用/禁用模块
        enabled_modules = self.config.get("enabled_modules", [])
        module_configs = self.config.get("module_configs", {})

        for module in discovered_modules:
            # 检查模块是否在启用列表中
            module_key = module.__class__.__name__.lower().replace('module', '')

            if module_key in enabled_modules:
                # 获取模块特定配置
                module_config = module_configs.get(module_key, {})
                
                # 如果是Chat模块，设置AgentCore引用以支持跨模块调用
                if hasattr(module, 'set_agent_core'):
                    module.set_agent_core(self)
                
                module.setup(module_config)
                self.modules.append(module)
            else:
                module.disable()
                self.modules.append(module)
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> List[str]:
        """处理用户消息"""
        if not message.strip():
            return ["请输入有效的消息"]
        
        results = []
        context = context or {}
        
        # 依次询问每个启用的模块
        for module in self.modules:
            if not module.enabled or not module.initialized:
                continue
                
            try:
                response = module.handle_message(message, context)
                if response:  # 模块有响应
                    results.append(response)
                    if self.config.get("global_settings", {}).get("debug_mode"):
                        print(f"🔍 [{module.name}] 响应: {response}")
            except Exception as e:
                error_msg = f"模块 {module.name} 处理消息时出错: {e}"
                print(f"❌ {error_msg}")
                if self.config.get("global_settings", {}).get("debug_mode"):
                    results.append(f"⚠️ {error_msg}")
        
        return results if results else ["没有模块能处理这个消息"]
    
    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """获取所有模块能力"""
        capabilities = {}
        for module in self.modules:
            if module.enabled:
                capabilities[module.name] = module.get_capabilities()
        return capabilities
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "total_modules": len(self.modules),
            "enabled_modules": len([m for m in self.modules if m.enabled]),
            "modules": [m.get_status() for m in self.modules],
            "config": self.config
        }
    
    def reload_modules(self):
        """重新加载模块"""
        # 清理现有模块
        for module in self.modules:
            module.cleanup()
        
        # 重新初始化
        self.modules.clear()
        self.initialize_modules()
        print("🔄 模块重新加载完成")
    
    def shutdown(self):
        """关闭系统"""
        for module in self.modules:
            module.cleanup()
        print("💤 Agent系统已关闭") 