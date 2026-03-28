"""Windows 前台窗口监控模块"""
import win32gui
import win32process
import psutil


class WindowMonitor:
    """检测当前前台活跃窗口"""

    def get_active_window_info(self):
        """获取当前前台窗口的进程名和窗口标题"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None, None

            window_title = win32gui.GetWindowText(hwnd)
            if not window_title:
                return None, None

            # 获取窗口对应的进程
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name()  # 例如 "code.exe"

            return process_name, window_title

        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return None, None

    def get_friendly_name(self, process_name: str, window_title: str) -> str:
        """把进程名转换成友好的 App 名称"""
        name_map = {
            "code.exe": "VS Code",
            "WINWORD.EXE": "Microsoft Word",
            "EXCEL.EXE": "Microsoft Excel",
            "POWERPNT.EXE": "PowerPoint",
            "chrome.exe": "Google Chrome",
            "msedge.exe": "Microsoft Edge",
            "firefox.exe": "Firefox",
            "explorer.exe": "文件管理器",
            "WindowsTerminal.exe": "Windows Terminal",
            "cmd.exe": "命令提示符",
            "python.exe": "Python",
            "pycharm64.exe": "PyCharm",
        }
        return name_map.get(process_name, process_name.replace(".exe", ""))
