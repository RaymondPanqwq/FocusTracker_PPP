"""
专注时间追踪器 - Windows 主程序入口
版本: v0.1（阶段一）
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 确保 data 目录存在
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

from config import DB_PATH
from core.db import init_db, get_device_id
from core.tracker import FocusTracker
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon


def main():
    print("=" * 50)
    print("  专注时间追踪器 v0.1")
    print("=" * 50)

    # 1. 初始化数据库
    init_db()
    device_id = get_device_id()
    print(f"[Main] 设备ID: {device_id}")
    print(f"[Main] 数据库: {DB_PATH}")

    # 2. 启动追踪引擎
    tracker = FocusTracker()
    tracker.start()

    # 3. 启动 Qt 应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，留在托盘

    # 4. 创建主窗口
    window = MainWindow(tracker)
    window.show()

    # 5. 创建系统托盘
    tray = TrayIcon(window, tracker, app)
    tray.show()

    # 6. 定时更新托盘信息
    tray_timer = QTimer()
    tray_timer.timeout.connect(tray.update_info)
    tray_timer.start(15000)  # 每 15 秒更新

    print("[Main] 程序启动完成！")

    # 7. 进入事件循环
    exit_code = app.exec()
    tracker.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()