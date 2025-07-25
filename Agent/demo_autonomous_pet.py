#!/usr/bin/env python3
"""
自主宠物模块演示脚本

这个脚本展示了如何使用新的自主宠物模块
"""

import sys
import os
import time

# 添加Agent路径
agent_dir = os.path.dirname(__file__)
project_root = os.path.dirname(agent_dir)
sys.path.insert(0, project_root)

# 现在可以正确导入
from Agent.core import AgentCore


def main():
    print("🚀 启动自主宠物演示...")
    
    # 初始化Agent核心
    agent = AgentCore()
    
    # 查找自主宠物模块
    autonomous_pet_module = None
    for module in agent.modules:
        if hasattr(module, 'name') and '自主宠物' in module.name:
            autonomous_pet_module = module
            break
    
    if not autonomous_pet_module:
        print("❌ 未找到自主宠物模块！")
        return
    
    print(f"✅ 找到模块: {autonomous_pet_module.name}")
    print(f"📊 模块状态: {autonomous_pet_module.initialized}")
    
    # 显示模块能力
    print("\n🎯 模块能力:")
    for capability in autonomous_pet_module.get_capabilities():
        print(f"  • {capability}")
    
    # 显示初始情感状态
    print(f"\n📊 初始情感状态:")
    print(autonomous_pet_module.get_emotion_report())
    
    # 模拟用户交互
    print("\n💬 模拟用户交互测试:")
    test_messages = [
        "你好",
        "你现在心情怎么样？",
        "我有点累了",
        "你在做什么？",
        "我们聊聊天吧"
    ]
    
    for msg in test_messages:
        print(f"\n👤 用户: {msg}")
        response = autonomous_pet_module.handle_message(msg)
        print(f"🐱 宠物: {response}")
        time.sleep(1)
    
    # 测试强制行为
    print("\n🧪 测试强制行为:")
    test_behaviors = ['greet', 'self_talk', 'care', 'explore', 'tool_call']
    
    for behavior in test_behaviors:
        print(f"\n🎭 强制执行: {behavior}")
        result = autonomous_pet_module.force_behavior(behavior)
        print(f"   结果: {result}")
        time.sleep(2)
    
    # 显示更新后的情感状态
    print(f"\n📊 交互后情感状态:")
    print(autonomous_pet_module.get_emotion_report())
    
    # 显示详细状态
    print(f"\n🔍 详细模块状态:")
    status = autonomous_pet_module.get_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    # 让程序运行一段时间观察自主行为
    print(f"\n⏰ 观察自主行为 (运行30秒)...")
    print("   (宠物会在后台自主思考和行动)")
    
    for i in range(30):
        time.sleep(1)
        if i % 10 == 9:
            print(f"   运行中... ({i+1}/30秒)")
    
    print(f"\n📊 最终情感状态:")
    print(autonomous_pet_module.get_emotion_report())
    
    print("\n🏁 演示完成!")
    print("💡 提示: 实际使用中，宠物会根据情感状态自主发起各种行为")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc() 