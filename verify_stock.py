import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "system", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT stock FROM goods WHERE id = 1")
stock = cursor.fetchone()[0]
print(f"压测后商品1库存：{stock}")

if stock >= 0:
    print("✅ 库存非负，高并发下无超卖，行锁防护生效")
else:
    print("❌ 库存为负，出现超卖")

# 顺便统计订单总数
cursor.execute("SELECT COUNT(*) FROM `order`")
total = cursor.fetchone()[0]
print(f"订单总数：{total}")
print(f"库存扣减量：{100 - stock}")
print(f"扣减量与订单数差值：{abs((100 - stock) - total)}")

conn.close()