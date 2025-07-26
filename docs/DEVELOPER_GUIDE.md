# PirPaw 开发者指南

## 🏗️ 项目架构

### 核心组件
```
PirPaw/
├── Agent/                    # AI Agent系统
│   ├── core.py              # Agent核心管理器
│   ├── modules/             # 功能模块
│   └── config.json          # 配置文件
├── DyberPet/               # 桌面宠物核心
│   ├── DyberPet.py         # 主程序
│   ├── modules.py          # 模块管理
│   └── settings.py         # 设置管理
└── res/                    # 资源文件
    ├── role/               # 宠物角色
    ├── items/              # 物品资源
    └── icons/              # 图标资源
```

### 模块化设计
- **Agent系统**：负责AI功能和工具调用
- **DyberPet系统**：负责桌面宠物显示和交互
- **资源系统**：管理角色、物品、图标等资源

## 🔧 开发环境设置

### 1. 环境准备
```bash
# 创建开发环境
conda create --name PirPaw-dev python=3.9.18
conda activate PirPaw-dev

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. 代码规范
- **Python代码**：遵循PEP 8规范
- **文档字符串**：使用Google风格
- **类型注解**：尽可能添加类型提示
- **测试覆盖**：新功能需要包含测试

### 3. 版本控制
```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送分支
git push origin feature/new-feature
```

## 🎯 添加新功能

### 1. AI工具开发

#### 创建新工具模块
```python
# Agent/modules/new_tool/module.py
from Agent.base_module import BaseModule

class NewToolModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.module_name = "new_tool"
    
    def call_function(self, function_name, arguments):
        """实现工具调用逻辑"""
        if function_name == "new_function":
            return self._new_function(arguments)
        return None
    
    def _new_function(self, arguments):
        """具体功能实现"""
        # 实现你的功能
        return {"result": "success"}
```

#### 注册工具到动画映射
```json
// Agent/modules/autonomous_pet/tool_animation_mapping.json
{
  "tool_animation_mapping": {
    "new_tool": {
      "new_function": "happy"
    }
  }
}
```

### 2. 宠物角色开发

#### 创建角色文件夹结构
```
res/role/NewPet/
├── action/              # 动画图片
│   ├── stand_0.png
│   ├── walk_0.png
│   └── ...
├── pet_conf.json        # 宠物配置
├── act_conf.json        # 动作配置
└── info/
    ├── info.json        # 角色信息
    └── NewPet.png       # 角色头像
```

#### 配置宠物属性
```json
// res/role/NewPet/pet_conf.json
{
  "name": "NewPet",
  "display_name": "新宠物",
  "description": "这是一个新宠物",
  "default_action": "stand",
  "patpat": {
    "0": "happy",
    "3": "excited"
  },
  "coin_config": {
    "name": "金币",
    "icon": "coin.svg"
  }
}
```

#### 配置动作属性
```json
// res/role/NewPet/act_conf.json
{
  "stand": {
    "act_num": 4,
    "frame_refresh": 200,
    "sound": "stand.wav"
  },
  "walk": {
    "act_num": 8,
    "frame_refresh": 150,
    "sound": "walk.wav"
  }
}
```

### 3. 物品开发

#### 添加物品图片
将物品图片放入 `res/items/` 目录

#### 配置物品属性
```json
// res/items/items_config.json
{
  "new_item": {
    "name": "新物品",
    "description": "这是一个新物品",
    "type": "consumable",
    "price": 100,
    "effect": {
      "hp": 10,
      "fv": 5
    }
  }
}
```

## 🔍 调试技巧

### 1. 日志系统
```python
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 使用日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 2. 断点调试
```python
import pdb

def debug_function():
    pdb.set_trace()  # 设置断点
    # 你的代码
```

### 3. 性能分析
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    # 你的代码
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

## 📦 打包发布

### 1. Windows打包
```bash
# 安装打包工具
pip install pyinstaller

# 执行打包
python build_exe.py
```

### 2. macOS打包
```bash
# 安装打包工具
pip install pyinstaller

# 执行打包
python build_dmg.py
```

### 3. 打包配置
- **图标文件**：确保 `res/icons/icon.png` 存在
- **语言文件**：确保 `res/language/langs.zh_CN.qm` 存在
- **依赖检查**：确保所有依赖都在 `requirements.txt` 中

## 🧪 测试指南

### 1. 单元测试
```python
import unittest

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        pass
    
    def test_new_function(self):
        """测试新功能"""
        # 测试代码
        self.assertEqual(result, expected)
    
    def tearDown(self):
        """测试后清理"""
        pass

if __name__ == '__main__':
    unittest.main()
```

### 2. 集成测试
```python
# 测试Agent系统集成
def test_agent_integration():
    from Agent.core import AgentCore
    
    agent = AgentCore()
    result = agent.process_message("测试消息")
    assert result is not None
```

### 3. 性能测试
```python
import time

def performance_test():
    start_time = time.time()
    # 执行功能
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"执行时间: {execution_time:.2f}秒")
```

## 📚 API文档

### Agent系统API

#### AgentCore类
```python
class AgentCore:
    def __init__(self):
        """初始化Agent核心"""
    
    def process_message(self, message):
        """处理用户消息"""
    
    def reload_api_keys(self):
        """重新加载API密钥"""
```

#### BaseModule类
```python
class BaseModule:
    def __init__(self):
        """初始化模块"""
    
    def call_function(self, function_name, arguments):
        """调用模块功能"""
    
    def setup(self):
        """设置模块"""
```

### DyberPet系统API

#### PetWidget类
```python
class PetWidget(QWidget):
    def __init__(self):
        """初始化宠物组件"""
    
    def show_bubble(self, text):
        """显示气泡消息"""
    
    def play_animation(self, action):
        """播放动画"""
```

## 🤝 贡献指南

### 1. 代码审查
- 所有代码提交需要经过审查
- 确保代码质量和测试覆盖
- 遵循项目编码规范

### 2. 文档更新
- 新功能需要更新相关文档
- 保持README和API文档同步
- 添加使用示例和说明

### 3. 版本发布
- 遵循语义化版本控制
- 更新CHANGELOG.md
- 创建Release标签

## 🐛 常见问题

### Q: 模块加载失败
**A**: 检查模块结构和依赖
1. 确认模块文件夹结构正确
2. 检查 `__init__.py` 文件
3. 验证依赖包安装

### Q: 动画不显示
**A**: 检查资源文件
1. 确认图片文件存在
2. 检查配置文件格式
3. 验证文件路径正确

### Q: API调用失败
**A**: 检查网络和配置
1. 确认API密钥正确
2. 检查网络连接
3. 验证API账户状态

## 📞 技术支持

- **GitHub Issues**：提交问题和建议
- **开发者群**：技术讨论和交流
- **文档Wiki**：详细开发文档
- **示例代码**：参考现有模块实现 