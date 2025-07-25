#!/usr/bin/env python3
"""
DyberPet 宠物背景故事管理器
负责加载和管理宠物的背景故事配置
"""

import os
import json
from typing import Dict, Optional
import DyberPet.settings as settings

class StoryManager:
    """宠物背景故事管理器"""
    
    def __init__(self):
        self.basedir = settings.BASEDIR
        self.stories_cache = {}
    
    def get_pet_story(self, pet_name: str) -> Optional[Dict]:
        """获取指定宠物的背景故事"""
        if pet_name in self.stories_cache:
            return self.stories_cache[pet_name]
        
        story_path = os.path.join(self.basedir, 'res', 'role', pet_name, 'story_conf.json')
        
        try:
            if os.path.exists(story_path):
                with open(story_path, 'r', encoding='utf-8') as f:
                    story_data = json.load(f)
                    self.stories_cache[pet_name] = story_data
                    return story_data
            else:
                print(f"⚠️ 未找到 {pet_name} 的故事配置文件")
                return self._get_default_story(pet_name)
        except Exception as e:
            print(f"❌ 加载 {pet_name} 故事配置失败: {e}")
            return self._get_default_story(pet_name)
    
    def _get_default_story(self, pet_name: str) -> Dict:
        """获取默认的故事模板"""
        return {
            "pet_name": pet_name,
            "pet_nickname": pet_name,
            "species": "神秘生物",
            "age": "未知",
            "personality": ["友好", "神秘"],
            "background_story": {
                "origin": f"{pet_name}是一个充满神秘色彩的伙伴，它的过去被迷雾笼罩，但它的善良和忠诚是毋庸置疑的。",
                "special_abilities": ["陪伴：永远在主人身边"],
                "life_story": f"关于{pet_name}的故事还在书写中...",
                "dreams_and_goals": "成为主人最好的伙伴",
                "favorite_things": ["与主人在一起的时光"],
                "catchphrase": "让我们一起创造美好的回忆！"
            },
            "relationship_with_user": {
                "role": "忠实伙伴",
                "bond_description": f"{pet_name}将主人视为最重要的存在。",
                "interaction_style": "友好而温暖"
            },
            "trivia": [
                f"{pet_name}的故事还在等待被发现..."
            ]
        }
    
    def get_current_pet_story(self) -> Optional[Dict]:
        """获取当前宠物的背景故事"""
        current_pet = getattr(settings, 'petname', None)
        if current_pet:
            return self.get_pet_story(current_pet)
        return None
    
    def get_all_available_stories(self) -> Dict[str, Dict]:
        """获取所有可用的宠物故事"""
        stories = {}
        role_dir = os.path.join(self.basedir, 'res', 'role')
        
        if os.path.exists(role_dir):
            for pet_dir in os.listdir(role_dir):
                pet_path = os.path.join(role_dir, pet_dir)
                if os.path.isdir(pet_path):
                    story = self.get_pet_story(pet_dir)
                    if story:
                        stories[pet_dir] = story
        
        return stories
    
    def format_story_for_display(self, story_data: Dict) -> str:
        """将故事数据格式化为显示文本"""
        if not story_data:
            return "暂无故事信息"
        
        formatted_text = ""
        
        # 基本信息
        formatted_text += f"🐾 **{story_data.get('pet_name', '未知')}** ({story_data.get('pet_nickname', '')})\n\n"
        formatted_text += f"🏷️ **种族**: {story_data.get('species', '未知')}\n\n"
        formatted_text += f"🎂 **年龄**: {story_data.get('age', '未知')}\n\n"
        
        # 性格特点
        personality = story_data.get('personality', [])
        if personality:
            formatted_text += f"✨ **性格**: {' • '.join(personality)}\n\n"
        
        # 外貌描述（如果有）
        appearance = story_data.get('appearance', {})
        if appearance:
            formatted_text += "👀 **外貌特征**\n\n"
            description = appearance.get('description', '')
            if description:
                formatted_text += f"📝 **描述**: {description}\n\n"
            
            accessories = appearance.get('accessories', [])
            if accessories:
                formatted_text += "🎒 **配饰**:\n"
                for accessory in accessories:
                    formatted_text += f"  • {accessory}\n"
                formatted_text += "\n"
            
            features = appearance.get('distinctive_features', [])
            if features:
                formatted_text += "⭐ **特征**:\n"
                for feature in features:
                    formatted_text += f"  • {feature}\n"
                formatted_text += "\n"
        
        # 背景故事
        bg_story = story_data.get('background_story', {})
        if bg_story:
            # 名字寓意
            name_meaning = bg_story.get('name_meaning', '')
            if name_meaning:
                formatted_text += f"📖 **名字寓意**:\n\n{name_meaning}\n\n"
            
            # 性格细节
            personality_details = bg_story.get('personality_details', [])
            if personality_details:
                formatted_text += "🎭 **性格特点**:\n\n"
                for detail in personality_details:
                    formatted_text += f"• {detail}\n\n"
            
            # 外貌标签
            appearance_list = bg_story.get('appearance', [])
            if appearance_list:
                formatted_text += "👀 **外貌标签**:\n\n"
                for item in appearance_list:
                    formatted_text += f"• {item}\n\n"
            
            # 角色发展
            character_dev = bg_story.get('character_development', '')
            if character_dev:
                formatted_text += f"🌱 **角色发展**:\n\n{character_dev}\n\n"
            
            # 自我介绍
            self_intro = bg_story.get('self_introduction', '')
            if self_intro:
                formatted_text += f"🎤 **自我介绍**:\n\n\"{self_intro}\"\n\n"
            
            # 兼容旧格式
            origin = bg_story.get('origin', '')
            if origin:
                formatted_text += f"🌟 **起源**:\n\n{origin}\n\n"
            
            abilities = bg_story.get('special_abilities', [])
            if abilities:
                formatted_text += "🔮 **特殊能力**:\n\n"
                for ability in abilities:
                    formatted_text += f"  • {ability}\n"
                formatted_text += "\n"
            
            life_story = bg_story.get('life_story', '')
            if life_story:
                formatted_text += f"📚 **生活经历**:\n\n{life_story}\n\n"
            
            dreams = bg_story.get('dreams_and_goals', '')
            if dreams:
                formatted_text += f"🎯 **梦想与目标**:\n\n{dreams}\n\n"
            
            favorites = bg_story.get('favorite_things', [])
            if favorites:
                formatted_text += f"💝 **喜欢的事物**: {' • '.join(favorites)}\n\n"
            
            catchphrase = bg_story.get('catchphrase', '')
            if catchphrase:
                formatted_text += f"💬 **口头禅**: \"{catchphrase}\"\n\n"
        
        # 与用户的关系
        relationship = story_data.get('relationship_with_user', {})
        if relationship:
            formatted_text += "👥 **与主人的关系**\n\n"
            formatted_text += f"🎭 **角色**: {relationship.get('role', '')}\n\n"
            
            bond_description = relationship.get('bond_description', '')
            if bond_description:
                formatted_text += f"💕 **关系描述**:\n\n{bond_description}\n\n"
            
            interaction_style = relationship.get('interaction_style', '')
            if interaction_style:
                formatted_text += f"🎪 **互动风格**:\n\n{interaction_style}\n\n"
        
        # 趣闻轶事
        trivia = story_data.get('trivia', [])
        if trivia:
            formatted_text += "🎈 **趣闻轶事**:\n\n"
            for i, fact in enumerate(trivia, 1):
                formatted_text += f"{i}. {fact}\n\n"
        
        return formatted_text

# 全局实例
story_manager = StoryManager() 