import time
import psutil
import win32gui
import win32process
import win32con
import comtypes
from pycaw.pycaw import AudioUtilities, IAudioSessionControl
from functools import lru_cache

def get_process_info_by_hwnd(hwnd):
    """
    根据窗口句柄获取进程名和窗口标题
    """
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = ""
        window_title = ""
        if pid:
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except Exception:
                process_name = ""
        try:
            window_title = win32gui.GetWindowText(hwnd)
        except Exception:
            window_title = ""
        return pid, process_name, window_title
    except Exception:
        return None, "", ""

def is_window_visible_and_foreground(hwnd):
    """
    检查指定窗口是否可见、未最小化且未被其他顶层窗口完全遮挡。
    更精确地判断窗口是否在用户视野内（即使不是前台窗口，只要没有被完全遮挡也算可见）。
    增加详细debug输出，便于排查判定逻辑。
    debug输出涉及到进程编号的都加上进程名和窗口名。
    """
    try:
        pid, process_name, window_title = get_process_info_by_hwnd(hwnd)
        # 是否可见
        if not win32gui.IsWindowVisible(hwnd):
            print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 不可见")
            return False
        # 是否最小化
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == 2:  # 2 = 最小化
            print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 已最小化")
            return False

        # 获取目标窗口矩形
        rect = win32gui.GetWindowRect(hwnd)
        if rect[0] == rect[2] or rect[1] == rect[3]:
            # 无效窗口
            print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 窗口矩形无效: {rect}")
            return False
        print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 初步可见，窗口矩形: {rect}")

        # 获取所有顶层窗口，按Z序从上到下
        hwnd_list = []
        def enum_windows_callback(h, _):
            if win32gui.IsWindowVisible(h):
                hwnd_list.append(h)
            return True
        win32gui.EnumWindows(enum_windows_callback, None)
        print(f"[Debug][is_window_visible_and_foreground] Z序顶层窗口数量: {len(hwnd_list)}")

        # 目标窗口在Z序中的索引
        try:
            idx = hwnd_list.index(hwnd)
            print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 在Z序中的索引: {idx}")
        except ValueError:
            print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 不在顶层窗口列表中")
            return False

        # 检查目标窗口上方的所有可见窗口是否有完全遮挡
        for h in hwnd_list[:idx]:
            if h == hwnd:
                continue
            if not win32gui.IsWindowVisible(h):
                continue
            placement2 = win32gui.GetWindowPlacement(h)
            if placement2[1] == 2:
                continue
            rect2 = win32gui.GetWindowRect(h)
            l1, t1, r1, b1 = rect
            l2, t2, r2, b2 = rect2
            pid2, process_name2, window_title2 = get_process_info_by_hwnd(h)
            if l2 <= l1 and t2 <= t1 and r2 >= r1 and b2 >= b1:
                print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 被上方窗口 hwnd={h} pid={pid2} 进程名={process_name2} 窗口名={window_title2} 完全遮挡，遮挡窗口矩形: {rect2}")
                return False
            else:
                # 输出部分遮挡信息
                if not (r2 <= l1 or l2 >= r1 or b2 <= t1 or t2 >= b1):
                    print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 被上方窗口 hwnd={h} pid={pid2} 进程名={process_name2} 窗口名={window_title2} 部分重叠，遮挡窗口矩形: {rect2}")

        # 没有被完全遮挡，认为可见
        print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} pid={pid} 进程名={process_name} 窗口名={window_title} 没有被完全遮挡，判定为可见")
        return True
    except Exception as e:
        print(f"[Debug][is_window_visible_and_foreground] hwnd={hwnd} 异常: {e}")
        return False

class VideoPlaybackDetector:
    def __init__(self):
        # 缓存最近检测结果，避免频繁调用系统API
        self.last_check_time = 0
        self.last_result = False
        self.cache_duration = 1.0  # 1秒缓存有效期

    @lru_cache(maxsize=32)
    def is_browser_video_playing(self, hwnd, process_name):
        """专门检测浏览器内的视频元素（不受静音影响）"""
        try:
            # 关键修复：获取真正的浏览器主窗口
            root_hwnd = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
            window_title = win32gui.GetWindowText(root_hwnd)

            # 验证是否为浏览器主窗口
            browser_titles = {
                "msedge.exe": "Microsoft Edge",
                "chrome.exe": "Google Chrome",
                "firefox.exe": "Mozilla Firefox"
            }
            browser_id = browser_titles.get(process_name, "")
            if browser_id and browser_id not in window_title:
                return False

            # 检查标题是否包含视频关键词
            video_keywords = {
                "youtube", "bilibili", "video", "netflix", "vimeo", "dailymotion",
                "twitch", "youtu.be", "vidéo", "filme", "movie", "stream", "live",
                "tv", "television", "影院", "影视", "电影", "电视剧", "直播", "赛事"
            }
            if any(keyword in window_title.lower() for keyword in video_keywords):
                # 检查窗口是否可见且在前台
                if is_window_visible_and_foreground(root_hwnd):
                    return True
                else:
                    return False
            return False
        except:
            return False

    def is_media_session_active(self):
        """检测媒体会话（适用于有声音频）"""
        try:
            sessions = AudioUtilities.GetAllSessions()
            video_players = {"vlc.exe", "potplayer.exe", "mpv.exe", "kmplayer.exe", "nplayer.exe"}
            browsers = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"}

            debug_audio_processes = []

            for session in sessions:
                try:
                    # 检查会话是否活跃
                    if session.State != 1:  # 1 = Active
                        continue

                    session_ctl = session.QueryInterface(IAudioSessionControl)
                    pid = session_ctl.GetProcessId()
                    if pid == 0:
                        continue

                    try:
                        process = psutil.Process(pid)
                        process_name = process.name().lower()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                    # 查找主窗口名
                    hwnd = self._find_main_window_by_pid(pid)
                    window_title = ""
                    if hwnd:
                        try:
                            window_title = win32gui.GetWindowText(hwnd)
                        except:
                            window_title = ""
                    debug_audio_processes.append((process_name, window_title))

                    # 检查是否是视频播放器
                    if process_name in video_players:
                        # 检查播放器主窗口是否可见
                        if hwnd and is_window_visible_and_foreground(hwnd):
                            print(f"[WatchTV - Debug] 检测到音频进程: {process_name}，窗口名: {window_title}")
                            return True
                        else:
                            continue

                    # 检查浏览器视频
                    if process_name in browsers:
                        try:
                            # 即使静音，浏览器媒体会话通常仍会报告标题
                            display_name = session_ctl.GetDisplayName()
                            if display_name:
                                video_keywords = {"video", "youtube", "bilibili", "netflix"}
                                if any(kw in display_name.lower() for kw in video_keywords):
                                    # 检查浏览器主窗口是否可见
                                    if hwnd and is_window_visible_and_foreground(hwnd):
                                        print(f"[WatchTV - Debug] 检测到音频进程: {process_name}，窗口名: {window_title}")
                                        return True
                                    else:
                                        continue
                        except:
                            # 无法获取标题时，假设浏览器可能在播放视频
                            if hwnd and is_window_visible_and_foreground(hwnd):
                                print(f"[WatchTV - Debug] 检测到音频进程: {process_name}，窗口名: {window_title}")
                                return True
                            else:
                                continue
                except:
                    continue
        except:
            pass
        return False

    def _find_main_window_by_pid(self, pid):
        """根据进程ID查找主窗口句柄"""
        result = []
        def callback(hwnd, _):
            try:
                _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
                if win_pid == pid and win32gui.IsWindowVisible(hwnd):
                    # 只返回顶层窗口
                    if win32gui.GetWindow(hwnd, win32con.GW_OWNER) == 0:
                        result.append(hwnd)
                        return False
            except:
                pass
            return True
        try:
            win32gui.EnumWindows(callback, None)
            if result:
                return result[0]
        except:
            pass
        return None

    def is_window_playing_video(self):
        """
        检测窗口标题和进程（解决静音问题）

        修正逻辑：只要窗口标题包含视频关键词且窗口可见，就判定为有视频播放（不再依赖is_browser_video_playing的二次判断）。
        """
        found = [False]
        debug_window_processes = []

        # 视频关键词，支持中英文和常见视频网站
        video_keywords = [
            "youtube", "bilibili", "video", "netflix", "vimeo", "dailymotion",
            "twitch", "youtu.be", "vidéo", "filme", "movie", "stream", "live",
            "tv", "television", "影院", "影视", "电影", "电视剧", "直播", "赛事",
            "腾讯视频", "爱奇艺", "优酷"
        ]

        def enum_window_callback(hwnd, _):
            try:
                # 排除不可见和最小化窗口
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] == 2:  # 最小化
                    return True

                # 获取进程ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if not pid:
                    return True

                # 获取进程信息
                try:
                    process = psutil.Process(pid)
                    process_name = process.name().lower()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return True

                # 只关注浏览器和视频播放器
                if process_name not in {"chrome.exe", "msedge.exe", "firefox.exe", "vlc.exe", "potplayer.exe"}:
                    return True

                # 获取根窗口和标题
                root_hwnd = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
                window_title = win32gui.GetWindowText(root_hwnd)

                debug_window_processes.append((process_name, window_title))

                # 只要窗口标题包含视频关键词且窗口可见，就判定为有视频播放
                if any(kw in window_title.lower() for kw in video_keywords):
                    if is_window_visible_and_foreground(root_hwnd):
                        print(f"[WatchTV - Debug] 检测到窗口进程: {process_name}，窗口名: {window_title}")
                        found[0] = True
                        return False  # 停止枚举
                    else:
                        return True

                # 对于本地播放器（如VLC、PotPlayer），只要窗口可见即可
                if process_name in {"vlc.exe", "potplayer.exe"} and window_title:
                    if is_window_visible_and_foreground(root_hwnd):
                        print(f"[WatchTV - Debug] 检测到窗口进程: {process_name}，窗口名: {window_title}")
                        found[0] = True
                        return False
                    else:
                        return True

            except Exception as e:
                pass
            return True

        try:
            win32gui.EnumWindows(enum_window_callback, None)
        except:
            pass

        # Debug output: print all enumerated process names and window titles
        if debug_window_processes:
            process_info = [f"{proc} - {title}" for proc, title in debug_window_processes]
            print(f"[WatchTV - Debug] is_window_playing_video() 枚举到的进程和窗口名: {process_info}")

        return found[0]

    def is_video_playing_in_browser_via_alternative(self):
        """
        检测浏览器中是否有视频正在播放（增强版，支持多种检测方式）

        优先级：
        1. 尝试通过Selenium自动化检测浏览器标签页中的video元素是否在播放
        2. （可选）通过浏览器扩展通信（如WebSocket）检测
        3. 回退到窗口可见性和进程名的简单检测
        """
        try:
            # 1. 使用Selenium检测浏览器标签页中的video元素
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            import socket

            # 只检测已知浏览器
            browsers = ["chrome.exe", "msedge.exe", "firefox.exe"]
            # 检查本地是否有可用的浏览器进程
            browser_pids = []
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] and proc.info['name'].lower() in browsers:
                    browser_pids.append(proc.info['pid'])

            if not browser_pids:
                return False

            # 检查本地是否有Chrome调试端口开放（默认9222）
            def is_port_open(port):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.2)
                try:
                    s.connect(('127.0.0.1', port))
                    s.close()
                    return True
                except Exception:
                    return False

            # 只检测Chrome调试端口（9222），如有可用则用Selenium连接
            chrome_debug_port = 9222
            if is_port_open(chrome_debug_port):
                try:
                    chrome_options = Options()
                    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_debug_port}")
                    driver = webdriver.Chrome(options=chrome_options)
                    # 检查所有标签页是否有video元素正在播放
                    for handle in driver.window_handles:
                        driver.switch_to.window(handle)
                        # 检查页面是否有正在播放的视频
                        js = """
                        var videos = document.getElementsByTagName('video');
                        for (var i=0; i<videos.length; i++) {
                            if (!videos[i].paused && !videos[i].ended && videos[i].currentTime > 0) {
                                return true;
                            }
                        }
                        return false;
                        """
                        playing = driver.execute_script(js)
                        if playing:
                            driver.quit()
                            return True
                    driver.quit()
                except Exception as e:
                    # Selenium连接失败，降级到下一个方法
                    pass

            # 2. 预留：可扩展为通过WebSocket与浏览器扩展通信检测
            # 例如：监听本地端口，接收扩展发来的“有视频播放”信号
            # 这里仅为占位，实际实现需配合扩展开发
            # if self._browser_extension_reports_video():
            #     return True

            # 3. 回退：检测主窗口是否可见（原有逻辑）
            for pid in browser_pids:
                hwnd = self._find_main_window_by_pid(pid)
                if hwnd and is_window_visible_and_foreground(hwnd):
                    # 进一步可尝试通过窗口标题关键字判断
                    window_title = win32gui.GetWindowText(hwnd)
                    video_keywords = ["youtube", "bilibili", "netflix", "腾讯视频", "爱奇艺", "优酷", "video"]
                    if any(kw.lower() in window_title.lower() for kw in video_keywords):
                        return True
                    # 如果没有明显关键字，也可认为有浏览器视频窗口可见
                    # return True

            return False
        except Exception as e:
            # 捕获所有异常，保证不影响主流程
            return False

    def is_any_video_playing(self):
        """
        综合检测是否有视频正在播放（支持静音情况）

        检测优先级：
        1. 媒体会话API（有声音频）
        2. 窗口标题分析（解决静音问题）
        3. 浏览器专用检测（最可靠）
        4. 替代浏览器检测（最后手段）
        """
        # 添加缓存避免频繁检测
        current_time = time.time()
        if current_time - self.last_check_time < self.cache_duration:
            return self.last_result

        # 1. 首先检查媒体会话（有声音频）
        if self.is_media_session_active():
            print(f"[WatchTV - VideoDetect] 通过媒体会话检测到视频正在播放且窗口可见")
            self.last_check_time = current_time
            self.last_result = True
            return True

        # 2. 检查窗口标题（解决静音问题）
        if self.is_window_playing_video():
            print(f"[WatchTV - VideoDetect] 通过窗口标题检测到视频正在播放且窗口可见")
            self.last_check_time = current_time
            self.last_result = True
            return True

        # 3. 专门检测浏览器视频（最可靠）
        if self.is_video_playing_in_browser_via_alternative():
            print(f"[WatchTV - VideoDetect] 通过浏览器专用检测检测到视频正在播放且窗口可见")
            self.last_check_time = current_time
            self.last_result = True
            return True

        self.last_check_time = current_time
        self.last_result = False
        return False