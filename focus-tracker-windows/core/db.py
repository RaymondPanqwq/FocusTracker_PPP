"""SQLite 数据库操作模块"""
import sqlite3
import uuid
import time
from datetime import datetime, timezone
from config import DB_PATH


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    return conn


def init_db():
    """初始化数据库，创建所有表"""
    conn = get_connection()
    cursor = conn.cursor()

    # App 使用记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            date TEXT NOT NULL,
            app_package TEXT NOT NULL,
            app_name TEXT NOT NULL,
            duration_sec INTEGER DEFAULT 0,
            updated_at INTEGER NOT NULL,
            synced INTEGER DEFAULT 0,
            UNIQUE(device_id, date, app_package)
        )
    """)

    # 设备信息表（存储本机 UUID）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_info (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # 番茄钟记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pomodoro_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time INTEGER NOT NULL,
            duration_min INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            synced INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] 数据库初始化完成")


def get_device_id():
    """获取或生成设备唯一 ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM device_info WHERE key = 'device_id'")
    row = cursor.fetchone()

    if row:
        device_id = row["value"]
    else:
        device_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO device_info (key, value) VALUES (?, ?)",
            ("device_id", device_id)
        )
        conn.commit()
        print(f"[DB] 生成新设备ID: {device_id}")

    conn.close()
    return device_id


def update_usage(device_id: str, app_package: str, app_name: str, seconds: int):
    """更新某个 App 的今日使用时长（累加）"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_ts = int(time.time())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage_records (device_id, date, app_package, app_name, duration_sec, updated_at, synced)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        ON CONFLICT(device_id, date, app_package)
        DO UPDATE SET
            duration_sec = duration_sec + ?,
            updated_at = ?,
            synced = 0
    """, (device_id, today, app_package, app_name, seconds, now_ts, seconds, now_ts))

    conn.commit()
    conn.close()


def get_today_usage(device_id: str):
    """获取今日所有 App 使用时长"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT app_package, app_name, duration_sec
        FROM usage_records
        WHERE device_id = ? AND date = ?
        ORDER BY duration_sec DESC
    """, (device_id, today))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_today_total(device_id: str):
    """获取今日总专注时长（秒）"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(duration_sec), 0) as total
        FROM usage_records
        WHERE device_id = ? AND date = ?
    """, (device_id, today))

    total = cursor.fetchone()["total"]
    conn.close()
    return total
