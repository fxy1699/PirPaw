# 🚀 **DyberPet Agent Function Call 系统指南**

## 📋 **概述**

本指南详细介绍了DyberPet Agent系统中集成的Function Call功能，该功能允许qwen-agent智能地选择和调用各个模块的功能，而不是简单的消息映射。

## ✨ **系统特性**

### 🔧 **核心功能**
- **智能模块发现**: 自动扫描和注册所有模块的可用功能
- **动态工具生成**: 将模块功能转换为符合OpenAI Function Call格式的工具
- **智能决策**: 让qwen-agent根据用户需求智能选择合适的工具
- **统一调用接口**: 提供统一的功能调用和结果处理机制
- **热插拔支持**: 支持模块的动态加载和卸载

### 🎯 **已集成模块**
- **宠物动作模块** (4个功能): 控制宠物动作、查询状态、切换宠物等
- **使用追踪模块** (5个功能): 获取使用统计、追踪控制、生成报告等  
- **屏幕分析模块** (3个功能): 截图分析、文字提取、图像理解等
- **其他模块**: 支持扩展更多模块功能

## 🏗️ **系统架构**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   qwen-agent    │    │  Chat Module     │    │ Other Modules   │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ 智能决策     │ │    │ │ Function     │ │    │ │ Function    │ │
│ │ 工具选择     │ │◄──►│ │ Registry     │ │◄──►│ │ Interface   │ │
│ │ 参数生成     │ │    │ │              │ │    │ │             │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 **核心组件**

### 1. **BaseModule扩展**
所有模块继承的基类，添加了Function Call接口：

```python
class BaseModule:
    def get_function_definitions(self) -> list:
        """返回模块功能的OpenAI Function Call格式定义"""
        return []
    
    def call_function(self, function_name: str, arguments: dict):
        """调用模块的具体功能"""
        raise NotImplementedError()
```

### 2. **ModuleFunctionRegistry**
模块功能注册和管理中心：

```python
class ModuleFunctionRegistry:
    def register_modules(self, modules):
        """注册所有模块功能"""
    
    def call_function_directly(self, function_name, arguments):
        """直接调用指定功能"""
    
    def get_tools_for_qwen_agent(self):
        """获取qwen-agent格式的工具定义"""
```

### 3. **ChatModule集成**
智能对话模块作为Function Call的协调中心：

```python
class ChatModule(BaseModule):
    def register_all_modules(self, modules):
        """注册所有模块到Function Call系统"""
    
    def _setup_module_functions(self):
        """初始化模块功能注册系统"""
```

## 🎯 **使用示例**

### **1. 为新模块添加Function Call支持**

```python
class MyModule(BaseModule):
    def get_function_definitions(self) -> list:
        return [
            {
                "name": "my_function",
                "description": "我的功能描述",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "参数描述"
                        }
                    },
                    "required": ["param1"]
                }
            }
        ]
    
    def call_function(self, function_name: str, arguments: dict):
        if function_name == "my_function":
            return self._my_function_impl(arguments)
        else:
            raise ValueError(f"未知功能: {function_name}")
    
    def _my_function_impl(self, arguments: dict):
        param1 = arguments.get("param1")
        # 实现具体逻辑
        return f"执行了功能，参数: {param1}"
```

### **2. 智能对话中的自动调用**

用户只需要自然语言交流，qwen-agent会自动选择合适的功能：

```
用户: "让小猫睡觉"
AI: 自动调用 petaction_control_pet_action(action_command="让小猫睡觉")

用户: "查看今天用了哪些应用"  
AI: 自动调用 tracker_get_usage_stats(period="today")

用户: "截个屏看看"
AI: 自动调用 vision_capture_screen(analysis_type="general")
```

### **3. 直接功能调用**

也可以通过代码直接调用注册的功能：

```python
# 获取注册系统
registry = chat_module.module_registry

# 直接调用功能
result = registry.call_function_directly(
    "petaction_get_pet_status", {}
)

# 获取可用功能列表
functions = registry.get_available_functions()
```

## 📦 **当前可用功能列表**

### **🐾 宠物动作模块**
- `petaction_control_pet_action`: 控制宠物执行动作
- `petaction_get_pet_status`: 获取宠物状态信息
- `petaction_switch_pet`: 切换到指定宠物
- `petaction_list_available_pets`: 列出所有可用宠物

### **📊 使用追踪模块**
- `tracker_get_usage_stats`: 获取使用统计信息
- `tracker_start_tracking`: 开始应用追踪
- `tracker_stop_tracking`: 停止应用追踪
- `tracker_get_tracking_status`: 获取追踪状态
- `tracker_generate_usage_report`: 生成使用报告

### **👁️ 屏幕分析模块**
- `vision_capture_screen`: 截取并分析屏幕
- `vision_analyze_image`: 分析图像内容
- `vision_extract_text`: 提取文字内容

## 🧪 **测试和验证**

### **1. 运行综合测试**
```bash
python Agent/test_function_call_system.py
```

### **2. 运行简单测试**
```bash
python Agent/simple_function_call_test.py
```

### **3. 启动交互式demo**
```bash
python Agent/demo.py
```

## 🎨 **扩展指南**

### **添加新模块功能**

1. **实现Function Call接口**：在模块中添加`get_function_definitions()`和`call_function()`方法
2. **定义功能描述**：使用OpenAI Function Call格式描述功能和参数
3. **实现功能逻辑**：在`call_function()`中路由到具体的功能实现
4. **自动注册**：系统会自动发现并注册新功能

### **命名规范**

- **功能名称**：`模块名_功能名` (如: `petaction_control_pet_action`)
- **参数名称**：使用清晰的英文名称和详细描述
- **返回值**：返回字符串格式的结果，便于显示

### **最佳实践**

1. **功能细粒度**：将复杂功能拆分为多个细粒度的功能
2. **参数验证**：在功能实现中验证参数的有效性
3. **错误处理**：提供清晰的错误信息和异常处理
4. **文档完善**：为每个功能提供详细的描述和示例

## 🔗 **相关文件**

- `Agent/base_module.py`: 基础模块类和Function Call接口
- `Agent/modules/chat/module_function_registry.py`: 功能注册管理系统
- `Agent/modules/chat/module.py`: Chat模块和系统集成
- `Agent/core.py`: Agent核心系统和模块加载
- `Agent/test_function_call_system.py`: 综合测试脚本
- `Agent/simple_function_call_test.py`: 简单测试脚本

## 🎉 **总结**

DyberPet Agent的Function Call系统实现了：

✅ **智能模块发现**：自动扫描和注册模块功能  
✅ **标准化接口**：统一的Function Call接口规范  
✅ **智能决策**：让AI模型选择合适的工具而非简单映射  
✅ **可扩展性**：支持新模块的热插拔和功能扩展  
✅ **完整测试**：提供完善的测试和验证机制  

现在您可以通过自然语言与DyberPet Agent交互，AI会智能地选择和调用合适的模块功能来满足您的需求！

---

*�� 本指南会根据系统功能的扩展持续更新* 