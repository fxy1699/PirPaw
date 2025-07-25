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
        """加载配置文件，优先使用环境变量，并合并 config.json"""
        env_config = None
        api_status = None
        json_config = None

        # 首先尝试从环境变量加载
        try:
            from .config_loader import load_env_config, get_api_key_status

            # 检查是否有.env文件或环境变量配置
            env_config = load_env_config()  # 加载默认 config.json
            api_status = get_api_key_status()
            
            # 如果有有效的API配置，使用环境变量配置
            if api_status["qwen_api"]["configured"]:
                print(f"🌍 使用环境变量配置 (Qwen API: {'✅' if api_status['qwen_api']['valid_format'] else '⚠️'})")
            else:
                print("💡 未检测到API密钥，回退到JSON配置文件")
                
        except ImportError:
            print("📄 config_loader模块未找到，使用JSON配置文件")
        except Exception as e:
            print(f"⚠️ 环境变量配置加载失败: {e}，使用JSON配置文件")

        # 加载 config.json
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                print(f"📄 JSON配置文件加载完成: {config_path}")
            else:
                # 创建默认配置
                json_config = self.get_default_config()
                self.save_config(config_path)
                print(f"📄 创建默认配置文件: {config_path}")
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            json_config = self.get_default_config()

        # 合并配置
        if json_config:
            self.config = json_config
            
            # 立即设置API key到环境变量（确保qwen-agent能找到）
            chat_config = self.config.get('module_configs', {}).get('chat', {})
            api_key = chat_config.get('qwen_api_key', '')
            if api_key:
                os.environ['DASHSCOPE_API_KEY'] = api_key
                print(f"🔑 已设置DASHSCOPE_API_KEY环境变量")
            
            # print(f"[DEBUG] config: {json.dumps(self.config, indent=4)}")
            print(f"🌍 使用环境变量配置 (Qwen API: {'✅' if api_status and api_status['qwen_api']['valid_format'] else '⚠️'})，并已加载 config.json")
        elif env_config:
            self.config = env_config
            print("使用默认配置")
        else:
            print("❌ 配置文件加载失败：.env 或者 config.json 不存在")

    def get_default_config(self):
        """获取默认配置"""
        return {
            "enabled_modules": ["chat", "vision", "camera", "tools", "tracker", "dreamgeneration", "daywork"],
            "global_settings": {
                "language": "zh-CN",
                "debug_mode": False
            },
            "module_configs": {
                "chat": {
                    "qwen_api_key": "",
                    "model": "qwen-plus",
                    "enable_thinking": True,
                    "max_tokens": 2000,
                    "max_conversation_history": 20,
                    "max_exec_steps": 10,
                    "personality": "可爱的桌面宠物助手",
                    "save_conversation_history": False
                },
                "vision": {
                    "auto_capture": False,
                    "capture_interval": 5,
                    "ocr_enabled": True,
                    "image_analysis_enabled": True,
                    "max_image_size": [1920, 1080]
                },
                "camera": {
                    "enabled": True,
                    "privacy_mode": False,
                    "pose_detection": True,
                    "gesture_recognition": False,
                    "health_monitoring": True,
                    "capture_interval": 2
                },
                "tools": {
                    "enabled_tools": ["time", "weather", "system_info", "file_operations"],
                    "weather_api_key": "",
                    "default_city": "北京"
                },
                "tracker": {
                    "data_file": "data/app_usage.json",
                    "tracking_interval": 5,
                    "auto_start": False,
                    "show_detailed_windows": True
                },
                "dreamgeneration": {
                    "enabled": True,
                    "model": "qwen-plus",
                    "max_tokens": 2000,
                    "max_conversation_history": 20,
                    "max_exec_steps": 10,
                    "personality": "梦境生成助手", 
                    "save_conversation_history": False
                },
                "daywork": {
                    "enabled": True,
                    "max_images": 10
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
        
        # 在所有模块加载完成后，注册模块功能到Function Call系统
        self._register_module_functions()

    def _register_module_functions(self):
        """注册所有模块功能到Function Call系统"""
        try:
            # 查找Chat模块
            chat_module = None
            for module in self.modules:
                if hasattr(module, 'register_all_modules') and module.enabled:
                    chat_module = module
                    break
            
            if chat_module:
                # 注册所有模块功能
                chat_module.register_all_modules(self.modules)
                print(f"🚀 Function Call系统注册完成")
            else:
                print("💡 未找到启用的Chat模块，跳过Function Call注册")
                
        except Exception as e:
            print(f"⚠️ Function Call系统注册失败: {e}")

    def process_message(self, message: str, context: Dict[str, Any] = None) -> List[str]:
        """处理用户消息"""
        if not message.strip():
            return ["请输入有效的消息"]

        # 只用 ChatModule 处理消息
        chat_module = None
        for module in self.modules:
            if module.__class__.__name__ == "ChatModule" and module.enabled and module.initialized:
                chat_module = module
                break

        results = []
        if chat_module:
            try:
                response = chat_module.handle_message(message, context)
                if response:
                    results.append(response)
                    if self.config.get("global_settings", {}).get("debug_mode"):
                        print(f"🔍 [{chat_module.name}] 响应: {response}")
            except Exception as e:
                error_msg = f"模块 {chat_module.name} 处理消息时出错: {e}"
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