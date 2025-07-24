# DyberPet Agent 安装指南

## 🚀 快速安装

### 1. 基础安装（推荐）

安装所有功能依赖：

```bash
cd Agent
pip install -r requirements.txt
```

### 2. 最小安装

只安装核心AI对话功能：

```bash
cd Agent
pip install -r requirements-minimal.txt
```

### 3. 开发环境安装

包含开发和测试工具：

```bash
cd Agent
pip install -r requirements-dev.txt
```

## 🔧 环境配置

### 方式一：运行配置向导（推荐）

```bash
python Agent/setup_env.py
```

这个脚本会引导你：
- 创建 `.env` 配置文件
- 配置API密钥
- 检查依赖安装情况
- 测试系统配置

### 方式二：手动配置

1. 复制环境配置模板：
```bash
cp env-example.txt .env
```

2. 编辑 `.env` 文件，配置必要的API密钥：
```bash
# 必需：Qwen DashScope API密钥
QWEN_API_KEY=sk-your-api-key-here

# 可选：网络搜索功能
SERPER_API_KEY=your-serper-key

# 可选：天气查询功能
AMAP_TOKEN=your-amap-token
```

## 📋 依赖说明

### 核心依赖（必需）
- **qwen-agent**: AI对话核心引擎
- **python-dotenv**: 环境变量支持
- **psutil**: 系统信息监控

### 功能模块依赖（可选）
- **pyautogui + Pillow**: 屏幕分析功能
- **opencv-python + mediapipe**: 摄像头姿态检测
- **paddleocr**: OCR文字识别增强
- **pywin32**: Windows系统支持

## 🧪 测试安装

运行演示程序测试：

```bash
python Agent/demo.py
```

如果看到以下输出，说明安装成功：

```
🚀 Agent系统启动完成，加载了 5 个模块
✅ 发现模块: 智能对话 by 开发者A
✅ 发现模块: 屏幕分析 by 开发者B
...
```

## 🔑 API密钥获取

### Qwen DashScope API（必需）
1. 访问：https://dashscope.aliyun.com/
2. 注册/登录阿里云账号
3. 进入控制台创建API Key
4. 复制密钥到 `QWEN_API_KEY`

### Serper 搜索API（可选）
1. 访问：https://serper.dev/
2. 注册账号获取免费额度
3. 复制API密钥到 `SERPER_API_KEY`

### 高德天气API（可选）
1. 访问：https://console.amap.com/
2. 注册开发者账号
3. 创建应用获取Key
4. 复制到 `AMAP_TOKEN`

## 🚨 常见问题

### Q: 模块加载失败
```bash
❌ 模块 xxx 加载失败: No module named 'xxx'
```
A: 检查对应模块的依赖是否安装，参考requirements.txt

### Q: Qwen API初始化失败
```bash
❌ 智能对话 初始化失败
```
A: 检查QWEN_API_KEY是否正确配置，确保网络连接正常

### Q: 摄像头功能无法使用
```bash
🔒 姿态监控 处于隐私模式
```
A: 在 `.env` 中设置 `ENABLE_CAMERA=true`

### Q: Windows系统缺少依赖
A: 安装Windows特定依赖：
```bash
pip install pywin32
```

## 📞 获取帮助

如果遇到问题：
1. 查看 [README.md](README.md) 详细文档
2. 运行 `python Agent/setup_env.py` 检查配置
3. 在项目仓库提交Issue 