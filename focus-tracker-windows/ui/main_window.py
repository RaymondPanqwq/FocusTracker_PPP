"""主窗口 - 今日使用时长列表"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from core.db import get_today_usage, get_today_total, get_device_id


class MainWindow(QMainWindow):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        self.device_id = get_device_id()
        self.setWindowTitle("专注时间追踪器 v0.1")
        self.setMinimumSize(800, 600)

        # 设置主控件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # === 顶部：今日总时长 ===
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #4A90D9;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header)

        title_label = QLabel("今日专注总时长")
        title_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        self.total_label = QLabel("0小时 0分钟")
        self.total_label.setFont(QFont("Microsoft YaHei", 36, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: white;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.total_label)

        self.status_label = QLabel("● 正在追踪中...")
        self.status_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.status_label)

        layout.addWidget(header)

        # === 中部：App 使用排行 ===
        table_title = QLabel("📊 今日 App 使用排行")
        table_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["App 名称", "进程名", "使用时长"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # === 底部按钮 ===
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 刷新数据")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90D9;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_data)
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)

        # 定时刷新（每 10 秒更新界面）
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(10000)

        # 首次加载
        self.refresh_data()

    def refresh_data(self):
        """刷新今日数据"""
        # 更新总时长
        total_sec = get_today_total(self.device_id)
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        self.total_label.setText(f"{hours}小时 {minutes}分钟")

        # 更新当前追踪状态
        if self.tracker.current_app:
            friendly = self.tracker.monitor.get_friendly_name(
                self.tracker.current_app, ""
            )
            self.status_label.setText(f"● 正在追踪: {friendly}")
        else:
            self.status_label.setText("○ 等待活跃窗口...")

        # 更新表格
        records = get_today_usage(self.device_id)
        self.table.setRowCount(len(records))

        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(record["app_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(record["app_package"]))

            # 格式化时长
            sec = record["duration_sec"]
            if sec >= 3600:
                time_str = f"{sec // 3600}h {(sec % 3600) // 60}m"
            elif sec >= 60:
                time_str = f"{sec // 60}m {sec % 60}s"
            else:
                time_str = f"{sec}s"
            self.table.setItem(i, 2, QTableWidgetItem(time_str))

    def closeEvent(self, event):
        """点击关闭按钮时最小化到托盘（而不是退出）"""
        event.ignore()
        self.hide()
