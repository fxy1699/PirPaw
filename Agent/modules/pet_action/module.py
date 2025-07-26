"""
宠物动作控制模块 (PetActionModule)
Agent系统的宠物动作控制接口，连接Agent与DyberPet
"""

import os
import sys
import time
from typing import Dict, List, Optional, Any
from Agent.base_module import BaseModule

# 导入子模块
from .action_discovery import ActionDiscovery
from .action_mapper import ActionMapper  
from .action_executor import ActionExecutor


class PetActionModule(BaseModule):
    """宠物动作控制模块 - Agent驱动DyberPet动作系统的核心接口"""
    
    name = "宠物动作"
    description = "智能控制桌面宠物执行各种动作和行为，支持自然语言指令"
    version = "1.0.0"
    author = "Agent团队"
    
    def __init__(self):
        super().__init__()
        
        # 子系统组件
        self.action_discovery = None
        self.action_mapper = None
        self.action_executor = None
        
        # 当前宠物信息
        self.current_pet_info = None
        self.current_pet_name = None
        self.available_pets = {}
        
        # DyberPet系统接口
        self.dyber_pet_bridge = None
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "last_action_time": None
        }
    
    def setup(self, config=None):
        """初始化宠物动作模块"""
        super().setup(config)
        
        try:
            print(f"🎭 {self.name} 模块初始化开始...")
            
            # 初始化动作发现系统
            self.action_discovery = ActionDiscovery()
            
            # 初始化动作映射系统
            self.action_mapper = ActionMapper()
            
            # 初始化动作执行系统
            self.action_executor = ActionExecutor()
            
            # 扫描可用宠物
            self._scan_available_pets()
            
            # 设置当前宠物（如果有的话）
            self._detect_current_pet()
            
            # 启动动作执行器
            self.action_executor.start()
            
            # 检查DyberPet连接状态
            self._check_dyberpet_connection()
            
            print(f"✅ {self.name} 模块初始化成功")
            print(f"   发现宠物: {len(self.available_pets)} 个")
            print(f"   当前宠物: {self.current_pet_name or '未检测到'}")
            print(f"   DyberPet连接: {self.action_executor.get_dyberpet_connection_status().value}")
            
        except Exception as e:
            print(f"❌ {self.name} 模块初始化失败: {e}")
            self.enabled = False
    
    def _check_dyberpet_connection(self):
        """检查与DyberPet的连接状态"""
        try:
            if self.action_executor.is_connected_to_dyberpet():
                print("🎉 已连接到DyberPet主框架，可以执行真实动作")
                
                # 尝试获取DyberPet中的宠物状态
                pet_state = self.action_executor.bridge.get_pet_state()
                if pet_state:
                    self.current_pet_name = pet_state.name
                    print(f"🐾 从DyberPet获取当前宠物: {pet_state.name}")
                    
                    # 更新可用动作列表
                    if pet_state.available_actions:
                        print(f"📋 DyberPet动作列表: {pet_state.available_actions}")
            else:
                print("💡 未连接到DyberPet，将使用模拟模式")
                
        except Exception as e:
            print(f"⚠️ 检查DyberPet连接失败: {e}")
    
    def connect_to_dyberpet(self, app_instance=None, pet_widget=None) -> bool:
        """
        手动连接到DyberPet实例
        
        Args:
            app_instance: DyberPetApp实例  
            pet_widget: PetWidget实例
            
        Returns:
            bool: 连接是否成功
        """
        try:
            success = self.action_executor.connect_to_dyberpet(app_instance, pet_widget)
            if success:
                self._check_dyberpet_connection()
                print("🔗 手动连接DyberPet成功")
            else:
                print("❌ 手动连接DyberPet失败")
            return success
        except Exception as e:
            print(f"❌ 连接DyberPet异常: {e}")
            return False
    
    def handle_message(self, message: str, context=None) -> Optional[str]:
        """处理用户的动作控制消息"""
        if not self.enabled:
            return None
        
        # 先检查是否是状态查询
        status_response = self.handle_status_request(message)
        if status_response:
            return status_response
            
        # 检查是否是能力查询
        capability_response = self.handle_capability_request(message)
        if capability_response:
            return capability_response
        
        # 检查是否是动作相关的消息
        if not self._is_action_related_message(message):
            return None
        
        try:
            print(f"🎯 处理动作请求: {message}")
            self.stats["total_requests"] += 1
            
            # 确保有可用的宠物
            if not self.current_pet_info:
                return "❌ 当前没有检测到可用的宠物，请确保DyberPet正在运行"
            
            # 将消息映射到动作
            action_results = self._map_message_to_actions(message, context)
            
            if not action_results:
                # 提供更有用的建议
                available_actions = list(self.current_pet_info.get("actions", {}).keys())[:5]
                if available_actions:
                    return f"🤔 抱歉，我没能理解您想要执行什么动作。当前宠物{self.current_pet_name}支持：{', '.join(available_actions)}等动作"
                else:
                    return "🤔 抱歉，我没能理解您想要执行什么动作。您可以尝试说'让小猫睡觉'、'走路'、'站立'等"
            
            # 执行最佳匹配的动作
            best_action = action_results[0]
            execution_result = self._execute_action(best_action, context)
            
            # 更新统计
            if execution_result["success"]:
                self.stats["successful_actions"] += 1
            else:
                self.stats["failed_actions"] += 1
            self.stats["last_action_time"] = time.time()
            
            return execution_result["message"]
            
        except Exception as e:
            print(f"❌ 处理动作请求失败: {e}")
            return f"❌ 处理动作请求时出现错误: {e}"
    
    def _scan_available_pets(self):
        """扫描可用的宠物"""
        try:
            self.available_pets = self.action_discovery.scan_all_pets()
            print(f"🔍 扫描完成，发现 {len(self.available_pets)} 个宠物")
        except Exception as e:
            print(f"❌ 扫描宠物失败: {e}")
            self.available_pets = {}
    
    def _detect_current_pet(self):
        """检测当前活跃的宠物"""
        # 简化实现：使用第一个可用宠物
        # 在实际集成中，这里应该从DyberPet系统获取当前宠物信息
        if self.available_pets:
            first_pet_name = list(self.available_pets.keys())[0]
            self.current_pet_name = first_pet_name
            self.current_pet_info = self.available_pets[first_pet_name]
            print(f"🐾 设置当前宠物: {self.current_pet_name}")
        else:
            print("⚠️ 未找到可用宠物")
    
    def _is_action_related_message(self, message: str) -> bool:
        """判断消息是否与动作控制相关"""
        action_keywords = [
            # 动作指令词
            "让", "使", "做", "执行", "表演", "播放",
            # 直接动作词
            "睡觉", "走路", "站立", "坐下", "跳", "跑",
            "开心", "生气", "伤心", "休息", "玩", "吃",
            # 宠物称呼
            "宠物", "小猫", "猫咪", "小狗", "狗狗",
            # 英文动作词
            "walk", "sleep", "stand", "sit", "jump", "play",
            # 状态询问
            "动作", "行为", "能做什么", "会什么", "状态", "现在",
            # 更多常见词
            "默认", "待机", "静止", "不动", "fall", "drag",
            "left", "right", "up", "down", "angry", "happy", "sad"
        ]
        
        message_lower = message.lower()
        # 先检查关键词匹配
        keyword_match = any(keyword in message_lower for keyword in action_keywords)
        
        if keyword_match:
            print(f"🔍 通过关键词识别到动作相关消息: {message_lower}")
        
        # 对于一些明确的动作关键词，强制认为是动作相关
        strong_action_keywords = ["睡觉", "走路", "站立", "开心", "生气", "伤心", "休息", "玩", 
                                 "跳舞", "唱歌", "飞行", "施法", "变身", "舞蹈", "歌唱", "魔法"]
        if any(keyword in message_lower for keyword in strong_action_keywords):
            print(f"🔍 通过强关键词识别到动作相关消息: {message_lower}")
            return True
        
        # 如果关键词匹配失败，尝试动作映射来判断
        if not keyword_match and hasattr(self, 'action_mapper'):
            try:
                results = self.action_mapper.map_message_to_actions(message_lower)
                if len(results) > 0:
                    print(f"🔍 通过动作映射识别到动作相关消息: {message_lower} -> {[r['action'] for r in results[:3]]}")
                    return True
            except Exception as e:
                print(f"⚠️ 动作映射检查异常: {e}")
                pass
        
        return keyword_match
    
    def _map_message_to_actions(self, message: str, context=None) -> List[Dict]:
        """将消息映射到动作"""
        print(f"🗺️ 开始映射消息: '{message}'")
        
        # 构建上下文信息
        pet_context = {
            "pet_status": self._get_pet_status(),
            "time": time.time(),
            "user_context": context
        }
        
        # 使用动作映射器
        results = self.action_mapper.map_message_to_actions(
            message=message,
            pet_info=self.current_pet_info,
            context=pet_context
        )
        
        print(f"🗺️ 映射结果: {len(results)} 个动作")
        for i, result in enumerate(results[:3]):
            print(f"   {i+1}. {result['action']} (置信度: {result['confidence']:.2f}, 类型: {result['match_type']})")
        
        return results
    
    def _execute_action(self, action_result: Dict, context=None) -> Dict:
        """执行动作"""
        action_name = action_result["action"]
        confidence = action_result["confidence"]
        
        print(f"▶️ 执行动作: {action_name} (置信度: {confidence:.2f})")
        
        try:
            # 检查动作是否被当前宠物支持
            # if not self._check_action_supported(action_name):
            #     # 尝试找到替代动作
            #     alternative = self._find_alternative_action(action_name)
            #     if alternative:
            #         return {
            #             "success": True,
            #             "message": f"✅ 当前宠物不支持 {action_name}，为您执行相似动作 {alternative} (置信度: {confidence:.1%})"
            #         }
            #     else:
            #         available_actions = list(self.current_pet_info.get("actions", {}).keys())[:5]
            #         return {
            #             "success": False,
            #             "message": f"❌ 当前宠物{self.current_pet_name}不支持 {action_name} 动作。支持的动作：{', '.join(available_actions)}"
            #         }
            
            # 提交到动作执行器
            request_id = self.action_executor.execute_action(
                action_name=action_name,
                parameters={"source": "agent", "confidence": confidence},
                priority=2  # 中等优先级
            )
            
            # 直接返回成功（因为是异步执行）
            return {
                "success": True,
                "message": f"✅ 小宠物开始执行 {action_name} 动作了~ (置信度: {confidence:.1%})"
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ 执行动作时出现异常: {e}"
            }
    
    def _check_action_supported(self, action_name: str) -> bool:
        """检查动作是否被当前宠物支持"""
        if not self.current_pet_info:
            return True  # 如果没有宠物信息，假设支持（允许尝试）
        
        # 检查基础动作
        basic_actions = self.current_pet_info.get("basic_actions", {})
        if action_name in basic_actions.values():
            return True
        
        # 检查所有动作
        actions = self.current_pet_info.get("actions", {})
        if action_name in actions:
            return True
        
        # 检查随机动作组
        for random_act in self.current_pet_info.get("random_actions", []):
            if action_name in random_act.get("act_list", []):
                return True
        
        # 对于一些通用动作，即使宠物不明确支持也允许尝试
        universal_actions = ["default", "stand", "sleep", "walk", "left_walk", "right_walk", 
                           "happy", "sad", "angry", "rest", "drag", "fall"]
        if action_name in universal_actions:
            return True
        
        return False
    
    def _get_pet_status(self) -> Dict:
        """获取宠物当前状态"""
        # 简化实现：返回模拟状态
        # 在实际集成中，这里应该从DyberPet系统获取真实状态
        return {
            "hp": 75,
            "fv": 60,
            "is_sleeping": False,
            "is_moving": False,
            "current_action": "default"
        }
    
    def get_capabilities(self) -> List[str]:
        """返回模块能力列表"""
        capabilities = [
            "自然语言动作控制",
            "宠物动作发现和映射",
            "智能动作推荐",
            "多宠物支持"
        ]
        
        if self.current_pet_info:
            # 添加当前宠物的特定能力
            pet_capabilities = self.action_discovery.get_action_capabilities(
                self.current_pet_name,
                self.current_pet_info.get("type", "role")
            )
            
            if pet_capabilities.get("basic_actions"):
                capabilities.append(f"基础动作: {', '.join(pet_capabilities['basic_actions'][:3])}")
            
            if pet_capabilities.get("movement_actions"):
                capabilities.append(f"移动动作: {', '.join(pet_capabilities['movement_actions'][:3])}")
                
            if pet_capabilities.get("random_action_groups"):
                capabilities.append(f"随机动作组: {', '.join(pet_capabilities['random_action_groups'][:2])}")
        
        return capabilities
    
    def get_pet_info(self) -> Dict:
        """获取当前宠物信息（供其他模块调用）"""
        return self.current_pet_info
    
    def get_pet_status(self) -> Dict:
        """获取当前宠物状态（供其他模块调用）"""
        return self._get_pet_status()
    
    def get_action_capabilities(self, pet_name: str, pet_type: str = 'role') -> Dict[str, List[str]]:
        """获取指定宠物的动作能力摘要（供外部调用）"""
        return self.action_discovery.get_action_capabilities(pet_name, pet_type)
    
    def switch_pet(self, pet_name: str) -> bool:
        """切换当前宠物"""
        if pet_name in self.available_pets:
            self.current_pet_name = pet_name
            self.current_pet_info = self.available_pets[pet_name]
            print(f"🔄 切换到宠物: {pet_name}")
            return True
        else:
            print(f"❌ 未找到宠物: {pet_name}")
            return False
    
    def refresh_pets(self):
        """刷新宠物列表"""
        print("🔄 刷新宠物列表...")
        self.action_discovery.clear_cache()
        self._scan_available_pets()
        
        # 如果当前宠物不再可用，重新检测
        if self.current_pet_name not in self.available_pets:
            self._detect_current_pet()
    
    def get_action_suggestions(self, context=None) -> List[str]:
        """获取动作建议"""
        if not self.current_pet_info:
            return ["请先确保有可用的宠物"]
        
        suggestions = self.action_mapper.suggest_actions(
            pet_info=self.current_pet_info,
            context={"pet_status": self._get_pet_status()}
        )
        
        return [f"{s['action']} - {s['reason']}" for s in suggestions[:3]]
    
    def get_module_stats(self) -> Dict:
        """获取模块统计信息"""
        executor_stats = self.action_executor.get_execution_stats() if self.action_executor else {}
        
        return {
            "pet_action_stats": self.stats,
            "available_pets": len(self.available_pets),
            "current_pet": self.current_pet_name,
            "executor_stats": executor_stats,
            "capabilities_count": len(self.get_capabilities())
        }
    
    def handle_status_request(self, message: str) -> Optional[str]:
        """处理状态查询请求"""
        if "状态" in message or "信息" in message or "现在" in message:
            if not self.current_pet_info:
                return "❌ 当前没有活跃的宠物"
            
            pet_status = self._get_pet_status()
            capabilities = self.get_capabilities()
            
            status_text = f"""🐾 当前宠物信息:
📛 名称: {self.current_pet_name}
❤️ 血量: {pet_status['hp']}%
💖 好感度: {pet_status['fv']}%
🎭 当前动作: {pet_status.get('current_action', '未知')}

🎯 可用能力:
{chr(10).join(f'• {cap}' for cap in capabilities[:5])}"""
            
            return status_text
        
        return None
    
    def _find_alternative_action(self, action_name: str) -> Optional[str]:
        """为不支持的动作寻找替代方案"""
        if not self.current_pet_info:
            return None
        
        available_actions = self.current_pet_info.get("actions", {})
        
        # 动作映射表：不支持的动作 -> 替代动作
        alternatives = {
            "sleep": "default",
            "rest": "default", 
            "left_walk": "left",
            "right_walk": "right",
            "walk": "default",
            "happy": "default",
            "sad": "default",
            "angry": "default",
            "play": "default",
            "eat": "default",
            "feed": "default"
        }
        
        # 查找直接替代
        if action_name in alternatives:
            alternative = alternatives[action_name]
            if alternative in available_actions:
                return alternative
        
        # 查找相似动作
        for available_action in available_actions:
            if action_name.lower() in available_action.lower() or available_action.lower() in action_name.lower():
                return available_action
        
        return None

    def handle_capability_request(self, message: str) -> Optional[str]:
        """处理能力查询请求"""
        capability_keywords = ["能做什么", "会什么", "支持什么", "有什么动作", "可以做"]
        
        if any(keyword in message for keyword in capability_keywords):
            if not self.current_pet_info:
                return "❌ 当前没有活跃的宠物"
            
            actions = self.current_pet_info.get("actions", {})
            basic_actions = list(self.current_pet_info.get("basic_actions", {}).values())
            random_actions = [act.get("name", "未命名") for act in self.current_pet_info.get("random_actions", [])]
            
            capability_text = f"""🎯 当前宠物 {self.current_pet_name} 支持以下动作:

📋 基础动作: {', '.join(basic_actions[:8])}
🎲 随机动作组: {', '.join(random_actions[:5])}
🎭 全部动作: {', '.join(list(actions.keys())[:10])}

💡 您可以说：
• "站立" / "default" - 默认姿态
• "向左" / "left" - 向左移动  
• "向右" / "right" - 向右移动
• "拖拽" / "drag" - 拖拽动作
• "下落" / "fall" - 下落动作"""
            
            return capability_text
        
        return None

    def cleanup(self):
        """清理资源"""
        if self.action_executor:
            self.action_executor.stop()
        
        super().cleanup()
        print(f"🧹 {self.name} 模块清理完成")

    # ============ Function Call 接口 ============
    
    def get_function_definitions(self) -> list:
        """获取宠物动作模块的Function Call工具定义"""
        return [
            {
                "name": "control_pet_action",
                "description": "控制桌面宠物执行指定动作，如睡觉、走路、跳舞等，支持中文自然语言描述",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_command": {
                            "type": "string",
                            "description": "动作指令，如'让小猫睡觉'、'走路'、'跳舞'、'站立'等自然语言描述"
                        }
                    },
                    "required": ["action_command"]
                }
            },
            {
                "name": "get_pet_status",
                "description": "获取当前宠物的状态信息，包括当前宠物名称和可用动作",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "switch_pet",
                "description": "切换到指定的宠物",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pet_name": {
                            "type": "string",
                            "description": "宠物名称，如'Kitty'、'ChrisKitty'、'TestPet'等"
                        }
                    },
                    "required": ["pet_name"]
                }
            },
            {
                "name": "list_available_pets",
                "description": "列出所有可用的宠物及其动作能力",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def call_function(self, function_name: str, arguments: dict):
        """调用宠物动作模块的具体功能"""
        if not self.enabled:
            raise RuntimeError(f"模块 {self.name} 已禁用")
        
        if function_name == "control_pet_action":
            return self._function_control_pet_action(arguments)
        elif function_name == "get_pet_status":
            return self._function_get_pet_status(arguments)
        elif function_name == "switch_pet":
            return self._function_switch_pet(arguments)
        elif function_name == "list_available_pets":
            return self._function_list_available_pets(arguments)
        else:
            raise ValueError(f"未知功能: {function_name}")
    
    def _function_control_pet_action(self, arguments: dict):
        """Function Call: 控制宠物动作"""
        action_command = arguments.get("action_command", "")
        
        if not action_command:
            return "❌ 请提供动作指令"
        
        # 使用现有的handle_message方法处理动作指令
        result = self.handle_message(action_command)
        
        if result:
            return result
        else:
            return "🤔 抱歉，我没能理解这个动作指令。请尝试使用'睡觉'、'走路'、'跳舞'等常见动作词"
    
    def _function_get_pet_status(self, arguments: dict):
        """Function Call: 获取宠物状态"""
        status_result = self.handle_status_request("现在的状态")
        if status_result:
            return status_result
        else:
            return f"🐾 当前宠物: {self.current_pet_name or '未检测到'}\n📋 发现宠物: {len(self.available_pets)} 个"
    
    def _function_switch_pet(self, arguments: dict):
        """Function Call: 切换宠物"""
        pet_name = arguments.get("pet_name", "")
        
        if not pet_name:
            return "❌ 请提供宠物名称"
        
        result = self.switch_pet(pet_name)
        if result == "成功":
            return f"✅ 已切换到宠物: {pet_name}"
        else:
            return f"❌ 切换宠物失败: {result}"
    
    def _function_list_available_pets(self, arguments: dict):
        """Function Call: 列出可用宠物"""
        capability_result = self.handle_capability_request("有什么动作")
        if capability_result:
            return capability_result
        else:
            pets_info = []
            for pet_id in self.available_pets:
                pet_name = pet_id.replace('_pet', '') if pet_id.endswith('_pet') else pet_id
                pets_info.append(f"• {pet_name}")
            
            return f"🐾 可用宠物:\n" + "\n".join(pets_info) 