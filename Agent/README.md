# DyberPet Agent系统

## 🎯 简介

这是一个**极简且适合多人协作**的AI Agent架构，专为DyberPet桌面宠物框架设计。每个开发者只需要实现一个简单的函数，就可以为系统添加新功能。

## 🚀 特点

- ✅ **零学习成本**：开发者只需了解一个函数接口
- ✅ **并行开发**：多人可以同时开发不同模块
- ✅ **即插即用**：新模块自动被发现和加载
- ✅ **故障隔离**：一个模块出错不影响其他模块
- ✅ **配置简单**：统一的JSON配置文件

## 📁 目录结构

```
Agent/
├── __init__.py           # 自动发现模块
├── base_module.py        # 模块基类
├── core.py              # 核心管理器
├── config.json          # 配置文件
├── demo.py              # 演示程序
├── README.md            # 说明文档
└── modules/             # 功能模块目录
    ├── chat/            # 对话模块
    ├── vision/          # 视觉模块
    ├── camera/          # 摄像头模块
    └── tools/           # 工具模块
```

## 🔧 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install qwen-agent pyautogui psutil

# 可选依赖（根据需要安装）
pip install opencv-python pillow  # 摄像头和图像处理
pip install paddleocr             # OCR文字识别
pip install mediapipe            # 姿态检测
```

### 2. 配置API密钥

编辑 `config.json` 文件，添加你的Qwen API密钥：

```json
{
  "module_configs": {
    "chat": {
      "qwen_api_key": "你的API密钥",
      "model": "qwen-plus"
    }
  }
}
```

### 3. 运行演示

```bash
python Agent/demo.py
```

### 4. 集成到DyberPet

在 `DyberPet.py` 中添加：

```python
from Agent.core import AgentCore

class DyberPet(QWidget):
    def __init__(self):
        super().__init__()
        # 现有代码...
        
        # 一行代码启动AI系统
        self.ai_core = AgentCore()
    
    def handle_user_input(self, message):
        """处理用户输入"""
        responses = self.ai_core.process_message(message)
        for response in responses:
            self.show_bubble(response)  # 显示气泡
```

## 👥 开发新模块

### 开发步骤

1. 在 `modules/` 目录下创建新文件夹（如 `weather/`）
2. 创建 `__init__.py` 和 `module.py`
3. 实现模块类
4. 重启程序，模块自动加载

### 模块模板

```python
# modules/新模块名/module.py
from Agent.base_module import BaseModule

class NewModule(BaseModule):
    name = "模块名称"
    description = "功能描述"
    author = "你的名字"
    version = "1.0.0"
    
    def handle_message(self, message, context=None):
        """处理消息的核心逻辑"""
        if "关键词" in message:
            # 你的处理逻辑
            return "模块响应"
        return None  # 不处理此消息
```

### 模块示例

```python
# 天气模块示例
class WeatherModule(BaseModule):
    name = "天气查询"
    author = "张三"
    
    def handle_message(self, message, context=None):
        if "天气" in message:
            return "🌤️ 今天晴天，22°C"
        return None
```

## 📋 现有模块

### 对话模块 (chat)
- 🤖 智能对话
- 🧠 基于Qwen-Agent
- 💬 多轮会话
- 🔧 工具调用

**触发词**：聊天、对话、?、你好、帮助

### 视觉模块 (vision)
- 👁️ 屏幕截取
- 📝 文字识别 (OCR)
- 🖼️ 图像分析
- 🎯 界面识别

**触发词**：看屏幕、截图、分析界面

### 摄像头模块 (camera)
- 📷 姿态检测
- 💺 坐姿分析
- ⚠️ 健康提醒
- 😴 疲劳检测

**触发词**：姿态、坐姿、健康、疲劳

### 工具模块 (tools)
- ⏰ 时间查询
- 🌤️ 天气信息
- 💻 系统监控
- 📁 文件操作

**触发词**：时间、天气、系统、文件

## 🛠️ 配置说明

### 全局配置

```json
{
  "enabled_modules": ["chat", "vision", "camera", "tools"],
  "global_settings": {
    "language": "zh-CN",
    "debug_mode": false
  }
}
```

### 模块配置

```json
{
  "module_configs": {
    "chat": {
      "qwen_api_key": "sk-xxx",
      "model": "qwen-plus",
      "enable_thinking": true
    },
    "vision": {
      "auto_capture": false,
      "ocr_enabled": true
    },
    "camera": {
      "privacy_mode": true,
      "pose_detection": true
    }
  }
}
```

## 🔍 调试技巧

### 启用调试模式

```json
{
  "global_settings": {
    "debug_mode": true
  }
}
```

### 查看模块状态

```python
from Agent.core import AgentCore

agent = AgentCore()
status = agent.get_system_status()
print(status)
```

### 测试单个模块

```python
# 直接测试模块
from Agent.modules.chat.module import ChatModule

module = ChatModule()
module.setup({'qwen_api_key': 'your-key'})
response = module.handle_message("你好")
print(response)
```

## 🚨 常见问题

### Q: 模块没有被发现
A: 检查模块目录结构，确保有 `__init__.py` 和 `module.py`

### Q: Qwen-Agent初始化失败
A: 检查API密钥配置，确保网络连接正常

### Q: 模块出错影响其他功能
A: 系统有故障隔离，一个模块出错不会影响其他模块

### Q: 如何禁用某个模块
A: 在 `config.json` 的 `enabled_modules` 中移除模块名

## 🤝 协作指南

### 分工建议
- **开发者A**：负责对话模块 (chat)
- **开发者B**：负责视觉模块 (vision)  
- **开发者C**：负责摄像头模块 (camera)
- **开发者D**：负责工具模块 (tools)

### 代码规范
1. 每个模块独立开发，避免依赖其他模块
2. 使用统一的错误处理和日志格式
3. 为模块添加详细的文档注释
4. 测试模块功能后再提交

### Git工作流
```bash
# 1. 创建功能分支
git checkout -b feature/weather-module

# 2. 开发模块
# 在 modules/weather/ 下开发

# 3. 测试功能
python Agent/demo.py

# 4. 提交代码
git add modules/weather/
git commit -m "添加天气查询模块"

# 5. 推送并创建PR
git push origin feature/weather-module
```

## 📝 更新日志

### v1.0.0
- ✅ 基础架构完成
- ✅ 四个核心模块实现
- ✅ 自动模块发现
- ✅ 配置管理系统
- ✅ 演示程序

## 📞 支持

如果在使用过程中遇到问题，请：

1. 查看调试日志
2. 检查配置文件
3. 运行演示程序测试
4. 查看模块状态信息

---

**Happy Coding! 🎉** 