import multiprocessing
import time
from Agent.base_module import BaseModule
import importlib

# 假设 is_any_video_playing 已经在 Agent/modules/watchtv/video_detect.py 中实现
from .video_detect import is_any_video_playing

class WatchTVModule(BaseModule):
    """
    看电视检测模块 - 检测用户是否在看视频并触发宠物动作
    """
    name = "看电视检测"
    description = "检测用户是否在看视频并触发宠物动作"
    version = "1.0.0"
    author = "开发者AAA"

    def __init__(self):
        super().__init__()
        self.process = None
        self.last_status = False
        self.running = multiprocessing.Event()
        self.agent_core_ref = None

    def setup(self, config=None):
        super().setup(config)
        self.running.set()
        self.process = multiprocessing.Process(target=self._monitor)
        self.process.start()
        print(f"[WatchTV] 监控进程已启动")

    def _monitor(self):
        while self.running.is_set():
            status = is_any_video_playing()
            if not self.last_status and status:
                # 状态从未看->在看，触发 watch_tv
                self.agent_core_ref.handle_message("让宠物看电视")
                print(f"[WatchTV] 让宠物看电视")
            elif self.last_status and not status:
                # 状态从在看->未看，触发 default
                self.pet_action.handle_message("让小猫站着")
                print(f"[WatchTV] 宠物不看电视了")
            self.last_status = status
            time.sleep(5)  # 每5秒检测一次

    def cleanup(self):
        self.running.clear()
        if self.process is not None:
            self.process.terminate()
            self.process.join()
        super().cleanup()
        print(f"[WatchTV] 监控进程已关闭") 
    
    def set_agent_core(self, agent_core):
        """设置AgentCore引用，用于跨模块调用"""
        self.agent_core_ref = agent_core

    def handle_message(self, message: str, context=None):
        """
        不提供 handle message
        """
        return None

    def get_capabilities(self) -> list:
        return [
            "检测用户是否在看视频并触发宠物动作"
        ]

    def get_function_definitions(self) -> list:
        return [
            {
                "name": "get_watch_status",
                "description": "获取当前是否在看视频",
                "parameters": []
            }
        ]