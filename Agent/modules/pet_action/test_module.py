#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PetAction模块测试脚本
验证Agent驱动DyberPet动作系统的功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from Agent.modules.pet_action.module import PetActionModule
from Agent.modules.pet_action.action_discovery import ActionDiscovery
from Agent.modules.pet_action.action_mapper import ActionMapper
from Agent.modules.pet_action.action_executor import ActionExecutor


def test_action_discovery():
    """测试动作发现系统"""
    print("=" * 60)
    print("🔍 测试动作发现系统")
    print("=" * 60)
    
    discovery = ActionDiscovery()
    
    # 测试扫描所有宠物
    pets = discovery.scan_all_pets()
    
    print(f"📋 发现宠物数量: {len(pets)}")
    for pet_name, pet_info in pets.items():
        print(f"\n🐾 宠物: {pet_name}")
        print(f"   类型: {pet_info['type']}")
        print(f"   动作数量: {len(pet_info['actions'])}")
        print(f"   基础动作: {list(pet_info['basic_actions'].keys())}")
        print(f"   随机动作组: {len(pet_info['random_actions'])}")
        
        # 显示前几个动作
        actions = list(pet_info['actions'].keys())[:5]
        print(f"   示例动作: {actions}")
    
    return pets


def test_action_mapper():
    """测试动作映射系统"""
    print("\n" + "=" * 60)
    print("🗺️ 测试动作映射系统")
    print("=" * 60)
    
    mapper = ActionMapper()
    
    # 获取映射统计
    stats = mapper.get_mapping_stats()
    print(f"📊 映射统计: {stats['total_categories']} 个分类, {stats['total_mappings']} 个映射")
    
    # 测试消息映射
    test_messages = [
        "让小猫睡觉",
        "走路",
        "站立",
        "开心一下", 
        "休息",
        "可以做什么动作",
        "fall_asleep",
        "angry"
    ]
    
    print(f"\n🧪 测试消息映射:")
    for message in test_messages:
        results = mapper.map_message_to_actions(message)
        print(f"\n'{message}' -> ")
        for result in results[:3]:  # 显示前3个结果
            print(f"  • {result['action']} (置信度: {result['confidence']:.2f}, 类型: {result['match_type']})")


def test_action_executor():
    """测试动作执行系统"""
    print("\n" + "=" * 60)
    print("⚡ 测试动作执行系统")
    print("=" * 60)
    
    executor = ActionExecutor()
    executor.start()
    
    # 测试预览动作
    print("🔍 测试动作预览:")
    preview = executor.preview_action("sleep")
    print(f"动作预览: {preview}")
    
    # 测试执行单个动作
    print(f"\n▶️ 测试执行动作:")
    request_id = executor.execute_action("default", parameters={"test": True})
    print(f"提交动作请求: {request_id}")
    
    # 等待一秒后检查状态
    import time
    time.sleep(1)
    
    status = executor.get_action_status()
    print(f"执行器状态: {status}")
    
    # 测试动作序列
    print(f"\n📋 测试动作序列:")
    sequence = [
        {"action_name": "default", "parameters": {}},
        {"action_name": "sleep", "parameters": {}}
    ]
    request_ids = executor.execute_action_sequence(sequence)
    print(f"序列请求IDs: {request_ids}")
    
    time.sleep(1)
    
    # 获取统计信息
    stats = executor.get_execution_stats()
    print(f"📊 执行统计: {stats}")
    
    executor.stop()


def test_pet_action_module():
    """测试完整的PetAction模块"""
    print("\n" + "=" * 60)
    print("🎭 测试PetAction模块")
    print("=" * 60)
    
    module = PetActionModule()
    module.setup()
    
    if not module.enabled:
        print("❌ 模块初始化失败")
        return
    
    print(f"✅ 模块初始化成功")
    
    # 测试能力查询
    capabilities = module.get_capabilities()
    print(f"\n🎯 模块能力:")
    for cap in capabilities:
        print(f"  • {cap}")
    
    # 测试消息处理
    test_messages = [
        "让小猫睡觉",
        "站立",
        "走路",
        "开心",
        "现在的状态",
        "能做什么动作",
        "不相关的消息"
    ]
    
    print(f"\n💬 测试消息处理:")
    for message in test_messages:
        print(f"\n用户: {message}")
        response = module.handle_message(message)
        if response:
            print(f"AI: {response}")
        else:
            print("AI: (无响应)")
    
    # 获取统计信息
    stats = module.get_module_stats()
    print(f"\n📊 模块统计: {stats}")
    
    module.cleanup()


def main():
    """主测试函数"""
    print("🚀 PetAction模块测试开始")
    print("=" * 60)
    
    try:
        # 1. 测试动作发现
        pets = test_action_discovery()
        
        # 2. 测试动作映射
        test_action_mapper()
        
        # 3. 测试动作执行
        test_action_executor()
        
        # 4. 测试完整模块
        test_pet_action_module()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 