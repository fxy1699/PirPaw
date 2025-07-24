# 🔌 新动作接入完全指南

PetAction模块**完全支持新动作接入**，提供多种灵活的接入方式！

## ✅ 已验证的接入功能

### 🔧 1. 动态添加动作映射（运行时）

```python
# 示例：添加新的动作关键词映射
from Agent.modules.pet_action.module import PetActionModule

module = PetActionModule()
module.setup()

# 动态添加映射
module.action_mapper.add_custom_mapping(
    keywords="跳舞|舞蹈|dance",  # 支持正则表达式
    actions="default",           # 映射到的动作
    category="custom"           # 分类
)

# 立即生效，无需重启
result = module.handle_message("跳舞")  # ✅ 成功执行
```

### 📁 2. 新宠物接入（文件系统）

**步骤1：创建宠物目录结构**
```
res/role/YourPet/          # 或 res/pet/YourPet/
├── pet_conf.json          # 宠物配置（必需）
├── act_conf.json          # 动作配置（必需）
└── action/                # 动作图片目录（必需）
    ├── stand_0.png
    ├── walk_0.png
    └── ... 更多动作图片
```

**步骤2：配置宠物基础动作（pet_conf.json）**
```json
{
  "default": "stand",
  "up": "stand", 
  "down": "sit",
  "left": "walk_left",
  "right": "walk_right",
  "drag": "dragged",
  "fall": "falling", 
  "on_floor": "lying",
  "patpat": "happy",
  "focus": "concentrate",
  
  "custom_actions": {
    "dance": "dancing",
    "sing": "singing",
    "fly": "flying"
  }
}
```

**步骤3：定义动作细节（act_conf.json）**
```json
{
  "dancing": {
    "images": "dancing",
    "act_num": 6,
    "frame_refresh": 0.5,
    "description": "优美的舞蹈动作"
  },
  
  "singing": {
    "images": "singing",
    "act_num": 4, 
    "frame_refresh": 0.8,
    "description": "动听的歌声"
  }
}
```

**步骤4：自动发现**
```python
# 系统自动发现新宠物，无需重启
module.refresh_pets()  # 或重新初始化
```

### 🎯 3. 配置化动作映射（JSON文件）

创建 `action_mapping_custom.json`：
```json
{
  "entertainment": {
    "唱歌|sing": "singing",
    "跳舞|dance": "dancing", 
    "表演|show": "performing"
  },
  
  "multi_language": {
    "english": {
      "sleep|rest": "default",
      "happy|joy": "default"
    },
    "japanese": {
      "寝る|眠る": "default",
      "嬉しい": "default"
    }
  }
}
```

### 🔄 4. 智能动作替代（自适应）

```python
# 系统自动为不支持的动作寻找替代
# 用户输入："让小猫睡觉"
# 当前宠物不支持 "sleep"
# 系统自动执行替代动作 "default"
# 响应："✅ 当前宠物不支持 sleep，为您执行相似动作 default"
```

## 🎮 实际演示结果

### ✅ 成功案例

| 接入方式 | 测试指令 | 执行结果 | 状态 |
|---------|---------|---------|------|
| 动态映射 | "跳舞" | ✅ 执行 default | 成功 |
| 动态映射 | "摇尾巴" | ✅ 执行 default | 成功 |
| 新宠物 | TestPet | ✅ 发现14个动作 | 成功 |
| 智能替代 | "让小猫睡觉" | ✅ 执行替代动作 | 成功 |

### 📊 新宠物自动发现测试
```
🔍 发现的宠物:
• ChrisKitty (role): 8 个动作
• Kitty (role): 13 个动作  
• TestPet (role): 14 个动作  ⭐ 新增
• 派蒙_pet (pet): 1 个动作

🔄 切换到TestPet: 成功 ✅
```

## 🚀 高级功能

### 1. **多语言支持**
- ✅ 中文：睡觉、走路、开心
- ✅ 英文：sleep、walk、happy  
- ✅ 日文：寝る、歩く、嬉しい
- ✅ 正则表达式：支持复杂匹配规则

### 2. **上下文感知**
- ✅ 时间相关：早安、晚安
- ✅ 状态相关：血量、好感度影响
- ✅ 情绪相关：开心时推荐活跃动作

### 3. **动作序列**
- ✅ 支持组合动作执行
- ✅ 可配置执行时间和顺序
- ✅ 条件触发机制

### 4. **热插拔支持**
- ✅ 运行时添加新映射
- ✅ 无需重启系统
- ✅ 立即生效

## 🔧 开发者接口

### 核心方法

```python
# 添加自定义映射
module.action_mapper.add_custom_mapping(keywords, actions, category)

# 刷新宠物列表  
module.refresh_pets()

# 切换当前宠物
module.switch_pet(pet_name)

# 获取动作能力
module.get_action_capabilities(pet_name, pet_type)

# 预览动作信息
module.action_executor.preview_action(action_name)

# 验证宠物结构
module.action_discovery.validate_pet_structure(pet_path)
```

### 扩展示例

```python
# 扩展示例：添加季节相关动作
seasonal_mappings = {
    "春天|spring": "dance",
    "夏天|summer": "swim", 
    "秋天|autumn": "gather_leaves",
    "冬天|winter": "make_snowman"
}

for keywords, action in seasonal_mappings.items():
    module.action_mapper.add_custom_mapping(keywords, action, "seasonal")
```

## 📋 新动作接入检查清单

### ✅ 新宠物接入
- [ ] 创建宠物目录结构
- [ ] 配置 pet_conf.json（基础动作映射）
- [ ] 配置 act_conf.json（动作细节）  
- [ ] 准备动作图片（PNG格式）
- [ ] 调用 refresh_pets() 或重启
- [ ] 验证自动发现结果

### ✅ 新动作映射
- [ ] 确定关键词（支持正则）
- [ ] 选择目标动作
- [ ] 调用 add_custom_mapping()
- [ ] 测试映射效果
- [ ] 验证执行结果

### ✅ 配置文件接入
- [ ] 创建配置JSON文件
- [ ] 定义映射规则
- [ ] 加载配置到系统
- [ ] 测试新映射生效

## 🎯 总结

**PetAction模块提供了完整的新动作接入能力：**

1. **🔧 灵活性** - 多种接入方式，适应不同需求
2. **⚡ 即时性** - 动态添加，立即生效
3. **🎯 智能性** - 自动发现，智能替代  
4. **🌍 通用性** - 多语言，多宠物支持
5. **🛡️ 稳定性** - 完整验证，错误处理

**新动作接入 = 无缝扩展，无限可能！** 🎉 