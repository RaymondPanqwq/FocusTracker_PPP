"""全局配置常量"""
import os

# 数据库路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "focus_tracker.db")

# 监控间隔（秒）
POLL_INTERVAL = 3  # 每3秒检测一次前台窗口

# 失焦暂停阈值（秒）
IDLE_THRESHOLD = 30  # 失焦超过30秒暂停计时

# 设备信息
DEVICE_ID = None  # 首次运行时自动生成 UUID
DEVICE_NAME = os.environ.get("COMPUTERNAME", "Windows PC")
PLATFORM = "windows"