"""
自主宠物模块 - 让宠物具有自我意识的核心模块
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import sys
import json

# 导入基类
from ...base_module import BaseModule

from .memory import PetMemory
from .emotions import EmotionSystem
from .brain import PetBrain
from .scheduler import AutonomousScheduler
from .behaviors import BehaviorExecutor

# 导入日记管理器
try:
    from ...data.diary.diary_manager import diary_manager
    DIARY_AVAILABLE = True
except ImportError:
    print("⚠️ 日记管理器不可用，自主行为将不会记录到日记")
    DIARY_AVAILABLE = False


class AutonomousPetModule(BaseModule):
    """自主宠物模块 - 让宠物具有情感、记忆、主动思考和行为的能力"""
    
    name = "自主宠物"
    description = "让宠物具有情感、记忆、主动思考和行为的能力"
    version = "1.0.0"
    author = "PirPaw Team"
    
    def __init__(self):
        super().__init__()
        
        # 核心组件
        self.memory = None
        self.emotions = None
        self.brain = None
        self.scheduler = None
        self.behavior_executor = None
        
        # DyberPet集成
        self.bubble_manager = None
        
        # Agent核心引用（用于调用其他模块工具）
        self.agent_core = None
        
        # 运行状态
        self.is_running = False
        self.scheduler_thread = None
        
        # Debug模式
        self.debug_mode = False
        self.debug_thread = None
        self.debug_running = False
        
        # 配置
        self.autonomous_enabled = True
        self.min_interval_minutes = 5
        self.max_interval_minutes = 30
        
        self.last_daywork_summary_date = None
        
    def setup(self, config=None):
        """初始化模块"""
        super().setup(config)
        
        # 从配置中获取设置
        self.autonomous_enabled = config.get('autonomous_enabled', True)
        self.min_interval_minutes = config.get('min_interval_minutes', 1)
        self.max_interval_minutes = config.get('max_interval_minutes', 5)
        self.debug_mode = config.get('debug_mode', False)
        
        print(f"🔧 自主宠物配置:")
        print(f"   启用状态: {self.autonomous_enabled}")
        print(f"   思考间隔: {self.min_interval_minutes}-{self.max_interval_minutes}分钟")
        print(f"   调试模式: {self.debug_mode}")
        
        if not self.autonomous_enabled:
            print("💤 自主宠物功能已禁用")
            self.initialized = False
            return
        
        # 检查必要的目录
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
        except Exception as e:
            print(f"⚠️ 创建数据目录失败: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            # 初始化记忆系统
            print("🧠 初始化宠物记忆系统...")
            self.memory = PetMemory()
            
            # 初始化情感系统
            print("😊 初始化情感系统...")
            self.emotions = EmotionSystem(self.memory)
            
            # 初始化大脑
            print("🤔 初始化宠物大脑...")
            self.brain = PetBrain(self.emotions, self.memory)
            
            # 初始化行为执行器
            print("🎭 初始化行为执行器...")
            self.behavior_executor = BehaviorExecutor(self.memory, self.emotions)
            
            # 初始化调度器
            print("⏰ 初始化自主行为调度器...")
            self.scheduler = AutonomousScheduler(
                brain=self.brain,
                behavior_executor=self.behavior_executor,
                min_interval=self.min_interval_minutes,
                max_interval=self.max_interval_minutes
            )
            
            # 应用配置
            self._apply_config()
            
            # 如果Agent核心引用已经设置，重新传递给组件
            if self.agent_core:
                print("🔄 重新设置Agent核心引用到各个组件...")
                self._setup_agent_core_references()
            
            # 启动自主行为
            self.start_autonomous_behavior()
            
            self.initialized = True
            print(f"✅ {self.name} 模块初始化完成")
            
        except Exception as e:
            print(f"❌ {self.name} 模块初始化失败: {e}")
            import traceback
            traceback.print_exc()
            self.initialized = False
    
    def _apply_config(self):
        """应用配置设置"""
        cfg = self.config
        print(f"🔧 开始应用配置: {cfg}")
        
        # Debug模式设置
        old_debug_mode = getattr(self, 'debug_mode', False)
        self.debug_mode = cfg.get('debug_mode', False)
        
        if self.debug_mode and not old_debug_mode:
            print("🐛 Debug模式已启用 - 将每10秒显示情绪数值")
            self.start_debug_monitor()
        elif not self.debug_mode and old_debug_mode:
            print("🐛 Debug模式已关闭")
            self.stop_debug_monitor()
        
        # 自主行为设置
        old_enabled = getattr(self, 'autonomous_enabled', True)
        old_min = getattr(self, 'min_interval_minutes', 5)
        old_max = getattr(self, 'max_interval_minutes', 30)
        
        self.autonomous_enabled = cfg.get('autonomous_enabled', True)
        self.min_interval_minutes = cfg.get('min_interval_minutes', 5)
        self.max_interval_minutes = cfg.get('max_interval_minutes', 30)
        
        print(f"⏱️ 间隔配置更新: {old_min}-{old_max}分钟 → {self.min_interval_minutes}-{self.max_interval_minutes}分钟")
        
        # 如果自主行为状态发生变化，重新启动或停止
        if self.autonomous_enabled != old_enabled:
            if self.autonomous_enabled:
                print("🔄 自主行为已启用，重新启动...")
                self.start_autonomous_behavior()
            else:
                print("⏸️ 自主行为已禁用，停止运行...")
                self.stop_autonomous_behavior()
        
        # 更新调度器的间隔设置
        if hasattr(self, 'scheduler') and self.scheduler:
            self.scheduler.min_interval_minutes = self.min_interval_minutes
            self.scheduler.max_interval_minutes = self.max_interval_minutes
            print(f"⏰ 思考间隔已更新: {self.min_interval_minutes}-{self.max_interval_minutes}分钟")
            print(f"📋 调度器配置已同步: {self.scheduler.min_interval_minutes}-{self.scheduler.max_interval_minutes}分钟")
            
            # 立即重新计算下次行为时间，使新配置生效
            if hasattr(self.scheduler, '_update_next_behavior_time'):
                self.scheduler._update_next_behavior_time()
                if self.scheduler.next_behavior_time:
                    next_time = self.scheduler.next_behavior_time.strftime("%H:%M:%S")
                    time_left = (self.scheduler.next_behavior_time - datetime.now()).total_seconds()
                    minutes_left = int(time_left // 60)
                    print(f"🔄 下次行为时间已重新计算: {next_time} (还有约{minutes_left}分钟)")
        else:
            print("⚠️ 调度器未初始化，无法更新配置")
        
        # 情感设置
        if 'emotion_decay_speed' in cfg:
            decay_multiplier = cfg['emotion_decay_speed']
            for emotion in self.emotions.decay_rates:
                self.emotions.decay_rates[emotion] *= decay_multiplier
        
        # 大脑设置
        if 'behavior_cooldown_minutes' in cfg:
            cooldown = cfg['behavior_cooldown_minutes']
            self.brain.min_action_interval = timedelta(minutes=cooldown)
        
        print(f"⚙️ 已应用配置: 自主行为={'开启' if self.autonomous_enabled else '关闭'}, "
              f"行为间隔={self.min_interval_minutes}-{self.max_interval_minutes}分钟")
    
    def start_autonomous_behavior(self):
        """启动自主行为线程"""
        if not self.autonomous_enabled or self.is_running:
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(
            target=self._autonomous_behavior_loop,
            daemon=True,
            name="AutonomousPetBehavior"
        )
        self.scheduler_thread.start()
        print("🚀 自主行为系统已启动")
    
    def stop_autonomous_behavior(self):
        """停止自主行为"""
        self.is_running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        print("⏹️ 自主行为系统已停止")
        
        # 同时停止debug监控
        if self.debug_running:
            self.stop_debug_monitor()
    
    def start_debug_monitor(self):
        """启动debug监控"""
        if self.debug_running:
            return
            
        self.debug_running = True
        self.debug_thread = threading.Thread(target=self._debug_monitor_loop, daemon=True)
        self.debug_thread.start()
        print("🐛 Debug监控已启动 - 每10秒显示情绪状态")
    
    def stop_debug_monitor(self):
        """停止debug监控"""
        self.debug_running = False
        if self.debug_thread and self.debug_thread.is_alive():
            self.debug_thread.join(timeout=1)
        print("🐛 Debug监控已停止")
    
    def _debug_monitor_loop(self):
        """Debug监控循环"""
        while self.debug_running:
            try:
                if self.emotions:
                    self._print_emotion_status()
                time.sleep(10)  # 每10秒检查一次
            except Exception as e:
                print(f"❌ Debug监控出错: {e}")
                time.sleep(10)
    
    def _print_emotion_status(self):
        """打印情绪状态"""
        try:
            if not self.emotions:
                print("⚠️ 情绪系统未初始化")
                return
                
            current_time = datetime.now().strftime("%H:%M:%S")
            emotions = self.emotions.get_current_emotions()
            
            print(f"\n🐛 [DEBUG {current_time}] 当前情绪状态:")
            print(f"   😊 快乐度: {emotions.get('happiness', 0):.1f}")
            print(f"   ⚡ 活力值: {emotions.get('energy', 0):.1f}")
            print(f"   😴 无聊度: {emotions.get('boredom', 0):.1f}")
            print(f"   🤔 好奇心: {emotions.get('curiosity', 0):.1f}")
            print(f"   😢 孤独感: {emotions.get('loneliness', 0):.1f}")
            
            # 显示主导情绪
            try:
                dominant_emotion = self.emotions.get_dominant_emotion()
                dominant_value = emotions.get(dominant_emotion, 0)
                print(f"   🎯 主导情绪: {dominant_emotion} ({dominant_value:.1f})")
            except Exception as e:
                print(f"   🎯 主导情绪: 获取失败 ({e})")
            
            # 显示可触发的行为（新增）
            try:
                behavior_types = ['seek_attention', 'play', 'rest', 'explore', 'self_talk', 'greet', 'care']
                triggerable_behaviors = []
                for behavior in behavior_types:
                    if self.emotions.should_trigger_behavior(behavior):
                        prob = self.emotions.get_behavior_probability(behavior)
                        triggerable_behaviors.append(f"{behavior}({prob:.2f})")
                
                if triggerable_behaviors:
                    print(f"   🎭 可触发行为: {', '.join(triggerable_behaviors)}")
                else:
                    print(f"   🎭 可触发行为: 无")
            except Exception as e:
                print(f"   🎭 可触发行为: 检查失败 ({e})")
            
            # 显示大脑冷却状态（新增）
            try:
                if self.brain:
                    now = datetime.now()
                    time_since_last = now - self.brain.last_proactive_action
                    cooldown_minutes = self.brain.min_action_interval.total_seconds() / 60
                    time_since_minutes = time_since_last.total_seconds() / 60
                    
                    if time_since_last >= self.brain.min_action_interval:
                        print(f"   🧠 大脑状态: 可行动 (距离上次 {time_since_minutes:.1f}分钟)")
                    else:
                        remaining_minutes = cooldown_minutes - time_since_minutes
                        print(f"   🧠 大脑状态: 冷却中 (还需 {remaining_minutes:.1f}分钟)")
                else:
                    print(f"   🧠 大脑状态: 未初始化")
            except Exception as e:
                print(f"   🧠 大脑状态: 检查失败 ({e})")
            
            # 显示自主行为状态
            print(f"   🔄 自主行为: {'开启' if self.autonomous_enabled else '关闭'}")
            print(f"   ⏱️ 思考间隔: {self.min_interval_minutes}-{self.max_interval_minutes}分钟")
            
            # 显示调度器实际配置（用于调试）
            if hasattr(self, 'scheduler') and self.scheduler:
                print(f"   📋 调度器配置: {self.scheduler.min_interval_minutes}-{self.scheduler.max_interval_minutes}分钟")
            
            # 计算下次行为时间（不显示错误）
            try:
                if hasattr(self.scheduler, 'next_behavior_time') and self.scheduler.next_behavior_time:
                    next_time = self.scheduler.next_behavior_time.strftime("%H:%M:%S")
                    time_left = (self.scheduler.next_behavior_time - datetime.now()).total_seconds()
                    if time_left > 0:
                        minutes_left = int(time_left // 60)
                        seconds_left = int(time_left % 60)
                        print(f"   ⏰ 下次行为: {next_time} (还有 {minutes_left}分{seconds_left}秒)")
                    else:
                        print(f"   ⏰ 下次行为: 即将执行")
                else:
                    print(f"   ⏰ 下次行为: 未安排")
            except:
                print(f"   ⏰ 下次行为: 计算中...")
            
            # 显示行为状态（不显示错误）
            try:
                if hasattr(self.behavior_executor, 'last_behavior_time') and self.behavior_executor.last_behavior_time:
                    last_time = self.behavior_executor.last_behavior_time.strftime("%H:%M:%S")
                    print(f"   🎭 上次行为: {last_time}")
                else:
                    print(f"   🎭 上次行为: 无")
            except:
                print(f"   🎭 上次行为: 未知")
            
            # 显示记忆统计（不显示错误）
            try:
                if self.memory:
                    interaction_count = len(self.memory.get_recent_interactions(hours=24))
                    print(f"   🧠 24小时内互动: {interaction_count} 次")
                else:
                    print(f"   🧠 24小时内互动: 记忆未初始化")
            except:
                print(f"   🧠 24小时内互动: 统计中...")
            
            print("─" * 50)
            
        except Exception as e:
            # 只在第一次失败时显示详细错误，之后简化显示
            if not hasattr(self, '_debug_error_count'):
                self._debug_error_count = 0
            
            self._debug_error_count += 1
            if self._debug_error_count <= 3:
                print(f"❌ Debug监控出错 ({self._debug_error_count}/3): {e}")
            elif self._debug_error_count == 4:
                print("⚠️ Debug监控持续出错，后续将静默处理")
            # 超过3次后静默处理
    
    def _autonomous_behavior_loop(self):
        """自主行为主循环"""
        print("🔄 自主行为循环开始...")
        
        while self.is_running:
            try:
                # ==== 新增：每天晚上8点自动触发每日总结 ====
                now = datetime.now()
                if now.hour == 20 and (self.last_daywork_summary_date != now.date()):
                    try:
                        action_plan = {
                            'action_type': 'tool_call',
                            'tool': 'work_summary',
                            'reason': '每日定时总结',
                            'timestamp': now.isoformat(),
                            'forced': True
                        }
                        if self.behavior_executor:
                            self.behavior_executor.execute_behavior(action_plan)
                            print("✅ 晚上8点自动触发了每日总结")
                            self.last_daywork_summary_date = now.date()
                    except Exception as e:
                        print(f"❌ 自动生成每日总结失败: {e}")
                # ==== 原有自主行为逻辑 ====
                # 检查是否到了执行时间
                should_execute = False
                if hasattr(self.scheduler, 'next_behavior_time') and self.scheduler.next_behavior_time:
                    now = datetime.now()
                    if now >= self.scheduler.next_behavior_time:
                        should_execute = True
                        print(f"⏰ 到达预定执行时间，开始思考...")
                else:
                    # 如果没有预定时间，立即执行一次
                    should_execute = True
                    print(f"⏰ 首次执行或时间未设置，立即开始思考...")
                
                # should_execute = True
                if should_execute:
                # 让大脑思考
                action_plan = self.brain.think()
                
                if action_plan:
                    print(f"🧠 宠物决定执行: {action_plan['action_type']}")
                        
                        # 记录执行前的情绪状态
                        emotions_before = self.emotions.emotions.copy() if self.emotions else {}
                    
                    # 执行行为
                    success = self.behavior_executor.execute_behavior(action_plan)
                    
                        # 记录结果到宠物内存
                    self.brain.record_behavior_result(action_plan, success)
                    
                        # 记录执行时间到调度器并更新下次行为时间
                        if hasattr(self.scheduler, 'record_execution'):
                            self.scheduler.record_execution()
                        
                        # 记录到日记本
                        if success and DIARY_AVAILABLE:
                            try:
                                emotions_after = self.emotions.emotions.copy() if self.emotions else {}
                                
                                # 获取行为内容
                                behavior_content = action_plan.get('content', '')
                                if not behavior_content and 'message' in action_plan:
                                    behavior_content = action_plan['message']
                                

                                # 获取当前宠物名称
                                pet_name = self._get_current_pet_name()

                                # 将 action_plan 转换为更自然的中文描述
                                natural_action_name, natural_content, natural_reason = self._convert_action_plan_to_natural_chinese(action_plan)

                                diary_manager.add_autonomous_behavior_entry(
                                    behavior_type='proactive',
                                    action_name=natural_action_name,  # 使用自然中文名称
                                    content=natural_content,  # 使用自然中文内容
                                    trigger_reason=natural_reason,  # 使用自然中文原因
                                    emotions_before=emotions_before,
                                    emotions_after=emotions_after,
                                    pet_name=pet_name,
                                    action_name_original=action_plan['action_type']
                                )
                                print(f"[DEBUG] 自主行为全部内容：{action_plan}")
                                print(f"📔 自主行为已记录到日记: {natural_action_name}")
                            except Exception as e:
                                print(f"⚠️ 记录自主行为到日记失败: {e}")
                        
                        print(f"✅ 行为执行完成，成功={success}")
                    else:
                        print(f"🤔 大脑思考后决定暂不行动")
                        # 即使不执行行为，也要更新下次行为时间
                        if hasattr(self.scheduler, '_update_next_behavior_time'):
                            self.scheduler._update_next_behavior_time()
                
                # 短暂休眠后继续检查
                time.sleep(10)  # 每10秒检查一次是否到了执行时间
                
            except Exception as e:
                print(f"⚠️ 自主行为循环出错: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(60)  # 出错后休眠1分钟
    
    def handle_message(self, message: str, context=None) -> str:
        """处理用户消息（响应式行为）"""
        if not self.initialized:
            return "自主宠物系统未初始化"
        
        try:
            # 记录用户互动
            self.memory.save_interaction(
                interaction_type="user_message",
                content=message,
                emotion_before=self.emotions.emotions.copy()
            )
            
            # 用户互动对情感的影响
            self.emotions.simulate_interaction_effects()
            
            # 生成响应
            response = self._generate_response(message, context)
            
            # 记录响应
            self.memory.save_interaction(
                interaction_type="pet_response",
                content=message,
                response=response,
                emotion_after=self.emotions.emotions.copy(),
                success=True
            )
            
            return response
            
        except Exception as e:
            print(f"❌ 处理消息时出错: {e}")
            return f"处理消息时遇到问题: {str(e)}"
    
    def _generate_response(self, message: str, context=None) -> str:
        """生成对用户消息的响应"""
        # 获取当前情感状态
        mood = self.emotions.get_mood_description()
        dominant_emotion = self.emotions.get_dominant_emotion()
        
        # 基于情感状态调整响应风格
        if '状态' in message or '心情' in message or '怎么样' in message:
            return f"我现在{mood}呢！主要是{dominant_emotion}的感觉。你想陪我聊聊吗？"
        
        elif '你好' in message or '早上' in message or '晚上' in message:
            if dominant_emotion == 'happiness':
                return f"你好呀！我现在{mood}，很高兴见到你！"
            elif dominant_emotion == 'loneliness':
                return f"终于等到你了！我{mood}，很需要你的陪伴。"
            else:
                return f"你好！我现在{mood}，谢谢你来陪我。"
        
        elif '累' in message or '休息' in message:
            return "要注意休息哦！我也会在你累的时候陪着你的。"
        
        elif '无聊' in message:
            if self.emotions.emotions['energy'] > 0.6:
                return "无聊的话我们一起玩点什么吧！我现在精力还挺充沛的~"
            else:
                return "我也有点无聊呢...要不要一起安静地待会儿？"
        
        else:
            # 默认响应，基于当前情感
            if dominant_emotion == 'happiness':
                return f"嗯嗯！我现在{mood}，你说的话让我很开心~"
            elif dominant_emotion == 'curiosity':
                return f"哦！这很有趣！我{mood}，想了解更多！"
            elif dominant_emotion == 'energy':
                return f"我现在{mood}！你的话让我更有活力了！"
            else:
                return f"谢谢你和我聊天，我现在{mood}。"
    
    def get_capabilities(self) -> list:
        """获取模块能力描述"""
        return [
            "💭 自主思考和决策",
            "😊 情感状态管理（开心、精力、无聊、好奇、孤独）",
            "🧠 记忆用户互动历史",
            "🎭 主动发起各种行为（问候、关怀、自言自语等）",
            "🔧 智能工具调用（天气查询、提醒、学习等）",
            "📈 成长和学习用户偏好",
            "⏰ 根据时间和上下文调整行为",
            "💬 情感驱动的自然对话"
        ]
    
    def get_status(self):
        """获取模块详细状态"""
        base_status = super().get_status()
        
        if not self.initialized:
            return base_status
        
        try:
            # 获取各组件状态
            emotion_status = self.emotions.get_emotion_summary()
            brain_status = self.brain.get_brain_status()
            
            # 获取最近行为统计
            behavior_stats = self.memory.get_behavior_stats(days=7)
            
            # 获取最近互动
            recent_interactions = self.memory.get_recent_interactions(hours=24, limit=3)
            
            base_status.update({
                "autonomous_running": self.is_running,
                "current_emotions": emotion_status,
                "brain_status": brain_status,
                "behavior_stats_7days": behavior_stats,
                "recent_interactions": len(recent_interactions),
                "memory_db_path": self.memory.db_path if self.memory else None
            })
            
        except Exception as e:
            base_status["status_error"] = str(e)
        
        return base_status
    
    def cleanup(self):
        """清理资源"""
        print(f"🧹 正在清理 {self.name} 模块...")
        
        # 停止自主行为
        self.stop_autonomous_behavior()
        
        # 保存最终状态
        if self.emotions:
            self.emotions.save_emotions("模块关闭")
        
        super().cleanup()
    
    def force_behavior(self, behavior_type: str) -> str:
        """强制执行某种行为（用于测试）"""
        if not self.initialized:
            return "模块未初始化"
        
        try:
            # 创建强制行为计划
            context = self.brain._analyze_context()
            action_plan = {
                'action_type': behavior_type,
                'probability': 1.0,
                'context_score': 1.0,
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'emotions_before': self.emotions.emotions.copy(),
                'forced': True
            }
            
            if behavior_type == 'tool_call':
                action_plan['tool'] = 'check_weather'
                action_plan['reason'] = '强制测试工具调用'
            else:
                action_plan['content'] = self.brain._generate_behavior_content(behavior_type, context)
            
            # 执行行为
            success = self.behavior_executor.execute_behavior(action_plan)
            
            if success:
                return f"✅ 成功执行强制行为: {behavior_type}"
            else:
                return f"❌ 强制行为执行失败: {behavior_type}"
                
        except Exception as e:
            return f"❌ 强制行为执行出错: {e}"
    
    def set_agent_core(self, agent_core):
        """设置Agent核心引用，用于调用其他模块工具"""
        print(f"🔗 开始设置Agent核心引用...")
        print(f"   agent_core: {agent_core}")
        print(f"   agent_core.modules数量: {len(agent_core.modules) if agent_core else 0}")
        
        self.agent_core = agent_core
        
        # 如果组件已经初始化，立即设置引用
        if self.brain and self.behavior_executor:
            print("✅ 组件已初始化，立即设置Agent核心引用")
            self._setup_agent_core_references()
        else:
            print("⏳ 组件尚未初始化，Agent核心引用将在setup完成后设置")
        
        print(f"✅ 自主宠物模块已连接到Agent核心，可调用 {len(agent_core.modules) if agent_core else 0} 个模块的功能")
    
    def connect_to_bubble_system(self, bubble_manager):
        """连接到DyberPet气泡系统"""
        try:
            print(f"🔗 开始连接气泡系统...")
            print(f"   bubble_manager: {bubble_manager}")
            print(f"   behavior_executor: {self.behavior_executor}")
            
            self.bubble_manager = bubble_manager
            
            # 设置气泡回调
            if self.behavior_executor:
                self.behavior_executor.set_bubble_callback(self._trigger_bubble)
                print(f"✅ 自主宠物已连接到气泡系统")
                print(f"   回调函数已设置: {self.behavior_executor.bubble_callback is not None}")
                return True
            else:
                print("❌ 行为执行器未初始化，无法连接气泡系统")
                return False
                
        except Exception as e:
            print(f"❌ 连接气泡系统失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _trigger_bubble(self, bubble_dict):
        """触发气泡显示，支持自动播放功能"""
        try:
            if self.bubble_manager:
                # 检查是否有自动播放信息
                if bubble_dict.get('auto_play', False):
                    # 使用新的自定义气泡方法
                    self.bubble_manager.trigger_custom_bubble(bubble_dict)
                    print(f"🎈 自动播放气泡已启动: {bubble_dict.get('message', '')} (共{len(bubble_dict.get('segments', [])) + 1}段)")
                else:
                    # 使用原有的方法
                self.bubble_manager.register_bubble.emit(bubble_dict)
                print(f"🎈 气泡已触发: {bubble_dict.get('message', '')}")
            else:
                print("⚠️ 气泡管理器未连接")
        except Exception as e:
            print(f"❌ 触发气泡失败: {e}")
            # 降级处理：直接发送信号
            try:
                if self.bubble_manager:
                    self.bubble_manager.register_bubble.emit(bubble_dict)
            except:
                pass
    
    def get_emotion_report(self) -> str:
        """获取情感报告"""
        if not self.initialized:
            return "模块未初始化"
        
        emotions = self.emotions.emotions
        mood = self.emotions.get_mood_description()
        dominant = self.emotions.get_dominant_emotion()
        
        report = f"📊 当前情感状态报告:\n"
        report += f"🎭 总体心情: {mood}\n"
        report += f"🎯 主导情感: {dominant}\n\n"
        report += "📈 详细数值:\n"
        
        for emotion, value in emotions.items():
            emoji = self.emotions._emotion_emoji(emotion)
            bar = '█' * int(value * 10) + '░' * (10 - int(value * 10))
            report += f"  {emoji} {emotion}: {bar} ({value:.2f})\n"
        
        return report 

    def _get_current_pet_name(self) -> str:
        """获取当前宠物名称"""
        try:
            # 尝试从DyberPet设置获取当前宠物名称
            import DyberPet.settings as dyber_settings
            if hasattr(dyber_settings, 'PET_NAME'):
                return dyber_settings.PET_NAME
            elif hasattr(dyber_settings, 'pet_name'):
                return dyber_settings.pet_name
            else:
                return "未知宠物"
        except Exception:
            return "未知宠物" 

    def refresh_behavior_schedule(self):
        """刷新行为调度，使新配置立即生效"""
        if hasattr(self, 'scheduler') and self.scheduler:
            # 更新调度器配置
            self.scheduler.min_interval_minutes = self.min_interval_minutes
            self.scheduler.max_interval_minutes = self.max_interval_minutes
            
            # 重新计算下次行为时间
            if hasattr(self.scheduler, '_update_next_behavior_time'):
                self.scheduler._update_next_behavior_time()
                if self.scheduler.next_behavior_time:
                    next_time = self.scheduler.next_behavior_time.strftime("%H:%M:%S")
                    time_left = (self.scheduler.next_behavior_time - datetime.now()).total_seconds()
                    minutes_left = int(time_left // 60)
                    print(f"🔄 行为调度已刷新: 下次行为 {next_time} (约{minutes_left}分钟后)")
                    return True
        return False 

    def _setup_agent_core_references(self):
        """设置Agent核心引用到各个组件"""
        if not self.agent_core:
            return
        
        # 传递给大脑
        if self.brain:
            self.brain.agent_core = self.agent_core
            print("🧠 大脑已获得Agent核心引用，可以调用其他模块工具")
        
        # 传递给行为执行器
        if self.behavior_executor:
            self.behavior_executor.set_agent_core(self.agent_core)
            print("🎭 行为执行器已获得Agent核心引用，可以执行真实工具调用") 

    def _convert_action_plan_to_natural_chinese(self, action_plan: Dict[str, Any]) -> tuple[str, str, str]:
        """
        将行为计划转换为更自然的中文描述。
        例如：{'action_type': 'tool_call', 'tool': 'check_weather', 'reason': '强制测试工具调用'}
        转换为：('工具调用', '检查天气', '强制测试工具调用')
        """
        action_type = action_plan.get('action_type', '未知行为')
        content = action_plan.get('content', '')
        reason = action_plan.get('reason', '')
        context = action_plan.get('context', {})
        
        # 基础行为类型映射
        action_type_mapping = {
            'seek_attention': '寻求关注',
            'self_talk': '自言自语',
            'greet': '主动问候',
            'care': '关怀用户',
            'explore': '探索学习',
            'rest': '休息放松',
            'play': '玩耍娱乐',
            'tool_call': '工具调用'
        }
        
        natural_action_name = action_type_mapping.get(action_type, action_type)
        
        # 处理工具调用
        if action_type == 'tool_call':
            tool_name = action_plan.get('tool', '未知工具')
            tool_mapping = {
                'get_time': '查看时间',
                'check_weather': '查看天气',
                'remind_user': '提醒用户',
                'learn_something': '学习新知识',
                'check_system': '检查系统状态',
                'pet_status': '查看宠物状态',
                'get_usage_stats': '查看使用统计',
                'take_screenshot': '截图',
                'check_posture': '检查坐姿',
                'analyze_screen': '分析屏幕',
                'extract_text': '提取文字',
                'analyze_image': '分析图像',
                'switch_pet': '切换宠物',
                'list_pets': '列出宠物',
                'control_pet': '控制宠物动作',
                'start_tracking': '开始追踪',
                'stop_tracking': '停止追踪',
                'tracking_status': '查看追踪状态',
                'usage_report': '生成使用报告',
                'check_health': '检查健康',
                'check_fatigue': '检查疲劳',
                'camera_status': '查看摄像头状态',
                'take_photo': '拍照',
                'work_summary': '工作总结'
            }
            
            natural_content = tool_mapping.get(tool_name, f'调用工具: {tool_name}')
            
            # 根据上下文生成更自然的原因描述
            dominant_emotion = context.get('dominant_emotion', '好奇')
            emotion_descriptions = {
                'happiness': '心情愉快',
                'energy': '精力充沛',
                'boredom': '感到无聊',
                'curiosity': '好奇心驱使',
                'loneliness': '感到孤独'
            }
            
            emotion_desc = emotion_descriptions.get(dominant_emotion, '自主思考')
            
            # 时间上下文
            hour = context.get('hour', 12)
            time_context = ''
            if 6 <= hour < 12:
                time_context = '早上'
            elif 12 <= hour < 18:
                time_context = '下午'
            elif 18 <= hour < 22:
                time_context = '晚上'
            else:
                time_context = '深夜'
            
            natural_reason = f"{time_context}{emotion_desc}，主动{natural_content}"
            
        else:
            # 处理社交行为
            if content:
                natural_content = content
            else:
                behavior_content_mapping = {
                    'seek_attention': '主动寻求主人的关注和互动',
                    'self_talk': '进行自我反思和思考',
                    'greet': '向主人表达问候',
                    'care': '表达对主人的关心',
                    'explore': '探索新知识和信息',
                    'rest': '进行休息和放松',
                    'play': '邀请主人一起玩耍'
                }
                natural_content = behavior_content_mapping.get(action_type, f'执行{natural_action_name}行为')
            
            # 生成自然的原因描述
            dominant_emotion = context.get('dominant_emotion', '好奇')
            emotion_descriptions = {
                'happiness': '心情愉快',
                'energy': '精力充沛',
                'boredom': '感到无聊',
                'curiosity': '好奇心驱使',
                'loneliness': '感到孤独'
            }
            
            emotion_desc = emotion_descriptions.get(dominant_emotion, '自主思考')
            
            # 时间上下文
            hour = context.get('hour', 12)
            time_context = ''
            if 6 <= hour < 12:
                time_context = '早上'
            elif 12 <= hour < 18:
                time_context = '下午'
            elif 18 <= hour < 22:
                time_context = '晚上'
            else:
                time_context = '深夜'
            
            natural_reason = f"{time_context}{emotion_desc}，{natural_content}"
        
        return natural_action_name, natural_content, natural_reason 