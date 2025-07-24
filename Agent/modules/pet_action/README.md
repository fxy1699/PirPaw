# 🎭 PetAction模块 - Agent驱动DyberPet动作系统

## 🎯 功能概述

PetAction模块是一个智能的宠物动作控制系统，它将Agent的自然语言理解能力与DyberPet的宠物动作系统完美结合，让用户可以通过简单的自然语言指令控制桌面宠物执行各种动作。

### 核心特性

- 🗣️ **自然语言控制**：支持"让小猫睡觉"、"走路"、"开心"等自然语言指令
- 🔍 **智能动作发现**：自动扫描和识别所有可用宠物及其支持的动作
- 🎯 **精确动作映射**：多层映射机制，包括精确匹配、模糊匹配、语义理解
- ⚡ **高效执行引擎**：队列化动作执行，支持优先级和序列控制
- 🔌 **热插拔支持**：支持新宠物的动态加载，无需重启系统
- 🧠 **上下文感知**：根据宠物状态、时间、用户偏好智能推荐动作

## 🏗️ 系统架构

```
PetActionModule (主模块)
├── ActionDiscovery (动作发现)
│   ├── 扫描宠物资源
│   ├── 解析动作配置
│   └── 构建动作数据库
├── ActionMapper (动作映射)
│   ├── 自然语言解析
│   ├── 关键词匹配
│   ├── 模糊匹配
│   └── 上下文推理
└── ActionExecutor (动作执行)
    ├── 动作队列管理
    ├── 优先级调度
    └── 执行状态追踪
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 自动安装（推荐）
python Agent/setup_pet_action.py

# 手动安装
pip install fuzzywuzzy python-Levenshtein
```

### 2. 启用模块

在 `Agent/config.json` 中确保模块已启用：

```json
{
  "enabled_modules": ["chat", "vision", "camera", "tools", "tracker", "pet_action"]
}
```

### 3. 测试功能

```bash
# 运行模块测试
python Agent/modules/pet_action/test_module.py

# 运行演示程序
python Agent/demo_pet_action.py

# 在Agent系统中测试
python Agent/demo.py
# 然后输入: "让小猫睡觉"
```

## 💬 使用示例

### 基础动作控制

```
用户: "让小猫睡觉"
AI: ✅ 小宠物开始执行 sleep 动作了~ (置信度: 95%)

用户: "走路"
AI: ✅ 小宠物听话地开始 left_walk 了！

用户: "站立"
AI: ✅ 动作执行成功：default

用户: "开心一下"
AI: ✅ 好的，让小宠物 happy 一下！
```

### 状态查询

```
用户: "现在的状态"
AI: 🐾 当前宠物信息:
📛 名称: Kitty
❤️ 血量: 75%
💖 好感度: 60%
🎭 当前动作: default

🎯 可用能力:
• 自然语言动作控制
• 宠物动作发现和映射
• 智能动作推荐
• 多宠物支持
• 基础动作: default, drag, fall
```

### 能力查询

```
用户: "能做什么动作"
AI: 🎯 当前宠物支持以下动作类型:
• 基础动作: default, left_walk, right_walk, sleep, angry
• 移动动作: left_walk, right_walk
• 随机动作组: 站立, 左右行走, 生气, 睡觉
```

## 🎛️ 配置选项

### 模块配置 (config.json)

```json
{
  "pet_action": {
    "auto_scan_pets": true,              // 是否自动扫描宠物
    "default_pet": null,                 // 默认宠物名称
    "dyber_pet_root": null,              // DyberPet根目录路径
    "enable_fuzzy_matching": true,       // 启用模糊匹配
    "confidence_threshold": 0.6,         // 置信度阈值
    "max_action_queue": 10,              // 最大动作队列长度
    "action_timeout": 30,                // 动作执行超时时间
    "enable_context_awareness": true,    // 启用上下文感知
    "response_style": "friendly"         // 回复风格
  }
}
```

### 动作映射配置 (action_mapping.json)

支持自定义关键词映射、宠物特定动作、上下文规则等高级配置。

## 🔧 开发者指南

### 添加新的动作映射

```python
# 在ActionMapper中添加自定义映射
mapper = ActionMapper()
mapper.add_custom_mapping(
    keywords="跳舞|舞蹈|dance",
    actions="dance",
    category="custom"
)
```

### 扩展宠物支持

1. 将新宠物文件夹放入 `res/role/` 或 `res/pet/`
2. 确保包含 `pet_conf.json` 和 `act_conf.json`
3. 调用 `module.refresh_pets()` 重新扫描

### 自定义执行接口

```python
# 设置DyberPet执行接口
def my_dyber_pet_interface(action, parameters):
    # 你的宠物控制逻辑
    return {"success": True}

executor.set_dyber_pet_interface(my_dyber_pet_interface)
```

## 📊 支持的宠物和动作

### 当前支持的宠物

| 宠物名称 | 类型 | 动作数量 | 特色功能 |
|---------|------|----------|----------|
| Kitty | role | 12+ | 完整生活动作(睡觉、行走、愤怒) |
| ChrisKitty | role | 8+ | 简化动作集 |
| 派蒙 | pet | 24+ | 丰富飞行动画 |

### 动作分类

- **基础动作**: default, up, down, left, right, drag, fall, on_floor
- **移动动作**: left_walk, right_walk
- **情感动作**: happy, sad, angry, excited
- **生活动作**: sleep, fall_asleep, eat, play
- **交互动作**: patpat, focus, feed
- **特殊动作**: 宠物特有的动作

## 🧪 测试和调试

### 运行完整测试套件

```bash
python Agent/modules/pet_action/test_module.py
```

### 调试模式

在 `config.json` 中启用调试模式：

```json
{
  "global_settings": {
    "debug_mode": true
  }
}
```

### 查看模块状态

```python
from Agent.modules.pet_action.module import PetActionModule

module = PetActionModule()
module.setup()

# 获取统计信息
stats = module.get_module_stats()
print(stats)

# 获取能力列表
capabilities = module.get_capabilities()
print(capabilities)
```

## 🔗 集成到DyberPet主系统

### 当前状态
- ✅ 完成核心架构和功能实现
- ✅ 独立模块测试通过
- 📋 待实现：与DyberPet主系统的实际通信接口

### 集成步骤

1. **在DyberPet.py中集成Agent**
```python
from Agent.core import AgentCore

class DyberPet(QWidget):
    def __init__(self):
        # 现有代码...
        self.ai_core = AgentCore()
```

2. **设置动作执行回调**
```python
def execute_pet_action(action_name, parameters):
    # 调用DyberPet的动作执行方法
    return self.pet_widget.execute_action(action_name)

# 设置接口
pet_action_module = self.ai_core.get_module("pet_action")
pet_action_module.action_executor.set_dyber_pet_interface(execute_pet_action)
```

3. **添加UI入口**
- 在右键菜单添加"AI控制"选项
- 在聊天界面集成动作指令
- 在仪表板显示AI状态

## ❓ 常见问题

### Q: 模块初始化失败？
A: 检查是否安装了fuzzywuzzy依赖，确保DyberPet目录结构正确

### Q: 找不到宠物？
A: 确保宠物文件夹在 `res/role/` 或 `res/pet/` 目录下，包含必需的配置文件

### Q: 动作映射不准确？
A: 可以通过配置文件自定义映射规则，或调整置信度阈值

### Q: 如何添加新的语言支持？
A: 在ActionMapper中添加对应语言的关键词映射

## 🤝 贡献指南

欢迎贡献代码和功能！

1. Fork项目仓库
2. 创建功能分支
3. 添加新功能或修复bug
4. 编写测试用例
5. 提交Pull Request

## 📝 更新日志

### v1.0.0 (当前版本)
- ✅ 完整的模块化架构
- ✅ 自然语言动作控制
- ✅ 多宠物支持
- ✅ 智能动作映射
- ✅ 配置化映射规则
- ✅ 完整的测试套件

---

**让AI与桌面宠物完美结合，创造更智能的交互体验！** 🎉 