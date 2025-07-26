# PirPaw - 智能桌面宠物

<div align="center">


**基于PySide6的智能桌面宠物系统，集成AI Agent功能**


</div>

## 🌟 项目特色

### 🎯 智能AI Agent系统
- **自主行为**：宠物可以自主思考、行动和与用户互动
- **工具调用**：支持时间查询、系统状态、截图、梦境生成等多种工具
- **情感系统**：基于情绪维度的智能情感模拟
- **日记功能**：AI驱动的文学性日记生成

### 🎨 丰富的桌面宠物功能
- **多角色支持**：支持多种宠物角色和自定义角色
- **动画系统**：流畅的动画效果和动作映射
- **交互功能**：拖拽、点击、语音等丰富交互
- **背包系统**：物品收集、使用和管理
- **任务系统**：番茄钟、专注时间、日常任务

### 🔧 开发者友好
- **模块化架构**：易于扩展和维护
- **配置驱动**：JSON配置文件管理
- **跨平台支持**：Windows、macOS、Linux
- **打包分发**：支持exe和dmg格式

## 🚀 快速开始

### 环境要求
- Python 3.9+
- PySide6 6.5.2+
- 推荐使用conda环境

### 安装步骤

#### Windows用户
```bash
# 创建conda环境
conda create --name PirPaw python=3.9.18
conda activate PirPaw

# 安装基础依赖
conda install -c conda-forge apscheduler pynput
pip install PySide6-Fluent-Widgets==1.5.4
pip install pyside6==6.5.2
pip install tendo

# 安装AI Agent依赖
pip install qwen-agent pyautogui psutil
pip install opencv-python pillow
pip install paddleocr mediapipe
```

#### macOS用户
```bash
# 创建conda环境
conda create --name PirPaw python=3.9.18
conda activate PirPaw

# 安装基础依赖
conda install -c conda-forge apscheduler
pip install pynput==1.7.6
pip install PySide6-Fluent-Widgets==1.5.4
pip install pyside6==6.5.2
pip install tendo

# 安装AI Agent依赖
pip install qwen-agent pyautogui psutil
pip install opencv-python pillow
pip install paddleocr mediapipe
```

### 配置API密钥

1. 复制环境变量模板：
```bash
cp env-example.txt .env
```

2. 编辑`.env`文件，添加你的API密钥：
```env
QWEN_API_KEY=你的Qwen API密钥
AMAP_API_KEY=你的高德地图API密钥（可选）
SERPER_API_KEY=你的Serper搜索API密钥（可选）
```

### 运行程序

```bash
python run_DyberPet.py
```

## 🎮 主要功能

### 智能AI Agent
- **自主宠物模式**：宠物可以自主思考和行动
- **工具调用**：时间、系统状态、截图、梦境生成等
- **情感系统**：基于情绪维度的智能情感模拟
- **日记功能**：AI驱动的文学性日记生成

### 桌面宠物
- **多角色支持**：支持多种宠物角色
- **动画系统**：流畅的动画效果
- **交互功能**：拖拽、点击、语音等
- **背包系统**：物品收集和管理
- **任务系统**：番茄钟、专注时间

### 设置功能
- **API密钥管理**：安全的API密钥配置
- **自主行为设置**：调整宠物行为参数
- **界面定制**：主题、语言、大小等设置

## 📁 项目结构

```
PirPaw/
├── Agent/                    # AI Agent系统
│   ├── core.py              # Agent核心
│   ├── modules/             # 功能模块
│   │   ├── chat/           # 对话模块
│   │   ├── autonomous_pet/ # 自主宠物
│   │   ├── vision/         # 视觉模块
│   │   ├── camera/         # 摄像头
│   │   └── tools/          # 工具模块
│   └── config.json         # 配置文件
├── DyberPet/               # 桌面宠物核心
│   ├── DyberPet.py        # 主程序
│   ├── modules.py         # 模块管理
│   └── settings.py        # 设置管理
├── res/                   # 资源文件
│   ├── role/             # 宠物角色
│   ├── items/            # 物品资源
│   └── icons/            # 图标资源
├── data/                 # 数据文件
├── docs/                 # 文档
└── run_DyberPet.py      # 启动程序
```

## 🔧 开发指南

### 添加新的AI工具

1. 在`Agent/modules/`下创建新模块
2. 实现`call_function`方法
3. 在`tool_animation_mapping.json`中添加动画映射

### 添加新的宠物角色

1. 在`res/role/`下创建角色文件夹
2. 添加动画图片和配置文件
3. 配置`pet_conf.json`和`act_conf.json`

### 添加新的物品

1. 在`res/items/`下添加物品图片
2. 在`items_config.json`中配置物品属性
3. 在角色配置中添加物品关联




## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [DyberPet](https://github.com/ChaozhongLiu/DyberPet) - 桌面宠物框架基础
- [PySide6-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - UI组件库
- [Qwen Agent](https://github.com/QwenLM/Qwen-Agent) - AI Agent框架

## 📞 联系方式


---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐ Star！**

</div>
