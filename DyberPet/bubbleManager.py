import os
import re
import json
import random
from PySide6.QtCore import QObject, Signal, QTimer, QMetaObject, Qt, QCoreApplication

import DyberPet.settings as settings
basedir = settings.BASEDIR

"""
List of buble behavior
-------------------------
1. Favorability
    - fv_lvlup
    - fv_drop

2. HP (Satiety)
    - hp_low
    - hp_zero

3. Feed
    - feed_done
    - feed_required [1]

4. patpat
    - pat_focus
    - pat_frequent
    - pat_random [2]

[1] The 'icon' is configured within the code, please keep it as null
[2] To cusomize this, add any number of pat_random_[0-9]* in configuration file
    


Config Structure
-------------------------
{
    BEHAVIOR: {
        "icon": "system",
        "message": "The text shown in the bubble",
        "countdown": 300, # if specified, a countdown will be triggered and shown on the bubble
        "start_audio" "system", # the string points to the note_type in note_icon.json
        "end_audio": null
    }
}

"""

# TODO: feed_required 相关翻译 更新开发文档

class BubbleManager(QObject):
    """
    Class to manage all behaviors of bubbleText
    """

    register_bubble = Signal(dict, name='register_bubble')

    attr_list = ["icon", "message", "countdown", "start_audio", "end_audio"]

    bubble_hp_tier = {0: ["fv_drop", "hp_zero", "feed_required"],
                      1: ["hp_low", "feed_required"],
                      2: ["hp_low", "feed_required"]}

    def __init__(self,
                 parent=None):
        super().__init__(parent=parent)
        self.bubble_conf = self.load_bubble_config()
        
        # 自动播放支持
        self.auto_play_timer = QTimer()
        self.auto_play_timer.timeout.connect(self._play_next_segment)
        self.current_auto_play = None  # 当前自动播放的气泡信息


    def load_bubble_config(self) -> dict:
        system_conf_file = os.path.join(basedir, 'res/icons/bubble_conf.json')
        pet_bb_conf_file = os.path.join(basedir, f'res/role/{settings.petname}/note/bubble_conf.json')
        bubble_conf = dict(json.load(open(system_conf_file, 'r', encoding='UTF-8')))

        # Load any changes made in pet config
        if os.path.exists(pet_bb_conf_file):
            pet_bb_conf = dict(json.load(open(pet_bb_conf_file, 'r', encoding='UTF-8')))
            # Default buble type config changes
            for k in bubble_conf.keys():
                if k in pet_bb_conf.keys():
                    bubble_conf[k].update(pet_bb_conf[k])
            
            # Any newly added bubble type in pet bubble config
            for k in pet_bb_conf.keys():
                if k not in bubble_conf.keys():
                    bubble_conf[k] = self._format_bubble_type_conf(pet_bb_conf[k])

        return bubble_conf
    
    def _format_bubble_type_conf(self, bubble_type_conf):
        final_conf = {}
        for k in self.attr_list:
            v = bubble_type_conf.get(k, None)
            final_conf[k] = v
        return final_conf

    def trigger_bubble(self, bb_type):
        bubble_dict = self.bubble_conf.get(bb_type, {}).copy()
        if not bubble_dict:
            return
        
        if bb_type == "feed_required":
            bubble_dict = self.prepare_feed_required()
            if not bubble_dict:
                return
        
        # change bubble type like 'pat_random_1' into 'pat_random'
        bb_type = "_".join(bb_type.split("_")[:2])
        bubble_dict['bubble_type'] = bb_type

        # Translate message
        message = bubble_dict.get('message', '')
        message = self.tr(message)

        # Change the nickname of user
        message = self._replace_usertag(message)
        bubble_dict['message'] = message

        if settings.bubble_on:
            self.register_bubble.emit(bubble_dict)

    def trigger_scheduled(self):
        # Randomly select bubble type
        cand_bubbles = self.bubble_hp_tier.get(settings.pet_data.hp_tier, [])
        if not cand_bubbles:
            return
        bb_type = random.choice(cand_bubbles)
        self.trigger_bubble(bb_type)
    
    def trigger_patpat_random(self):
        candidates = [k for k in self.bubble_conf.keys() if k.startswith("pat_random_")]
        if candidates:
            bb_type = random.choice(candidates)
            self.trigger_bubble(bb_type)
    
    def trigger_custom_bubble(self, bubble_dict):
        """触发自定义气泡，支持自动播放"""
        # 检查是否是自动播放气泡
        if bubble_dict.get('auto_play') and bubble_dict.get('segments'):
            print(f"🎈 自动播放气泡已启动: {bubble_dict['message']} (共{len(bubble_dict['segments'])}段)")
            
            # 保存自动播放信息
            self.current_auto_play = {
                'bubble_dict': bubble_dict.copy(),
                'segments': bubble_dict['segments'].copy(),
                'current_segment': 0,
                'delay': bubble_dict.get('segment_delay', 2000)
            }
            
            # 移除自动播放相关信息，显示第一段
            display_dict = bubble_dict.copy()
            display_dict.pop('auto_play', None)
            display_dict.pop('segments', None)
            display_dict.pop('segment_delay', None)
            display_dict.pop('current_segment', None)
            
            # 显示第一段
            self._emit_bubble(display_dict)
            
            # 确保在主线程中启动定时器
            if self.current_auto_play['segments']:
                self._start_timer_safely()
        else:
            # 普通气泡，直接显示
            self._emit_bubble(bubble_dict)
    
    def _start_timer_safely(self):
        """安全地在主线程中启动定时器"""
        if QCoreApplication.instance().thread() == self.thread():
            # 当前已在主线程，直接启动
            self.auto_play_timer.start(self.current_auto_play['delay'])
            print(f"🎈 定时器已在主线程启动，延迟: {self.current_auto_play['delay']}ms")
        else:
            # 在子线程中，通过元对象调用切换到主线程
            QMetaObject.invokeMethod(
                self,
                "_start_timer_in_main_thread",
                Qt.QueuedConnection
            )
            print(f"🎈 通过队列调用切换到主线程启动定时器")
    
    def _start_timer_in_main_thread(self):
        """在主线程中启动定时器"""
        if self.current_auto_play and self.current_auto_play['segments']:
            self.auto_play_timer.start(self.current_auto_play['delay'])
            print(f"🎈 定时器已在主线程启动，延迟: {self.current_auto_play['delay']}ms")
    
    def _play_next_segment(self):
        """播放下一段文本"""
        if not self.current_auto_play or not self.current_auto_play['segments']:
            print("🎈 自动播放结束或无更多段落")
            self.auto_play_timer.stop()
            self.current_auto_play = None
            return
        
        # 获取下一段文本
        next_segment = self.current_auto_play['segments'].pop(0)
        print(f"🎈 播放下一段: {next_segment[:20]}... (剩余{len(self.current_auto_play['segments'])}段)")
        
        # 创建气泡字典
        bubble_dict = self.current_auto_play['bubble_dict'].copy()
        bubble_dict['message'] = next_segment
        
        # 移除自动播放相关信息
        bubble_dict.pop('auto_play', None)
        bubble_dict.pop('segments', None)
        bubble_dict.pop('segment_delay', None)
        bubble_dict.pop('current_segment', None)
        
        # 显示当前段
        self._emit_bubble(bubble_dict)
        
        # 检查是否还有更多段落
        if self.current_auto_play['segments']:
            # 继续下一段
            print(f"🎈 准备播放下一段，延迟: {self.current_auto_play['delay']}ms")
            self.auto_play_timer.start(self.current_auto_play['delay'])
        else:
            # 播放完毕
            print("🎈 所有段落播放完毕")
            self.auto_play_timer.stop()
            self.current_auto_play = None
    
    def _emit_bubble(self, bubble_dict):
        """发送气泡显示信号"""
        # 翻译消息
        message = bubble_dict.get('message', '')
        message = self.tr(message)
        
        # 替换用户标签
        message = self._replace_usertag(message)
        bubble_dict['message'] = message
        
        if settings.bubble_on:
            self.register_bubble.emit(bubble_dict)
    
    def stop_auto_play(self):
        """停止当前的自动播放"""
        if self.auto_play_timer.isActive():
            self.auto_play_timer.stop()
        self.current_auto_play = None

    def prepare_feed_required(self):
        # Check if hp and fv are already full
        hp_full = settings.pet_data.hp >= ((settings.HP_TIERS[-1]-1)*settings.HP_INTERVAL)
        fv_full = (settings.pet_data.fv_lvl == (len(settings.LVL_BAR)-1)) and (settings.pet_data.fv==settings.LVL_BAR[settings.pet_data.fv_lvl])
        if hp_full and fv_full:
            return {}
        
        bubble_dict = self.bubble_conf['feed_required'].copy()

        # List all candidate items
        all_items = settings.items_data.item_dict.keys()
        candidate_items = [i for i in all_items if settings.items_data.item_dict[i]['item_type'] == 'consumable']
        # exclude dislike items
        dislike_items = set(settings.pet_conf.item_dislike.keys())
        candidate_items = [i for i in candidate_items if i not in dislike_items and i != 'coin']
        # exclude items with negative effect
        candidate_items = [i for i in candidate_items if settings.items_data.item_dict[i]['effect_HP'] > 0 or settings.items_data.item_dict[i]['effect_FV'] > 0]
        # check if list empty
        if not candidate_items:
            return {}
        # Choose one
        selected_item = random.choice(candidate_items)
        
        # Update the bubble_dict
        bubble_dict['icon'] = selected_item
        bubble_dict['item'] = selected_item
        bubble_dict['message'] = self.tr(bubble_dict['message'])
        bubble_dict['message'] = bubble_dict['message'].replace("ITEMNAME", f"[{selected_item}]")

        return bubble_dict
    
    def add_usertag(self, bubble_dict:dict, position:str = 'front', send:bool = False):
        # add USERTAG in string
        message = bubble_dict.get('message', '')
        if position == 'front':
            message = f'USERTAG {message}'
        elif position == 'end':
            message = f'{message} USERTAG'

        # replace usertag
        message = self._replace_usertag(message)
        bubble_dict['message'] = message

        if send and settings.bubble_on:
            self.register_bubble.emit(bubble_dict)
        else:
            return bubble_dict
    
    def _replace_usertag(self, message):
        usertag = settings.usertag_dict.get(settings.petname, "")
        if usertag:
            message = message.replace('USERTAG', usertag)
        else:
            message = message.replace('USERTAG', usertag)
        message = message.strip(' ')
        # Remove consecutive spaces
        message = re.sub(r'\s{2,}', ' ', message)
        return message
    
    def _trigger_HP(self):
        return
    
    def _trigger_FV(self):
        return
    
    def _trigger_feed(self):
        return
    
    def _trigger_focus(self):
        return





