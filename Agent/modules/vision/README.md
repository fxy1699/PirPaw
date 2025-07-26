# Vision Module - 视觉识别与屏幕分析模块

## 📖 概述

Vision Module 是 PirPaw Agent 系统的视觉识别模块，专注于屏幕截取、图像分析和文字识别（OCR）。它可以自动截取用户屏幕，分析界面内容，提取文字信息，辅助实现智能屏幕理解和自动化。

## 🎯 主要功能

### 核心功能
- **屏幕截取**：自动或手动截取全屏或指定区域
- **图像分析**：对截取的屏幕进行内容理解和结构分析
- **文字识别（OCR）**：提取屏幕中的文字信息
- **界面内容识别**：识别界面元素、代码、文档、错误信息等
- **快捷键支持**：支持F1快捷键一键截图

### 可选功能
- **自定义分析类型**：支持通用、代码、文档、错误、界面等多种分析模式
- **区域截屏**：支持自定义区域截图

## 🚀 快速开始

### 安装依赖

```bash
# 基础依赖
pip install pyautogui pillow

# OCR功能（可选）
pip install paddleocr

# 快捷键监听（可选）
pip install pynput
```

### 基本使用

```python
from Agent.modules.vision import VisionModule

# 创建模块实例
vision_module = VisionModule()

# 初始化配置
config = {
    'ocr_enabled': True,  # 启用OCR文字识别
    'image_analysis_enabled': True  # 启用图像理解
}

# 设置模块
vision_module.setup(config)

# 截取屏幕
screenshot = vision_module.capture_screen()

# 分析截图内容
result = vision_module.analyze_screenshot(screenshot, "请分析当前界面")
print(result)
```

## ⚙️ 配置选项

### 基础配置

```json
{
    "ocr_enabled": true,
    "image_analysis_enabled": true,
    "hotkey_enabled": true
}
```

### 配置说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `ocr_enabled` | bool | true | 启用OCR文字识别功能 |
| `image_analysis_enabled` | bool | true | 启用图像理解功能 |
| `hotkey_enabled` | bool | true | 启用F1快捷键截图 |

## 📋 API 接口

### 核心方法

#### `capture_screen(region=None)`
截取屏幕（可选区域）
```python
screenshot = vision_module.capture_screen()
# 返回: PIL.Image对象
```

#### `analyze_screenshot(screenshot, user_message)`
分析截图内容
```python
result = vision_module.analyze_screenshot(screenshot, "分析界面")
# 返回: 分析结果字符串
```

#### `extract_text(image)`
提取图片中的文字（OCR）
```python
text = vision_module.extract_text(screenshot)
# 返回: 文字内容字符串
```

## 🔧 Function Call 接口

模块支持通过 Function Call 方式调用，提供以下功能：

### 可用函数

1. **capture_screen** - 截取屏幕并分析
2. **analyze_image** - 分析已有截图或图片内容
3. **extract_text** - 提取图片中的文字
4. **simple_screenshot** - 快速截屏并保存

### 使用示例

```python
# 获取函数定义
functions = vision_module.get_function_definitions()

# 调用函数
result = vision_module.call_function("capture_screen", {"analysis_type": "general"})
```

## 🛠️ 开发者指南

### 模块结构

```
vision/
├── __init__.py          # 模块导出
├── module.py           # 主要实现
└── README.md           # 本文档
```

### 核心类

#### `VisionModule`
继承自 `BaseModule`，实现屏幕截取与视觉分析的核心类。

### 扩展开发

#### 添加新的分析类型

```python
def custom_analysis(self, image, user_message):
    """自定义分析逻辑"""
    # 实现你的分析逻辑
    return analysis_result
```

#### 添加新的OCR引擎

```python
def _init_ocr(self):
    """自定义OCR引擎初始化"""
    # 替换为你喜欢的OCR库
    self.ocr_engine = ...
```

### 错误处理

- **依赖缺失**: 提供清晰的安装指导
- **截图失败**: 返回详细错误信息
- **OCR失败**: 自动降级为无OCR模式
- **资源清理**: 自动释放资源

## 🔒 隐私安全

### 隐私保护措施

1. **本地处理**: 截图和分析均在本地完成，不上传服务器
2. **临时存储**: 截图仅临时保存，处理后可自动删除
3. **可控访问**: 用户可随时启用/禁用模块

### 权限说明

- **屏幕访问**: 需要操作系统授权
- **文件读写**: 仅用于保存临时截图

## 🐛 常见问题

#### 1. 截图失败
```
错误: 未安装pyautogui
解决: pip install pyautogui
```

#### 2. OCR功能不可用
```
错误: OCR引擎初始化失败
解决: pip install paddleocr
```

#### 3. 快捷键无效
```
错误: 快捷键注册失败
解决: pip install pynput
```

#### 4. 权限不足
```
错误: 操作系统未授权屏幕访问
解决: 检查系统隐私设置，允许屏幕录制/截图
```