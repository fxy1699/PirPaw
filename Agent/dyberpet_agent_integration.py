"""
DyberPet与Agent系统集成脚本
在DyberPet启动时自动集成Agent系统，实现真实的宠物动作控制
"""

import sys
import os
from pathlib import Path
import threading
import time

# 添加路径
project_root = Path(__file__).parent.parent
agent_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(agent_root))


class DyberPetAgentIntegration:
    """DyberPet与Agent系统集成管理器"""
    
    def __init__(self):
        """初始化集成管理器"""
        self.dyberpet_app = None
        self.pet_widget = None
        self.agent_core = None
        self.pet_action_module = None
        self.integration_active = False
        
        print("🔗 DyberPet-Agent集成管理器初始化")
    
    def integrate_with_dyberpet(self, dyberpet_app):
        """
        与DyberPet应用集成
        
        Args:
            dyberpet_app: DyberPetApp实例
        """
        try:
            self.dyberpet_app = dyberpet_app
            self.pet_widget = dyberpet_app.p if hasattr(dyberpet_app, 'p') else None
            
            if not self.pet_widget:
                print("❌ 无法获取PetWidget实例")
                return False
            
            print(f"🐾 已获取DyberPet实例，当前宠物: {getattr(self.pet_widget, 'curr_pet_name', 'Unknown')}")
            
            # 启动Agent系统
            if self._setup_agent_core():
                # 连接pet_action模块到DyberPet
                if self._connect_pet_action_module():
                    self.integration_active = True
                    print("🎉 DyberPet与Agent系统集成成功！")
                    
                    # 设置状态监听
                    self._setup_status_monitoring()
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ 集成失败: {e}")
            return False
    
    def _setup_agent_core(self):
        """设置Agent核心系统"""
        try:
            from Agent.core import AgentCore
            
            self.agent_core = AgentCore()
            
            print(f"🤖 Agent核心已启动，加载模块: {len(self.agent_core.modules)} 个")
            
            # 寻找pet_action模块
            for module in self.agent_core.modules:
                if hasattr(module, 'action_executor'):
                    self.pet_action_module = module
                    print(f"🎭 找到pet_action模块: {module.__class__.__name__}")
                    break
            
            if not self.pet_action_module:
                print("❌ 未找到pet_action模块")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 设置Agent核心失败: {e}")
            return False
    
    def _connect_pet_action_module(self):
        """连接pet_action模块到DyberPet"""
        try:
            if not self.pet_action_module or not self.pet_widget:
                return False
            
            # 手动连接到DyberPet
            success = self.pet_action_module.connect_to_dyberpet(
                self.dyberpet_app, 
                self.pet_widget
            )
            
            # 确保全局桥接器也连接到同一个实例
            from Agent.modules.pet_action.dyberpet_bridge import get_dyberpet_bridge
            global_bridge = get_dyberpet_bridge()
            global_success = global_bridge.connect_to_dyberpet(self.dyberpet_app, self.pet_widget)
            print(f"🌉 全局桥接器连接结果: {global_success}")
            
            if success:
                print("🔗 pet_action模块已连接到DyberPet")
                
                # 测试连接
                test_result = self.pet_action_module.handle_message("现在的状态")
                print(f"📋 连接测试结果: {test_result}")
                
                return True
            else:
                print("❌ pet_action模块连接失败")
                return False
                
        except Exception as e:
            print(f"❌ 连接pet_action模块失败: {e}")
            return False
    
    def _setup_status_monitoring(self):
        """设置状态监听"""
        try:
            # 连接DyberPet的信号到Agent系统
            if hasattr(self.pet_widget, 'hp_updated'):
                self.pet_widget.hp_updated.connect(self._on_hp_changed)
            
            if hasattr(self.pet_widget, 'fv_updated'):
                self.pet_widget.fv_updated.connect(self._on_fv_changed)
            
            if hasattr(self.pet_widget, 'change_note'):
                self.pet_widget.change_note.connect(self._on_pet_changed)
            
            print("🔔 状态监听已设置")
            
        except Exception as e:
            print(f"⚠️ 设置状态监听失败: {e}")
    
    def _on_hp_changed(self, hp):
        """HP变化回调"""
        print(f"💖 HP变化: {hp}")
        if self.pet_action_module:
            # 通知pet_action模块HP变化
            pass
    
    def _on_fv_changed(self, fv, level):
        """好感度变化回调"""
        print(f"💝 好感度变化: {fv} (等级: {level})")
        if self.pet_action_module:
            # 通知pet_action模块好感度变化
            pass
    
    def _on_pet_changed(self):
        """宠物切换回调"""
        if self.pet_widget:
            new_pet = getattr(self.pet_widget, 'curr_pet_name', 'Unknown')
            print(f"🔄 宠物切换到: {new_pet}")
            
            if self.pet_action_module:
                # 重新检查DyberPet连接状态
                self.pet_action_module._check_dyberpet_connection()
    
    def execute_action_from_external(self, action_command: str) -> str:
        """
        从外部执行动作（用于其他模块调用）
        
        Args:
            action_command: 动作命令
            
        Returns:
            str: 执行结果
        """
        if not self.integration_active or not self.pet_action_module:
            return "❌ Agent-DyberPet集成未激活"
        
        try:
            result = self.pet_action_module.handle_message(action_command)
            return result or "✅ 动作已执行"
        except Exception as e:
            return f"❌ 执行动作失败: {e}"
    
    def get_integration_status(self) -> dict:
        """获取集成状态信息"""
        return {
            "integration_active": self.integration_active,
            "dyberpet_connected": self.pet_widget is not None,
            "agent_core_loaded": self.agent_core is not None,
            "pet_action_module_found": self.pet_action_module is not None,
            "current_pet": getattr(self.pet_widget, 'curr_pet_name', None) if self.pet_widget else None,
            "bridge_status": self.pet_action_module.action_executor.get_dyberpet_connection_status().value if self.pet_action_module else None
        }
    
    def shutdown(self):
        """关闭集成系统"""
        try:
            if self.pet_action_module and hasattr(self.pet_action_module, 'action_executor'):
                self.pet_action_module.action_executor.stop()
            
            self.integration_active = False
            print("🔌 DyberPet-Agent集成已关闭")
            
        except Exception as e:
            print(f"⚠️ 关闭集成系统时出错: {e}")


# 全局集成管理器实例
_integration_manager = None


def get_integration_manager() -> DyberPetAgentIntegration:
    """获取全局集成管理器"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = DyberPetAgentIntegration()
    return _integration_manager


def integrate_agent_with_dyberpet(dyberpet_app):
    """
    便捷函数：将Agent系统与DyberPet集成
    
    Args:
        dyberpet_app: DyberPetApp实例
        
    Returns:
        bool: 集成是否成功
    """
    manager = get_integration_manager()
    return manager.integrate_with_dyberpet(dyberpet_app)


def execute_agent_action(action_command: str) -> str:
    """
    便捷函数：通过Agent执行宠物动作
    
    Args:
        action_command: 动作命令
        
    Returns:
        str: 执行结果
    """
    manager = get_integration_manager()
    return manager.execute_action_from_external(action_command)


def get_agent_status() -> dict:
    """便捷函数：获取Agent集成状态"""
    manager = get_integration_manager()
    return manager.get_integration_status()


# ============ DyberPet启动时的自动集成 ============

def auto_integrate_on_startup():
    """DyberPet启动时自动尝试集成Agent"""
    try:
        # 等待一段时间让DyberPet完全初始化
        time.sleep(2)
        
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        
        if app and hasattr(app, 'p'):
            print("🚀 检测到DyberPet启动，开始自动集成Agent...")
            
            success = integrate_agent_with_dyberpet(app)
            
            if success:
                print("🎉 Agent自动集成成功！")
                
                # 显示集成状态
                status = get_agent_status()
                print(f"📊 集成状态: {status}")
                
            else:
                print("❌ Agent自动集成失败")
        else:
            print("💡 未检测到DyberPet应用")
            
    except Exception as e:
        print(f"❌ 自动集成异常: {e}")


def start_auto_integration_monitor():
    """启动自动集成监视器"""
    monitor_thread = threading.Thread(
        target=auto_integrate_on_startup, 
        daemon=True,
        name="AgentIntegrationMonitor"
    )
    monitor_thread.start()
    print("🔍 Agent集成监视器已启动")


# ============ 测试函数 ============

def test_integration():
    """测试集成功能"""
    print("🧪 测试DyberPet-Agent集成")
    
    status = get_agent_status()
    print(f"📊 当前状态: {status}")
    
    if status["integration_active"]:
        print("\n🎭 测试动作执行:")
        
        test_commands = [
            "现在的状态",
            "让小猫睡觉",
            "走路",
            "你有什么能力"
        ]
        
        for cmd in test_commands:
            print(f"\n📝 执行命令: {cmd}")
            result = execute_agent_action(cmd)
            print(f"   结果: {result}")
    else:
        print("❌ 集成未激活，无法测试")


if __name__ == "__main__":
    # 如果直接运行此脚本，启动自动集成监视器
    print("🚀 启动DyberPet-Agent集成系统")
    start_auto_integration_monitor()
    
    # 保持脚本运行
    try:
        while True:
            time.sleep(10)
            
            # 定期检查集成状态
            status = get_agent_status()
            if status["integration_active"]:
                print(f"✅ 集成正常运行 - 当前宠物: {status['current_pet']}")
            else:
                print("⏳ 等待DyberPet启动...")
                
    except KeyboardInterrupt:
        print("\n🛑 用户中断，关闭集成系统")
        manager = get_integration_manager()
        manager.shutdown() 