# Camera Module - 摄像头姿态监控模块

## 📖 概述

Camera Module 是 PirPaw Agent 系统的摄像头识别模块，专门用于人体姿态识别和健康监控。通过摄像头实时监控用户的坐姿、头部姿态、与屏幕的距离等，提供健康提醒和手势识别功能。

## 🎯 主要功能

### 核心功能
- **姿态检测**: 实时分析用户坐姿、头部、肩膀、背部姿态
- **健康监控**: 久坐提醒、疲劳检测、健康建议
- **距离监控**: 检测用户与屏幕的距离，预防近视
- **手势识别**: 识别用户手势，支持交互控制
- **自动检测**: 定时自动检测姿态，提供健康提醒

### 隐私保护
- **隐私模式**: 可配置的隐私保护模式，需要用户明确授权
- **本地处理**: 图像数据本地处理，保护用户隐私
- **可控访问**: 用户可随时启用/禁用摄像头功能

## 🚀 快速开始

### 安装依赖

```bash
# 基础依赖
pip install opencv-python

# AI姿态分析（可选）
pip install qwen-agent

# 姿态检测（可选）
pip install mediapipe
```

### 基本使用

```python
from Agent.modules.camera import CameraModule

# 创建模块实例
camera_module = CameraModule()

# 初始化配置
config = {
    'privacy_mode': False,  # 关闭隐私模式
    'pose_detection': True,  # 启用姿态检测
    'health_monitoring': True,  # 启用健康监控
    'gesture_recognition': True  # 启用手势识别
}

# 设置模块
camera_module.setup(config)

# 检查姿态
result = camera_module.check_posture()
print(result)
```

## ⚙️ 配置选项

### 基础配置

```json
{
    "privacy_mode": false,
    "pose_detection": true,
    "health_monitoring": true,
    "gesture_recognition": true,
    "auto_check_interval": 40,
    "camera_index": 0,
    "photo_quality": 0.8
}
```

### 配置说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `privacy_mode` | bool | true | 隐私保护模式，true时需用户授权 |
| `pose_detection` | bool | true | 启用姿态检测功能 |
| `health_monitoring` | bool | true | 启用健康监控功能 |
| `gesture_recognition` | bool | true | 启用手势识别功能 |
| `auto_check_interval` | int | 40 | 自动检测间隔（分钟） |
| `camera_index` | int | 0 | 摄像头设备索引 |
| `photo_quality` | float | 0.8 | 照片质量（0-1） |

## 📋 API 接口

### 核心方法

#### `check_posture()`
检查用户当前坐姿和姿态
```python
result = camera_module.check_posture()
# 返回: 姿态分析结果和建议
```

#### `check_health_status()`
检查用户健康状态
```python
result = camera_module.check_health_status()
# 返回: 健康状态报告和建议
```

#### `check_fatigue()`
检查用户疲劳状态
```python
result = camera_module.check_fatigue()
# 返回: 疲劳检测结果
```

#### `capture_photo(save_path=None)`
拍照并保存
```python
photo_path = camera_module.capture_photo("photo.jpg")
# 返回: 照片保存路径
```

#### `get_camera_status()`
获取摄像头状态
```python
status = camera_module.get_camera_status()
# 返回: 摄像头功能状态信息
```

### 自动检测控制

#### `start_auto_pose_check(interval_minutes=40)`
启动自动姿态检测
```python
camera_module.start_auto_pose_check(30)  # 每30分钟检测一次
```

#### `stop_auto_pose_check()`
停止自动姿态检测
```python
camera_module.stop_auto_pose_check()
```

## 🔧 Function Call 接口

模块支持通过 Function Call 方式调用，提供以下功能：

### 可用函数

1. **check_posture** - 检查用户姿态
2. **check_health_status** - 检查健康状态  
3. **check_fatigue** - 检查疲劳状态
4. **get_camera_status** - 获取摄像头状态
5. **capture_photo** - 拍照

### 使用示例

```python
# 获取函数定义
functions = camera_module.get_function_definitions()

# 调用函数
result = camera_module.call_function("check_posture", {})
```

## 🛠️ 开发者指南

### 模块结构

```
camera/
├── __init__.py          # 模块导出
├── module.py           # 主要实现
└── README.md           # 本文档
```

### 核心类

#### `CameraModule`
继承自 `BaseModule`，实现摄像头功能的核心类。

### 扩展开发

#### 添加新的姿态检测算法

```python
def _custom_pose_detection(self, image):
    """自定义姿态检测算法"""
    # 实现你的检测逻辑
    return pose_data
```

#### 添加新的健康指标

```python
def check_custom_health_metric(self):
    """检查自定义健康指标"""
    # 实现你的健康检测逻辑
    return health_report
```

### 错误处理

模块包含完善的错误处理机制：

- **摄像头访问失败**: 自动降级到无摄像头模式
- **依赖缺失**: 提供清晰的安装指导
- **隐私保护**: 用户未授权时拒绝访问
- **资源清理**: 自动释放摄像头资源

## 🔒 隐私安全

### 隐私保护措施

1. **默认隐私模式**: 默认启用隐私保护，需要用户明确授权
2. **本地处理**: 图像数据在本地处理，不上传服务器
3. **临时存储**: 照片临时存储，处理完成后自动删除
4. **可控访问**: 用户可随时启用/禁用功能

### 权限说明

- **摄像头访问**: 需要用户明确授权
- **文件读写**: 仅用于保存临时照片
- **网络访问**: 仅用于AI分析（可选功能）

## 🐛 故障排除

### 常见问题

#### 1. 摄像头无法访问
```
错误: 找不到使用数据文件
解决: 检查摄像头权限，确保应用有摄像头访问权限
```

#### 2. OpenCV 导入失败
```
错误: 未安装opencv-python
解决: pip install opencv-python
```

#### 3. 隐私模式阻止访问
```
错误: 摄像头功能处于隐私保护模式
解决: 在配置中设置 privacy_mode: false
```

#### 4. AI分析失败
```
错误: AI姿态分析助手初始化失败
解决: 安装 qwen-agent 或禁用AI分析功能
```

### 调试模式

启用调试模式获取详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

camera_module = CameraModule()
camera_module.setup()
```
