import sqlite3
import os

# 数据库文件路径
db_path = os.path.join(os.path.dirname(__file__), "system", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. 超卖防护验证
cursor.execute("SELECT stock FROM goods WHERE id = 1")
stock = cursor.fetchone()[0]
print(f"压测后商品1库存：{stock}")
if stock >= 0:
    print("✅ 库存非负，高并发下无超卖，行锁防护生效")
else:
    print("❌ 库存为负，出现超卖")

# 2. 接口幂等性验证
cursor.execute("""
    SELECT request_id, COUNT(*) as cnt 
    FROM `order` 
    WHERE request_id IS NOT NULL 
    GROUP BY request_id 
    HAVING cnt > 1
""")
duplicate = cursor.fetchall()
print(f"重复订单数量：{len(duplicate)}")
if len(duplicate) == 0:
    print("✅ 无重复订单，幂等性验证通过")
else:
    print("❌ 存在重复订单，幂等失效")

conn.close()
