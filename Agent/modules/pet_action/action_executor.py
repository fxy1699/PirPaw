"""
动作执行接口系统 (ActionExecutor)
负责实际执行宠物动作，与DyberPet系统通信
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum


class ActionStatus(Enum):
    """动作执行状态"""
    PENDING = "pending"
    EXECUTING = "executing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ActionRequest:
    """动作执行请求"""
    action_name: str
    parameters: Dict[str, Any] = None
    priority: int = 1  # 1=低, 2=中, 3=高
    timeout: float = 30.0
    callback: Callable = None
    request_id: str = None


@dataclass
class ActionResult:
    """动作执行结果"""
    request_id: str
    action_name: str
    status: ActionStatus
    message: str = ""
    execution_time: float = 0.0
    error: str = None


class ActionExecutor:
    """动作执行管理器"""
    
    def __init__(self):
        """初始化动作执行器"""
        self.action_queue = Queue()
        self.current_action = None
        self.execution_history = []
        self.is_running = False
        self.worker_thread = None
        
        # DyberPet系统接口（通过回调函数设置）
        self.dyber_pet_interface = None
        self.pet_status_getter = None
        self.pet_info_getter = None
        
        # 状态追踪
        self.action_results = {}
        self.next_request_id = 1
        
        print("⚡ ActionExecutor 初始化完成")
    
    def set_dyber_pet_interface(self, interface_callback: Callable):
        """
        设置与DyberPet系统的接口
        
        Args:
            interface_callback: DyberPet接口回调函数
        """
        self.dyber_pet_interface = interface_callback
        print("🔗 DyberPet接口已连接")
    
    def set_pet_status_getter(self, status_getter: Callable):
        """设置宠物状态获取器"""
        self.pet_status_getter = status_getter
    
    def set_pet_info_getter(self, info_getter: Callable):
        """设置宠物信息获取器"""
        self.pet_info_getter = info_getter
    
    def start(self):
        """启动动作执行器"""
        if self.is_running:
            print("⚠️ ActionExecutor 已在运行")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("🚀 ActionExecutor 已启动")
    
    def stop(self):
        """停止动作执行器"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        print("🛑 ActionExecutor 已停止")
    
    def execute_action(self, action_name: str, parameters: Dict = None, 
                      priority: int = 1, timeout: float = 30.0,
                      callback: Callable = None) -> str:
        """
        执行单个动作
        
        Args:
            action_name: 动作名称
            parameters: 动作参数
            priority: 优先级 (1=低, 2=中, 3=高)
            timeout: 超时时间（秒）
            callback: 完成回调函数
        
        Returns:
            请求ID
        """
        request_id = f"req_{self.next_request_id}"
        self.next_request_id += 1
        
        request = ActionRequest(
            action_name=action_name,
            parameters=parameters or {},
            priority=priority,
            timeout=timeout,
            callback=callback,
            request_id=request_id
        )
        
        # 根据优先级插入队列
        self._enqueue_with_priority(request)
        
        print(f"📝 动作请求已提交: {action_name} (ID: {request_id})")
        return request_id
    
    def execute_action_sequence(self, actions: List[Dict], priority: int = 1) -> List[str]:
        """
        执行动作序列
        
        Args:
            actions: 动作列表，每个元素是包含action_name和parameters的字典
            priority: 整个序列的优先级
        
        Returns:
            请求ID列表
        """
        request_ids = []
        
        for i, action_info in enumerate(actions):
            action_name = action_info.get("action_name") or action_info.get("action")
            parameters = action_info.get("parameters", {})
            
            # 序列中的动作优先级递增，确保按顺序执行
            action_priority = priority + i * 0.1
            
            request_id = self.execute_action(
                action_name=action_name,
                parameters=parameters,
                priority=action_priority
            )
            request_ids.append(request_id)
        
        print(f"📋 动作序列已提交: {len(actions)} 个动作")
        return request_ids
    
    def get_action_status(self, request_id: str = None) -> Dict:
        """
        获取动作执行状态
        
        Args:
            request_id: 请求ID，如果为None则返回当前动作状态
        
        Returns:
            状态信息字典
        """
        if request_id:
            result = self.action_results.get(request_id)
            if result:
                return {
                    "request_id": result.request_id,
                    "action_name": result.action_name,
                    "status": result.status.value,
                    "message": result.message,
                    "execution_time": result.execution_time,
                    "error": result.error
                }
            else:
                return {"error": f"未找到请求ID: {request_id}"}
        else:
            # 返回当前状态
            return {
                "current_action": self.current_action.action_name if self.current_action else None,
                "queue_size": self.action_queue.qsize(),
                "is_running": self.is_running,
                "recent_results": [
                    {
                        "action": result.action_name,
                        "status": result.status.value,
                        "time": result.execution_time
                    }
                    for result in list(self.action_results.values())[-5:]
                ]
            }
    
    def stop_current_action(self) -> bool:
        """
        停止当前正在执行的动作
        
        Returns:
            是否成功停止
        """
        if self.current_action:
            print(f"🛑 停止当前动作: {self.current_action.action_name}")
            
            # 标记为取消
            result = ActionResult(
                request_id=self.current_action.request_id,
                action_name=self.current_action.action_name,
                status=ActionStatus.CANCELLED,
                message="用户取消",
                execution_time=0.0
            )
            self.action_results[self.current_action.request_id] = result
            
            # 通知DyberPet停止动作（如果有接口）
            if self.dyber_pet_interface:
                try:
                    self.dyber_pet_interface("stop_action", {})
                except Exception as e:
                    print(f"❌ 停止动作失败: {e}")
            
            self.current_action = None
            return True
        else:
            print("ℹ️ 当前没有正在执行的动作")
            return False
    
    def clear_queue(self):
        """清空动作队列"""
        queue_size = self.action_queue.qsize()
        
        # 清空队列
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except Empty:
                break
        
        print(f"🧹 已清空动作队列 ({queue_size} 个动作)")
    
    def preview_action(self, action_name: str) -> Dict:
        """
        预览动作信息（不实际执行）
        
        Args:
            action_name: 动作名称
        
        Returns:
            动作预览信息
        """
        preview_info = {
            "action_name": action_name,
            "supported": False,
            "description": "",
            "frame_count": 0,
            "duration": 0.0,
            "has_movement": False,
            "requirements": []
        }
        
        # 获取宠物信息
        if self.pet_info_getter:
            try:
                pet_info = self.pet_info_getter()
                if pet_info and "actions" in pet_info:
                    action_info = pet_info["actions"].get(action_name)
                    if action_info:
                        preview_info.update({
                            "supported": True,
                            "description": action_info.get("description", ""),
                            "frame_count": action_info.get("frame_count", 0),
                            "duration": action_info.get("frame_refresh", 0.5) * action_info.get("frame_count", 1),
                            "has_movement": action_info.get("has_movement", False)
                        })
            except Exception as e:
                print(f"⚠️ 获取动作预览失败: {e}")
        
        return preview_info
    
    def _enqueue_with_priority(self, request: ActionRequest):
        """按优先级插入队列（简化实现，使用普通队列）"""
        # 注意：这是简化实现，真正的优先级队列需要使用PriorityQueue
        self.action_queue.put(request)
    
    def _worker_loop(self):
        """工作线程主循环"""
        print("🔄 ActionExecutor 工作线程已启动")
        
        while self.is_running:
            try:
                # 获取下一个动作请求
                request = self.action_queue.get(timeout=1.0)
                self._execute_request(request)
                
            except Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                print(f"❌ 工作线程异常: {e}")
        
        print("🔄 ActionExecutor 工作线程已退出")
    
    def _execute_request(self, request: ActionRequest):
        """
        执行单个动作请求
        
        Args:
            request: 动作请求
        """
        print(f"▶️ 开始执行动作: {request.action_name}")
        
        self.current_action = request
        start_time = time.time()
        
        result = ActionResult(
            request_id=request.request_id,
            action_name=request.action_name,
            status=ActionStatus.EXECUTING
        )
        
        try:
            # 检查动作是否支持
            if not self._check_action_supported(request.action_name):
                raise Exception(f"不支持的动作: {request.action_name}")
            
            # 检查执行前置条件
            if not self._check_preconditions(request):
                raise Exception("不满足执行条件")
            
            # 调用DyberPet接口执行动作
            success = self._call_dyber_pet_action(request)
            
            if success:
                result.status = ActionStatus.COMPLETED
                result.message = f"动作 {request.action_name} 执行成功"
                print(f"✅ 动作执行成功: {request.action_name}")
            else:
                result.status = ActionStatus.FAILED
                result.message = "DyberPet执行失败"
                print(f"❌ 动作执行失败: {request.action_name}")
        
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
            result.message = f"执行异常: {e}"
            print(f"❌ 动作执行异常 {request.action_name}: {e}")
        
        finally:
            # 计算执行时间
            result.execution_time = time.time() - start_time
            
            # 保存结果
            self.action_results[request.request_id] = result
            
            # 调用回调函数
            if request.callback:
                try:
                    request.callback(result)
                except Exception as e:
                    print(f"⚠️ 回调函数异常: {e}")
            
            # 清理当前动作
            self.current_action = None
    
    def _check_action_supported(self, action_name: str) -> bool:
        """检查动作是否被当前宠物支持"""
        if not self.pet_info_getter:
            return True  # 无法检查，假设支持
        
        try:
            pet_info = self.pet_info_getter()
            if pet_info and "actions" in pet_info:
                return action_name in pet_info["actions"]
        except Exception as e:
            print(f"⚠️ 检查动作支持失败: {e}")
        
        return True  # 默认支持
    
    def _check_preconditions(self, request: ActionRequest) -> bool:
        """检查动作执行的前置条件"""
        # 检查宠物状态
        if self.pet_status_getter:
            try:
                status = self.pet_status_getter()
                hp = status.get("hp", 100)
                
                # 某些动作需要最低血量
                high_energy_actions = ["left_walk", "right_walk", "play", "jump"]
                if request.action_name in high_energy_actions and hp < 20:
                    print(f"⚠️ 血量过低 ({hp}%)，无法执行高强度动作")
                    return False
                    
            except Exception as e:
                print(f"⚠️ 检查宠物状态失败: {e}")
        
        return True
    
    def _call_dyber_pet_action(self, request: ActionRequest) -> bool:
        """
        调用DyberPet接口执行动作
        
        Args:
            request: 动作请求
        
        Returns:
            是否执行成功
        """
        if not self.dyber_pet_interface:
            print("⚠️ DyberPet接口未连接，模拟执行")
            time.sleep(0.5)  # 模拟执行时间
            return True
        
        try:
            # 调用DyberPet接口
            result = self.dyber_pet_interface("execute_action", {
                "action_name": request.action_name,
                "parameters": request.parameters
            })
            
            return result.get("success", False)
            
        except Exception as e:
            print(f"❌ 调用DyberPet接口失败: {e}")
            return False
    
    def get_execution_stats(self) -> Dict:
        """获取执行统计信息"""
        total_requests = len(self.action_results)
        if total_requests == 0:
            return {"total_requests": 0}
        
        status_counts = {}
        total_time = 0.0
        
        for result in self.action_results.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            total_time += result.execution_time
        
        return {
            "total_requests": total_requests,
            "status_distribution": status_counts,
            "average_execution_time": total_time / total_requests,
            "queue_size": self.action_queue.qsize(),
            "is_running": self.is_running
        } 