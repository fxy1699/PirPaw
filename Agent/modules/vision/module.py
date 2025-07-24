from Agent.base_module import BaseModule
import base64
import io


class VisionModule(BaseModule):
    """视觉识别模块 - 屏幕截取和图像分析"""
    
    name = "屏幕分析"
    description = "截取用户屏幕并进行智能分析，理解屏幕内容"
    version = "1.0.0"
    author = "开发者B"
    
    def __init__(self):
        super().__init__()
        self.last_screenshot = None
        self.ocr_engine = None
        
    def setup(self, config=None):
        """初始化视觉功能"""
        super().setup(config)
        
        try:
            # 检查依赖
            import pyautogui
            print(f"✅ {self.name} 初始化成功")
            
            # 可选：初始化OCR引擎
            if self.config.get('ocr_enabled', True):
                self._init_ocr()
                
        except ImportError:
            print("❌ 未安装pyautogui，请运行: pip install pyautogui")
            self.enabled = False
        except Exception as e:
            print(f"❌ {self.name} 初始化失败: {e}")
            self.enabled = False
    
    def _init_ocr(self):
        """初始化OCR引擎"""
        try:
            # 可以使用PaddleOCR或其他OCR库
            # import paddleocr
            # self.ocr_engine = paddleocr.PaddleOCR(use_angle_cls=True, lang='ch')
            print("💡 OCR功能需要额外配置")
        except:
            print("⚠️ OCR引擎初始化失败")
    
    def handle_message(self, message, context=None):
        """处理视觉相关请求"""
        if not self.enabled:
            return None
        
        # 判断是否是视觉相关请求
        vision_keywords = ['看屏幕', '截图', '屏幕', '分析界面', '看看', '界面', '显示的', '当前']
        if not any(keyword in message for keyword in vision_keywords):
            return None
        
        try:
            # 截取屏幕
            screenshot = self.capture_screen()
            
            # 简单分析
            analysis_result = self.analyze_screenshot(screenshot, message)
            
            return f"👁️ {analysis_result}"
            
        except Exception as e:
            print(f"❌ 视觉处理失败: {e}")
            return f"👁️ 屏幕分析遇到问题: {str(e)}"
    
    def capture_screen(self, region=None):
        """截取屏幕"""
        try:
            import pyautogui
            
            # 设置截图区域
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                # 限制截图大小以节省资源
                max_size = self.config.get('max_image_size', [1920, 1080])
                screenshot = pyautogui.screenshot()
                
                # 如果图像太大，缩放它
                if screenshot.size[0] > max_size[0] or screenshot.size[1] > max_size[1]:
                    try:
                        from PIL import Image
                        screenshot.thumbnail(max_size, Image.LANCZOS)
                    except ImportError:
                        # 如果没有PIL，就不缩放
                        pass
            
            self.last_screenshot = screenshot
            return screenshot
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None
    
    def analyze_screenshot(self, screenshot, user_message):
        """分析截图内容"""
        if not screenshot:
            return "无法获取屏幕截图"
        
        # 基础分析
        analysis = f"已截取屏幕，图像大小: {screenshot.size[0]}x{screenshot.size[1]}"
        
        # OCR文字识别
        if self.config.get('ocr_enabled', True):
            text_content = self.extract_text(screenshot)
            if text_content:
                analysis += f"\n📝 识别到的文字: {text_content[:200]}..."
        
        # 简单的内容推测
        analysis += self.guess_content_type(user_message)
        
        return analysis
    
    def extract_text(self, image):
        """提取图像中的文字"""
        if not self.ocr_engine:
            return "OCR功能未启用"
        
        try:
            # 这里应该调用实际的OCR引擎
            # result = self.ocr_engine.ocr(image_array)
            # return self.process_ocr_result(result)
            return "需要配置OCR引擎才能识别文字"
        except Exception as e:
            return f"文字识别失败: {e}"
    
    def guess_content_type(self, user_message):
        """根据用户消息猜测要分析的内容类型"""
        if "代码" in user_message:
            return "\n💻 检测到可能在查看代码"
        elif "文档" in user_message or "PDF" in user_message:
            return "\n📄 检测到可能在查看文档"
        elif "网页" in user_message or "浏览器" in user_message:
            return "\n🌐 检测到可能在浏览网页"
        elif "错误" in user_message or "报错" in user_message:
            return "\n⚠️ 如有错误信息，建议仔细查看错误详情"
        else:
            return "\n💡 如需详细分析，请描述您想了解的具体内容"
    
    def get_capabilities(self):
        """返回模块能力"""
        capabilities = [
            "屏幕截取",
            "基础图像分析",
            "界面内容识别"
        ]
        
        if self.config.get('ocr_enabled'):
            capabilities.append("文字识别(OCR)")
        
        if self.config.get('image_analysis_enabled'):
            capabilities.append("图像理解")
            
        return capabilities
    
    def cleanup(self):
        """清理资源"""
        self.last_screenshot = None
        super().cleanup()

    # ============ Function Call 接口 ============
    
    def get_function_definitions(self) -> list:
        """获取Vision模块的Function Call工具定义"""
        return [
            {
                "name": "capture_screen",
                "description": "截取用户屏幕并进行基础分析，可以理解当前显示的内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "enum": ["general", "code", "document", "error", "interface"],
                            "description": "分析类型：general通用分析，code代码分析，document文档分析，error错误诊断，interface界面分析"
                        },
                        "region": {
                            "type": "string",
                            "description": "截图区域（可选），格式: 'x,y,width,height'，如 '100,100,800,600'"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "analyze_image",
                "description": "分析已有的截图或图像内容，提供详细的视觉信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "focus": {
                            "type": "string",
                            "description": "分析焦点，如'文字'、'界面元素'、'错误信息'、'代码'等"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "extract_text",
                "description": "从屏幕截图中提取文字内容（OCR功能）",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def call_function(self, function_name: str, arguments: dict):
        """调用Vision模块的具体功能"""
        if not self.enabled:
            raise RuntimeError(f"模块 {self.name} 已禁用")
        
        if function_name == "capture_screen":
            return self._function_capture_screen(arguments)
        elif function_name == "analyze_image":
            return self._function_analyze_image(arguments)
        elif function_name == "extract_text":
            return self._function_extract_text(arguments)
        else:
            raise ValueError(f"未知功能: {function_name}")
    
    def _function_capture_screen(self, arguments: dict):
        """Function Call: 截取屏幕"""
        analysis_type = arguments.get("analysis_type", "general")
        region_str = arguments.get("region")
        
        # 解析区域参数
        region = None
        if region_str:
            try:
                coords = [int(x.strip()) for x in region_str.split(',')]
                if len(coords) == 4:
                    region = tuple(coords)
            except:
                pass
        
        # 截取屏幕
        screenshot = self.capture_screen(region)
        if not screenshot:
            return "❌ 截图失败，可能是权限问题或系统不支持"
        
        # 根据分析类型进行分析
        if analysis_type == "general":
            result = self.analyze_screenshot(screenshot, "截取屏幕进行通用分析")
        elif analysis_type == "code":
            result = self.analyze_screenshot(screenshot, "分析代码界面") + "\n💻 建议关注语法高亮、错误标记、调试信息等"
        elif analysis_type == "document":
            result = self.analyze_screenshot(screenshot, "分析文档内容") + "\n📄 可以提取文字内容进行详细分析"
        elif analysis_type == "error":
            result = self.analyze_screenshot(screenshot, "分析错误信息") + "\n⚠️ 请重点关注红色错误提示、异常堆栈等信息"
        elif analysis_type == "interface":
            result = self.analyze_screenshot(screenshot, "分析用户界面") + "\n🎨 关注按钮、菜单、输入框等UI元素"
        else:
            result = self.analyze_screenshot(screenshot, f"进行{analysis_type}分析")
        
        return result
    
    def _function_analyze_image(self, arguments: dict):
        """Function Call: 分析图像"""
        focus = arguments.get("focus", "整体内容")
        
        if not self.last_screenshot:
            return "❌ 没有可分析的截图，请先截取屏幕"
        
        result = f"🔍 针对'{focus}'的图像分析:\n"
        result += self.analyze_screenshot(self.last_screenshot, f"分析{focus}")
        
        if "文字" in focus:
            text_content = self.extract_text(self.last_screenshot)
            result += f"\n📝 提取的文字内容: {text_content}"
        
        return result
    
    def _function_extract_text(self, arguments: dict):
        """Function Call: 提取文字"""
        if not self.last_screenshot:
            # 先截取屏幕
            screenshot = self.capture_screen()
            if not screenshot:
                return "❌ 无法截取屏幕进行文字提取"
        else:
            screenshot = self.last_screenshot
        
        text_content = self.extract_text(screenshot)
        return f"📝 从屏幕提取的文字内容:\n{text_content}" 