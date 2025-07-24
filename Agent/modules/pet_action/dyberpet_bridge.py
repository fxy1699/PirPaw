"""
DyberPet 桥接器 (DyberPet Bridge)
实现Agent的pet_action模块与DyberPet主框架的实际接入
"""

import os
import sys
import threading
import time
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum

# 添加DyberPet路径到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
dyberpet_path = os.path.join(project_root, 'DyberPet')
if dyberpet_path not in sys.path:
    sys.path.insert(0, dyberpet_path)


class DyberPetBridgeError(Exception):
    """DyberPet桥接器异常"""
    pass


class ConnectionStatus(Enum):
    """连接状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class PetState:
    """宠物状态信息"""
    name: str
    current_action: str = "default"
    hp: int = 100
    fv: int = 100
    position: tuple = (0, 0)
    available_actions: List[str] = None
    is_active: bool = True


class DyberPetBridge:
    """DyberPet桥接器 - 连接Agent和DyberPet主框架"""
    
    def __init__(self):
        """初始化桥接器"""
        self.status = ConnectionStatus.DISCONNECTED
        self.pet_widget = None
        self.app_instance = None
        self.current_pet_state = None
        self.action_callbacks = {}
        self.status_callbacks = []
        
        # 线程锁
        self._lock = threading.Lock()
        
        print("🌉 DyberPet桥接器初始化完成")
    
    def connect_to_dyberpet(self, app_instance=None, pet_widget=None) -> bool:
        """
        连接到DyberPet实例
        
        Args:
            app_instance: DyberPetApp实例
            pet_widget: PetWidget实例
            
        Returns:
            bool: 连接是否成功
        """
        try:
            self.status = ConnectionStatus.CONNECTING
            print("🔗 正在连接到DyberPet主框架...")
            
            # 方式1: 直接传入实例
            if app_instance and pet_widget:
                self.app_instance = app_instance
                self.pet_widget = pet_widget
                print("✅ 使用传入的DyberPet实例")
            
            # 方式2: 尝试从全局变量或模块中获取
            elif self._try_find_dyberpet_instance():
                print("✅ 自动发现DyberPet实例")
            
            # 方式3: 创建新的连接
            else:
                print("💡 未找到运行中的DyberPet实例，使用模拟模式")
                self.status = ConnectionStatus.DISCONNECTED
                return False
            
            # 验证连接
            if self._validate_connection():
                self.status = ConnectionStatus.CONNECTED
                self._setup_callbacks()
                self._update_pet_state()
                print("🎉 成功连接到DyberPet主框架！")
                return True
            else:
                self.status = ConnectionStatus.ERROR
                print("❌ DyberPet连接验证失败")
                return False
                
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            print(f"❌ 连接DyberPet失败: {e}")
            return False
    
    def _try_find_dyberpet_instance(self) -> bool:
        """尝试自动发现DyberPet实例"""
        try:
            # 方法1: 检查全局应用实例
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            
            if app and hasattr(app, 'p'):
                self.app_instance = app
                self.pet_widget = app.p
                return True
            
            # 方法2: 检查顶级窗口
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, '_show_act') and hasattr(widget, 'curr_pet_name'):
                        self.pet_widget = widget
                        self.app_instance = app
                        return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ 自动发现DyberPet实例失败: {e}")
            return False
    
    def _validate_connection(self) -> bool:
        """验证连接是否有效"""
        try:
            if not self.pet_widget:
                return False
            
            # 检查必要的方法是否存在
            required_methods = ['_show_act', '_change_pet']
            for method in required_methods:
                if not hasattr(self.pet_widget, method):
                    print(f"❌ PetWidget缺少必要方法: {method}")
                    return False
            
            # 检查宠物是否可用
            if hasattr(self.pet_widget, 'curr_pet_name'):
                print(f"🐾 当前宠物: {self.pet_widget.curr_pet_name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 连接验证异常: {e}")
            return False
    
    def _setup_callbacks(self):
        """设置回调函数"""
        try:
            # 如果有信号系统，可以连接状态变化信号
            if hasattr(self.pet_widget, 'hp_updated'):
                self.pet_widget.hp_updated.connect(self._on_hp_changed)
            
            if hasattr(self.pet_widget, 'fv_updated'):
                self.pet_widget.fv_updated.connect(self._on_fv_changed)
                
            print("🔔 已设置状态回调")
            
        except Exception as e:
            print(f"⚠️ 设置回调失败: {e}")
    
    def _update_pet_state(self):
        """更新宠物状态"""
        try:
            if not self.pet_widget:
                return
            
            with self._lock:
                self.current_pet_state = PetState(
                    name=getattr(self.pet_widget, 'curr_pet_name', 'Unknown'),
                    current_action=getattr(self.pet_widget, 'curr_act', 'default'),
                    hp=getattr(self.pet_widget, 'hp', 100),
                    fv=getattr(self.pet_widget, 'fv', 100),
                    position=self._get_position(),
                    available_actions=self._get_available_actions(),
                    is_active=True
                )
            
        except Exception as e:
            print(f"⚠️ 更新宠物状态失败: {e}")
    
    def _get_position(self) -> tuple:
        """获取宠物位置"""
        try:
            if hasattr(self.pet_widget, 'pos'):
                pos = self.pet_widget.pos()
                return (pos.x(), pos.y())
            return (0, 0)
        except:
            return (0, 0)
    
    def _get_available_actions(self) -> List[str]:
        """获取可用动作列表"""
        try:
            if hasattr(self.pet_widget, 'act_list'):
                return list(self.pet_widget.act_list.keys())
            return []
        except:
            return []
    
    # ============ 公共接口方法 ============
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        connected = (self.status == ConnectionStatus.CONNECTED and 
                    self.pet_widget is not None and 
                    self.app_instance is not None)
        
        if not connected:
            print(f"🔍 桥接器连接检查失败:")
            print(f"   状态: {self.status}")
            print(f"   pet_widget: {self.pet_widget is not None}")
            print(f"   app_instance: {self.app_instance is not None}")
        
        return connected
    
    def get_connection_status(self) -> ConnectionStatus:
        """获取连接状态"""
        return self.status
    
    def get_pet_state(self) -> Optional[PetState]:
        """获取当前宠物状态"""
        with self._lock:
            return self.current_pet_state
    
    def execute_action(self, action_name: str, **kwargs) -> bool:
        """
        执行宠物动作
        
        Args:
            action_name: 动作名称
            **kwargs: 额外参数
            
        Returns:
            bool: 执行是否成功
        """
        if not self.is_connected():
            print("❌ 未连接到DyberPet，无法执行动作")
            return False
        
        try:
            print(f"🎭 执行DyberPet动作: {action_name}")
            print(f"🔍 pet_widget: {self.pet_widget}")
            print(f"🔍 pet_widget类型: {type(self.pet_widget)}")
            
            # 调用DyberPet的动作执行方法
            if hasattr(self.pet_widget, '_show_act'):
                print(f"✅ 找到_show_act方法，开始调用")
                
                # 使用Qt的信号槽机制在主线程中安全调用
                try:
                    from PySide6.QtCore import QMetaObject, Qt
                    
                    # 检查是否在主线程中
                    from PySide6.QtCore import QThread
                    is_main_thread = QThread.currentThread() == self.app_instance.thread() if self.app_instance else True
                    print(f"🔍 当前线程是主线程: {is_main_thread}")
                    
                    if is_main_thread:
                        # 在主线程中直接调用
                        self.pet_widget._show_act(action_name)
                        print(f"🎯 主线程调用pet_widget._show_act('{action_name}')")
                    else:
                        # 在非主线程中使用队列调用
                        def safe_call():
                            self.pet_widget._show_act(action_name)
                            print(f"🎯 队列调用pet_widget._show_act('{action_name}')")
                        
                        QMetaObject.invokeMethod(
                            self.pet_widget,
                            safe_call,
                            Qt.QueuedConnection
                        )
                        print(f"📞 已排队调用pet_widget._show_act('{action_name}')")
                    
                except Exception as call_error:
                    print(f"❌ 调用_show_act失败: {call_error}")
                    import traceback
                    print(f"📋 调用错误详情: {traceback.format_exc()}")
                    raise call_error
                
                # 更新状态
                self._update_pet_state()
                
                # 执行回调
                if action_name in self.action_callbacks:
                    self.action_callbacks[action_name](True, f"动作 {action_name} 执行成功")
                
                print(f"✅ 动作 {action_name} 已发送到DyberPet")
                return True
            else:
                print("❌ PetWidget没有_show_act方法")
                print(f"🔍 PetWidget可用方法: {[method for method in dir(self.pet_widget) if not method.startswith('_')][:10]}")
                return False
                
        except Exception as e:
            print(f"❌ 执行动作失败: {e}")
            if action_name in self.action_callbacks:
                self.action_callbacks[action_name](False, str(e))
            return False
    
    def change_pet(self, pet_name: str) -> bool:
        """
        切换宠物
        
        Args:
            pet_name: 宠物名称
            
        Returns:
            bool: 切换是否成功
        """
        if not self.is_connected():
            print("❌ 未连接到DyberPet，无法切换宠物")
            return False
        
        try:
            print(f"🔄 切换宠物到: {pet_name}")
            
            if hasattr(self.pet_widget, '_change_pet'):
                self.pet_widget._change_pet(pet_name)
                self._update_pet_state()
                print(f"✅ 已切换到宠物: {pet_name}")
                return True
            else:
                print("❌ PetWidget没有_change_pet方法")
                return False
                
        except Exception as e:
            print(f"❌ 切换宠物失败: {e}")
            return False
    
    def register_action_callback(self, action_name: str, callback: Callable):
        """注册动作执行回调"""
        self.action_callbacks[action_name] = callback
    
    def register_status_callback(self, callback: Callable):
        """注册状态变化回调"""
        self.status_callbacks.append(callback)
    
    # ============ 信号回调方法 ============
    
    def _on_hp_changed(self, hp: int):
        """HP变化回调"""
        if self.current_pet_state:
            self.current_pet_state.hp = hp
            self._notify_status_callbacks('hp_changed', hp)
    
    def _on_fv_changed(self, fv: int, level: int):
        """好感度变化回调"""
        if self.current_pet_state:
            self.current_pet_state.fv = fv
            self._notify_status_callbacks('fv_changed', {'fv': fv, 'level': level})
    
    def _notify_status_callbacks(self, event_type: str, data: Any):
        """通知状态回调"""
        for callback in self.status_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"⚠️ 状态回调执行失败: {e}")
    
    def disconnect(self):
        """断开连接"""
        try:
            self.status = ConnectionStatus.DISCONNECTED
            self.pet_widget = None
            self.app_instance = None
            self.current_pet_state = None
            self.action_callbacks.clear()
            self.status_callbacks.clear()
            print("🔌 已断开DyberPet连接")
        except Exception as e:
            print(f"⚠️ 断开连接时出错: {e}")


# 全局桥接器实例
_global_bridge = None


def get_dyberpet_bridge() -> DyberPetBridge:
    """获取全局DyberPet桥接器实例"""
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = DyberPetBridge()
    return _global_bridge


def connect_to_dyberpet(app_instance=None, pet_widget=None) -> bool:
    """便捷函数：连接到DyberPet"""
    bridge = get_dyberpet_bridge()
    return bridge.connect_to_dyberpet(app_instance, pet_widget)


def execute_pet_action(action_name: str, **kwargs) -> bool:
    """便捷函数：执行宠物动作"""
    bridge = get_dyberpet_bridge()
    return bridge.execute_action(action_name, **kwargs)


def get_pet_status() -> Optional[PetState]:
    """便捷函数：获取宠物状态"""
    bridge = get_dyberpet_bridge()
    return bridge.get_pet_state()


# ============ 模拟模式支持 ============

class MockDyberPetBridge(DyberPetBridge):
    """模拟DyberPet桥接器 - 用于测试和开发"""
    
    def __init__(self):
        super().__init__()
        self.mock_actions = ['stand', 'walk', 'run', 'sleep', 'dance', 'jump']
        self.current_pet_state = PetState(
            name="MockPet",
            current_action="stand",
            hp=100,
            fv=80,
            position=(100, 100),
            available_actions=self.mock_actions,
            is_active=True
        )
    
    def connect_to_dyberpet(self, app_instance=None, pet_widget=None) -> bool:
        """模拟连接"""
        self.status = ConnectionStatus.CONNECTED
        print("🎭 模拟模式：已连接到虚拟DyberPet")
        return True
    
    def execute_action(self, action_name: str, **kwargs) -> bool:
        """模拟执行动作"""
        print(f"🎭 模拟执行动作: {action_name}")
        
        if action_name in self.mock_actions:
            self.current_pet_state.current_action = action_name
            print(f"✅ 模拟动作 {action_name} 执行成功")
            return True
        else:
            print(f"❌ 模拟模式不支持动作: {action_name}")
            return False
    
    def change_pet(self, pet_name: str) -> bool:
        """模拟切换宠物"""
        print(f"🎭 模拟切换宠物到: {pet_name}")
        self.current_pet_state.name = pet_name
        return True 