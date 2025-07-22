import os
import importlib
from .base_module import BaseModule

def auto_discover_modules():
    """自动发现所有模块，开发者无需手动注册"""
    modules = []
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    
    if not os.path.exists(modules_dir):
        print("❌ modules目录不存在")
        return modules
    
    # 扫描modules目录
    for folder in os.listdir(modules_dir):
        folder_path = os.path.join(modules_dir, folder)
        if not os.path.isdir(folder_path):
            continue
            
        try:
            # 动态导入模块
            module_path = f"Agent.modules.{folder}.module"
            mod = importlib.import_module(module_path)
            
            # 查找BaseModule的子类
            for item in dir(mod):
                cls = getattr(mod, item)
                if (isinstance(cls, type) and 
                    issubclass(cls, BaseModule) and 
                    cls != BaseModule):
                    modules.append(cls())
                    print(f"✅ 发现模块: {cls.name} by {cls.author}")
                    break
        except Exception as e:
            print(f"❌ 模块 {folder} 加载失败: {e}")
    
    return modules

# 版本信息
__version__ = "1.0.0"
__author__ = "DyberPet Team" 