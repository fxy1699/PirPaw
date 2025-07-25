import win32gui
import win32process
import psutil

def is_video_playing_in_window(hwnd):
    """检测单个窗口是否在播放视频"""
    try:
        # 获取窗口标题
        window_title = win32gui.GetWindowText(hwnd)
        if not window_title:
            return False
        # 获取进程ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return False
        # 获取进程对象
        process = psutil.Process(pid)
        process_name = process.name().lower()
        # 常见视频播放器进程名匹配
        video_players = {
            "vlc.exe", "potplayer.exe", "mpv.exe", 
            "kmplayer.exe", "nplayer.exe"
        }
        # 场景浏览器
        web_browsers = {
            "chrome.exe", "firefox.exe", "edge.exe", 
            "safari.exe", "opera.exe"
        }
        # 浏览器视频播放标题关键词匹配
        browser_keywords = {
            "youtube", "bilibili", "video", "netflix"
        }
        # 判断逻辑
        if process_name in video_players:
            print(f"[INFO] Video playing in video_players: {process_name}, window_title: {window_title}")
            return True  # 匹配到独立播放器进程
        elif process_name in web_browsers and any(keyword.lower() in window_title.lower() for keyword in browser_keywords):
            print(f"[INFO] Video playing in browser: {window_title}, process_name: {process_name}")
            return True  # 是浏览器进程 && 匹配到浏览器视频关键词
    except Exception:
        return False
    return False

def is_any_video_playing():
    """遍历所有可见且未被最小化的窗口检测视频播放"""
    def enum_window_callback(hwnd, _):
        # 排除不可见窗口
        if not win32gui.IsWindowVisible(hwnd):
            return True
        # 排除最小化窗口
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == 2:  # 2 corresponds to SW_SHOWMINIMIZED
            return True
        # 检测视频播放状态
        if is_video_playing_in_window(hwnd):
            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)
            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            # 获取进程对象
            process = psutil.Process(pid)
            process_name = process.name().lower()
            # 打印窗口句柄和进程信息
            print(f"[INFO] Video playing in window: hwnd={hwnd}, process_name={process_name}, window_title={window_title}")
            raise RuntimeError("Video found")
        return True
    try:
        win32gui.EnumWindows(enum_window_callback, None)
    except RuntimeError:
        return True  # 捕获到视频窗口存在信号
    return False  # 所有窗口均未播放视频 