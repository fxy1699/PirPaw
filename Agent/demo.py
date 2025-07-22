#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DyberPet Agent系统演示程序
展示如何使用简化的AI模块架构

运行方式：
python Agent/demo.py
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.core import AgentCore


def main():
    """主演示程序"""
    print("🎯 DyberPet Agent系统演示")
    print("=" * 50)
    
    # 初始化Agent核心
    try:
        agent_core = AgentCore()
        print()
    except Exception as e:
        print(f"❌ Agent系统初始化失败: {e}")
        return
    
    # 显示系统状态
    print("📊 系统状态:")
    status = agent_core.get_system_status()
    print(f"• 总模块数: {status['total_modules']}")
    print(f"• 启用模块数: {status['enabled_modules']}")
    
    # 显示模块列表
    print("\n📋 模块列表:")
    for module_status in status['modules']:
        status_icon = "✅" if module_status['enabled'] else "❌"
        print(f"  {status_icon} {module_status['name']} - {module_status['author']}")
    
    # 显示所有能力
    print("\n🚀 系统能力:")
    capabilities = agent_core.get_all_capabilities()
    for module_name, caps in capabilities.items():
        if caps:
            print(f"• {module_name}: {', '.join(caps)}")
    
    print("\n" + "=" * 50)
    print("💬 开始对话测试（输入 'quit' 退出）")
    print("=" * 50)
    
    # 对话循环
    while True:
        try:
            user_input = input("\n👤 用户: ")
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                break
            
            if not user_input.strip():
                continue
            
            # 处理用户消息
            responses = agent_core.process_message(user_input)
            
            # 显示响应
            print("\n🤖 AI回复:")
            for i, response in enumerate(responses, 1):
                if len(responses) > 1:
                    print(f"  [{i}] {response}")
                else:
                    print(f"  {response}")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ 处理消息时出错: {e}")
    
    # 关闭系统
    print("\n👋 感谢使用！正在关闭系统...")
    agent_core.shutdown()


def test_examples():
    """演示一些示例对话"""
    examples = [
        "你好，现在几点了？",
        "看一下我的屏幕",
        "检查一下我的坐姿",
        "北京的天气怎么样？",
        "系统性能如何？",
        "帮我聊聊天"
    ]
    
    print("\n🎯 示例对话:")
    for example in examples:
        print(f"  • {example}")


if __name__ == "__main__":
    # 显示使用说明
    print("💡 使用说明:")
    print("1. 确保已安装必要依赖: pip install qwen-agent pyautogui psutil")
    print("2. 配置Qwen API密钥（在config.json中）")
    print("3. 输入各种消息测试不同模块功能")
    print()
    
    test_examples()
    
    # 运行演示
    main() 