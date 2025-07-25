import sys
from sys import platform
import ctypes
from tendo import singleton
import os
from DyberPet.utils import read_json
from DyberPet.DyberPet import PetWidget
from DyberPet.Notification import DPNote
from DyberPet.Accessory import DPAccessory

from PySide6.QtWidgets import QApplication
from PySide6 import QtCore
from PySide6.QtCore import Qt, QLocale, QTimer, QDateTime, QDate, Signal, QTime

from qfluentwidgets import  FluentTranslator, setThemeColor
from DyberPet.DyberSettings.DyberControlPanel import ControlMainWindow
from DyberPet.Dashboard.DashboardUI import DashboardMainWindow

try:
    size_factor = 1 #ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
except:
    size_factor = 1

import DyberPet.settings as settings


# For translation:
# pylupdate5 langs.pro
# lrelease langs.zh_CN.ts

# For .exe:
# Now we use pyinstaller 6.5.0
# pyinstaller --noconsole --icon="000.ico" --hidden-import="pynput.mouse._win32" --hidden-import="pynput.keyboard._win32" run_DyberPet.py

# For Mac:
# pyinstaller --windowed --icon 000.icns --add-data="res:res" --add-data="DyberPet:DyberPet" --hidden-import="pynput.mouse._darwin" --hidden-import="pynput.keyboard._darwin" run_DyberPet.py


class DyberPetApp(QApplication):
    date_changed = Signal(QDate)

    def __init__(self, *args, **kwargs):
        super(DyberPetApp, self).__init__(*args, **kwargs)

        self.setQuitOnLastWindowClosed(False)
        screens = self.screens()
        primary_screen = self.primaryScreen()

        if primary_screen in screens:
            screens.insert(0, screens.pop(screens.index(primary_screen)))
        else:
            screens.insert(0, primary_screen)

        # internationalization
        fluentTranslator = FluentTranslator(QLocale(settings.language_code))
        self.installTranslator(fluentTranslator)
        self.installTranslator(settings.translator)
        if settings.themeColor:
            setThemeColor(settings.themeColor)
        

        # Pet Object
        self.p = PetWidget(screens=screens)

        # Notification System
        self.note = DPNote()

        # Accessory System
        self.acc = DPAccessory()

        # System Panel
        self.conp = ControlMainWindow()

        # Dashboard
        self.board = DashboardMainWindow()

        # Midnight Timer
        self.current_date = QDate.currentDate()
        self.set_midnight_timer()

        # Signal Links
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        # Main Widget - others
        self.p.setup_notification.connect(self.note.setup_notification)
        self.p.setup_bubbleText.connect(self.note.setup_bubbleText)
        self.p.change_note.connect(self.note.change_pet)
        self.p.change_note.connect(self.conp.charCardInterface._finishStateTooltip)
        self.p.close_bubble.connect(self.note.close_bubble)
        self.p.hptier_changed_main_note.connect(self.note.hpchange_note)
        self.p.fvlvl_changed_main_note.connect(self.note.fvchange_note)
        self.p.setup_acc.connect(self.acc.setup_accessory)
        self.p.move_sig.connect(self.acc.send_main_movement)
        self.p.move_sig.connect(self.note.send_main_movement)
        self.p.close_all_accs.connect(self.acc.closeAll)

        # System Widgets - others
        self.conp.settingInterface.ontop_changed.connect(self.acc.ontop_changed)
        self.conp.settingInterface.scale_changed.connect(self.acc.reset_size_sig)

        self.conp.settingInterface.ontop_changed.connect(self.p.ontop_update)
        self.conp.settingInterface.scale_changed.connect(self.p.reset_size)
        self.conp.settingInterface.lang_changed.connect(self.p.lang_changed)
        self.p.change_note.connect(self.conp.settingInterface._update_scale)

        self.conp.charCardInterface.change_pet.connect(self.p._change_pet)
        self.p.show_controlPanel.connect(self.conp.show_window)

        self.conp.gamesaveInterface.refresh_pet.connect(self.p.refresh_pet)

        # Dashboard - others
        self.p.show_dashboard.connect(self.board.show_window)
        self.note.noteToLog.connect(self.board.statusInterface._addNote)
        self.p.hp_updated.connect(self.board.statusInterface.StatusCard._updateHP)
        self.p.fv_updated.connect(self.board.statusInterface.StatusCard._updateFV)
        self.p.change_note.connect(self.board.statusInterface._changePet)
        self.board.statusInterface.changeStatus.connect(self.p._change_status)
        self.p.stopAllThread.connect(self.board.statusInterface.stopBuffThread)

        self.acc.acc_withdrawed.connect(self.board.backpackInterface.acc_withdrawed)
        self.board.backpackInterface.use_item_inven.connect(self.p.use_item)
        self.board.backpackInterface.item_note.connect(self.p.register_notification)
        self.board.backpackInterface.item_drop.connect(self.p.item_drop_anim)
        self.p.fvlvl_changed_main_inve.connect(self.board.backpackInterface.fvchange)
        self.p.fvlvl_changed_main_inve.connect(self.board.shopInterface.fvchange)
        self.p.addItem_toInven.connect(self.board.backpackInterface.add_items)
        self.p.compensate_rewards.connect(self.board.backpackInterface.compensate_rewards)
        self.p.refresh_bag.connect(self.board.backpackInterface.refresh_bag)
        self.p.autofeed.connect(self.board.backpackInterface.autofeed)
        self.p.refresh_bag.connect(self.board.shopInterface.refresh_shop)
        self.p.addCoins.connect(self.board.backpackInterface.addCoins)

        # Tasks and Timer
        self.board.taskInterface.focusPanel.start_pomodoro.connect(self.p.run_tomato)
        self.board.taskInterface.focusPanel.cancel_pomodoro.connect(self.p.cancel_tomato)
        self.board.taskInterface.focusPanel.start_focus.connect(self.p.run_focus)
        self.board.taskInterface.focusPanel.cancel_focus.connect(self.p.cancel_focus)
        self.p.taskUI_Timer_update.connect(self.board.taskInterface.focusPanel.update_Timer)
        self.p.taskUI_task_end.connect(self.board.taskInterface.focusPanel.taskFinished)
        self.p.single_pomo_done.connect(self.board.taskInterface.focusPanel.single_pomo_done)

        # Animation Panel
        self.board.animInterface.animatPanel.updateList.connect(self.p.updateList)
        self.board.animInterface.animatPanel.playAct.connect(self.p._show_act)
        self.p.refresh_acts.connect(self.board.animInterface.animatPanel.updateAct)
        self.p.refresh_acts.connect(self.board.animInterface.updateDesignUI)
        self.board.animInterface.loadNewAct.connect(self.p._addNewAct)
        self.board.animInterface.deletewAct.connect(self.p._deleteAct)

        # Midnight Trigger
        self.date_changed.connect(self.p._mightEventTrigger)
    
    def set_midnight_timer(self):
        now = QDateTime.currentDateTime()
        midnight = QDateTime(QDate.currentDate().addDays(1), QTime(0, 0, 0))  # Next midnight
        msecs_until_midnight = now.msecsTo(midnight)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.check_date)
        self.timer.start(msecs_until_midnight)
    
    def check_date(self):
        new_date = QDate.currentDate()
        if new_date != self.current_date:
            self.current_date = new_date
            self.date_changed.emit(new_date)
        self.set_midnight_timer()  # Reset the timer for the next midnight


        


if platform == 'win32':
    basedir = ''
else:
    basedir = os.path.dirname(__file__)

if __name__ == '__main__':

    # Avoid multiple process
    try:
        me = singleton.SingleInstance()
    except:
        sys.exit()


    # Create App
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    #QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    #QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = DyberPetApp(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    # ============ Agent系统后台线程集成 ============
    from PySide6.QtCore import QThread, QObject, Signal
    
    class AgentInitThread(QThread):
        """Agent系统初始化线程 - 只处理非UI逻辑"""
        
        # 信号定义
        init_started = Signal()
        init_completed = Signal(bool, object)  # 成功/失败，Agent核心对象
        init_error = Signal(str)               # 错误信息
        
        def __init__(self):
            super().__init__()
        
        def run(self):
            """在后台线程中初始化Agent系统核心（不涉及UI）"""
            try:
                self.init_started.emit()
                print("🤖 后台线程开始初始化Agent核心系统...")
                
                # 添加Agent路径
                import os
                import sys
                agent_path = os.path.join(os.path.dirname(__file__), 'Agent')
                if agent_path not in sys.path:
                    sys.path.insert(0, agent_path)
                
                # 只初始化Agent核心，不进行UI集成
                from Agent.core import AgentCore
                agent_core = AgentCore()
                
                print(f"🎉 Agent核心系统初始化成功，加载了 {len(agent_core.modules)} 个模块")
                self.init_completed.emit(True, agent_core)
                    
            except Exception as e:
                error_msg = f"Agent核心初始化出错: {e}"
                print(f"❌ {error_msg}")
                self.init_error.emit(error_msg)
                self.init_completed.emit(False, None)
    
    # 设置初始状态
    app.chat_integration_success = False
    app.agent_initializing = True
    
    # 创建并启动Agent初始化线程
    agent_thread = AgentInitThread()
    
    # 连接信号处理
    def on_agent_init_started():
        print("🚀 DyberPet已启动，Agent核心系统正在后台线程中初始化...")
    
    def on_agent_init_completed(success, agent_core):
        """在主线程中处理Agent初始化完成 - 进行UI集成"""
        app.agent_initializing = False
        
        if success and agent_core:
            try:
                print("🔗 在主线程中进行UI集成...")
                
                # 在主线程中进行UI相关的集成操作
                from Agent.dyberpet_agent_integration import get_integration_manager
                manager = get_integration_manager()
                
                # 设置Agent核心
                manager.agent_core = agent_core
                
                # 连接PetAction模块到DyberPet（在主线程中）
                if hasattr(app, 'p') and app.p:
                    for module in agent_core.modules:
                        if hasattr(module, 'action_executor'):
                            success = module.connect_to_dyberpet(app, app.p)
                            if success:
                                manager.pet_action_module = module
                                print(f"✅ PetAction模块已连接到DyberPet")
                                break
                
                app.chat_integration_success = True
                
                # 刷新宠物右键菜单以添加智能聊天选项
                try:
                    print("🔄 刷新DyberPet菜单以添加聊天功能...")
                    if hasattr(app.p, '_set_Statusmenu'):
                        app.p._set_Statusmenu()
                        print("✅ DyberPet菜单已刷新，智能聊天选项已添加")
                    else:
                        print("⚠️ 无法找到_set_Statusmenu方法")
                except Exception as e:
                    print(f"⚠️ 刷新菜单失败: {e}")
                
                print("🎉 Agent系统UI集成完成!")
                print("💬 现在可以通过聊天窗口控制宠物了:")
                print("   • 右键宠物 → 选择'智能聊天'")
                print("   • 输入 '让小猫睡觉' 来控制动作")
                print("   • 输入 '现在的状态' 查看宠物信息")
                print("   • 输入 '走路' 或 '跳舞' 等动作指令")
                
            except Exception as e:
                print(f"❌ UI集成失败: {e}")
                app.chat_integration_success = False
        else:
            app.chat_integration_success = False
            print("⚠️ Agent核心初始化失败，但DyberPet正常运行")
    
    def on_agent_init_error(error_msg):
        print(f"❌ {error_msg}")
        print("💡 DyberPet将正常运行，但无Agent功能")
        app.agent_initializing = False
        app.chat_integration_success = False
    
    # 连接信号
    agent_thread.init_started.connect(on_agent_init_started)
    agent_thread.init_completed.connect(on_agent_init_completed)
    agent_thread.init_error.connect(on_agent_init_error)
    
    # 启动Agent初始化线程
    agent_thread.start()
    
    # 保存线程引用防止被回收
    app.agent_thread = agent_thread
    # =========================================

    sys.exit(app.exec())


