import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "system", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 把id=1的商品库存重置为100
try:
    cursor.execute("UPDATE goods SET stock = 100 WHERE id = 1")
    conn.commit()
    stock = cursor.execute("SELECT stock FROM goods WHERE id = 1").fetchone()[0]
    print(f"库存重置成功，当前商品1库存：{stock}")
except Exception as e:
    print("出错了：", e)
finally:
    conn.close()