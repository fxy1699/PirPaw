"""
模块功能自动发现和注册系统
自动扫描所有模块，发现可用的Function Call功能，并生成统一的工具描述
"""

import inspect
from typing import Dict, List, Any
from Agent.base_module import BaseModule


class ModuleFunctionRegistry:
    """模块功能注册中心"""
    
    def __init__(self, agent_core=None):
        self.agent_core = agent_core
        self.registered_modules = {}
        self.function_definitions = []
        self.function_map = {}  # function_name -> (module, function_name)
        
    def register_modules(self, modules: List[BaseModule]):
        """
        注册模块列表
        
        Args:
            modules (List[BaseModule]): 要注册的模块列表
        """
        self.registered_modules.clear()
        self.function_definitions.clear()
        self.function_map.clear()
        
        for module in modules:
            if not module.enabled:
                continue
                
            # 获取模块的Function定义
            definitions = module.get_function_definitions()
            if not definitions:
                continue
                
            module_name = module.__class__.__name__
            self.registered_modules[module_name] = module
            
            # 处理每个Function定义
            for definition in definitions:
                func_name = definition["name"]
                
                # 确保Function名称唯一（加模块前缀）
                unique_func_name = f"{module_name.lower().replace('module', '')}_{func_name}"
                
                # 创建工具定义
                tool_definition = {
                    "type": "function",
                    "function": {
                        "name": unique_func_name,
                        "description": f"[{module.name}] {definition['description']}",
                        "parameters": definition.get("parameters", {"type": "object", "properties": {}})
                    }
                }
                
                self.function_definitions.append(tool_definition)
                self.function_map[unique_func_name] = (module, func_name)
                
        print(f"🔧 模块功能注册完成: {len(self.function_definitions)} 个功能")
        self._print_registered_functions()
    
    def _print_registered_functions(self):
        """打印已注册的功能列表"""
        if not self.function_definitions:
            return
            
        print("📋 已注册的模块功能:")
        for definition in self.function_definitions:
            func_info = definition["function"]
            print(f"  • {func_info['name']}: {func_info['description']}")
    
    def get_tools_for_qwen_agent(self) -> List[Dict]:
        """
        获取符合qwen-agent格式的工具定义列表
        
        Returns:
            List[Dict]: 工具定义列表
        """
        return self.function_definitions
    
    def get_function_list_for_qwen_agent(self):
        """
        获取可供qwen-agent调用的函数列表
        
        Returns:
            list: Python函数列表
        """
        functions = []
        
        for func_name, (module, original_func_name) in self.function_map.items():
            # 创建调用包装函数
            def create_wrapper_function(mod, orig_name, display_name):
                def wrapper_function(**kwargs):
                    try:
                        print(f"🔧 调用 {mod.name} 模块的 {orig_name} 功能...")
                        print(f"📝 参数: {kwargs}")
                        
                        result = mod.call_function(orig_name, kwargs)
                        
                        print(f"✅ {display_name} 执行成功")
                        return str(result) if result is not None else f"{display_name} 执行完成"
                        
                    except Exception as e:
                        error_msg = f"❌ {display_name} 执行失败: {str(e)}"
                        print(error_msg)
                        return error_msg
                
                # 设置函数元数据
                wrapper_function.__name__ = display_name
                wrapper_function.__doc__ = f"调用{mod.name}模块的{orig_name}功能"
                
                return wrapper_function
            
            functions.append(create_wrapper_function(module, original_func_name, func_name))
        
        return functions
    
    def call_function_directly(self, function_name: str, arguments: dict):
        """
        直接调用指定的功能
        
        Args:
            function_name (str): 功能名称
            arguments (dict): 功能参数
            
        Returns:
            Any: 功能执行结果
        """
        if function_name not in self.function_map:
            raise ValueError(f"未找到功能: {function_name}")
        
        module, original_func_name = self.function_map[function_name]
        
        if not module.enabled:
            raise RuntimeError(f"模块 {module.name} 已禁用")
        
        return module.call_function(original_func_name, arguments)
    
    def get_available_functions(self) -> List[str]:
        """获取所有可用功能的名称列表"""
        return list(self.function_map.keys())
    
    def get_module_functions(self, module_name: str) -> List[str]:
        """获取指定模块的功能列表"""
        functions = []
        for func_name, (module, _) in self.function_map.items():
            if module.__class__.__name__.lower().replace('module', '') in module_name.lower():
                functions.append(func_name)
        return functions
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """获取功能的详细信息"""
        if function_name not in self.function_map:
            return None
        
        module, original_func_name = self.function_map[function_name]
        
        # 找到对应的工具定义
        for definition in self.function_definitions:
            if definition["function"]["name"] == function_name:
                return {
                    "name": function_name,
                    "original_name": original_func_name,
                    "module": module.name,
                    "description": definition["function"]["description"],
                    "parameters": definition["function"]["parameters"],
                    "enabled": module.enabled
                }
        
        return None 