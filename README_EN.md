# PirPaw - Intelligent Desktop Pet

<div align="center">

![PirPaw Logo](docs/preview_img/alpha.png)

**Intelligent Desktop Pet System based on PySide6 with AI Agent Integration**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.5.2-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)]()

</div>

## 🌟 Key Features

### 🎯 Intelligent AI Agent System
- **Autonomous Behavior**: Pets can think, act, and interact with users autonomously
- **Tool Calling**: Support for time queries, system status, screenshots, dream generation, and more
- **Emotion System**: Intelligent emotion simulation based on emotional dimensions
- **Diary Function**: AI-driven literary diary generation

### 🎨 Rich Desktop Pet Features
- **Multi-Character Support**: Support for various pet characters and custom characters
- **Animation System**: Smooth animation effects and action mapping
- **Interactive Features**: Drag, click, voice, and other rich interactions
- **Backpack System**: Item collection, usage, and management
- **Task System**: Pomodoro timer, focus time, daily tasks

### 🔧 Developer Friendly
- **Modular Architecture**: Easy to extend and maintain
- **Configuration Driven**: JSON configuration file management
- **Cross-Platform Support**: Windows, macOS, Linux
- **Package Distribution**: Support for exe and dmg formats

## 🚀 Quick Start

### Requirements
- Python 3.9+
- PySide6 6.5.2+
- Recommended to use conda environment

### Installation

#### Windows Users
```bash
# Create conda environment
conda create --name PirPaw python=3.9.18
conda activate PirPaw

# Install basic dependencies
conda install -c conda-forge apscheduler pynput
pip install PySide6-Fluent-Widgets==1.5.4
pip install pyside6==6.5.2
pip install tendo

# Install AI Agent dependencies
pip install qwen-agent pyautogui psutil
pip install opencv-python pillow
pip install paddleocr mediapipe
```

#### macOS Users
```bash
# Create conda environment
conda create --name PirPaw python=3.9.18
conda activate PirPaw

# Install basic dependencies
conda install -c conda-forge apscheduler
pip install pynput==1.7.6
pip install PySide6-Fluent-Widgets==1.5.4
pip install pyside6==6.5.2
pip install tendo

# Install AI Agent dependencies
pip install qwen-agent pyautogui psutil
pip install opencv-python pillow
pip install paddleocr mediapipe
```

### Configure API Keys

1. Copy the environment variable template:
```bash
cp env-example.txt .env
```

2. Edit the `.env` file and add your API keys:
```env
QWEN_API_KEY=Your Qwen API key
AMAP_API_KEY=Your Amap API key (optional)
SERPER_API_KEY=Your Serper search API key (optional)
```

### Run the Program

```bash
python run_DyberPet.py
```

## 🎮 Main Features

### Intelligent AI Agent
- **Autonomous Pet Mode**: Pets can think and act autonomously
- **Tool Calling**: Time, system status, screenshots, dream generation, etc.
- **Emotion System**: Intelligent emotion simulation based on emotional dimensions
- **Diary Function**: AI-driven literary diary generation

### Desktop Pet
- **Multi-Character Support**: Support for various pet characters
- **Animation System**: Smooth animation effects
- **Interactive Features**: Drag, click, voice, etc.
- **Backpack System**: Item collection and management
- **Task System**: Pomodoro timer, focus time

### Settings
- **API Key Management**: Secure API key configuration
- **Autonomous Behavior Settings**: Adjust pet behavior parameters
- **Interface Customization**: Theme, language, size, and other settings

## 📁 Project Structure

```
PirPaw/
├── Agent/                    # AI Agent System
│   ├── core.py              # Agent Core
│   ├── modules/             # Feature Modules
│   │   ├── chat/           # Chat Module
│   │   ├── autonomous_pet/ # Autonomous Pet
│   │   ├── vision/         # Vision Module
│   │   ├── camera/         # Camera
│   │   └── tools/          # Tools Module
│   └── config.json         # Configuration File
├── DyberPet/               # Desktop Pet Core
│   ├── DyberPet.py        # Main Program
│   ├── modules.py         # Module Management
│   └── settings.py        # Settings Management
├── res/                   # Resource Files
│   ├── role/             # Pet Characters
│   ├── items/            # Item Resources
│   └── icons/            # Icon Resources
├── data/                 # Data Files
├── docs/                 # Documentation
└── run_DyberPet.py      # Startup Program
```

## 🔧 Development Guide

### Adding New AI Tools

1. Create a new module under `Agent/modules/`
2. Implement the `call_function` method
3. Add animation mapping in `tool_animation_mapping.json`

### Adding New Pet Characters

1. Create a character folder under `res/role/`
2. Add animation images and configuration files
3. Configure `pet_conf.json` and `act_conf.json`

### Adding New Items

1. Add item images under `res/items/`
2. Configure item properties in `items_config.json`
3. Add item associations in character configuration

## 📦 Package Distribution

### Windows (.exe)
```bash
python build_exe.py
```

### macOS (.dmg)
```bash
python build_dmg.py
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [DyberPet](https://github.com/ChaozhongLiu/DyberPet) - Desktop Pet Framework Base
- [PySide6-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - UI Component Library
- [Qwen Agent](https://github.com/QwenLM/Qwen-Agent) - AI Agent Framework

## 📞 Contact

- Project Homepage: [GitHub](https://github.com/your-username/PirPaw)
- Issue Reports: [Issues](https://github.com/your-username/PirPaw/issues)
- Feature Suggestions: [Discussions](https://github.com/your-username/PirPaw/discussions)

---

<div align="center">

**If this project helps you, please give it a ⭐ Star!**

</div>

