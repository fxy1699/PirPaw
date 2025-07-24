#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PetAction模块安装脚本
帮助用户安装和配置宠物动作控制模块
"""

import os
import sys
import subprocess
import importlib.util


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True


def install_package(package_name, description=""):
    """安装Python包"""
    try:
        # 先检查是否已安装
        spec = importlib.util.find_spec(package_name.replace("-", "_"))
        if spec is not None:
            print(f"✅ {package_name} 已安装")
            return True
        
        print(f"📦 安装 {package_name}... {description}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package_name} 安装成功")
            return True
        else:
            print(f"❌ {package_name} 安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装 {package_name} 时出现异常: {e}")
        return False


def install_dependencies():
    """安装PetAction模块的依赖"""
    print("📦 安装PetAction模块依赖...")
    print("=" * 50)
    
    dependencies = [
        ("fuzzywuzzy", "模糊字符串匹配库"),
        ("python-Levenshtein", "提高fuzzywuzzy性能的可选依赖")
    ]
    
    success_count = 0
    
    for package, description in dependencies:
        if install_package(package, description):
            success_count += 1
    
    print(f"\n📊 依赖安装结果: {success_count}/{len(dependencies)} 成功")
    
    if success_count == len(dependencies):
        print("✅ 所有依赖安装成功！")
        return True
    else:
        print("⚠️ 部分依赖安装失败，模块功能可能受限")
        return False


def verify_dyber_pet_structure():
    """验证DyberPet目录结构"""
    print("\n🔍 验证DyberPet目录结构...")
    
    # 检查项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 检查DyberPet目录
    dyber_pet_path = os.path.join(project_root, "DyberPet")
    if not os.path.exists(dyber_pet_path):
        print(f"❌ 未找到DyberPet目录: {dyber_pet_path}")
        return False
    
    print(f"✅ 找到DyberPet目录: {dyber_pet_path}")
    
    # 检查资源目录
    res_path = os.path.join(project_root, "res")
    if not os.path.exists(res_path):
        print(f"❌ 未找到资源目录: {res_path}")
        return False
    
    print(f"✅ 找到资源目录: {res_path}")
    
    # 检查宠物目录
    role_path = os.path.join(res_path, "role")
    pet_path = os.path.join(res_path, "pet")
    
    role_count = len(os.listdir(role_path)) if os.path.exists(role_path) else 0
    pet_count = len(os.listdir(pet_path)) if os.path.exists(pet_path) else 0
    
    print(f"📁 角色目录: {role_count} 个角色")
    print(f"📁 宠物目录: {pet_count} 个宠物")
    
    if role_count + pet_count == 0:
        print("⚠️ 未找到任何宠物资源")
        return False
    
    print(f"✅ 目录结构验证通过")
    return True


def test_module():
    """测试模块功能"""
    print("\n🧪 测试PetAction模块...")
    
    try:
        # 添加项目根目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # 导入模块
        from Agent.modules.pet_action.module import PetActionModule
        
        print("✅ 模块导入成功")
        
        # 初始化模块
        module = PetActionModule()
        module.setup()
        
        if module.enabled:
            print("✅ 模块初始化成功")
            
            # 测试基本功能
            capabilities = module.get_capabilities()
            print(f"✅ 模块能力: {len(capabilities)} 项")
            
            # 测试消息处理
            test_message = "站立"
            response = module.handle_message(test_message)
            if response:
                print(f"✅ 消息处理测试通过: '{test_message}' -> '{response[:50]}...'")
            else:
                print("⚠️ 消息处理测试无响应")
            
            module.cleanup()
            return True
        else:
            print("❌ 模块初始化失败")
            return False
            
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 模块测试失败: {e}")
        return False


def update_requirements():
    """更新requirements.txt文件"""
    print("\n📝 更新requirements.txt...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(current_dir, "requirements.txt")
    
    new_deps = [
        "# PetAction模块额外依赖",
        "fuzzywuzzy>=0.18.0             # 模糊字符串匹配",
        "python-Levenshtein>=0.12.0     # 提高fuzzywuzzy性能"
    ]
    
    try:
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已经添加
            if "fuzzywuzzy" in content:
                print("✅ requirements.txt 已包含PetAction依赖")
                return True
            
            # 添加新依赖
            with open(requirements_path, 'a', encoding='utf-8') as f:
                f.write("\n\n")
                f.write("\n".join(new_deps))
                f.write("\n")
            
            print("✅ 已更新requirements.txt")
            return True
        else:
            print(f"⚠️ 未找到requirements.txt文件: {requirements_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新requirements.txt失败: {e}")
        return False


def create_demo_script():
    """创建演示脚本"""
    print("\n📋 创建演示脚本...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    demo_path = os.path.join(current_dir, "demo_pet_action.py")
    
    demo_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PetAction模块演示脚本
展示Agent如何控制DyberPet动作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.modules.pet_action.module import PetActionModule


def main():
    """主演示函数"""
    print("🎭 PetAction模块演示")
    print("=" * 50)
    
    # 初始化模块
    module = PetActionModule()
    module.setup()
    
    if not module.enabled:
        print("❌ 模块初始化失败")
        return
    
    print("✅ 模块初始化成功")
    
    # 显示能力
    capabilities = module.get_capabilities()
    print(f"\\n🎯 模块能力:")
    for cap in capabilities:
        print(f"  • {cap}")
    
    # 交互式测试
    print(f"\\n💬 交互式测试 (输入'quit'退出):")
    print("尝试输入: '让小猫睡觉', '走路', '站立', '开心', '状态'等")
    
    while True:
        try:
            user_input = input("\\n👤 用户: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                break
            
            if not user_input:
                continue
            
            response = module.handle_message(user_input)
            if response:
                print(f"🤖 AI: {response}")
            else:
                print("🤖 AI: (此消息不是动作相关)")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 处理异常: {e}")
    
    module.cleanup()
    print("\\n👋 演示结束！")


if __name__ == "__main__":
    main()
'''
    
    try:
        with open(demo_path, 'w', encoding='utf-8') as f:
            f.write(demo_content)
        
        print(f"✅ 演示脚本已创建: {demo_path}")
        return True
    except Exception as e:
        print(f"❌ 创建演示脚本失败: {e}")
        return False


def main():
    """主安装函数"""
    print("🚀 PetAction模块安装程序")
    print("=" * 50)
    
    success_count = 0
    total_steps = 6
    
    # 1. 检查Python版本
    if check_python_version():
        success_count += 1
    
    # 2. 安装依赖
    if install_dependencies():
        success_count += 1
    
    # 3. 验证目录结构
    if verify_dyber_pet_structure():
        success_count += 1
    
    # 4. 测试模块
    if test_module():
        success_count += 1
    
    # 5. 更新requirements
    if update_requirements():
        success_count += 1
    
    # 6. 创建演示脚本
    if create_demo_script():
        success_count += 1
    
    # 总结
    print("\n" + "=" * 50)
    print(f"📊 安装结果: {success_count}/{total_steps} 步骤成功")
    
    if success_count == total_steps:
        print("🎉 PetAction模块安装完成！")
        print("\n📋 下一步:")
        print("1. 运行 'python Agent/demo_pet_action.py' 测试功能")
        print("2. 在Agent系统中使用 '让小猫睡觉' 等指令控制宠物")
        print("3. 查看模块文档了解更多功能")
    else:
        print("⚠️ 安装过程中遇到一些问题，请检查上面的错误信息")
    
    print("=" * 50)


if __name__ == "__main__":
    main() 