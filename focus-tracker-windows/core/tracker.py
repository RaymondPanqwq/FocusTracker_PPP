"""使用时长追踪引擎 - 核心计时逻辑"""
import time
import threading
from core.monitor import WindowMonitor
from core.db import update_usage, get_device_id
from config import POLL_INTERVAL, IDLE_THRESHOLD


class FocusTracker:
    """定时轮询前台窗口，累计 App 使用时长"""

    def __init__(self):
        self.monitor = WindowMonitor()
        self.device_id = get_device_id()
        self.running = False
        self._thread = None

        # 当前追踪状态
        self.current_app = None       # 当前前台 App 进程名
        self.current_title = None     # 当前窗口标题
        self.current_start = None     # 当前 App 开始计时时间
        self.last_active_time = None  # 上次检测到活跃的时间

        # 白名单（空列表 = 追踪所有 App）
        self.whitelist = []

        # 回调函数：当前台 App 变化时触发（UI 可注册）
        self.on_app_change = None
        self.on_duration_update = None

    def start(self):
        """启动追踪（在后台线程运行）"""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        print(f"[Tracker] 开始追踪，设备ID: {self.device_id}")

    def stop(self):
        """停止追踪"""
        self.running = False
        self._save_current()
        print("[Tracker] 停止追踪")

    def _poll_loop(self):
        """核心轮询循环"""
        while self.running:
            process_name, window_title = self.monitor.get_active_window_info()
            now = time.time()

            if process_name:
                self.last_active_time = now

                # 检查是否切换了 App
                if process_name != self.current_app:
                    # 保存上一个 App 的使用时长
                    self._save_current()

                    # 开始追踪新 App
                    self.current_app = process_name
                    self.current_title = window_title
                    self.current_start = now

                    friendly_name = self.monitor.get_friendly_name(
                        process_name, window_title
                    )
                    print(f"[Tracker] 切换到: {friendly_name} ({process_name})")

                    # 触发回调
                    if self.on_app_change:
                        self.on_app_change(process_name, friendly_name)

            else:
                # 无法检测到前台窗口（可能锁屏/最小化）
                if (self.last_active_time and
                        now - self.last_active_time > IDLE_THRESHOLD):
                    # 超过阈值，暂停计时
                    self._save_current()
                    self.current_app = None
                    self.current_start = None

            time.sleep(POLL_INTERVAL)

    def _save_current(self):
        """将当前 App 的使用时长写入数据库"""
        if self.current_app and self.current_start:
            elapsed = int(time.time() - self.current_start)

            if elapsed <= 0:
                return

            # 白名单过滤
            if self.whitelist and self.current_app not in self.whitelist:
                self.current_start = time.time()
                return

            friendly_name = self.monitor.get_friendly_name(
                self.current_app, self.current_title or ""
            )

            update_usage(
                device_id=self.device_id,
                app_package=self.current_app,
                app_name=friendly_name,
                seconds=elapsed,
            )

            print(f"[Tracker] 记录: {friendly_name} +{elapsed}秒")

            # 重置起始时间（避免重复计时）
            self.current_start = time.time()

            # 触发回调
            if self.on_duration_update:
                self.on_duration_update()
