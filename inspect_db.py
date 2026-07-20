import sqlite3

conn = sqlite3.connect("data/cleaned_data.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = cur.fetchall()
    print(f"\n--- {t} ---")
    for c in cols:
        print(f"  {c[1]} ({c[2]})")
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  Row count: {cur.fetchone()[0]}")
    cur.execute(f"SELECT * FROM {t} LIMIT 2")
    rows = cur.fetchall()
    for row in rows:
        print(f"  Sample: {row}")

conn.close()
