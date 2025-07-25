import time
from Agent.base_module import BaseModule
import threading
import platform

# 检查依赖
try:
    if platform.system() == "Windows":
        import comtypes
        from .video_detect import VideoPlaybackDetector
        DEPENDENCIES_AVAILABLE = True
    else:
        # 非Windows系统不需要这个模块
        DEPENDENCIES_AVAILABLE = False
        print("⚠️ WatchTV模块仅支持Windows系统")
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"⚠️ WatchTV模块依赖缺失: {e}")
    print("💡 请安装: pip install comtypes pycaw")

class WatchTVModule(BaseModule):
    name = "看电视检测"
    description = "检测用户是否在看视频并触发宠物动作"
    version = "1.0.0"
    author = "开发者AAA"

    def __init__(self):
        super().__init__()
        self.thread = None
        self.running = False
        self.last_status = False
        self.agent_core_ref = None
        self.detector = None
        
        # 检查依赖是否可用
        if not DEPENDENCIES_AVAILABLE:
            self.initialized = False
            print(f"❌ {self.name} 模块因依赖缺失而禁用")
            return

    def setup(self, config=None):
        if not DEPENDENCIES_AVAILABLE:
            print(f"⚠️ {self.name} 模块跳过初始化（依赖不可用）")
            return
            
        super().setup(config)
        self.detector = VideoPlaybackDetector()
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
        print(f"[WatchTV] 监控线程已启动")

    def _monitor(self):
        while self.running:
            try:
                status = self.detector.is_any_video_playing()
                print(f"[WatchTV] 监测中，是否有视频播放：{status}")
                if not self.last_status and status:
                    self.agent_core_ref.process_message("让宠物看电视")
                    print(f"[WatchTV] 让宠物看电视")
                elif self.last_status and not status:
                    self.agent_core_ref.process_message("让宠物站着")
                    print(f"[WatchTV] 宠物不看电视了")
                self.last_status = status
                time.sleep(5)
            except Exception as e:
                print(f"[WatchTV] 监控异常: {e}")
                break

    def cleanup(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=3)
        super().cleanup()
        print(f"[WatchTV] 监控已停止")

    def set_agent_core(self, agent_core):
        self.agent_core_ref = agent_core

    def handle_message(self, message: str, context=None):
        return None

    def get_capabilities(self) -> list:
        return ["检测用户是否在看视频并触发宠物动作"]

    def get_function_definitions(self) -> list:
        return [
            {
                "name": "get_watch_status",
                "description": "获取当前是否在看视频",
                "parameters": {}
            }
        ]