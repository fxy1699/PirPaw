from Agent.base_module import BaseModule
import time


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
        
    def setup(self, config=None):
        """初始化摄像头功能"""
        super().setup(config)
        
        # 检查隐私模式
        if self.config.get('privacy_mode', True):
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
        """检查用户姿态"""
        if not self._can_capture():
            return "📷 暂时无法检测姿态"
        
        try:
            # 模拟姿态检测
            pose_data = self._detect_pose()
            
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
    
    def _detect_pose(self):
        """检测用户姿态"""
        if not self.pose_detector:
            return None
        
        try:
            # 这里应该调用实际的姿态检测
            # 返回模拟数据
            return {
                "head_tilt": 5,  # 头部倾斜角度
                "shoulder_level": True,  # 肩膀是否水平
                "back_straight": False,  # 背部是否挺直
                "distance_to_screen": 60  # 到屏幕距离(cm)
            }
        except Exception as e:
            print(f"姿态检测失败: {e}")
            return None
    
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