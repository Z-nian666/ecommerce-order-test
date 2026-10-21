import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "system", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. 添加request_id字段，允许为空，默认NULL
    cursor.execute("ALTER TABLE `order` ADD COLUMN request_id VARCHAR(64) NULL")
    print("✅ 字段添加成功")

    # 2. 给request_id加唯一索引（NULL不触发冲突，符合幂等需求）
    cursor.execute("CREATE UNIQUE INDEX idx_order_request_id ON `order`(request_id)")
    print("✅ 唯一索引添加成功")

    conn.commit()
except Exception as e:
    print("出错了：", e)
finally:
    conn.close()