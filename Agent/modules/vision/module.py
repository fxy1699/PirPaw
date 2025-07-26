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
        self._hotkey_listener = None  # 新增：快捷键监听句柄
        
    def setup(self, config=None):
        """初始化视觉功能"""
        super().setup(config)
        
        try:
            # 检查依赖
            import pyautogui
            import PIL
            print(f"✅ {self.name} 模块依赖检查通过")
            
            # 可选：初始化OCR引擎
            if self.config.get('ocr_enabled', True):
                self._init_ocr()
                
            print(f"✅ {self.name} 初始化成功")

            # 注册全局快捷键（Ctrl+Alt+S）- 使用 pynput 替代 keyboard
            try:
                import threading
                from pynput import keyboard as pynput_keyboard  # pip install pynput
                def on_activate():
                    screenshot = self.capture_screen()
                    if screenshot:
                        print("📸 快捷键截图已保存！")
                    else:
                        print("❌ 快捷键截图失败！")
                def start_hotkey():
                    # 监听 F1
                    with pynput_keyboard.GlobalHotKeys({
                        '<f1>': on_activate
                    }) as h:
                        h.join()
                self._hotkey_listener = threading.Thread(target=start_hotkey, daemon=True)
                self._hotkey_listener.start()
                print("💡 已注册截图快捷键 F1 (pynput)")
            except Exception as e:
                print(f"⚠️ 快捷键注册失败: {e}")
                
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
            import paddleocr
            self.ocr_engine = paddleocr.PaddleOCR(use_angle_cls=True, lang='ch')
            print("💡 OCR功能需要额外配置")
        except Exception as e:
            print(f"⚠️ OCR引擎初始化失败: {e}")
    
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
        """截取屏幕并保存到screenshots文件夹"""
        try:
            import pyautogui
            import os
            from datetime import datetime

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
                        pass

            self.last_screenshot = screenshot

            # 保存到screenshots文件夹（按天分文件夹）
            save_dir = os.path.join(os.getcwd(), 'screenshots')
            day_folder = datetime.now().strftime('%Y%m%d')
            save_dir = os.path.join(save_dir, day_folder)
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(save_dir, f'screenshot_{timestamp}.png')
            screenshot.save(save_path)

            # 新增：自动复制到剪切板
            self._copy_image_to_clipboard(screenshot)

            return screenshot  # 如需返回路径可 return screenshot, save_path
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None

    def _copy_image_to_clipboard(self, pil_image):
        """将PIL图片复制到剪切板（支持Windows和macOS）"""
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Windows实现
                try:
                    import io
                    from PIL import Image
                    import win32clipboard
                    
                    output = io.BytesIO()
                    pil_image.save(output, format='BMP')
                    data = output.getvalue()[14:]  # Remove BMP header
                    output.close()
                    
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    print("✅ 截图已复制到Windows剪切板！")
                except ImportError:
                    # 如果win32clipboard不可用，尝试使用pyperclip
                    print("⚠️ win32clipboard不可用，跳过剪切板操作")
                    
            elif system == "Darwin":
                # macOS实现
                try:
                    from AppKit import NSPasteboard, NSPasteboardTypePNG, NSImage
                    from Foundation import NSData
                    import io

                    output = io.BytesIO()
                    pil_image.save(output, format='PNG')
                    data = output.getvalue()
                    output.close()

                    nsdata = NSData.dataWithBytes_length_(data, len(data))
                    image = NSImage.alloc().initWithData_(nsdata)
                    pb = NSPasteboard.generalPasteboard()
                    pb.clearContents()
                    pb.writeObjects_([image])
                    print("✅ 截图已复制到macOS剪切板！")
                except ImportError:
                    print("⚠️ macOS剪切板依赖不可用，跳过剪切板操作")
            else:
                # Linux等其他系统
                print(f"⚠️ {system}系统暂不支持剪切板操作")
                
        except Exception as e:
            print(f"⚠️ 复制图片到剪切板失败: {e}")
    
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
            result = self.ocr_engine.ocr(image)
            return self.process_ocr_result(result)
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
        # 移除快捷键监听（pynput 无需手动 unhook，但可尝试安全退出）
        # 若有更复杂的监听管理，可在此处补充
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
            },
            {
                "name": "simple_screenshot",
                "description": "快速截屏并保存，不进行任何分析或OCR处理",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "截图区域（可选），格式: 'x,y,width,height'，如 '100,100,800,600'"
                        }
                    },
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
        elif function_name == "simple_screenshot":
            return self._function_simple_screenshot(arguments)
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
    
    def _function_simple_screenshot(self, arguments: dict):
        """Function Call: 简单截屏"""
        region = arguments.get("region")
        
        # 解析region参数
        region_coords = None
        if region:
            try:
                coords = [int(x.strip()) for x in region.split(',')]
                if len(coords) == 4:
                    region_coords = tuple(coords)
            except:
                print(f"⚠️ 无效的区域参数: {region}")
        
        # 执行截屏
        from datetime import datetime
        screenshot = self.capture_screen(region_coords)
        
        if screenshot:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            size_info = f"{screenshot.size[0]}x{screenshot.size[1]}"
            return f"📸 截屏成功！\n🕒 时间: {timestamp}\n📐 尺寸: {size_info}\n💾 已保存到screenshots文件夹\n📋 已复制到剪切板"
        else:
            return "❌ 截屏失败，请检查系统权限"