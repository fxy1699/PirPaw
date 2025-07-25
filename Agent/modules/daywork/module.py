from Agent.base_module import BaseModule
import time
import os
import random
import json
from datetime import datetime


class DayWork(BaseModule):
    """工作总结模块，通过图片、使用时间等等，分析用户的工作状态,包括时间、工作内容、工作效率等"""

    name = "工作助手"
    description = (
        "通过图片、使用时间等等，总结用户的工作状态,包括时间、工作内容、工作效率等"
    )
    version = "1.0.0"
    author = "开发者C"

    def __init__(self):
        super().__init__()
        self.sitting_start_time = None

    def setup(self, config=None):
        super().setup(config)

    def handle_message(self, message, context=None):
        """处理工作相关请求"""
        print(f"🔍 处理工作相关请求: {message}")
        if not any(keyword in message for keyword in ['工作', '总结', '工作总结']):
            return None

        try:
            if "工作" in message or "总结" in message:
                return self.generate_daily_summary()
            else:
                return "📷 工作总结遇到问题: 未知请求" + message + "，请使用工作助手"

        except Exception as e:
            print(f"❌ 工作总结处理失败: {e}")
            return f"📷 工作总结遇到问题: {str(e)}"


    def generate_daily_summary(self, max_images=10):
        """生成工作总结：获取今日截图和应用时长统计（仅从app_usage.json读取）"""
        today = datetime.now().strftime("%Y%m%d")
        folder = os.path.join(os.getcwd(), "screenshots", today)
        images = []
        if os.path.exists(folder):
            images = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(".png")
            ]
            if len(images) > max_images:
                images = random.sample(images, max_images)
        # 只从Agent/data/app_usage.json读取今日应用时长
        try:
            usage_file = os.path.join(
                os.getcwd(), "data", "app_usage.json"
            )
            if os.path.exists(usage_file):
                with open(usage_file, "r", encoding="utf-8") as f:
                    usage_data = json.load(f)
                today_str = datetime.now().strftime("%Y-%m-%d")
                if today_str in usage_data:
                    app_usage = usage_data[today_str]
                    # 统计并格式化输出
                    if isinstance(app_usage, dict) and app_usage:
                        lines = ["你今天在以下软件上工作了："]
                        for app, data in sorted(app_usage.items(), key=lambda x: x[1].get("total_seconds", 0), reverse=True):
                            seconds = int(data.get("total_seconds", 0))
                            h = seconds // 3600
                            m = (seconds % 3600) // 60
                            s = seconds % 60
                            lines.append(f"- {app}：{h}小时{m}分{s}秒")
                        summary = "\n".join(lines)
                    else:
                        summary = "今日无应用时长数据"
                else:
                    summary = "今日无应用时长数据"
            else:
                summary = "未找到应用时长数据文件"
        except Exception as e:
            summary = f"读取应用时长数据失败: {e}"
        return summary

    def get_capabilities(self):
        """返回模块能力"""
        capabilities = []

        capabilities.extend(["工作总结"])

        return capabilities

    def cleanup(self):
        """清理资源"""
        super().cleanup()

    def get_status(self):
        """获取模块详细状态"""
        status = super().get_status()
        status.update(
            {
                "sitting_start_time": self.sitting_start_time,
            }
        )
        return status

    # ============ Function Call 接口 ============
    def get_function_definitions(self) -> list:
        """
        获取DayWork模块的Function Call工具定义
        """
        return [
            {
                "name": "generate_daily_summary",
                "description": "生成用户的工作总结，包括工作内容、工作时间、工作效率等",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        ]

    def call_function(self, function_name: str, arguments: dict):
        """
        调用DayWork模块的具体功能
        """
        if not self.enabled:
            raise RuntimeError(f"模块 {self.name} 已禁用")

        if function_name == "generate_daily_summary":
            return self.generate_daily_summary()
        else:
            raise ValueError(f"未知功能: {function_name}") 