# 🎮 DyberPet真实控制完整指南

## 🚀 快速开始

### 方式1：自动集成（推荐）

**已经完成配置！** 只需要：

1. **启动DyberPet**
```bash
cd D:/project/PirPaw
python run_DyberPet.py
```

2. **看到集成成功提示**
```
🎉 Agent系统已成功集成到DyberPet!
💬 现在可以通过自然语言控制宠物了:
   • 在聊天中输入 '让小猫睡觉' 来控制动作
   • 输入 '现在的状态' 查看宠物信息
   • 输入 '走路' 或 '跳舞' 等动作指令
```

3. **开始控制宠物**
- 右键宠物 → 聊天功能
- 输入自然语言命令控制宠物

### 方式2：独立测试控制

**在DyberPet运行时：**

```bash
cd D:/project/PirPaw
python Agent/test_real_control.py
```

选择模式：
- `1` - 自动测试模式（验证功能）
- `2` - 交互控制模式（手动输入命令）

## 🎯 可用的控制命令

### 🎭 动作控制
```
让小猫睡觉     → 执行睡觉动作
走路          → 执行左右走路
站立          → 执行站立动作
跳舞          → 执行跳舞动作（如果支持）
跳跃          → 执行跳跃动作
飞行          → 执行飞行动作（TestPet支持）
施法          → 执行施法动作（TestPet支持）
变身          → 执行变身动作（TestPet支持）
```

### 📊 状态查询
```
现在的状态     → 查看宠物血量、好感度、当前动作
你有什么能力   → 查看可用功能列表
宠物列表      → 查看所有可用宠物
```

### 🔄 宠物管理
```
切换到Kitty      → 切换到Kitty宠物
切换到ChrisKitty → 切换到ChrisKitty宠物
切换到TestPet    → 切换到TestPet宠物
切换到派蒙       → 切换到派蒙宠物
```

## 🔧 技术原理

### 🌉 桥接器系统
```
用户输入 → Agent系统 → DyberPet桥接器 → PetWidget._show_act() → 宠物动作
```

### 🎯 智能映射
```
"让小猫睡觉" → 关键词识别 → 动作映射 → 支持性检查 → 智能替代 → 执行反馈
```

### 🔄 自动连接
- 自动检测运行中的DyberPet实例
- 无DyberPet时自动回退到模拟模式
- 支持热插拔和重连

## 🛠️ 故障排除

### ❌ 常见问题

**1. "未检测到运行中的Qt应用"**
```
解决方案：
- 确保DyberPet正在运行
- 重新启动DyberPet
- 检查PySide6是否安装正确
```

**2. "检测到Qt应用，但不是DyberPet"**
```
解决方案：
- 关闭其他Qt应用
- 确保运行的是DyberPet而不是其他程序
- 重新启动DyberPet
```

**3. "连接DyberPet失败"**
```
解决方案：
- 检查Agent路径是否正确
- 确保所有依赖都已安装
- 查看控制台错误信息
```

**4. "动作执行失败"**
```
解决方案：
- 检查宠物是否支持该动作
- 尝试使用基础动作（stand, walk）
- 查看动作映射是否正确
```

### 🔍 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

查看桥接器状态：
```python
from Agent.modules.pet_action.dyberpet_bridge import get_dyberpet_bridge
bridge = get_dyberpet_bridge()
print(f"连接状态: {bridge.get_connection_status()}")
print(f"宠物状态: {bridge.get_pet_state()}")
```

## 🎮 实际使用示例

### 示例1：基础控制
```bash
# 启动DyberPet
python run_DyberPet.py

# 在控制台看到：
🎉 Agent系统已成功集成到DyberPet!

# 右键宠物 → 聊天
# 输入: "让小猫睡觉"
# 结果: 宠物执行睡觉动作
```

### 示例2：交互式控制
```bash
# DyberPet运行时，新开终端
python Agent/test_real_control.py

# 选择: 2 (交互控制模式)
# 输入各种命令测试
```

### 示例3：编程控制
```python
from Agent.dyberpet_agent_integration import execute_agent_action

# 执行动作
result = execute_agent_action("让小猫睡觉")
print(result)

# 查看状态  
status = execute_agent_action("现在的状态")
print(status)
```

## 🔮 高级功能

### 🤖 Function Call集成

系统已集成到智能对话中，AI可以自动选择合适的宠物控制功能：

```
用户: "我想让宠物休息一下"
AI: 自动调用 petaction_control_pet_action("睡觉")
结果: 宠物执行睡觉动作
```

### 📊 状态监听

实时监听宠物状态变化：
```python
def on_hp_changed(hp):
    print(f"血量变化: {hp}")

def on_fv_changed(fv, level):
    print(f"好感度变化: {fv} (等级: {level})")

# 注册回调
bridge = get_dyberpet_bridge()
bridge.register_status_callback(my_callback)
```

### 🎯 自定义动作

添加新的动作映射：
```json
// 在 action_mapping.json 中添加
{
  "performance_actions": {
    "唱歌": "singing",
    "表演": "performing"
  }
}
```

## 📈 扩展开发

### 添加新功能
1. 在 `dyberpet_bridge.py` 中添加新方法
2. 在 `action_executor.py` 中实现执行逻辑
3. 在 `module.py` 中暴露Function Call接口

### 集成其他AI模型
系统支持任何实现Function Call的AI模型，只需要：
1. 实现标准的Function Call接口
2. 注册宠物控制功能
3. 处理AI的功能调用请求

## 🎉 享受控制吧！

现在你可以：
- 🗣️ **用自然语言控制宠物动作**
- 📊 **实时查看宠物状态**  
- 🔄 **随时切换不同宠物**
- 🤖 **通过AI智能对话控制**
- 🎮 **编程自动化控制**

**开始探索DyberPet的智能控制世界吧！** 🚀 