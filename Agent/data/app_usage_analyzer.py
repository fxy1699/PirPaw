import json
import os
from typing import Dict, List, Tuple
from collections import defaultdict

def analyze_app_usage_by_windows(usage_file: str = None) -> Dict[str, Dict[str, float]]:
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
    with open(usage_file, 'r', encoding='utf-8') as f:
        usage_data = json.load(f)
    
    # 汇总所有应用和窗口的使用时长
    app_window_usage = defaultdict(lambda: defaultdict(float))
    
    # 遍历所有日期的数据
    for date, apps in usage_data.items():
        for app_name, app_data in apps.items():
            # 获取该应用的总使用时长
            total_seconds = app_data.get('total_seconds', 0)
            
            # 获取各个窗口的使用时长
            windows = app_data.get('windows', {})
            for window_name, window_seconds in windows.items():
                app_window_usage[app_name][window_name] += window_seconds
    
    # 转换为普通字典并排序
    result = {}
    for app_name, windows in app_window_usage.items():
        # 按使用时长降序排序窗口
        sorted_windows = dict(sorted(windows.items(), key=lambda x: x[1], reverse=True))
        result[app_name] = sorted_windows
    
    return result
# 使用示例
if __name__ == "__main__":
    try:
        # 获取所有应用和窗口的使用时长
        usage_data = analyze_app_usage_by_windows()
        
        print("=== 应用使用时长分析（按窗口） ===")
        for app_name, windows in usage_data.items():
            total_seconds = sum(windows.values())
            print(f"\n{app_name} (总计: {total_seconds:.2f}秒)")
            for window_name, seconds in list(windows.items())[:5]:  # 只显示前5个窗口
                print(f"  - {window_name}: {seconds:.2f}秒")
        
        print("\n=== 使用时长最长的前5个应用 ===")
        top_apps = get_top_apps_by_usage(top_n=5)
        for i, (app_name, seconds) in enumerate(top_apps, 1):
            print(f"{i}. {app_name}: {seconds:.2f}秒")
        
        print("\n=== Cursor应用中使用时长最长的前5个窗口 ===")
        cursor_windows = get_top_windows_by_app(app_name="Cursor", top_n=5)
        for i, (window_name, seconds) in enumerate(cursor_windows, 1):
            print(f"{i}. {window_name}: {seconds:.2f}秒")
            
    except Exception as e:
        print(f"分析过程中出现错误: {e}") 