from Agent.base_module import BaseModule
import time
import threading
import os
from datetime import datetime


class CameraModule(BaseModule):
    """摄像头识别模块 - 人体姿态识别和健康监控"""
    
    name = "姿态监控"
    description = "通过摄像头监控用户姿态，提供健康提醒和手势识别"
    version = "1.0.0"
    author = "开发者C"
    
    def __init__(self):
        super().__init__()
        self.camera = None
        self.pose_detector = None
        self.last_pose_check = 0
        self.sitting_start_time = None
        self._auto_check_thread = None
        self._auto_check_running = False
        
    def setup(self, config=None):
        """初始化摄像头功能"""
        super().setup(config)
        
        # 检查隐私模式
        if self.config.get('privacy_mode', False):
            print(f"🔒 {self.name} 处于隐私模式，需要用户授权才能启用")
            self.enabled = False
            return
        
        try:
            # 检查摄像头依赖
            import cv2
            print(f"✅ {self.name} 初始化成功")
            
            # 可选：初始化姿态检测
            if self.config.get('pose_detection', True):
                self._init_pose_detection()
                
        except ImportError:
            print("❌ 未安装opencv-python，请运行: pip install opencv-python")
            self.enabled = False
        except Exception as e:
            print(f"❌ {self.name} 初始化失败: {e}")
            self.enabled = False
        # 自动启动定时姿态检测
        if self.enabled:
            try:
                self.start_auto_pose_check()
            except Exception as e:
                print(f"❌ 自动姿态检测启动失败: {e}")
    def _init_pose_detection(self):
        """初始化姿态检测"""
        try:
            # 可以使用MediaPipe进行姿态检测
            import mediapipe as mp
            self.pose_detector = mp.solutions.pose.Pose()
            print("💡 姿态检测功能需要额外配置MediaPipe")
        except Exception as e:
            print(f"⚠️ 姿态检测初始化失败: {e}")
    
    def handle_message(self, message, context=None):
        """处理摄像头相关请求"""
        if not self.enabled:
            if self.config.get('privacy_mode', True):
                return "🔒 摄像头功能处于隐私保护模式，请在设置中启用"
            return None
        
        # 判断是否是摄像头相关请求
        camera_keywords = ['姿态', '坐姿', '健康', '摄像头', '监控', '疲劳', '久坐']
        if not any(keyword in message for keyword in camera_keywords):
            return None
        
        try:
            if '姿态' in message or '坐姿' in message:
                return self.check_posture()
            elif '健康' in message or '久坐' in message:
                return self.check_health_status()
            elif '疲劳' in message:
                return self.check_fatigue()
            else:
                return self.get_camera_status()
                
        except Exception as e:
            print(f"❌ 摄像头处理失败: {e}")
            return f"📷 摄像头分析遇到问题: {str(e)}"
    
    def check_posture(self):
        """检查用户姿态（集成拍照）"""
        if not self._can_capture():
            return "📷 暂时无法检测姿态"
        try:
            photo_path = self.capture_photo()
            if not photo_path:
                return "📷 拍照失败，无法检测姿态"
            pose_data = self._detect_pose(photo_path)
            if pose_data:
                return self._analyze_posture(pose_data)
            else:
                return "📷 未检测到用户，请确保坐在摄像头前"
        except Exception as e:
            return f"📷 姿态检测失败: {e}"
    
    def check_health_status(self):
        """检查健康状态"""
        current_time = time.time()
        
        # 模拟久坐检测
        if self.sitting_start_time is None:
            self.sitting_start_time = current_time
            return "💺 开始监控您的坐姿时间"
        
        sitting_duration = current_time - self.sitting_start_time
        sitting_minutes = int(sitting_duration / 60)
        
        if sitting_minutes > 60:
            return f"⚠️ 您已经坐了{sitting_minutes}分钟了，建议起来活动一下！"
        elif sitting_minutes > 30:
            return f"💡 您已经坐了{sitting_minutes}分钟，注意适当休息"
        else:
            return f"✅ 坐姿时间正常({sitting_minutes}分钟)"
    
    def check_fatigue(self):
        """检查疲劳状态"""
        if not self._can_capture():
            return "📷 无法检测疲劳状态"
        
        # 模拟疲劳检测
        fatigue_indicators = [
            "眨眼频率",
            "头部姿态",
            "面部表情"
        ]
        
        return f"👁️ 正在分析疲劳指标: {', '.join(fatigue_indicators)}\n💡 建议定期休息，保护视力"
    
    def get_camera_status(self):
        """获取摄像头状态"""
        if not self.enabled:
            return "📷 摄像头功能已禁用"
        
        status = "📷 摄像头状态:\n"
        status += f"• 隐私模式: {'开启' if self.config.get('privacy_mode') else '关闭'}\n"
        status += f"• 姿态检测: {'开启' if self.config.get('pose_detection') else '关闭'}\n"
        status += f"• 健康监控: {'开启' if self.config.get('health_monitoring') else '关闭'}"
        
        return status
    
    def _can_capture(self):
        """检查是否可以捕获摄像头"""
        return self.enabled and not self.config.get('privacy_mode', True)
    
    def _detect_pose(self, photo_path=None):
        """检测用户姿态（支持图片输入，暂为模拟）"""
        # 这里可以用MediaPipe等库分析photo_path
        # 暂时返回模拟数据
        return {
            "head_tilt": 5,  # 头部倾斜角度
            "shoulder_level": True,  # 肩膀是否水平
            "back_straight": False,  # 背部是否挺直
            "distance_to_screen": 60  # 到屏幕距离(cm)
        }
    
    def _analyze_posture(self, pose_data):
        """分析姿态数据"""
        analysis = "📊 姿态分析结果:\n"
        
        # 分析头部倾斜
        if abs(pose_data.get("head_tilt", 0)) > 15:
            analysis += "⚠️ 头部倾斜过度，建议调整坐姿\n"
        else:
            analysis += "✅ 头部姿态良好\n"
        
        # 分析肩膀水平
        if not pose_data.get("shoulder_level", True):
            analysis += "⚠️ 肩膀不够水平，注意保持平衡\n"
        else:
            analysis += "✅ 肩膀姿态正常\n"
        
        # 分析背部挺直
        if not pose_data.get("back_straight", True):
            analysis += "⚠️ 背部弯曲，建议挺直腰背\n"
        else:
            analysis += "✅ 背部姿态良好\n"
        
        # 分析距离
        distance = pose_data.get("distance_to_screen", 60)
        if distance < 50:
            analysis += "⚠️ 距离屏幕过近，建议保持50-70cm距离"
        elif distance > 80:
            analysis += "💡 距离屏幕较远，可以适当靠近"
        else:
            analysis += "✅ 与屏幕距离适中"
        
        return analysis
    
    def get_capabilities(self):
        """返回模块能力"""
        capabilities = []
        
        if self.config.get('pose_detection'):
            capabilities.extend([
                "姿态检测",
                "坐姿分析",
                "距离监控"
            ])
        
        if self.config.get('health_monitoring'):
            capabilities.extend([
                "久坐提醒",
                "健康监控",
                "疲劳检测"
            ])
        
        if self.config.get('gesture_recognition'):
            capabilities.append("手势识别")
            
        return capabilities
    
    def cleanup(self):
        """清理资源"""
        if self.camera:
            try:
                self.camera.release()
            except:
                pass
        super().cleanup()

    # ============ Function Call 接口 ============
    
    def get_function_definitions(self) -> list:
        """获取Camera模块的Function Call工具定义"""
        return [
            {
                "name": "check_posture",
                "description": "检查用户当前坐姿和姿态，分析头部、肩膀、背部姿态",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "check_health_status",
                "description": "检查用户健康状态，包括久坐时间和健康建议",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "check_fatigue",
                "description": "检查用户疲劳状态，分析眼部疲劳和精神状态",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_camera_status",
                "description": "获取摄像头功能状态和隐私设置信息",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "capture_photo",
                "description": "拍照并返回图片路径",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def call_function(self, function_name: str, arguments: dict):
        """调用Camera模块的具体功能"""
        print('call_function', function_name, arguments)
        if not self.enabled:
            if self.config.get('privacy_mode', True):
                raise RuntimeError("🔒 摄像头功能处于隐私保护模式，请在设置中启用")
            else:
                raise RuntimeError(f"模块 {self.name} 已禁用")
        
        if function_name == "check_posture":
            return self._function_check_posture(arguments)
        elif function_name == "check_health_status":
            return self._function_check_health_status(arguments)
        elif function_name == "check_fatigue":
            return self._function_check_fatigue(arguments)
        elif function_name == "get_camera_status":
            return self._function_get_camera_status(arguments)
        elif function_name == "capture_photo":
            return self._function_capture_photo(arguments)
        else:
            raise ValueError(f"未知功能: {function_name}")
    
    def _function_check_posture(self, arguments: dict):
        """Function Call: 检查姿态"""
        return self.check_posture()
    
    def _function_check_health_status(self, arguments: dict):
        """Function Call: 检查健康状态"""
        return self.check_health_status()
    
    def _function_check_fatigue(self, arguments: dict):
        """Function Call: 检查疲劳状态"""
        return self.check_fatigue()
    
    def _function_get_camera_status(self, arguments: dict):
        """Function Call: 获取摄像头状态"""
        return self.get_camera_status() 

    def _function_capture_photo(self, arguments: dict):
        """Function Call: 拍照并返回图片路径"""
        return self.capture_photo()

    def start_auto_pose_check(self, interval_minutes=3):
        """启动定时自动姿态检测"""
        if self._auto_check_thread and self._auto_check_thread.is_alive():
            print("[CameraModule] 自动姿态检测线程已在运行")
            return
        self._auto_check_running = True
        self._auto_check_thread = threading.Thread(target=self._auto_pose_check_loop, args=(interval_minutes,), daemon=True)
        self._auto_check_thread.start()
        print(f"[CameraModule] 已自动开启定时姿态检测（每{interval_minutes}分钟）")

    def stop_auto_pose_check(self):
        """停止自动姿态检测"""
        self._auto_check_running = False
        print("[CameraModule] 已停止自动姿态检测")

    def _auto_pose_check_loop(self, interval_minutes):
        while self._auto_check_running:
            if self.enabled:
                print("[CameraModule] 自动检测用户姿态...")
                result = self.check_posture()
                # 这里可以将result存储到日志、数据库，或推送到前端/通知
                print(f"[CameraModule] 姿态检测报告：\n{result}")
            time.sleep(interval_minutes * 60) 

    def capture_photo(self, save_path=None):
        """拍照并保存图片到指定路径，返回图片路径"""
        if not self.enabled:
            return None
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            # 丢弃前几帧，等待摄像头自动曝光
            for _ in range(5):
                cap.read()
                time.sleep(0.05)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                print("❌ 拍照失败，无法获取摄像头画面")
                return None
            if save_path is None:
                today = datetime.now().strftime("%Y%m%d")
                save_dir = os.path.join(os.getcwd(), "camera_photos", today)
                os.makedirs(save_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(save_dir, f"photo_{timestamp}.png")
            cv2.imwrite(save_path, frame)
            print(f"✅ 拍照成功，已保存到: {save_path}")
            return save_path
        except Exception as e:
            print(f"❌ 拍照异常: {e}")
            return None 