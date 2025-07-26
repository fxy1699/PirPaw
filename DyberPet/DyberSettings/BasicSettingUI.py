# coding:utf-8
import os
import json
import urllib.request
from sys import platform

from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, HyperlinkCard,InfoBar,
                            ComboBoxSettingCard, ScrollArea, ExpandLayout, InfoBarPosition,
                            setThemeColor)

from qfluentwidgets import FluentIcon as FIF
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths, QLocale
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QApplication
#from qframelesswindow import FramelessWindow

from .custom_utils import Dyber_RangeSettingCard, Dyber_ComboBoxSettingCard, CustomColorSettingCard
import DyberPet.settings as settings

basedir = settings.BASEDIR
module_path = os.path.join(basedir, 'DyberPet/DyberSettings/')
'''
if platform == 'win32':
    basedir = ''
    module_path = 'DyberPet/DyberSettings/'
else:
    #from pathlib import Path
    basedir = os.path.dirname(__file__) #Path(os.path.dirname(__file__))
    #basedir = basedir.parent
    basedir = basedir.replace('\\','/')
    basedir = '/'.join(basedir.split('/')[:-2])

    module_path = os.path.join(basedir, 'DyberPet/DyberSettings/')
'''


class SettingInterface(ScrollArea):
    """ Setting interface """

    ontop_changed = Signal(name='ontop_changed')
    scale_changed = Signal(name='scale_changed')
    lang_changed = Signal(name='lang_changed')

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingInterface")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)
        
        # Mode =========================================================================================
        self.ModeGroup = SettingCardGroup(self.tr('Mode'), self.scrollWidget)
        # Always on top
        self.AlwaysOnTopCard = SwitchSettingCard(
            FIF.PIN,
            self.tr("Always-On-Top"),
            self.tr("Pet will be displayed on top of the other Apps"),
            parent=self.ModeGroup #DisplayModeGroup
        )
        if settings.on_top_hint:
            self.AlwaysOnTopCard.setChecked(True)
        else:
            self.AlwaysOnTopCard.setChecked(False)
        self.AlwaysOnTopCard.switchButton.checkedChanged.connect(self._AlwaysOnTopChanged)

        # Allow drop
        self.AllowDropCard = SwitchSettingCard(
            QIcon(os.path.join(basedir, 'res/icons/system/falldown.svg')),
            self.tr("Allow Drop"),
            self.tr("When mouse released, pet falls to the ground (on) / stays at the site (off)"),
            parent=self.ModeGroup #DisplayModeGroup
        )
        if settings.set_fall:
            self.AllowDropCard.setChecked(True)
        else:
            self.AllowDropCard.setChecked(False)
        self.AllowDropCard.switchButton.checkedChanged.connect(self._AllowDropChanged)

        # Auto-Lock
        self.AutoLockCard = SwitchSettingCard(
            QIcon(os.path.join(basedir, 'res/icons/system/lock.svg')),
            self.tr("Auto-Lock"),
            self.tr("When screen is locked, HP and FV will be locked too (currently only works in Windows)"),
            parent=self.ModeGroup #DisplayModeGroup
        )
        if settings.auto_lock:
            self.AutoLockCard.setChecked(True)
        else:
            self.AutoLockCard.setChecked(False)
        self.AutoLockCard.switchButton.checkedChanged.connect(self._AutoLockChanged)
        if platform != 'win32':
            self.AutoLockCard.switchButton.indicator.setEnabled(False)


        # Interaction parameters =======================================================================
        self.InteractionGroup = SettingCardGroup(self.tr('Interaction'), self.scrollWidget)
        self.GravityCard = Dyber_RangeSettingCard(
            1, 200, 0.01,
            QIcon(os.path.join(basedir, 'res/icons/system/gravity.svg')),
            self.tr("Gravity"),
            self.tr("Pet falling down acceleration"),
            parent=self.InteractionGroup
        )

        self.GravityCard.setValue(int(settings.gravity*100))
        self.GravityCard.slider.valueChanged.connect(self._GravityChanged)

        self.DragCard = Dyber_RangeSettingCard(
            0, 200, 0.01,
            QIcon(os.path.join(basedir, 'res/icons/system/mousedrag.svg')),
            self.tr("Drag Speed"),
            self.tr("Mouse speed factor"),
            parent=self.InteractionGroup
        )
        self.DragCard.setValue(int(settings.fixdragspeedx*100))
        self.DragCard.slider.valueChanged.connect(self._DragChanged)


        # Notification parameters ======================================================================
        self.VolumnGroup = SettingCardGroup(self.tr('Notification'), self.scrollWidget)
        self.VolumnCard = Dyber_RangeSettingCard(
            0, 10, 0.1,
            QIcon(os.path.join(basedir, 'res/icons/system/speaker.svg')),
            self.tr("Volumn"),
            self.tr("Volumn of notification and pet"),
            parent=self.VolumnGroup
        )
        self.VolumnCard.setValue(int(settings.volume*10))
        self.VolumnCard.slider.valueChanged.connect(self._VolumnChanged)

        self.AllowToasterCard = SwitchSettingCard(
            QIcon(os.path.join(basedir, 'res/icons/system/popup.svg')),
            self.tr("Pop-up Toaster"),
            self.tr("When turned on, notification will pop-up at the bottom right corner"),
            parent=self.VolumnGroup
        )
        if settings.toaster_on:
            self.AllowToasterCard.setChecked(True)
        else:
            self.AllowToasterCard.setChecked(False)
        self.AllowToasterCard.switchButton.checkedChanged.connect(self._AllowToasterChanged)

        self.AllowBubbleCard = SwitchSettingCard(
            QIcon(os.path.join(basedir, 'res/icons/system/bubble.svg')),
            self.tr("Dialogue Bubble"),
            self.tr("When turned on, various kinds of bubbles will pop-up above the pet"),
            parent=self.VolumnGroup
        )
        if settings.bubble_on:
            self.AllowBubbleCard.setChecked(True)
        else:
            self.AllowBubbleCard.setChecked(False)
        self.AllowBubbleCard.switchButton.checkedChanged.connect(self._AllowBubbleChanged)

        # Personalization ==============================================================================
        self.PersonalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.ScaleCard = Dyber_RangeSettingCard(
            1, 50, 0.1,
            QIcon(os.path.join(basedir, 'res/icons/system/resize.svg')),
            self.tr("Pet Scale"),
            self.tr("Adjust size of the pet"),
            parent=self.PersonalGroup
        )
        self.ScaleCard.setValue(int(settings.tunable_scale*10))
        self.ScaleCard.slider.valueChanged.connect(self._ScaleChanged)

        pet_list = settings.pets
        self.DefaultPetCard = Dyber_ComboBoxSettingCard(
            pet_list,
            pet_list,
            QIcon(os.path.join(basedir, 'res/icons/system/homestar.svg')),
            self.tr('Default Pet'),
            self.tr('Pet to show everytime App starts'),
            parent=self.PersonalGroup
        )
        self.DefaultPetCard.comboBox.currentTextChanged.connect(self._DefaultPetChanged)

        lang_choices = list(settings.lang_dict.keys())
        lang_now = lang_choices[list(settings.lang_dict.values()).index(settings.language_code)]
        lang_choices.remove(lang_now)
        lang_choices = [lang_now] + lang_choices
        self.languageCard = Dyber_ComboBoxSettingCard(
            lang_choices,
            lang_choices,
            FIF.LANGUAGE,
            self.tr('Language/语言'),
            self.tr('Set your preferred language for UI'),
            parent=self.PersonalGroup
        )
        self.languageCard.comboBox.currentTextChanged.connect(self._LanguageChanged)

        self.themeColorCard = CustomColorSettingCard(
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.PersonalGroup
        )
        self.themeColorCard.colorChanged.connect(self.colorChanged)

        # Agent自主宠物 ==============================================================================
        self.AutonomousGroup = SettingCardGroup(self.tr('Autonomous Pet'), self.scrollWidget)
        
        # 启用自主行为
        self.AutonomousEnabledCard = SwitchSettingCard(
            QIcon(os.path.join(basedir, 'res/icons/system/homestar.svg')),
            self.tr("Enable Autonomous Behavior"),
            self.tr("Allow pet to think and act autonomously"),
            parent=self.AutonomousGroup
        )
        if settings.autonomous_enabled:
            self.AutonomousEnabledCard.setChecked(True)
        else:
            self.AutonomousEnabledCard.setChecked(False)
        self.AutonomousEnabledCard.switchButton.checkedChanged.connect(self._AutonomousEnabledChanged)
        
        # 思考间隔（最小）
        self.AutonomousMinIntervalCard = Dyber_RangeSettingCard(
            0.1, 60, 0.1,
            QIcon(os.path.join(basedir, 'res/icons/Timer_icon.png')),
            self.tr("Min Think Interval"),
            self.tr("Minimum time between autonomous thoughts (minutes, supports 0.1-60)"),
            parent=self.AutonomousGroup
        )
        self.AutonomousMinIntervalCard._is_autonomous_interval = True
        self.AutonomousMinIntervalCard.setValue(int(settings.autonomous_min_interval * 10))
        self.AutonomousMinIntervalCard.slider.valueChanged.connect(self._AutonomousMinIntervalChanged)
        
        # 思考间隔（最大）
        self.AutonomousMaxIntervalCard = Dyber_RangeSettingCard(
            0.5, 120, 0.1,
            QIcon(os.path.join(basedir, 'res/icons/Timer_icon.png')),
            self.tr("Max Think Interval"),
            self.tr("Maximum time between autonomous thoughts (minutes, supports 0.5-120)"),
            parent=self.AutonomousGroup
        )
        self.AutonomousMaxIntervalCard._is_autonomous_interval = True
        self.AutonomousMaxIntervalCard.setValue(int(settings.autonomous_max_interval * 10))
        self.AutonomousMaxIntervalCard.slider.valueChanged.connect(self._AutonomousMaxIntervalChanged)
        
        # Debug模式
        self.AutonomousDebugCard = SwitchSettingCard(
            QIcon(os.path.join(basedir, 'res/icons/system/more.svg')),
            self.tr("Debug Mode"),
            self.tr("Show emotion values every 10 seconds in console"),
            parent=self.AutonomousGroup
        )
        if settings.autonomous_debug:
            self.AutonomousDebugCard.setChecked(True)
        else:
            self.AutonomousDebugCard.setChecked(False)
        self.AutonomousDebugCard.switchButton.checkedChanged.connect(self._AutonomousDebugChanged)
        
        # WatchTV Debug模式
        self.WatchTVDebugCard = SwitchSettingCard(
            QIcon(os.path.join(basedir, 'res/icons/system/more.svg')),
            self.tr("WatchTV Debug Mode"),
            self.tr("Show video detection status in console"),
            parent=self.AutonomousGroup
        )
        if settings.watchtv_debug:
            self.WatchTVDebugCard.setChecked(True)
        else:
            self.WatchTVDebugCard.setChecked(False)
        self.WatchTVDebugCard.switchButton.checkedChanged.connect(self._WatchTVDebugChanged)

        # About ==============================================================================
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        update_needed, update_text = self._checkUpdate()
        settings.UPDATE_NEEDED = update_needed
        self.aboutCard = HyperlinkCard(
            settings.RELEASE_URL,
            self.tr('Release Website'),
            QIcon(os.path.join(basedir, 'res/icons/system/update.svg')),
            self.tr('Check Updates'),
            update_text, #self.tr('Check update and learn more about the project on our GitHub page'),
            self.aboutGroup
        )
        self.helpCard = HyperlinkCard(
            settings.HELP_URL,
            self.tr('Issue Page'),
            FIF.HELP,
            self.tr('Help & Issue'),
            self.tr('Post your issue or question on our GitHub Issue, or contact us on BiliBili'),
            self.aboutGroup
        )
        self.devCard = HyperlinkCard(
            settings.DEVDOC_URL,
            self.tr('Developer Document'),
            QIcon(os.path.join(basedir, 'res/icons/system/document.svg')),
            self.tr('Re-development'),
            self.tr('If you want to develop your own pet/item/actions... Check here'),
            self.aboutGroup
        )


        self.__initWidget()

    def __initWidget(self):
        #self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 75, 0, 20)
        self.setWidget(self.scrollWidget)
        #self.scrollWidget.resize(1000, 800)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        #self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(50, 20)

        # add cards to group
        self.ModeGroup.addSettingCard(self.AlwaysOnTopCard)
        self.ModeGroup.addSettingCard(self.AllowDropCard)
        self.ModeGroup.addSettingCard(self.AutoLockCard)

        self.InteractionGroup.addSettingCard(self.GravityCard)
        self.InteractionGroup.addSettingCard(self.DragCard)

        self.VolumnGroup.addSettingCard(self.VolumnCard)
        self.VolumnGroup.addSettingCard(self.AllowToasterCard)
        self.VolumnGroup.addSettingCard(self.AllowBubbleCard)

        self.PersonalGroup.addSettingCard(self.ScaleCard)
        self.PersonalGroup.addSettingCard(self.DefaultPetCard)
        self.PersonalGroup.addSettingCard(self.languageCard)
        self.PersonalGroup.addSettingCard(self.themeColorCard)

        self.AutonomousGroup.addSettingCard(self.AutonomousEnabledCard)
        self.AutonomousGroup.addSettingCard(self.AutonomousMinIntervalCard)
        self.AutonomousGroup.addSettingCard(self.AutonomousMaxIntervalCard)
        self.AutonomousGroup.addSettingCard(self.AutonomousDebugCard)
        self.AutonomousGroup.addSettingCard(self.WatchTVDebugCard)

        self.aboutGroup.addSettingCard(self.aboutCard)
        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.devCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)

        self.expandLayout.addWidget(self.ModeGroup)
        self.expandLayout.addWidget(self.InteractionGroup)
        self.expandLayout.addWidget(self.VolumnGroup)
        self.expandLayout.addWidget(self.PersonalGroup)
        self.expandLayout.addWidget(self.AutonomousGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'light' #if isDarkTheme() else 'light'
        with open(os.path.join(basedir, 'res/icons/system/qss/', theme, 'setting_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _AlwaysOnTopChanged(self, isChecked):
        if isChecked:
            settings.on_top_hint = True
            settings.save_settings()
            self.ontop_changed.emit()
        else:
            settings.on_top_hint = False
            settings.save_settings()
            self.ontop_changed.emit()

    def _AllowDropChanged(self, isChecked):
        if isChecked:
            settings.set_fall = True
        else:
            settings.set_fall = False
        settings.save_settings()

    def _AutoLockChanged(self, isChecked):
        if isChecked:
            settings.auto_lock = True
        else:
            settings.auto_lock = False
        settings.save_settings()

    def _GravityChanged(self, value):
        settings.gravity = value*0.01
        settings.save_settings()

    def _DragChanged(self, value):
        settings.fixdragspeedx, settings.fixdragspeedy = value*0.01, value*0.01
        settings.save_settings()

    def _VolumnChanged(self, value):
        settings.volume = round(value*0.1, 3)
        settings.save_settings()

    def _ScaleChanged(self, value):
        settings.tunable_scale = value*0.1
        settings.scale_dict[settings.petname] = settings.tunable_scale
        settings.save_settings()
        self.scale_changed.emit()

    def _update_scale(self):
        self.ScaleCard.setValue(int(settings.tunable_scale*10))

    def _DefaultPetChanged(self, value):
        settings.default_pet = value
        settings.save_settings()

    def _LanguageChanged(self, value):
        settings.language_code = settings.lang_dict[value]
        settings.save_settings()
        settings.change_translator(settings.lang_dict[value])
        #self.retranslateUi()
        self.__showRestartTooltip()
        self.lang_changed.emit()
    
    def _AutonomousEnabledChanged(self, isChecked):
        settings.autonomous_enabled = isChecked
        settings.save_settings()
        self._notifyAutonomousChange()
    
    def _AutonomousMinIntervalChanged(self, value):
        settings.autonomous_min_interval = value * 0.1
        # 确保最小间隔不大于最大间隔
        if value * 0.1 > settings.autonomous_max_interval:
            settings.autonomous_max_interval = value * 0.1
            self.AutonomousMaxIntervalCard.setValue(int(settings.autonomous_max_interval * 10))
        settings.save_settings()
        self._notifyAutonomousChange()
    
    def _AutonomousMaxIntervalChanged(self, value):
        settings.autonomous_max_interval = value * 0.1
        # 确保最大间隔不小于最小间隔
        if value * 0.1 < settings.autonomous_min_interval:
            settings.autonomous_min_interval = value * 0.1
            self.AutonomousMinIntervalCard.setValue(int(settings.autonomous_min_interval * 10))
        settings.save_settings()
        self._notifyAutonomousChange()
    
    def _AutonomousDebugChanged(self, isChecked):
        settings.autonomous_debug = isChecked
        settings.save_settings()
        self._notifyAutonomousChange()
    
    def _WatchTVDebugChanged(self, isChecked):
        settings.watchtv_debug = isChecked
        settings.save_settings()
        self._notifyAutonomousChange()
    
    def _notifyAutonomousChange(self):
        """通知自主宠物系统配置已更改"""
        try:
            # 尝试获取自主宠物模块并更新配置
            from Agent.dyberpet_agent_integration import get_agent_core
            
            agent_core = get_agent_core()
            if agent_core and hasattr(agent_core, 'modules'):
                # agent_core.modules 是一个列表，不是字典
                for module in agent_core.modules:
                    if hasattr(module, 'name') and '自主宠物' in module.name:
                        # 更新模块配置
                        new_config = {
                            'autonomous_enabled': settings.autonomous_enabled,
                            'min_interval_minutes': settings.autonomous_min_interval,
                            'max_interval_minutes': settings.autonomous_max_interval,
                            'debug_mode': settings.autonomous_debug,
                            'watchtv_debug': settings.watchtv_debug
                        }
                        module.config.update(new_config)
                        
                        # 重新应用配置
                        if hasattr(module, '_apply_config'):
                            module._apply_config()
                            print(f"✅ 自主宠物设置已更新: {new_config}")
                            
                            # 刷新行为调度，使新配置立即生效
                            if hasattr(module, 'refresh_behavior_schedule'):
                                success = module.refresh_behavior_schedule()
                                if success:
                                    print("🔄 行为调度已刷新，新间隔设置立即生效")
                                else:
                                    print("⚠️ 行为调度刷新失败")
                        break
                    elif hasattr(module, 'name') and '看电视检测' in module.name:
                        # 更新WatchTV模块配置
                        new_config = {
                            'watchtv_debug': settings.watchtv_debug
                        }
                        module.config.update(new_config)
                        print(f"✅ WatchTV模块设置已更新: {new_config}")
                        
                        # 重新应用配置
                        if hasattr(module, 'setup'):
                            module.setup(new_config)
                            print("🔄 WatchTV模块配置已重新应用")
                else:
                    print("⚠️ 未找到相关模块")
            else:
                print("⚠️ Agent系统未运行，设置已保存，将在下次启动时生效")
        except ImportError:
            print("⚠️ Agent系统未安装，设置已保存")
        except Exception as e:
            print(f"⚠️ 更新设置失败: {e}")
    
    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart\n此设置在重启后生效'),
            duration=3000,
            position=InfoBarPosition.BOTTOM,
            parent=self.window()
        )

    def colorChanged(self, color_str):
        setThemeColor(color_str)
        settings.themeColor = color_str
        settings.save_settings()

    def _checkUpdate(self):
        local_version = settings.VERSION
        success, github_version = get_latest_version()
        if success:
            update_needed = compare_versions(local_version, github_version)
            if update_needed:
                return True, local_version + "  " + self.tr("New version available")
            else:
                return False, local_version + "  " + self.tr("Already the latest")
        else:
            return False, self.tr("Failed to check updates. Please check the website.")
        
    def _AllowToasterChanged(self, isChecked):
        if isChecked:
            settings.toaster_on = True
        else:
            settings.toaster_on = False
        settings.save_settings()

    def _AllowBubbleChanged(self, isChecked):
        if isChecked:
            settings.bubble_on = True
        else:
            settings.bubble_on = False
        settings.save_settings()





def get_latest_version():
    url = settings.RELEASE_API
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            return True, data['tag_name']
    except Exception as e:
        return False, None

def compare_versions(local_version, github_version):
    # Remove 'v' prefix from version strings
    local_version = local_version.lstrip('v')
    github_version = github_version.lstrip('v')

    # Split version strings into their components
    local_parts = local_version.split('.')
    github_parts = github_version.split('.')

    # Convert version components to integers
    local_numbers = [int(part) for part in local_parts]
    github_numbers = [int(part) for part in github_parts]

    # Compare each component
    for local, github in zip(local_numbers, github_numbers):
        if local < github:
            return True  # User should update
        elif local > github:
            return False  # Local version is ahead

    # If all components are equal, check for additional components
    if len(local_numbers) < len(github_numbers):
        return True  # User should update
    else:
        return False  # Local version is up to date or ahead