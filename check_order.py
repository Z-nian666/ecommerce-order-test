import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "system", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. 统计订单总数
cursor.execute("SELECT COUNT(*) FROM `order`")
total = cursor.fetchone()[0]
print(f"订单总数：{total}")

# 2. 幂等性验证：查看有没有重复的request_id
cursor.execute("SELECT request_id, COUNT(*) as cnt FROM `order` GROUP BY request_id HAVING cnt > 1")
duplicate = cursor.fetchall()
if duplicate:
    print("❌ 发现重复订单：", duplicate)
else:
    print("✅ 无重复订单，幂等性验证通过")

# 3. 超卖防护验证：查询商品1当前库存
cursor.execute("SELECT stock FROM goods WHERE id = 1")
stock = cursor.fetchone()[0]
print(f"商品1当前库存：{stock}")
if stock >= 0:
    print("✅ 库存非负，超卖防护验证通过")
else:
    print("❌ 库存为负，出现超卖！")

conn.close()