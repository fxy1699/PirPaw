"""
环境变量配置加载器
支持从.env文件和环境变量中读取配置
"""

import os
import json
from typing import Dict, Any, Optional


def load_env_config() -> Dict[str, Any]:
    """
    从环境变量加载配置，支持.env文件
    
    Returns:
        包含所有配置的字典
    """
    # 尝试加载python-dotenv
    try:
        from dotenv import load_dotenv
        
        # 加载.env文件
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"📄 已加载环境配置文件: {env_file}")
        else:
            print("💡 未找到.env文件，使用系统环境变量")
            
    except ImportError:
        print("⚠️ 未安装python-dotenv，请运行: pip install python-dotenv")
        print("📍 当前使用系统环境变量")
    
    # 构建配置字典
    config = {
        "enabled_modules": get_env_list("ENABLED_MODULES", ["chat", "vision", "camera", "tools", "tracker"]),
        "global_settings": {
            "language": get_env_str("LANGUAGE", "zh-CN"),
            "debug_mode": get_env_bool("DEBUG_MODE", False),
            "log_level": get_env_str("LOG_LEVEL", "INFO")
        },
        "module_configs": {
            "chat": {
                "qwen_api_key": get_env_str("QWEN_API_KEY", ""),
                "model": get_env_str("QWEN_MODEL", "qwen-plus"),
                "enable_thinking": get_env_bool("QWEN_ENABLE_THINKING", True),
                "max_tokens": get_env_int("QWEN_MAX_TOKENS", 2000),
                "max_conversation_history": get_env_int("QWEN_MAX_HISTORY", 20),
                "max_exec_steps": get_env_int("QWEN_MAX_EXEC_STEPS", 10),
                "personality": "可爱的桌面宠物助手",
                "save_conversation_history": get_env_bool("QWEN_SAVE_HISTORY", False)
            },
            "vision": {
                "auto_capture": False,
                "capture_interval": 5,
                "ocr_enabled": get_env_bool("ENABLE_VISION", True),
                "image_analysis_enabled": get_env_bool("ENABLE_VISION", True),
                "max_image_size": [1920, 1080]
            },
            "camera": {
                "privacy_mode": not get_env_bool("ENABLE_CAMERA", False),
                "pose_detection": get_env_bool("ENABLE_CAMERA", False),
                "gesture_recognition": False,
                "health_monitoring": get_env_bool("ENABLE_CAMERA", False),
                "capture_interval": 2
            },
            "tools": {
                "enabled_tools": ["time", "weather", "system_info", "file_operations"],
                "weather_api_key": get_env_str("WEATHER_API_KEY", ""),
                "default_city": get_env_str("DEFAULT_CITY", "北京")
            },
            "tracker": {
                "data_file": "data/app_usage.json",
                "tracking_interval": get_env_int("TRACKING_INTERVAL", 5),
                "auto_start": get_env_bool("AUTO_START_TRACKING", False),
                "show_detailed_windows": True
            }
        }
    }
    
    return config


def get_env_str(key: str, default: str = "") -> str:
    """获取字符串环境变量"""
    return os.getenv(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    """获取整数环境变量"""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def get_env_bool(key: str, default: bool = False) -> bool:
    """获取布尔环境变量"""
    value = os.getenv(key, "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    elif value in ("false", "0", "no", "off"):
        return False
    else:
        return default


def get_env_list(key: str, default: list = None) -> list:
    """获取列表环境变量（逗号分隔）"""
    if default is None:
        default = []
    
    value = os.getenv(key, "")
    if value:
        return [item.strip() for item in value.split(",")]
    else:
        return default


def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式"""
    if not api_key:
        return False
    
    # DashScope API密钥通常以sk-开头
    if api_key.startswith("sk-") and len(api_key) > 10:
        return True
    
    return False


def get_api_key_status() -> Dict[str, Any]:
    """获取API密钥配置状态"""
    qwen_key = get_env_str("QWEN_API_KEY")
    weather_key = get_env_str("WEATHER_API_KEY")
    
    return {
        "qwen_api": {
            "configured": bool(qwen_key),
            "valid_format": validate_api_key(qwen_key),
            "model": get_env_str("QWEN_MODEL", "qwen-plus")
        },
        "weather_api": {
            "configured": bool(weather_key),
            "provider": "OpenWeatherMap" if weather_key else "模拟数据"
        }
    }


def show_config_guide():
    """显示配置指南"""
    print("\n🔧 DyberPet Agent 配置指南")
    print("=" * 50)
    
    status = get_api_key_status()
    
    print("📋 API密钥状态:")
    if status["qwen_api"]["configured"]:
        if status["qwen_api"]["valid_format"]:
            print(f"✅ Qwen API: 已配置 (模型: {status['qwen_api']['model']})")
        else:
            print("⚠️ Qwen API: 密钥格式可能有误")
    else:
        print("❌ Qwen API: 未配置")
        print("   获取方式: https://dashscope.aliyun.com/")
    
    if status["weather_api"]["configured"]:
        print(f"✅ 天气API: 已配置 ({status['weather_api']['provider']})")
    else:
        print("💡 天气API: 未配置 (将使用模拟数据)")
    
    print("\n📝 配置步骤:")
    print("1. 复制 .env.example 为 .env")
    print("2. 在 .env 中填入你的API密钥")
    print("3. 根据需要调整其他配置项")
    print("4. 重启Agent系统")
    
    env_example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.example')
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    if not os.path.exists(env_path):
        print(f"\n💡 快速开始:")
        print(f"   cp {env_example_path} {env_path}")
        print(f"   然后编辑 {env_path} 文件")


if __name__ == "__main__":
    # 测试配置加载
    show_config_guide()
    
    print("\n🧪 测试配置加载:")
    config = load_env_config()
    print(f"✅ 配置加载完成，包含 {len(config['module_configs'])} 个模块配置") 