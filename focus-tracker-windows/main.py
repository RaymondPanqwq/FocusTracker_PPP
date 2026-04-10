# main.py 顶部替换原来的路径处理
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

def get_base_dir():
    """
    兼容直接运行(.py)和打包运行(.exe)两种模式
    - 打包后: sys._MEIPASS 是临时解压目录（只读资源）
    - 运行时数据（db等）始终放在 EXE 同级目录
    """
    if getattr(sys, 'frozen', False):
        # 打包后 EXE 所在目录（可写）
        return os.path.dirname(sys.executable)
    else:
        # 开发模式
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_dir():
    """获取只读资源目录（assets等）"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS   # PyInstaller 解压的临时目录
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
RESOURCE_DIR = get_resource_dir()

# data 目录始终在 EXE 同级
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ⚠️ 在 import config 之前注入路径
import config
config.BASE_DIR = BASE_DIR
config.DB_PATH = os.path.join(BASE_DIR, "data", "focus_tracker.db")
config.RESOURCE_DIR = RESOURCE_DIR

from core.db import init_db, get_device_id
from core.tracker import FocusTracker
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon

def main():
    print("=" * 50)
    print("  专注时间追踪器 v0.1")
    print("=" * 50)

    init_db()
    device_id = get_device_id()
    print(f"[Main] 设备ID: {device_id}")
    print(f"[Main] 数据库: {config.DB_PATH}")

    tracker = FocusTracker()
    tracker.start()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(tracker)
    window.show()

    # ⚠️ 图标路径使用资源目录
    tray = TrayIcon(window, tracker, app,
                    icon_path=os.path.join(RESOURCE_DIR, "assets", "paimon1.ico"))
    tray.show()

    tray_timer = QTimer()
    tray_timer.timeout.connect(tray.update_info)
    tray_timer.start(15000)

    print("[Main] 程序启动完成！")

    exit_code = app.exec()
    tracker.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()