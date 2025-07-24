"""
动作发现系统 (ActionDiscovery)
自动扫描和发现DyberPet宠物的所有可用动作
"""

import os
import json
import glob
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class ActionDiscovery:
    """宠物动作发现和管理系统"""
    
    def __init__(self, dyber_pet_root: str = None):
        """
        初始化动作发现系统
        
        Args:
            dyber_pet_root: DyberPet根目录路径
        """
        # 自动检测DyberPet根目录
        if dyber_pet_root is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            dyber_pet_root = project_root
            
        self.dyber_pet_root = dyber_pet_root
        self.role_path = os.path.join(dyber_pet_root, "res", "role")
        self.pet_path = os.path.join(dyber_pet_root, "res", "pet")
        
        # 缓存已扫描的动作
        self._action_cache = {}
        self._pet_cache = {}
        
        print(f"🔍 ActionDiscovery 初始化")
        print(f"   DyberPet根目录: {dyber_pet_root}")
        print(f"   角色目录: {self.role_path}")
        print(f"   宠物目录: {self.pet_path}")
    
    def scan_all_pets(self) -> Dict[str, Dict]:
        """
        扫描所有可用的宠物和它们的动作
        
        Returns:
            字典，键为宠物名，值为宠物信息和动作
        """
        all_pets = {}
        
        # 扫描角色 (res/role/)
        if os.path.exists(self.role_path):
            for pet_name in os.listdir(self.role_path):
                pet_dir = os.path.join(self.role_path, pet_name)
                if os.path.isdir(pet_dir) and pet_name != 'sys':  # 排除系统目录
                    pet_info = self.scan_pet_actions(pet_name, 'role')
                    if pet_info:
                        all_pets[pet_name] = pet_info
        
        # 扫描宠物 (res/pet/)
        if os.path.exists(self.pet_path):
            for pet_name in os.listdir(self.pet_path):
                pet_dir = os.path.join(self.pet_path, pet_name)
                if os.path.isdir(pet_dir):
                    pet_info = self.scan_pet_actions(pet_name, 'pet')
                    if pet_info:
                        all_pets[f"{pet_name}_pet"] = pet_info
        
        print(f"📋 发现 {len(all_pets)} 个宠物: {list(all_pets.keys())}")
        return all_pets
    
    def scan_pet_actions(self, pet_name: str, pet_type: str = 'role') -> Optional[Dict]:
        """
        扫描指定宠物的所有动作
        
        Args:
            pet_name: 宠物名称
            pet_type: 宠物类型 ('role' 或 'pet')
        
        Returns:
            宠物信息字典，包含基础信息和动作列表
        """
        cache_key = f"{pet_type}_{pet_name}"
        if cache_key in self._action_cache:
            return self._action_cache[cache_key]
        
        # 确定宠物目录
        if pet_type == 'role':
            pet_dir = os.path.join(self.role_path, pet_name)
        else:
            pet_dir = os.path.join(self.pet_path, pet_name)
        
        if not os.path.exists(pet_dir):
            print(f"⚠️ 宠物目录不存在: {pet_dir}")
            return None
        
        try:
            # 读取宠物配置
            pet_conf_path = os.path.join(pet_dir, "pet_conf.json")
            act_conf_path = os.path.join(pet_dir, "act_conf.json")
            
            if not os.path.exists(pet_conf_path) or not os.path.exists(act_conf_path):
                print(f"⚠️ 宠物配置文件缺失: {pet_name}")
                return None
            
            # 解析配置文件
            with open(pet_conf_path, 'r', encoding='utf-8') as f:
                pet_config = json.load(f)
            
            with open(act_conf_path, 'r', encoding='utf-8') as f:
                act_config = json.load(f)
            
            # 扫描动作图片
            action_dir = os.path.join(pet_dir, "action")
            available_images = self._scan_action_images(action_dir)
            
            # 构建宠物信息
            pet_info = {
                "name": pet_name,
                "type": pet_type,
                "path": pet_dir,
                "config": pet_config,
                "actions": self._parse_actions(act_config, available_images),
                "basic_actions": self._extract_basic_actions(pet_config),
                "random_actions": self._extract_random_actions(pet_config),
                "accessory_actions": self._extract_accessory_actions(pet_config)
            }
            
            # 缓存结果
            self._action_cache[cache_key] = pet_info
            
            print(f"✅ 成功扫描宠物: {pet_name} ({len(pet_info['actions'])} 个动作)")
            return pet_info
            
        except Exception as e:
            print(f"❌ 扫描宠物失败 {pet_name}: {e}")
            return None
    
    def _scan_action_images(self, action_dir: str) -> Dict[str, List[str]]:
        """
        扫描动作目录中的图片文件
        
        Args:
            action_dir: 动作图片目录
        
        Returns:
            动作名到图片文件列表的映射
        """
        if not os.path.exists(action_dir):
            return {}
        
        image_groups = {}
        image_files = glob.glob(os.path.join(action_dir, "*.png"))
        
        for img_file in image_files:
            filename = os.path.basename(img_file)
            # 解析文件名格式: action_name_frame.png
            match = re.match(r'^(.+)_(\d+)\.png$', filename)
            if match:
                action_name, frame_num = match.groups()
                if action_name not in image_groups:
                    image_groups[action_name] = []
                image_groups[action_name].append(filename)
        
        # 对每个动作的帧进行排序
        for action_name in image_groups:
            image_groups[action_name].sort(key=lambda x: int(re.search(r'_(\d+)\.png$', x).group(1)))
        
        return image_groups
    
    def _parse_actions(self, act_config: Dict, available_images: Dict[str, List[str]]) -> Dict[str, Dict]:
        """
        解析动作配置
        
        Args:
            act_config: 动作配置字典
            available_images: 可用图片映射
        
        Returns:
            解析后的动作信息
        """
        actions = {}
        
        for action_name, action_conf in act_config.items():
            image_prefix = action_conf.get('images', action_name)
            
            action_info = {
                "name": action_name,
                "config": action_conf,
                "images": available_images.get(image_prefix, []),
                "frame_count": len(available_images.get(image_prefix, [])),
                "has_movement": action_conf.get('need_move', False),
                "direction": action_conf.get('direction'),
                "frame_refresh": action_conf.get('frame_refresh', 0.5),
                "act_num": action_conf.get('act_num', 1),
                "description": self._generate_action_description(action_name, action_conf)
            }
            
            actions[action_name] = action_info
        
        return actions
    
    def _extract_basic_actions(self, pet_config: Dict) -> Dict[str, str]:
        """提取基础必需动作"""
        basic_action_keys = [
            'default', 'up', 'down', 'left', 'right', 
            'drag', 'fall', 'on_floor', 'patpat', 'focus'
        ]
        
        basic_actions = {}
        for key in basic_action_keys:
            if key in pet_config:
                basic_actions[key] = pet_config[key]
        
        return basic_actions
    
    def _extract_random_actions(self, pet_config: Dict) -> List[Dict]:
        """提取随机动作组"""
        return pet_config.get('random_act', [])
    
    def _extract_accessory_actions(self, pet_config: Dict) -> List[Dict]:
        """提取附件动作组"""
        return pet_config.get('accessory_act', [])
    
    def _generate_action_description(self, action_name: str, action_conf: Dict) -> str:
        """生成动作描述"""
        descriptions = {
            'default': '默认待机动作',
            'stand': '站立姿态',
            'walk': '行走移动',
            'left_walk': '向左行走',
            'right_walk': '向右行走',
            'sleep': '睡觉休息',
            'fall_asleep': '入睡过程',
            'angry': '愤怒表情',
            'happy': '开心表情',
            'sad': '悲伤表情',
            'drag': '被拖拽时的动作',
            'fall': '自由下落',
            'patpat': '被拍拍时的反应',
            'focus': '专注工作状态'
        }
        
        desc = descriptions.get(action_name, f"{action_name}动作")
        
        # 添加移动信息
        if action_conf.get('need_move'):
            direction = action_conf.get('direction', '')
            if direction:
                desc += f" (向{direction}移动)"
        
        return desc
    
    def get_action_capabilities(self, pet_name: str, pet_type: str = 'role') -> Dict[str, List[str]]:
        """
        获取指定宠物的动作能力摘要
        
        Args:
            pet_name: 宠物名称
            pet_type: 宠物类型
        
        Returns:
            分类的动作能力字典
        """
        pet_info = self.scan_pet_actions(pet_name, pet_type)
        if not pet_info:
            return {}
        
        capabilities = {
            "basic_actions": list(pet_info["basic_actions"].values()),
            "movement_actions": [],
            "emotional_actions": [],
            "special_actions": [],
            "random_action_groups": []
        }
        
        # 分类动作
        for action_name, action_info in pet_info["actions"].items():
            if action_info["has_movement"]:
                capabilities["movement_actions"].append(action_name)
            elif action_name in ['happy', 'sad', 'angry', 'excited']:
                capabilities["emotional_actions"].append(action_name)
            elif action_name in ['focus', 'patpat', 'feed']:
                capabilities["special_actions"].append(action_name)
        
        # 添加随机动作组名称
        for random_act in pet_info["random_actions"]:
            if random_act.get("name"):
                capabilities["random_action_groups"].append(random_act["name"])
        
        return capabilities
    
    def validate_pet_structure(self, pet_path: str) -> Tuple[bool, List[str]]:
        """
        验证宠物文件结构完整性
        
        Args:
            pet_path: 宠物目录路径
        
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查基本文件
        required_files = ["pet_conf.json", "act_conf.json"]
        for file_name in required_files:
            file_path = os.path.join(pet_path, file_name)
            if not os.path.exists(file_path):
                errors.append(f"缺少必需文件: {file_name}")
        
        # 检查action目录
        action_dir = os.path.join(pet_path, "action")
        if not os.path.exists(action_dir):
            errors.append("缺少action动作图片目录")
        elif not os.listdir(action_dir):
            errors.append("action目录为空")
        
        # 检查配置文件格式
        try:
            pet_conf_path = os.path.join(pet_path, "pet_conf.json")
            if os.path.exists(pet_conf_path):
                with open(pet_conf_path, 'r', encoding='utf-8') as f:
                    pet_config = json.load(f)
                
                # 检查必需的基础动作
                required_actions = ['default', 'drag', 'fall']
                for action in required_actions:
                    if action not in pet_config:
                        errors.append(f"pet_conf.json缺少必需动作: {action}")
        except json.JSONDecodeError as e:
            errors.append(f"pet_conf.json格式错误: {e}")
        except Exception as e:
            errors.append(f"读取pet_conf.json失败: {e}")
        
        return len(errors) == 0, errors
    
    def clear_cache(self):
        """清空缓存"""
        self._action_cache.clear()
        self._pet_cache.clear()
        print("🧹 动作缓存已清空") 