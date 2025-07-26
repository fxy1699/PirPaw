from Agent.base_module import BaseModule
import time
import os
import random
import json
from datetime import datetime
import base64
import mimetypes
from typing import Dict
from collections import defaultdict


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
        self.image_desc_bot = self._init_image_desc_bot()

    def _init_image_desc_bot(self):
        try:
            from qwen_agent.agents import Assistant

            llm_cfg = {"model": "qwen-vl-plus"}
            system = "你是一个图片内容分析助手，用户会上传一张图片，请你用简洁的语言描述图片的主要内容、场景、事件和细节。"
            bot = Assistant(
                llm=llm_cfg,
                name="图片内容分析助手",
                description="分析单张图片内容",
                system_message=system,
                function_list=[],
            )
            return bot
        except Exception as e:
            print(f"⚠️ 图片内容分析助手初始化失败: {e}")
            print("💡 图片内容分析功能将使用简化模式")
            return None

    def _get_image_description(self, image_path):
        """用image_desc_bot分析单张图片内容，返回描述（Qwen-Agent多模态接口兼容格式）"""
        if not self.image_desc_bot:
            return "[未启用图片内容分析助手]"
        try:
            import mimetypes

            with open(image_path, "rb") as f:
                image_bytes = f.read()
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "image/png"
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:{mime_type};base64,{image_b64}"
            messages = [
                {
                    "role": "user",
                    "content": [{"image": image_url}, {"text": "请描述这张图片的内容"}],
                }
            ]
            response = []
            for chunk in self.image_desc_bot.run(messages=messages):
                response.extend(chunk)
            if response:
                return response[-1].get("content", "[未获得图片描述]")
            else:
                return "[未获得图片描述]"
        except Exception as e:
            return f"[图片描述失败: {e}]"

    def analyze_app_usage_by_windows(
        self, usage_file: str = None
    ) -> Dict[str, Dict[str, float]]:
        """
        分析应用使用时长，细化到标签页（窗口）级别

        Args:
            usage_file: app_usage.json文件路径，默认为None时会自动查找

        Returns:
            Dict[str, Dict[str, float]]: 格式为 {应用名: {窗口名: 使用时长(秒)}}
        """
        if usage_file is None:
            usage_file = os.path.join(os.getcwd(), "data", "app_usage.json")

        # 检查文件是否存在
        if not os.path.exists(usage_file):
            raise FileNotFoundError(f"找不到使用数据文件: {usage_file}")

        # 读取JSON文件
        with open(usage_file, "r", encoding="utf-8") as f:
            usage_data = json.load(f)

        # 汇总所有应用和窗口的使用时长
        app_window_usage = defaultdict(lambda: defaultdict(float))

        # 遍历所有日期的数据
        for date, apps in usage_data.items():
            for app_name, app_data in apps.items():
                # 获取该应用的总使用时长
                total_seconds = app_data.get("total_seconds", 0)

                # 获取各个窗口的使用时长
                windows = app_data.get("windows", {})
                for window_name, window_seconds in windows.items():
                    app_window_usage[app_name][window_name] += window_seconds

        # 转换为普通字典并排序
        result = {}
        for app_name, windows in app_window_usage.items():
            # 按使用时长降序排序窗口
            sorted_windows = dict(
                sorted(windows.items(), key=lambda x: x[1], reverse=True)
            )
            result[app_name] = sorted_windows

        return result

    def generate_daily_summary(self, max_images=4):
        """生成工作总结：只返回图片描述和应用时长统计，不做大模型总结"""
        today_date = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().hour

        # # 检查时间，如果还没到晚上7点，提示用户晚点再来
        # if current_hour < 19:
        #     remaining_hours = 19 - current_hour
        #     if remaining_hours == 1:
        #         time_msg = "还有1小时"
        #     else:
        #         time_msg = f"还有{remaining_hours}小时"

        #     prompt = f"⏰ 现在还太早了！现在是{current_hour}点，{time_msg}才到晚上7点。\n\n💡 建议等到晚上7点后再来获取工作总结，这样能获得更完整的一天数据哦！"
        #     print(f"📋 时间检查：当前{current_hour}点，未到晚上7点，返回提示信息")
        #     return prompt

        # 先检查今天是否已经保存过内容
        # try:
        #     from Agent.data.diary.diary_manager import diary_manager

        #     existing_summary = diary_manager.get_log_summary_by_date(today_date)
        #     if existing_summary and existing_summary.get("content"):
        #         print(f"📋 今天的工作总结已存在，直接返回已保存的内容")
        #         return existing_summary["content"]
        # except Exception as e:
        #     print(f"⚠️ 检查已保存工作总结失败: {e}")

        # 如果没有保存过，则生成新的总结
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
        image_descriptions = []
        for img_path in images:
            desc = self._get_image_description(img_path)
            image_descriptions.append(
                f"图片: {os.path.basename(img_path)}\n描述: {desc}"
            )
        # 获取所有应用和窗口的使用时长
        usage_data = self.analyze_app_usage_by_windows()

        summary = ""
        summary += "=== 应用使用时长分析（按窗口） ===\n"
        for app_name, windows in usage_data.items():
            total_seconds = sum(windows.values())
            summary += f"\n{app_name} (总计: {total_seconds:.2f}秒)"
            for window_name, seconds in list(windows.items())[:5]:  # 只显示前5个窗口
                summary += f"  - {window_name}: {seconds:.2f}秒\n"

        result = "【今日截图内容分析】\n" + "\n\n".join(image_descriptions)
        result += "\n\n【今日应用使用统计】\n" + summary

        # # 生成用于AI的总结提示词
        # # 目标：让AI根据result内容，生成结构化、自然的工作总结，格式参考注释
        # prompt = (
        #     "喵！我是你的桌面宠物，来帮你总结今天的工作啦~\n"
        #     "请帮我根据下面的内容，生成一份结构化又可爱的工作总结，要求内容包含：\n"
        #     "1. 今日工作概览（比如总工作时间、专注度、效率评分等，记得用轻松活泼的语气哦）\n"
        #     "2. 工作场景分析（对截图内容进行简要描述，可以加点俏皮的感叹）\n"
        #     "3. 应用使用详情（各软件的使用时长，适当加点表情符号）\n"
        #     "输出格式请参考如下示例：\n"
        #     "📊 今日工作概览\n"
        #     "⏰ 工作时间: 8小时30分钟\n"
        #     "🎯 专注度: 85%\n"
        #     "📈 效率评分: 9/10\n"
        #     "\n"
        #     "💻 应用使用详情:\n"
        #     "- 微信：4小时0分0秒\n"
        #     "- 小红书：2小时0分0秒\n"
        #     "- 抖音：1小时30分0秒\n"
        #     "\n"
        #     "请根据以下原始内容进行总结：\n"
        #     f"{result}\n"
        #     "请严格按照上述结构化格式输出，内容要简明扼要、自然流畅，还要有桌面宠物的可爱风格哦！(可以适当加点表情和拟声词)"
        # )

        # 保存到日志总结表
        try:
            from Agent.data.diary.diary_manager import diary_manager

            diary_manager.save_log_summary(today_date, result)
            print(f"✅ 工作总结已保存到日志总结表: {today_date}")
        except Exception as e:
            print(f"⚠️ 保存工作总结到日志总结表失败: {e}")

        return result

    def setup(self, config=None):
        super().setup(config)

    def handle_message(self, message, context=None):
        """处理工作相关请求"""
        print(f"🔍 处理工作相关请求: {message}")
        if not any(keyword in message for keyword in ["工作", "总结", "工作总结"]):
            return None

        try:
            if "工作" in message or "总结" in message:
                return self.generate_daily_summary()
            else:
                return "📷 工作总结遇到问题: 未知请求" + message + "，请使用工作助手"

        except Exception as e:
            print(f"❌ 工作总结处理失败: {e}")
            return f"📷 工作总结遇到问题: {str(e)}"

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
