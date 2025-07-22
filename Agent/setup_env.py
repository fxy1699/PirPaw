#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DyberPet Agent 环境配置设置脚本
帮助用户快速配置API密钥和环境变量
"""

import os
import sys
import shutil


def setup_env_file():
    """设置.env配置文件"""
    print("🔧 DyberPet Agent 环境配置向导")
    print("=" * 50)
    
    # 检查env-example.txt是否存在
    project_root = os.path.dirname(os.path.dirname(__file__))
    env_example_path = os.path.join(project_root, 'env-example.txt')
    env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_example_path):
        print("❌ 未找到env-example.txt文件")
        return False
    
    # 检查是否已有.env文件
    if os.path.exists(env_path):
        print(f"📄 发现现有.env文件: {env_path}")
        overwrite = input("是否覆盖现有配置? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("📝 保留现有配置，您可以手动编辑.env文件")
            return True
    
    # 复制.env.example到.env
    try:
        shutil.copy2(env_example_path, env_path)
        print(f"✅ 已创建配置文件: {env_path}")
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False
    
    # 引导用户配置API密钥
    print("\n🔑 API密钥配置")
    print("=" * 30)
    
    # Qwen API配置
    print("\n1. 配置Qwen DashScope API密钥")
    print("   获取地址: https://dashscope.aliyun.com/")
    print("   注册登录后，在控制台创建API Key")
    
    qwen_key = input("\n请输入Qwen API密钥 (sk-xxx): ").strip()
    
    if qwen_key:
        # 更新.env文件中的API密钥
        update_env_value(env_path, "QWEN_API_KEY", qwen_key)
        
        # 选择模型
        print("\n选择Qwen模型:")
        print("1. qwen-turbo (最快，成本最低)")
        print("2. qwen-plus (平衡性能和成本，推荐)")
        print("3. qwen-max (最强性能)")
        
        model_choice = input("请选择模型 (1-3，默认2): ").strip()
        model_map = {
            "1": "qwen-turbo",
            "2": "qwen-plus", 
            "3": "qwen-max"
        }
        model = model_map.get(model_choice, "qwen-plus")
        update_env_value(env_path, "QWEN_MODEL", model)
        
        print(f"✅ 已配置Qwen API密钥和模型: {model}")
    else:
        print("⚠️ 跳过Qwen API配置，系统将运行在本地模式")
    
    # 天气API配置（可选）
    print("\n2. 配置天气API密钥 (可选)")
    print("   获取地址: https://openweathermap.org/api")
    
    weather_key = input("请输入天气API密钥 (可选，直接回车跳过): ").strip()
    if weather_key:
        update_env_value(env_path, "WEATHER_API_KEY", weather_key)
        print("✅ 已配置天气API密钥")
    
    # 其他配置选项
    print("\n3. 其他配置选项")
    
    # 是否启用摄像头
    enable_camera = input("是否启用摄像头功能? (y/N): ").lower().strip() == 'y'
    update_env_value(env_path, "ENABLE_CAMERA", "true" if enable_camera else "false")
    
    # 是否自动启动追踪
    auto_tracking = input("是否自动启动应用使用追踪? (y/N): ").lower().strip() == 'y'
    update_env_value(env_path, "AUTO_START_TRACKING", "true" if auto_tracking else "false")
    
    # 是否启用调试模式
    debug_mode = input("是否启用调试模式? (y/N): ").lower().strip() == 'y'
    update_env_value(env_path, "DEBUG_MODE", "true" if debug_mode else "false")
    
    print("\n✅ 环境配置完成!")
    return True


def update_env_value(env_path: str, key: str, value: str):
    """更新.env文件中的特定值"""
    try:
        # 读取现有内容
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找并更新对应的行
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        # 如果没找到，添加到末尾
        if not updated:
            lines.append(f"{key}={value}\n")
        
        # 写回文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
    except Exception as e:
        print(f"❌ 更新配置失败: {e}")


def check_dependencies():
    """检查必要的依赖"""
    print("\n📦 检查依赖包")
    print("=" * 20)
    
    required_packages = [
        ("qwen-agent", "Qwen Agent SDK"),
        ("python-dotenv", "环境变量支持"),
        ("psutil", "系统监控"),
    ]
    
    optional_packages = [
        ("pyautogui", "屏幕截取功能"),
        ("opencv-python", "摄像头功能 (macOS)"),
        ("pywin32", "摄像头功能 (Windows)")
    ]
    
    missing_required = []
    missing_optional = []
    
    # 检查必需包
    for package, description in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description} (未安装)")
            missing_required.append(package)
    
    # 检查可选包
    for package, description in optional_packages:
        try:
            if package == "pywin32" and sys.platform != "win32":
                continue
            __import__(package.replace("-", "_"))
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"💡 {package}: {description} (可选)")
            missing_optional.append(package)
    
    # 给出安装建议
    if missing_required:
        print(f"\n⚠️ 需要安装必需依赖:")
        print(f"   pip install {' '.join(missing_required)}")
    
    if missing_optional:
        print(f"\n💡 可选依赖 (根据需要安装):")
        print(f"   pip install {' '.join(missing_optional)}")
    
    return len(missing_required) == 0


def test_configuration():
    """测试配置是否正确"""
    print("\n🧪 测试配置")
    print("=" * 15)
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from Agent.config_loader import load_env_config, get_api_key_status
        
        config = load_env_config()
        status = get_api_key_status()
        
        print("📊 配置状态:")
        print(f"• 模块数量: {len(config['module_configs'])}")
        print(f"• Qwen API: {'✅' if status['qwen_api']['configured'] else '❌'}")
        print(f"• 天气API: {'✅' if status['weather_api']['configured'] else '💡 使用模拟数据'}")
        
        if status['qwen_api']['configured']:
            print(f"• 使用模型: {status['qwen_api']['model']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 DyberPet Agent 环境配置工具")
    print("=" * 40)
    
    # 1. 设置环境文件
    if not setup_env_file():
        print("❌ 环境文件设置失败")
        return
    
    # 2. 检查依赖
    if not check_dependencies():
        print("\n⚠️ 请先安装必需的依赖包")
        return
    
    # 3. 测试配置
    if test_configuration():
        print("\n🎉 配置完成! 现在可以启动Agent系统了:")
        print("   python Agent/demo.py")
    else:
        print("\n❌ 配置测试失败，请检查配置")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置过程出错: {e}") 