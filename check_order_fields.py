import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "system", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询order表的所有字段名
cursor.execute("PRAGMA table_info(`order`)")
fields = cursor.fetchall()
print("订单表所有字段：")
for f in fields:
    print(f"字段名：{f[1]}，类型：{f[2]}")

conn.close()