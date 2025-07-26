# DayWork 工作总结模块

## 📋 模块概述

DayWork 是一个智能工作总结模块，通过分析用户的屏幕截图、应用使用时长等数据，自动生成每日工作总结。该模块与自主宠物系统集成，支持定时自动总结和手动触发。

## 🎯 核心功能

### 1. 智能截图分析
- 自动截取屏幕内容
- 使用多模态AI分析图片内容
- 识别工作场景、文档类型、代码等

### 2. 应用使用统计
- 统计各软件的使用时长
- 分析工作模式和效率
- 生成详细的时间分配报告

### 3. 自动总结生成
- 结合截图分析和应用统计
- 生成结构化的工作总结
- 支持自然语言描述

### 4. 定时触发
- 与自主宠物系统集成
- 支持每天晚上8点自动总结
- 避免重复生成

## 🏗️ 代码结构

```
Agent/modules/daywork/
├── __init__.py          # 模块初始化
├── module.py            # 核心实现
└── README.md           # 本文档
```

### 核心类：DayWork

```python
class DayWork(BaseModule):
    """工作总结模块，通过图片、使用时间等等，分析用户的工作状态"""
    
    def __init__(self):
        # 初始化截图开始时间
        # 初始化图片描述机器人
        
    def generate_daily_summary(self, max_images=4):
        # 生成工作总结的核心方法
        
    def handle_message(self, message, context=None):
        # 处理用户消息
        
    def get_function_definitions(self):
        # 获取Function Call定义
```

## 🚀 使用方法

### 1. 基本使用

```python
from Agent.modules.daywork import DayWork

# 创建模块实例
daywork = DayWork()
daywork.setup()

# 生成工作总结
summary = daywork.generate_daily_summary()
print(summary)
```

### 2. 通过自主宠物调用

```python
# 在自主宠物模块中
action_plan = {
    'action_type': 'tool_call',
    'tool': 'work_summary',
    'reason': '用户请求工作总结'
}
behavior_executor.execute_behavior(action_plan)
```

### 3. 定时自动总结

模块已集成到自主宠物系统中，每天晚上8点会自动触发工作总结：

```python
# 在 AutonomousPetModule._autonomous_behavior_loop 中
if now.hour == 20 and (self.last_daywork_summary_date != now.date()):
    action_plan = {
        'action_type': 'tool_call',
        'tool': 'work_summary',
        'reason': '每日定时总结'
    }
    self.behavior_executor.execute_behavior(action_plan)
```

## ⚙️ 配置选项

### 1. 模块配置

```python
config = {
    'enabled': True,                    # 是否启用模块
    'max_images': 4,                    # 最大分析图片数量
    'ocr_enabled': True,                # 是否启用OCR
    'image_analysis_enabled': True      # 是否启用图像分析
}
```

### 2. 时间控制

- **时间检查**：晚上7点前会提示用户晚点再来
- **自动触发**：每天晚上8点自动生成总结
- **重复控制**：同一天只生成一次总结

## 📊 数据存储

### 1. 截图存储

```
screenshots/
├── 20240115/
│   ├── screenshot_20240115_143022.png
│   └── screenshot_20240115_160845.png
└── 20240116/
    └── screenshot_20240116_093015.png
```

### 2. 应用使用数据

```json
{
  "2024-01-15": {
    "Visual Studio Code": {
      "total_seconds": 14400,
      "sessions": [...]
    },
    "Chrome": {
      "total_seconds": 7200,
      "sessions": [...]
    }
  }
}
```

### 3. 日志总结存储

通过 `diary_manager` 保存到 `log_summary` 表：

```sql
CREATE TABLE log_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    content TEXT,
    told_user BOOLEAN DEFAULT 0
);
```

## 🔧 API 接口

### 1. Function Call 接口

```python
def get_function_definitions(self) -> list:
    """获取Function Call工具定义"""
    return [
        {
            "name": "generate_daily_summary",
            "description": "生成用户的工作总结，包括工作内容、工作时间、工作效率等",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    ]
```

### 2. 核心方法

#### generate_daily_summary(max_images=4)

生成每日工作总结。

**参数：**
- `max_images` (int): 最大分析图片数量，默认4张

**返回：**
- `str`: 格式化的工作总结文本

**示例输出：**
```
【今日截图内容分析】
图片: screenshot_20240115_143022.png
描述: 用户正在使用Visual Studio Code编写Python代码，屏幕上显示着代码编辑器和终端窗口

图片: screenshot_20240115_160845.png
描述: 浏览器中打开了多个标签页，包括GitHub、Stack Overflow等技术网站

【今日应用使用统计】
你今天在以下软件上工作了：
- Visual Studio Code：4小时0分0秒
- Chrome：2小时0分0秒
- Terminal：1小时30分0秒
```

## 🛠️ 开发指南

### 1. 扩展图片分析

```python
def _get_image_description(self, image_path):
    """扩展图片分析功能"""
    # 添加自定义分析逻辑
    custom_analysis = self._custom_image_analysis(image_path)
    return custom_analysis
```

### 2. 添加新的统计维度

```python
def _analyze_work_patterns(self, usage_data):
    """分析工作模式"""
    patterns = {
        'focus_time': self._calculate_focus_time(usage_data),
        'break_patterns': self._analyze_break_patterns(usage_data),
        'productivity_score': self._calculate_productivity(usage_data)
    }
    return patterns
```

### 3. 自定义总结模板

```python
def _generate_custom_summary(self, image_descriptions, app_usage, patterns):
    """生成自定义格式的总结"""
    template = """
    📊 今日工作概览
    ⏰ 工作时间: {total_hours}小时
    🎯 专注度: {focus_score}%
    📈 效率评分: {productivity_score}/10
    
    📸 工作场景分析:
    {image_analysis}
    
    💻 应用使用详情:
    {app_usage}
    """
    return template.format(...)
```

## 🔍 调试和故障排除

### 1. 常见问题

#### 问题：图片分析失败
**原因：** 多模态AI服务不可用
**解决：** 检查网络连接和API配置

#### 问题：应用使用数据为空
**原因：** 应用使用追踪未启用
**解决：** 确保tracker模块正常运行

#### 问题：总结重复生成
**原因：** 时间检查逻辑失效
**解决：** 检查 `last_daywork_summary_date` 变量

### 2. 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试图片分析
daywork = DayWork()
result = daywork._get_image_description("test.png")
print(f"图片分析结果: {result}")
```

### 3. 性能监控

```python
import time

start_time = time.time()
summary = daywork.generate_daily_summary()
end_time = time.time()

print(f"总结生成耗时: {end_time - start_time:.2f}秒")
```