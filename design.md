# DyberPet AI Agent系统设计文档

## 🎯 设计理念

基于**极简且适合多人协作**的原则，为DyberPet桌面宠物框架设计了一个轻量级AI Agent系统。该系统采用基于Qwen-Agent SDK的完整功能实现，同时保持开发的简单性和扩展性。

### 核心原则
- **模块独立**：每个人可以独立开发一个模块
- **接口统一**：所有模块遵循相同的简单接口
- **即插即用**：新模块加入零配置
- **故障隔离**：一个模块出错不影响其他模块
- **文档优先**：每个模块自说明

## 🏗️ 架构设计

### 1. **整体架构图**

```
DyberPet/
└── Agent/                          # AI系统总目录
    ├── __init__.py                 # 自动发现和注册模块
    ├── base_module.py              # 模块基类（统一接口）
    ├── core.py                     # 核心管理器
    ├── config.json                 # 全局配置文件
    ├── demo.py                     # 演示程序
    ├── README.md                   # 完整文档
    └── modules/                    # 功能模块目录
        ├── chat/                   # 智能对话模块
        │   ├── __init__.py
        │   └── module.py           # 基于Qwen-Agent实现
        ├── vision/                 # 屏幕分析模块
        │   ├── __init__.py
        │   └── module.py           # 屏幕截取+图像分析
        ├── camera/                 # 摄像头模块
        │   ├── __init__.py
        │   └── module.py           # 姿态识别+健康监控
        └── tools/                  # 系统工具模块
            ├── __init__.py
            └── module.py           # 时间+天气+系统信息
```

### 2. **分层架构设计**

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                            │
│  DyberPet主程序 → 右键菜单 → 聊天气泡 → 状态显示        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   Agent核心层                           │
│  AgentCore → 消息路由 → 模块调度 → 响应聚合             │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   功能模块层                            │
│  ChatModule │ VisionModule │ CameraModule │ ToolsModule │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   基础服务层                            │
│  Qwen-Agent SDK │ 图像处理 │ 摄像头API │ 系统API        │
└─────────────────────────────────────────────────────────┘
```

## 💡 核心设计

### 3. **模块接口设计**

#### 3.1 BaseModule基类
```python
class BaseModule:
    """超简单的模块基类，只需实现一个函数"""
    
    # 模块元信息
    name = "模块名称"
    description = "功能描述"
    author = "开发者姓名"
    version = "1.0.0"
    
    def handle_message(self, message, context=None):
        """核心接口：处理用户消息"""
        # 开发者只需实现这一个函数！
        if "关键词" in message:
            return "模块响应"
        return None  # 不处理此消息
```

#### 3.2 自动发现机制
```python
def auto_discover_modules():
    """扫描modules目录，自动加载所有模块"""
    for folder in modules_directory:
        try:
            # 动态导入 modules.{folder}.module
            # 查找BaseModule的子类
            # 自动实例化并注册
        except Exception:
            # 忽略错误模块，不影响其他模块
```

### 4. **核心管理器设计**

#### 4.1 AgentCore架构
```python
class AgentCore:
    """不到100行的核心管理器"""
    
    def __init__(self):
        self.modules = auto_discover_modules()  # 自动发现
        self.load_config()                      # 加载配置
        
    def process_message(self, message):
        """消息处理流程"""
        results = []
        for module in self.enabled_modules:
            try:
                response = module.handle_message(message)
                if response:
                    results.append(response)
            except Exception:
                # 故障隔离：模块出错不影响其他模块
                continue
        return results
```

#### 4.2 配置管理
```json
{
  "enabled_modules": ["chat", "vision", "camera", "tools"],
  "global_settings": {
    "language": "zh-CN",
    "debug_mode": false
  },
  "module_configs": {
    "chat": {
      "qwen_api_key": "sk-xxx",
      "model": "qwen-plus",
      "enable_thinking": true
    },
    "vision": {
      "auto_capture": false,
      "ocr_enabled": true
    }
  }
}
```

## 🔧 功能模块设计

### 5. **对话模块 (ChatModule)**

#### 5.1 基于Qwen-Agent完整实现
```python
class ChatModule(BaseModule):
    name = "智能对话"
    author = "开发者A"
    
    def setup(self, config):
        """初始化Qwen-Agent"""
        from qwen_agent.agents import Assistant
        
        self.agent = Assistant(
            llm={'model': 'qwen-plus', 'api_key': config['qwen_api_key']},
            system_message="你是可爱的桌面宠物小柏...",
            function_list=[],  # 可注册自定义工具
            files=[]
        )
    
    def handle_message(self, message, context=None):
        if any(keyword in message for keyword in ['聊天', '对话', '?', '你好']):
            # 调用Qwen-Agent处理
            response = self.agent.run([{'role': 'user', 'content': message}])
            return f"🤖 {response[-1]['content']}"
        return None
```

#### 5.2 功能特性
- ✅ **多轮对话**：保持对话上下文
- ✅ **深度思考**：启用thinking模式
- ✅ **工具调用**：可扩展外部工具
- ✅ **代码执行**：内置代码解释器
- ✅ **个性化**：宠物专属的对话风格

### 6. **视觉模块 (VisionModule)**

#### 6.1 屏幕分析实现
```python
class VisionModule(BaseModule):
    name = "屏幕分析"
    author = "开发者B"
    
    def handle_message(self, message, context=None):
        if any(keyword in message for keyword in ['看屏幕', '截图', '分析界面']):
            # 截取屏幕
            screenshot = self.capture_screen()
            # 分析内容
            analysis = self.analyze_screenshot(screenshot, message)
            return f"👁️ {analysis}"
        return None
    
    def capture_screen(self):
        import pyautogui
        return pyautogui.screenshot()
```

#### 6.2 功能特性
- 🖼️ **屏幕截取**：全屏或区域截图
- 📝 **文字识别**：OCR提取文本内容
- 🎯 **内容理解**：识别界面类型和内容
- 💻 **代码分析**：识别代码并提供建议
- 📄 **文档理解**：分析PDF、网页等内容

### 7. **摄像头模块 (CameraModule)**

#### 7.1 姿态监控实现
```python
class CameraModule(BaseModule):
    name = "姿态监控"
    author = "开发者C"
    
    def handle_message(self, message, context=None):
        if '姿态' in message or '坐姿' in message:
            pose_data = self.detect_pose()
            return self.analyze_posture(pose_data)
        elif '健康' in message:
            return self.check_health_status()
        return None
    
    def detect_pose(self):
        # 使用MediaPipe或OpenCV检测姿态
        return {"head_tilt": 5, "back_straight": False}
```

#### 7.2 功能特性
- 📷 **姿态检测**：实时监控用户姿态
- 💺 **坐姿分析**：评估坐姿健康度
- ⚠️ **健康提醒**：久坐、不良姿态警告
- 😴 **疲劳检测**：识别眨眼频率等
- 🤲 **手势识别**：支持手势控制（可选）

### 8. **工具模块 (ToolsModule)**

#### 8.1 系统工具实现
```python
class ToolsModule(BaseModule):
    name = "系统工具"
    author = "开发者D"
    
    def handle_message(self, message, context=None):
        if '时间' in message:
            return self.get_current_time()
        elif '天气' in message:
            return self.get_weather_info(message)
        elif '系统' in message:
            return self.get_system_info(message)
        return None
```

#### 8.2 功能特性
- ⏰ **时间查询**：当前时间、日期、星期
- 🌤️ **天气信息**：实时天气查询
- 💻 **系统监控**：CPU、内存、磁盘使用率
- 📁 **文件操作**：文件搜索、管理
- 🔧 **快捷工具**：计算器、单位转换等

## 🚀 集成方案

### 9. **集成到DyberPet主框架**

#### 9.1 最小侵入集成
```python
# 在DyberPet.py中添加（仅需几行代码）
from Agent.core import AgentCore

class DyberPet(QWidget):
    def __init__(self):
        super().__init__()
        # ... 现有初始化代码 ...
        
        # 一行代码启动AI系统
        self.ai_core = AgentCore()
    
    def show_ai_chat(self):
        """显示AI对话界面"""
        user_input = self.get_user_input()  # 获取用户输入
        responses = self.ai_core.process_message(user_input)
        for response in responses:
            self.show_response_bubble(response)
```

#### 9.2 右键菜单扩展
```python
# 在custom_roundmenu.py中添加AI菜单项
ai_menu = RoundMenu()
ai_menu.addAction("💬 聊天对话", self.start_chat)
ai_menu.addAction("👁️ 分析屏幕", self.analyze_screen)
ai_menu.addAction("📷 检查姿态", self.check_posture)
ai_menu.addAction("⚙️ AI设置", self.show_ai_settings)
```

### 10. **UI扩展设计**

#### 10.1 气泡对话界面
```python
class ChatBubble(QWidget):
    """聊天气泡组件"""
    def show_user_message(self, message):
        # 显示用户消息气泡
        
    def show_ai_response(self, response):
        # 显示AI回复气泡，支持打字机效果
        
    def show_thinking_process(self, thinking):
        # 显示AI思考过程（可选）
```

#### 10.2 状态指示器
```python
class AIStatusIndicator(QWidget):
    """AI状态指示器"""
    def show_processing(self):
        # 显示AI处理中状态
        
    def show_module_status(self, modules):
        # 显示各模块状态
```

## 👥 团队协作方案

### 11. **开发分工**

#### 11.1 并行开发策略
```
开发者A：对话模块 (chat/)
├── Qwen-Agent集成优化
├── 多轮对话逻辑
├── 工具调用扩展
└── 个性化对话风格

开发者B：视觉模块 (vision/)
├── 屏幕截取优化
├── OCR文字识别
├── 图像内容分析
└── UI元素检测

开发者C：摄像头模块 (camera/)
├── 姿态检测算法
├── 健康监控逻辑
├── 疲劳状态分析
└── 手势识别功能

开发者D：工具模块 (tools/)
├── 系统信息查询
├── 天气API集成
├── 文件操作工具
└── 实用小工具
```

#### 11.2 协作流程
```
1. 选择模块 → 2. 复制模板 → 3. 实现功能 → 4. 本地测试 → 5. 提交PR
```

### 12. **扩展机制**

#### 12.1 新模块开发模板
```python
# 5分钟创建新模块
class NewModule(BaseModule):
    name = "新功能"
    description = "功能描述"
    author = "你的名字"
    
    def setup(self, config):
        """可选：模块初始化"""
        pass
    
    def handle_message(self, message, context=None):
        """必须：消息处理逻辑"""
        if "触发词" in message:
            return "功能响应"
        return None
    
    def get_capabilities(self):
        """可选：返回功能列表"""
        return ["功能1", "功能2"]
```

#### 12.2 工具扩展机制
```python
# Chat模块可以调用其他模块的功能
class ChatModule(BaseModule):
    def handle_message(self, message, context=None):
        if "看屏幕" in message:
            # 调用视觉模块功能
            vision_module = self.get_module("vision")
            result = vision_module.capture_and_analyze()
            return f"🤖 根据屏幕内容，我看到：{result}"
```

## 📈 性能和优化

### 13. **性能考虑**

#### 13.1 资源管理
```python
# 配置中的资源限制
{
  "global_settings": {
    "max_response_length": 1000,
    "response_timeout": 30,
    "max_concurrent_requests": 3
  }
}
```

#### 13.2 错误处理
```python
def process_message(self, message):
    results = []
    for module in self.modules:
        try:
            response = module.handle_message(message)
            if response:
                results.append(response)
        except Exception as e:
            # 故障隔离：记录错误但不影响其他模块
            if self.debug_mode:
                results.append(f"⚠️ {module.name}模块出错: {e}")
    return results
```

### 14. **安全和隐私**

#### 14.1 隐私保护
```python
# 摄像头模块的隐私控制
class CameraModule(BaseModule):
    def setup(self, config):
        if config.get('privacy_mode', True):
            self.enabled = False  # 默认禁用摄像头
            
    def handle_message(self, message, context=None):
        if not self.enabled:
            return "🔒 摄像头功能处于隐私保护模式"
```

#### 14.2 数据安全
- 🔐 **本地处理**：敏感数据本地处理，不上传
- 🔑 **API密钥保护**：加密存储用户API密钥
- 📝 **对话记录**：用户可控制是否保存对话历史
- 🗑️ **数据清理**：定期清理临时数据和缓存

## 🎯 实施路线图

### 15. **开发阶段**

#### 阶段一：核心框架 (已完成)
- ✅ 基础架构搭建
- ✅ 模块自动发现系统
- ✅ 配置管理机制
- ✅ 演示程序

#### 阶段二：功能完善 (1-2周)
- 🔄 Chat模块：完善Qwen-Agent集成
- 🔄 Vision模块：添加OCR和图像分析
- 🔄 Camera模块：实现真实姿态检测
- 🔄 Tools模块：集成实际API服务

#### 阶段三：UI集成 (1周)
- 📋 集成到DyberPet主界面
- 📋 设计聊天气泡组件
- 📋 添加右键菜单选项
- 📋 状态指示和反馈

#### 阶段四：优化完善 (1周)
- 📋 性能优化和资源管理
- 📋 错误处理和日志系统
- 📋 用户体验优化
- 📋 文档完善和测试

### 16. **成功指标**

- 🎯 **开发效率**：新模块5分钟内可完成开发
- 🎯 **稳定性**：单个模块故障不影响系统运行
- 🎯 **可扩展性**：支持第三方开发者贡献模块
- 🎯 **用户体验**：响应时间<3秒，操作简单直观
- 🎯 **团队协作**：多人并行开发无冲突

---

## 📝 总结

这个设计基于**实用主义**和**协作优先**的原则，创建了一个真正简单易用的AI Agent系统。通过极简的接口设计和自动化的模块管理，让团队成员能够专注于功能实现而不是架构复杂性，同时保证了系统的扩展性和稳定性。

**核心价值**：让DyberPet从简单的桌面宠物升级为智能AI助手，同时保持开发的简单性和乐趣。

