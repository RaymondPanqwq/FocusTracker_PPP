"""系统托盘图标"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from core.db import get_today_total, get_device_id


class TrayIcon(QSystemTrayIcon):  
    def __init__(self, main_window, tracker, app, icon_path="assets/paimon1.ico"):  
        super().__init__()  
        self.main_window = main_window
        self.tracker = tracker
        self.app = app
        self.device_id = get_device_id()

        # 设置图标
        self.setIcon(QIcon(icon_path))  # 使用传入路径  
        self.setToolTip("专注时间追踪器")

        # 创建右键菜单
        menu = QMenu()

        self.time_action = QAction("今日: 计算中...")
        self.time_action.setEnabled(False)
        menu.addAction(self.time_action)

        self.current_action = QAction("当前: 无")
        self.current_action.setEnabled(False)
        menu.addAction(self.current_action)

        menu.addSeparator()

        show_action = QAction("打开主界面")
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("退出")
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

        # 单击托盘图标切换主界面显示
        self.activated.connect(self._on_activated)

    def update_info(self):
        """更新托盘菜单中显示的信息"""
        total = get_today_total(self.device_id)
        hours = total // 3600
        minutes = (total % 3600) // 60
        self.time_action.setText(f"今日: {hours}h {minutes}m")

        if self.tracker.current_app:
            name = self.tracker.monitor.get_friendly_name(
                self.tracker.current_app, ""
            )
            self.current_action.setText(f"当前: {name}")
        else:
            self.current_action.setText("当前: 无活跃窗口")

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        self.main_window.refresh_data()

    def _quit(self):
        self.tracker.stop()
        self.app.quit()