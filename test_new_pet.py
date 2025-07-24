#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, '.')

from Agent.modules.pet_action.module import PetActionModule

def test_new_pet():
    print("=== 测试新宠物和新动作接入 ===")
    
    # 初始化模块
    m = PetActionModule()
    m.setup()
    
    if not m.enabled:
        print("❌ 模块初始化失败")
        return
    
    # 显示发现的宠物
    print("\n🔍 发现的宠物:")
    for name, info in m.available_pets.items():
        pet_type = info["type"]
        action_count = len(info["actions"])
        print(f"  • {name} ({pet_type}): {action_count} 个动作")
    
    print(f"\n🐾 当前宠物: {m.current_pet_name}")
    
    # 尝试切换到TestPet
    if "TestPet" in m.available_pets:
        print("\n🔄 切换到TestPet...")
        success = m.switch_pet("TestPet")
        print(f"切换结果: {'成功' if success else '失败'}")
        print(f"当前宠物: {m.current_pet_name}")
        
        if success:
            # 显示TestPet的动作能力
            capabilities = m.get_action_capabilities("TestPet", "role")
            if capabilities:
                print(f"\n🎯 TestPet 动作能力:")
                for category, actions in capabilities.items():
                    if actions:
                        print(f"  • {category}: {actions}")
            
            # 测试新动作
            print(f"\n💬 测试新动作:")
            
            test_messages = [
                "跳舞",
                "唱歌", 
                "飞行",
                "施法",
                "变身"
            ]
            
            for message in test_messages:
                print(f"\n用户: {message}")
                try:
                    result = m.handle_message(message)
                    if result:
                        print(f"AI: {result}")
                    else:
                        print("AI: (无响应)")
                except Exception as e:
                    print(f"错误: {e}")
    else:
        print("⚠️ 未发现TestPet宠物")
    
    m.cleanup()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_new_pet() 